"""应用构建任务"""
import os
import shutil
import json
from mako.lookup import TemplateLookup
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger
from lbkit.build_conan_parallel import BuildConanParallel
from concurrent.futures import ThreadPoolExecutor
from lbkit.codegen.codegen import __version__ as codegen_version

log = Logger("product_build")


class ManifestValidateError(OSError):
    """Raised when validation manifest.yml failed."""

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class TaskClass(Task):
    """根据产品配置构建所有app,记录待安装应用路径到self.config.conan_install路径"""
    def __init__(self, cfg: Config, name: str):
        super().__init__(cfg, name)
        self.conan_build = os.path.join(self.config.temp_path, "conan")
        if os.path.isdir(self.conan_build):
            shutil.rmtree(self.conan_build)
        os.makedirs(self.conan_build)
        if self.config.build_type == "debug":
            self.conan_settings = " -s build_type=Debug"
        elif self.config.build_type == "release":
            self.conan_settings = " -s build_type=Release"
        elif self.config.build_type == "minsize":
            self.conan_settings = " -s build_type=MinSizeRel"
        self.common_args = "-r " + self.config.remote
        self.common_args += " -pr:b {} -pr:h {}".format(self.config.profile_build, self.config.profile_host)
        self.common_args += " -o */*:test=False"
        cv = self.get_manifest_config("metadata/codegen_version")
        if cv == "latest":
            cv = codegen_version.str
        self.common_args += " -o */*:codegen_version=" + cv
        os.environ["CODEGEN_VERSION"] = cv

    def deploy(self, graph_file):
        with open(graph_file, "r") as fp:
            order_info = json.load(fp)
        for orders in order_info.get("order", []):
            for order in orders:
                ref = order.get("ref")
                packages = order.get("packages", [])
                for package in packages:
                    for pkg in package:
                        binary = pkg.get("context", "")
                        if binary != "host":
                            continue
                        id = pkg.get("package_id", "")
                        cmd = f"conan cache path {ref}:{id}"
                        package_folder = self.tools.run(cmd).stdout.strip()
                        self.config.conan_install.append(package_folder)

    def build_rootfs(self):
        """构建产品rootfs包"""
        log.info("build rootfs")

        manifest = self.load_manifest()
        # 使用模板生成litebmc组件的配置
        lookup = TemplateLookup(directories=os.path.join(src_cwd, "template"))
        template = lookup.get_template("rootfs.py.mako")
        conanfile = template.render(lookup=lookup, pkg=manifest)

        recipe = os.path.join(self.conan_build, "rootfs")
        os.makedirs(recipe, exist_ok=True)
        os.chdir(recipe)
        fp = open("conanfile.py", "w", encoding="utf-8")
        fp.write(conanfile)
        fp.close()

        self.exec(f"conan create . {self.common_args} --build=missing", verbose=True)

    def build_litebmc(self):
        """构建产品conan包"""
        log.info("build litebmc")

        manifest = self.load_manifest()
        hook_name = "hook.prepare_manifest"
        self.do_hook(hook_name)
        # 使用模板生成litebmc组件的配置
        lookup = TemplateLookup(directories=os.path.join(src_cwd, "template"))
        template = lookup.get_template("conanfile.py.mako")
        conanfile = template.render(lookup=lookup, pkg=manifest, real_dependencies=self.config.get_dependencies())

        recipe = os.path.join(self.conan_build, "litebmc")
        os.makedirs(recipe, exist_ok=True)
        os.chdir(recipe)
        fp = open("conanfile.py", "w", encoding="utf-8")
        fp.write(conanfile)
        fp.close()

        base_cmd = f"{self.common_args} {self.conan_settings}"
        lockfile = os.path.join(self.config.code_path, "conan.lock")
        orderfile = os.path.join(self.config.temp_path, "build-order.json")
        graph_cmd = f"conan graph build-order . {base_cmd} --order-by=recipe -f json --out-file={orderfile}"
        if self.config.from_source:
            graph_cmd += " --build='*'"
        else:
            graph_cmd += " --build=missing"
        if self.config.update_lockfile or not os.path.isfile(lockfile):
            graph_cmd += f" --lockfile-out={lockfile}"
        else:
            graph_cmd += f" --lockfile={lockfile} --lockfile-partial"
        self.exec(graph_cmd, verbose=True)
        bcp = BuildConanParallel(orderfile, self.config.remote)
        bcp.build()

        self.exec(f"sed -i 's@rootfs_df190c/0.0.1#.*\"@rootfs_df190c/0.0.1\"@g' {lockfile}")
        # 部署应用到self.config.conan_install
        self.deploy(orderfile)

    def run(self):
        """任务入口"""
        self.build_rootfs()
        self.build_litebmc()
        return 0

if __name__ == "__main__":
    config = Config()
    build = TaskClass(config, "test")
    build.run()
