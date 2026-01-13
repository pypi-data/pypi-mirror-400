"""环境准备"""
import os
import shutil
import jinja2
import configparser
from string import Template
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger
from lbkit.misc import DownloadFlag

log = Logger("product_prepare")


class ManifestValidateError(OSError):
    """Raised when validation manifest.yml failed."""

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class TaskClass(Task):
    def __init__(self, config, name):
        super().__init__(config, name)
        self.compiler_path = self.config.compiler_path
        self.sysroot_path = os.path.join(self.config.compiler_path, "sysroot")

    def decompress_file(self, dir, name, toolchain):
        compiler = toolchain.get(name)
        file = compiler.get("file")
        strip = compiler.get("strip_components", 0)
        flag_file = os.path.join(dir, ".file.sha256")
        _, hash = DownloadFlag.read(flag_file)
        file_hash = self.tools.file_digest_sha256(file)
        if hash and file_hash == hash:
            return
        # 可能标记不匹配，所以尝试删除目录后重新创建
        if os.path.isdir(dir):
            shutil.rmtree(dir)
        os.makedirs(dir)
        cmd = f"tar -xf {file} -C {dir}"
        if strip:
            cmd += f" --strip-components={strip}"
        self.exec(cmd)
        sha256 = self.tools.file_digest_sha256(file)
        DownloadFlag.create(flag_file, file, sha256)

    def decompress_toolchain(self):
        toolchain = self.config.get_product_config("toolchain")
        if not toolchain:
            # todo：toolchain成为强制配置项
            return
        self.decompress_file(self.compiler_path, "compiler", toolchain)
        self.decompress_file(self.sysroot_path, "sysroot", toolchain)

    def get_conan_profile(self):
        profile = self.config.get_product_config("toolchain/profile")
        if profile:
            file = profile.get("file")
            name = profile.get("name")
        else:
            file = self.get_manifest_config("metadata/profile")
            name = "litebmc"
        return file, name


    def load_conan_profile(self):
        profile, name = self.get_conan_profile()
        log.info("Copy profile %s", profile)
        profiles_dir = os.path.expanduser("~/.conan2/profiles")
        if not os.path.isdir(profiles_dir):
            cmd = "conan profile detect -f"
            self.exec(cmd, ignore_error=True)
        dst_profile = os.path.join(profiles_dir, name)
        with open(dst_profile, "w+") as dst_fp:
            src_fd = open(profile, "r")
            template = Template(src_fd.read())
            src_fd.close()
            content = template.safe_substitute(compiler_path=self.compiler_path,
                                               sysroot_path=self.sysroot_path,
                                               code_path=self.config.code_path)
            dst_fp.write(content)

        with open(dst_profile, "r") as fp:
            profile_data = jinja2.Template(fp.read()).render()
            parser = configparser.ConfigParser(allow_no_value=True, delimiters=('=',))
            parser.read_string(profile_data)
            strip = "strip"
            if parser.has_option("buildenv", "STRIP"):
                strip = parser.get("buildenv", "STRIP")
            path = ""
            if parser.has_option("buildenv", "PATH+"):
                path = parser.get("buildenv", "PATH+")
                if path.startswith("(path)"):
                    path = path[6:]
            elif parser.has_option("buildenv", "PATH"):
                path = parser.get("buildenv", "PATH")
                if path.startswith("(path)"):
                    path = path[6:]
            self.config.strip = os.path.join(path, strip)

    def run(self):
        """任务入口"""
        self.decompress_toolchain()
        """检查manifest文件是否满足schema格式描述"""
        self.config.load_manifest()
        self.load_conan_profile()
        return 0

if __name__ == "__main__":
    config = Config()
    build = TaskClass(config, "test")
    build.run()