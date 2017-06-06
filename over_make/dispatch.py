"""Contains only dispatch. It disptaches request into the correct handler."""
import pickle


def dispatch(sock, request, output_handler, hook_parser, hook_logger, hook_config, debug=False):
    """Get the request (as a dict), look at the "resquest_type" field and handle them as necessary"""
    if debug:
        d = {
            "output": "\033[1;49;34moutput\033[0m",
            "report": "\033[1;49;36mreport\033[0m",
            "summary": "\033[1;49;32msummary\033[0m",
        }
        print("request type", d[request["request_type"]])
    if request["request_type"] == "output":
        output_handler.handle_output(request["args"])
    elif request["request_type"] == "report":
        output_handler.handle_report(request["args"])
    elif request["request_type"] == "summary":
        output_handler.handle_summary(request["args"]["input_files"], request["args"]["output_file"])
    elif request["request_type"] == "parse_args":
        namespace, unknown = hook_parser.parse_known_args(request["args"]['argv'][1:])
        response = pickle.dumps((namespace, unknown))
        size = len(response).to_bytes(4, byteorder="big")
        sock.send(size + response)
    elif request["request_type"] == "log":
        hook_logger.dispatch(request)
    elif request["request_type"] == "get_config":
        response = pickle.dumps(hook_config)
        size = len(response).to_bytes(4, byteorder="big")
        sock.send(size + response)
    else:
        print("\033[1;49;31mUnknown request type: %s\033[0m", request)
