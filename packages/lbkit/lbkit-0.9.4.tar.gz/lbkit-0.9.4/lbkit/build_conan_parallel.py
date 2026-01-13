"""任务基础类"""
import os
import json
import tempfile
from lbkit.log import Logger
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from lbkit import misc
from lbkit.tools import Tools
from lbkit.misc import Color

tools = Tools("comp_build")
log = Logger("comp_build")


class BuildConanParallel(object):
    def __init__(self, orderinfo, remote):
        self.orderinfo = orderinfo
        self.remote = remote

    def _build_package(self, logfile, build_args, public_args):
        cmd = f"conan install {build_args} {public_args}"
        log.info("{}build start:    '{}".format(Color.GREEN, Color.RESET_ALL) + cmd + '  log file: ' + logfile)
        tools.exec(cmd, ignore_error=True, log_name=logfile, echo_cmd=False)
        log.info("{}build finished: '{}".format(Color.GREEN, Color.RESET_ALL) + cmd + '  log file: ' + logfile)

    def _build(self):
        with open(self.orderinfo, "r") as fp:
            order_info = json.load(fp)
        public_args = order_info.get("profiles", {}).get("self", {}).get("args", "")
        for orders in order_info.get("order", []):
            threadPool = ThreadPoolExecutor(max_workers=(os.cpu_count() + 1) // 2)
            results: list[Future] = []
            for order in orders:
                ref = order.get("ref")
                pkgname = ref.split("/")[0]
                logfile = f"{misc.LOG_DIR}/conan_{pkgname}.log"
                packages = order.get("packages", [])
                for package in packages:
                    for pkg in package:
                        binary = pkg.get("binary", "")
                        if binary == 'Download':
                            pkgid = pkg.get("package_id")
                            cmd = f'conan download {ref}:{pkgid}'
                            if self.remote:
                                cmd += f' -r {self.remote}'
                            tools.exec(cmd)
                            continue
                        if binary != "Build":
                            continue
                        build_args = pkg.get("build_args", "")
                        result = threadPool.submit(self._build_package, logfile, build_args, public_args)
                        results.append(result)
            for result in as_completed(results):
                result.result()

    def build(self):
        cwd = os.getcwd()
        tmp = tempfile.TemporaryDirectory()
        os.chdir(tmp.name)
        self._build()
        os.chdir(cwd)
