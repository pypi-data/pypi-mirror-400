"""组件测试"""
import shutil
import re
import os
import importlib.machinery
import unittest
import yaml
import time
import subprocess
from multiprocessing import Pool
from lbkit.component.build import BuildComponent
from lbkit.component.arg_parser import ArgParser
from lbkit import errors
from lbkit.tools import Tools
from lbkit.misc import Color

tool = Tools("comp_test")
log = tool.log


def run_command(cmd):
    """执行shell命令并返回结果"""
    try:
        log.info(">>>> Start run: " + cmd)
        subprocess.run([cmd], check=True)
        return True
    except Exception as e:
        log.warning(str(e))
        return False


class TestComponent():
    def __init__(self, args:list[str]=None):
        self.cwd = os.getcwd()
        self.execute_only = False
        if "-e" in args:
            self.execute_only = True
            args.remove("-e")
        else:
            log.info("If you just want to execute the binary program, run the -e parameter")

        self.build_parser = ArgParser.new(True)
        self.build_parser.parse_args(args) # 共享命令参数

        self.origin_args = args
        self.origin_args.append("--cov")
        self.origin_args.append("--test")
        self.package_id = ""

    def _collect_coverage_data(self, build_folder, test_src_folder):
        coverage_dir = os.path.join(".temp/coverage")
        shutil.rmtree(coverage_dir, ignore_errors=True)
        os.makedirs(coverage_dir)
        # 覆盖率数据路径由conanbase.make在build配置cflags时定义
        cmd = f"lcov --compat-libtool -c -q -d {build_folder} -o {coverage_dir}/cover.info"
        tool.exec(cmd)
        for dir in test_src_folder:
            cmd = f"lcov --compat-libtool -r {coverage_dir}/cover.info \"{build_folder}/{dir}/*\" -o {coverage_dir}/cover.info"
            tool.exec(cmd)
        cmd = f"lcov --compat-libtool -r {coverage_dir}/cover.info \"*/include/*\" -o {coverage_dir}/cover.info"
        tool.exec(cmd)
        cmd = f"genhtml -o {coverage_dir}/html --legend {coverage_dir}/cover.info"
        tool.exec(cmd)

        index_file = os.path.join(coverage_dir, "html/index.html")
        with open(index_file, "r") as fp:
            content = fp.read()
        matches = re.search(r"Lines:</td\>\n.*headerCovTableEntry\"\>([0-9]+).*\n.*headerCovTableEntry\"\>([0-9]+).*\n.*headerCovTableEntry(Lo|Hi|Med)\"\>([0-9.]+) %", content)
        if matches is None:
            raise errors.LiteBmcException(f"Read line coverage data from {index_file} failed")
        line_hit = int(matches.group(1))
        line_total = int(matches.group(2))
        line_cov = float(matches.group(4))
        line_level = matches.group(3)
        log.info("Coverage info:")
        if line_level == "Hi":
            log.info(Color.GREEN + f"Line:     hit %-10d total %-10d coverage %.02f %% (High)" % (line_hit, line_total, line_cov) + Color.RESET_ALL)
        elif line_level == "Med":
            log.info(Color.YELLOW + f"Line:     hit %-10d total %-10d coverage %.02f %% (Medium)" % (line_hit, line_total, line_cov) + Color.RESET_ALL)
        elif line_level == "Lo":
            log.info(Color.RED + f"Line:     hit %-10d total %-10d coverage %.02f %% (Low)" % (line_hit, line_total, line_cov) + Color.RESET_ALL)
        matches = re.search(r"Functions:</td\>\n.*headerCovTableEntry\"\>([0-9]+).*\n.*headerCovTableEntry\"\>([0-9]+).*\n.*headerCovTableEntry(Lo|Hi|Med)\"\>([0-9.]+) %", content)
        if matches is None:
            raise errors.LiteBmcException(f"Read function coverage data from {index_file} failed")
        func_hit = int(matches.group(1))
        func_total = int(matches.group(2))
        func_cov = float(matches.group(4))
        func_level = matches.group(3)
        if func_level == "Hi":
            log.info(Color.GREEN + f"Function: hit %-10d total %-10d coverage %.02f %% (High)" % (func_hit, func_total, func_cov) + Color.RESET_ALL)
        elif func_level == "Med":
            log.info(Color.YELLOW + f"Function: hit %-10d total %-10d coverage %.02f %% (Medium)" % (func_hit, func_total, func_cov) + Color.RESET_ALL)
        elif func_level == "Lo":
            log.info(Color.RED + f"Function: hit %-10d total %-10d coverage %.02f %% (Low)" % (func_hit, func_total, func_cov) + Color.RESET_ALL)

    def _make_ld_library_path(self, rootfs_dir):
        cmd = f"find {rootfs_dir} -name *.so"
        res = tool.run(cmd)
        files = res.stdout.strip().split("\n")
        ld_library_path = os.environ.get("LD_LIBRARY_PATH", "").strip()
        paths = []
        for path in ld_library_path.split(":"):
            if not path:
                continue
            if not ".temp/rootfs" in path:
                paths.append(path)
        for file in files:
            dir = os.path.dirname(file)
            if dir not in paths:
                paths.append(dir)
        path_str = ":".join(paths)
        os.environ["LD_LIBRARY_PATH"] = path_str
        log.info("export LD_LIBRARY_PATH={}".format(path_str))

    def _make_dbus_session(self, rootfs_dir):
        if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
            if not os.path.isfile("/dev/shm/session-dbus"):
                tool.pipe(["dbus-launch --sh-syntax"], out_file="/dev/shm/session-dbus")
            tool.exec(f"mkdir {rootfs_dir}/var/run/dbus -p")
            tool.exec(f"cp /dev/shm/session-dbus {rootfs_dir}/var/run/dbus/session-dbus")

        log.info("export ROOTFS_DIR={}".format(rootfs_dir))

    def _run_bins(self, rootfs_dir):
        self._make_dbus_session(rootfs_dir)

        with open("metadata/package.yml", "r") as fp:
            metadata = yaml.safe_load(fp)
        Pool
        bins = metadata.get("package_info", {}).get("bins", [])
        count = len(bins)
        pool = Pool(count + 1)
        if not bins:
            log.warning("The metadata/package.yml file does not contain executable binary program records(package_info/bins)")
            return pool

        for bin in bins:
            bin = os.path.join(rootfs_dir, bin)
            if not os.path.isfile(bin):
                log.warning(f"Execute file {bin} not eixst")
            pool.map_async(run_command, (bin, ))
        lb_im = os.path.join(rootfs_dir, "opt/litebmc/apps/lb_interface_manager/lb_interface_manager")
        if os.path.isfile(lb_im):
            pool.map_async(run_command, (lb_im, ))
        return pool

    def run(self):
        # 当term_flag文件存在时所有app进程会主动退出，首先清除标记文件
        term_flag = "/dev/shm/litebmc_terminate"
        if os.path.isfile(term_flag):
            os.unlink(term_flag)
        # 构建组件
        build = BuildComponent(self.build_parser, self.origin_args)
        build.run()

        self._make_ld_library_path(build.rootfs_dir)
        self._make_dbus_session(build.rootfs_dir)

        pool = self._run_bins(build.rootfs_dir)
        pool.close()
        if self.execute_only:
            pool.join()
            return 0

        # 为确保路径正确，切换到初始路径
        os.chdir(self.cwd)
        # 必须存在test.py时才测试
        if not os.path.isfile("test.py"):
            log.warn("Test file(test.py) not exist, skip test")
            return 0
        # 从test.py加载LiteBmcComponentTest实例并运行用命
        loader = importlib.machinery.SourceFileLoader("test", os.path.join(self.cwd, "test.py"))
        mod = loader.load_module()
        klass = getattr(mod, "LiteBmcComponentTest")
        if klass is None:
            log.warn("test.py does not provide the LiteBmcComponentTest class, skip test")
            return 0
        test = klass(rootfs_dir=build.rootfs_dir)
        test_method = getattr(test, "test")
        if test_method is None:
            log.warn("The LiteBmcComponentTest class provided by test.py does not provide test methods, skip test")
            return 0

        log.success("call test method...")
        ret = test.test()
        if ret is not None:
            if isinstance(ret, unittest.TestResult) and (len(ret.errors) > 0 or len(ret.failures) > 0):
                raise errors.TestException(f"Test failed, ret: {ret}")
            elif isinstance(ret, int) and ret != 0:
                raise errors.TestException(f"Test failed, ret: {ret}")

        test_src_folder = getattr(test, "test_src_folder", [])
        with open(term_flag, "w") as fp:
            pass
        time.sleep(1)
        os.unlink(term_flag)
        # 设置ROOTFS_DIR环境变量，为DT测试提供相对路径
        self._collect_coverage_data(build.build_folder, test_src_folder)
        log.success("Test finished")


# GCOV_PREFIX和GCOV_PREFIX_STRIP用于指定不同目录或层级生成gcda文件
# 参考网址: https://gcc.gnu.org/onlinedocs/gcc/Cross-profiling.html