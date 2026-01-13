from gwaslab.info.g_Log import Log
import sys

def _show_version(log=Log(), verbose=True):
    # show version when loading sumstats
    log.write(" -GWASLab Agent v{} https://cloufield.github.io/gwaslab-agent/".format(gwaslab_info()["version"]), verbose=verbose)
    log.write(" -(C) 2025-2025, Yunye He, Kamatani Lab, GPL-3.0 license, gwaslab@gmail.com", verbose=verbose)
    log.write(f" -Python version: {sys.version}", verbose=verbose)

def _get_version():
    return "v{}".format(gwaslab_info()["version"])

def gwaslab_info():
    # version meta information
    dic={
   "version":"0.1.0",
   "release_date":"20260104"
    }
    return dic   
