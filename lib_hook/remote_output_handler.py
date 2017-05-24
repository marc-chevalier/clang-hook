import json
import pickle
import typing
import lib_hook


class ClientOutputHandler:
    def __init__(self, config, logger, socket):
        self.config = config
        self.logger = logger
        self.socket = socket

    def handle_output(self,
                      output: str,
                      stage: lib_hook.Stage,
                      input_file: typing.Union[str, typing.List[str]],
                      output_file: typing.Union[str, typing.List[str]]):

        request = pickle.dumps({
            "request_type": "output",
            "args": {
                "stage": lib_hook.stage_to_str(stage),
                "input_file": input_file,
                "output_file": output_file,
                "stdout": output
                },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)

        compile_obj = {
            "c_file": input_file,
            "obj_file": output_file,
            "stage": lib_hook.stage_to_str(stage),
            "matches": []}
        lines = output.strip("\n").split("\n")
        to_report = False
        for line in lines:
            for f in self.config.filters:
                try:
                    match = f.search(line, stage)
                    if match is not None:
                        compile_obj["matches"].append({"name": f.name, "match": match})
                        to_report = True
                except lib_hook.InvalidStage:
                    pass
        if to_report:
            request = pickle.dumps({
                "request_type": "report",
                "args": compile_obj,
            })
            size = len(request).to_bytes(4, byteorder="big")
            self.socket.send(size + request)

    def make_summary(self, input_files: typing.List[str], output_file: str):
        request = pickle.dumps({
            "request_type": "summary",
            "args": {
                "input_files": input_files,
                "output_file": output_file,
            },
        })
        size = len(request).to_bytes(4, byteorder="big")
        self.socket.send(size+request)


class ServerOutputHandler:
    def __init__(self, hook_config):
        self.config = hook_config
        self.output_obj = {"config": hook_config.data, "compils": []}
        self.report_obj = {"config": hook_config.data, "compils": [], "summary": []}

    def handle_output(self,
                      output: typing.Dict[str, str]):
        self.output_obj["compils"].append(output)

    def handle_report(self,
                      report: typing.Dict[str, typing.Union[str, typing.List[typing.Dict[str, str]]]]):
        self.report_obj["compils"].append(report)

    def handle_summary(self,
                       input_files: typing.List[str],
                       output_file: str):
        summary_obj = {
            "executable": output_file,
            "obj_files": input_files,
            "results": []
        }
        results = {}
        for compil in self.report_obj["compils"]:
            if compil["obj_file"] in input_files:
                for match in compil["matches"]:
                    if match["name"] in results:
                        results[match["name"]].append(match["match"])
                    else:
                        results[match["name"]] = [match["match"]]
        for f in self.config.filters:
            if f.name in results:
                if f.summary == "sum":
                    results[f.name] = sum(results[f.name])
                elif f.summary == "mean":
                    results[f.name] = sum(results[f.name])/len(results[f.name])
        summary_obj["results"] = [{"name": k, "result": v} for k, v in results.items()]
        self.report_obj["summary"].append(summary_obj)

    def finalize(self):
        with open(self.config.output_file, "w") as fd:
            json.dump(self.output_obj, fd, indent=4)

        with open(self.config.report_file, "w") as fd:
            json.dump(self.report_obj, fd, indent=4)
