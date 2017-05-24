import typing

from .hook_parser import OptimisationLevel
from .hook_config import HookConfig


def get_passes(config: HookConfig, level: OptimisationLevel) -> typing.List[str]:
    default = {OptimisationLevel.O0: "-targetlibinfo -tti -verify".split(),
               OptimisationLevel.O1: "-targetlibinfo -tti -tbaa -scoped-noalias -assumption-cache-tracker -forceattrs "
                                     "-inferattrs -ipsccp -globalopt -domtree -mem2reg -deadargelim -basicaa -aa "
                                     "-domtree -instcombine -simplifycfg -basiccg -globals-aa -prune-eh -always-inline "
                                     "-functionattrs -domtree -sroa -early-cse -lazy-value-info -jump-threading "
                                     "-correlated-propagation -simplifycfg -basicaa -aa -domtree -instcombine "
                                     "-tailcallelim -simplifycfg -reassociate -domtree -loops -loop-simplify -lcssa "
                                     "-loop-rotate -basicaa -aa -licm -loop-unswitch -simplifycfg -basicaa -aa "
                                     "-domtree -instcombine -loops -scalar-evolution -loop-simplify -lcssa -indvars "
                                     "-aa -loop-idiom -loop-deletion -loop-unroll -basicaa -aa -memdep -memcpyopt "
                                     "-sccp -domtree -demanded-bits -bdce -basicaa -aa -instcombine -lazy-value-info "
                                     "-jump-threading -correlated-propagation -domtree -basicaa -aa -memdep -dse "
                                     "-loops -loop-simplify -lcssa -aa -licm -adce -simplifycfg -basicaa -aa -domtree "
                                     "-instcombine -barrier -basiccg -rpo-functionattrs -basiccg -globals-aa "
                                     "-float2int -domtree -loops -loop-simplify -lcssa -loop-rotate -branch-prob "
                                     "-block-freq -scalar-evolution -basicaa -aa -loop-accesses -demanded-bits "
                                     "-loop-vectorize -instcombine -simplifycfg -basicaa -aa -domtree -instcombine "
                                     "-loops -loop-simplify -lcssa -scalar-evolution -loop-unroll -basicaa -aa "
                                     "-instcombine -loop-simplify -lcssa -aa -licm -scalar-evolution "
                                     "-alignment-from-assumptions -strip-dead-prototypes -verify".split(),
               OptimisationLevel.O2: "-targetlibinfo -tti -tbaa -scoped-noalias -assumption-cache-tracker -forceattrs "
                                     "-inferattrs -ipsccp -globalopt -domtree -mem2reg -deadargelim -basicaa -aa "
                                     "-domtree -instcombine -simplifycfg -basiccg -globals-aa -prune-eh -inline "
                                     "-functionattrs -domtree -sroa -early-cse -lazy-value-info -jump-threading "
                                     "-correlated-propagation -simplifycfg -basicaa -aa -domtree -instcombine "
                                     "-tailcallelim -simplifycfg -reassociate -domtree -loops -loop-simplify -lcssa "
                                     "-loop-rotate -basicaa -aa -licm -loop-unswitch -simplifycfg -basicaa -aa "
                                     "-domtree -instcombine -loops -scalar-evolution -loop-simplify -lcssa -indvars "
                                     "-aa -loop-idiom -loop-deletion -loop-unroll -basicaa -aa -mldst-motion -aa "
                                     "-memdep -gvn -basicaa -aa -memdep -memcpyopt -sccp -domtree -demanded-bits "
                                     "-bdce -basicaa -aa -instcombine -lazy-value-info -jump-threading "
                                     "-correlated-propagation -domtree -basicaa -aa -memdep -dse -loops -loop-simplify "
                                     "-lcssa -aa -licm -adce -simplifycfg -basicaa -aa -domtree -instcombine -barrier "
                                     "-basiccg -rpo-functionattrs -elim-avail-extern -basiccg -globals-aa -float2int "
                                     "-domtree -loops -loop-simplify -lcssa -loop-rotate -branch-prob -block-freq "
                                     "-scalar-evolution -basicaa -aa -loop-accesses -demanded-bits -loop-vectorize "
                                     "-instcombine -scalar-evolution -aa -slp-vectorizer -simplifycfg -basicaa -aa "
                                     "-domtree -instcombine -loops -loop-simplify -lcssa -scalar-evolution "
                                     "-loop-unroll -basicaa -aa -instcombine -loop-simplify -lcssa -aa -licm "
                                     "-scalar-evolution -alignment-from-assumptions -strip-dead-prototypes -globaldce "
                                     "-constmerge -verify".split(),
               OptimisationLevel.O3: "-targetlibinfo -tti -tbaa -scoped-noalias -assumption-cache-tracker -forceattrs "
                                     "-inferattrs -ipsccp -globalopt -domtree -mem2reg -deadargelim -basicaa -aa "
                                     "-domtree -instcombine -simplifycfg -basiccg -globals-aa -prune-eh -inline "
                                     "-functionattrs -argpromotion -domtree -sroa -early-cse -lazy-value-info "
                                     "-jump-threading -correlated-propagation -simplifycfg -basicaa -aa -domtree "
                                     "-instcombine -tailcallelim -simplifycfg -reassociate -domtree -loops "
                                     "-loop-simplify -lcssa -loop-rotate -basicaa -aa -licm -loop-unswitch "
                                     "-simplifycfg -basicaa -aa -domtree -instcombine -loops -scalar-evolution "
                                     "-loop-simplify -lcssa -indvars -aa -loop-idiom -loop-deletion -loop-unroll "
                                     "-basicaa -aa -mldst-motion -aa -memdep -gvn -basicaa -aa -memdep -memcpyopt "
                                     "-sccp -domtree -demanded-bits -bdce -basicaa -aa -instcombine -lazy-value-info "
                                     "-jump-threading -correlated-propagation -domtree -basicaa -aa -memdep -dse "
                                     "-loops -loop-simplify -lcssa -aa -licm -adce -simplifycfg -basicaa -aa "
                                     "-domtree -instcombine -barrier -basiccg -rpo-functionattrs -elim-avail-extern "
                                     "-basiccg -globals-aa -float2int -domtree -loops -loop-simplify -lcssa "
                                     "-loop-rotate -branch-prob -block-freq -scalar-evolution -basicaa -aa "
                                     "-loop-accesses -demanded-bits -loop-vectorize -instcombine -scalar-evolution -aa "
                                     "-slp-vectorizer -simplifycfg -basicaa -aa -domtree -instcombine -loops "
                                     "-loop-simplify -lcssa -scalar-evolution -loop-unroll -basicaa -aa -instcombine "
                                     "-loop-simplify -lcssa -aa -licm -scalar-evolution -alignment-from-assumptions "
                                     "-strip-dead-prototypes -globaldce -constmerge -verify".split(),
               }

    if config.passes:
        def gen_load(l):
            for p in l:
                yield "-load"
                yield p
        passes = list(gen_load(config.load))
        return passes + config.passes
    return default[level]
