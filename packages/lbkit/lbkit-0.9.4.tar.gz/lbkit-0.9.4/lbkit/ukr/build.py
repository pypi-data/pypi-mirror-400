"""组件构建"""
import os
import yaml
import shutil
from string import Template
from lbkit.tools import Tools
from lbkit.tasks.task_download import DownloadTask
from lbkit.misc import DownloadFlag
from lbkit.tools import Tools
from lbkit.utils.env_detector import EnvDetector
from lbkit.misc import load_yml_with_json_schema_validate


tools = Tools("comp_build")
log = tools.log
lb_cwd = os.path.split(os.path.realpath(__file__))[0]

class SourceDest():
    def __init__(self, cfg):
        self.source = cfg.get("source")
        self.dest = cfg.get("dest")
        self.pattern = cfg.get("pattern")

    def copy(self, source_dir, dest_dir, with_template, **kwargs):
        source = os.path.join(source_dir, self.source)
        dest = os.path.join(dest_dir, self.dest)
        if self.pattern and os.path.isdir(source):
            if not source.endswith("/"):
                source += "/"
            files = tools.pipe([f"find {source} -name {self.pattern}"], out_file=None).decode("utf-8").split("\n")
            for file in files:
                file = file.strip()
                if not file:
                    continue
                new_dest = os.path.join(dest, file[len(source):])
                self._copy(file, new_dest, with_template, **kwargs)
        else:
            self._copy(source, dest, with_template, **kwargs)

    def _copy(self, source, dest, with_template, **kwargs):
        if os.path.isfile(dest):
            os.unlink(dest)
        dest_dir = os.path.dirname(dest)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        log.info(f"cp {source} to  {dest}")
        if with_template:
            with open(source, "r") as fp:
                template = Template(fp.read())
            content = template.safe_substitute(kwargs)
            with open(dest, "w+") as fp:
                fp.write(content)
        else:
            shutil.copyfile(source, dest)


class BuildGeneral():
    def __init__(self, config, cwd, cfg_key, dir_name):
        self.cwd = cwd
        self.name = cfg_key
        self.work_dir = os.path.join(cwd, ".temp")
        self.output = os.path.join(self.work_dir, "output")
        if not os.path.isdir(self.output):
            os.makedirs(self.output)
        os.chdir(self.work_dir)
        self.arch = config.get("base").get("arch")
        self.cross_compile = config.get("base").get("cross_compile")
        self.cfg = config.get(cfg_key)
        self.dir_name = os.path.realpath(dir_name)
        self.tools = Tools(self.dir_name + ".log")

    def download(self):
        tmp_file = self.dir_name + ".tar.gz"
        url = self.cfg.get("url")
        sha256 = self.cfg.get("sha256")
        verify = self.cfg.get("verify", True)
        strip_components = self.cfg.get("strip_components")
        cfg = {
            "url": url,
            "file": tmp_file,
            "decompress": {
                "dirname": os.getcwd(),
                "strip_components": strip_components
            },
            "sha256": sha256,
            "verify": verify
        }
        task = DownloadTask(cfg, os.getcwd())
        task.start()
        cmd = f"tar -xf {task.dst} -C {self.dir_name}"
        if task.strip_components:
            cmd += f" --strip-components={task.strip_components}"
        if os.path.isdir(self.dir_name):
            shutil.rmtree(self.dir_name)
        os.makedirs(self.dir_name)
        self.tools.exec(cmd)
        DownloadFlag.create(self.dir_name, url, sha256)

    def prepare_defconfig(self):
        defconf = self.cfg.get("defconfig")
        compiler_path=os.path.join(self.work_dir, "toolchain")
        if isinstance(defconf, list):
            for conf in defconf:
                sd = SourceDest(conf)
                sd.copy(self.cwd, os.path.join(self.work_dir, self.dir_name), True, compiler_path=compiler_path)
        else:
            sd = SourceDest(defconf)
            sd.copy(self.cwd, os.path.join(self.work_dir, self.dir_name), True, compiler_path=compiler_path)
        os.environ["ARCH"] = self.arch
        os.environ["CROSS_COMPILE"] = os.path.join(compiler_path, "bin", self.cross_compile + "-")
        path = os.environ.get("PATH", "")
        if compiler_path not in path:
            path += ":" + compiler_path + "/bin"
            os.environ["PATH"] = path
        self.defconfig = os.path.basename(sd.dest)

    def build(self):
        os.chdir(self.dir_name)
        cmds = self.cfg.get("cmds", [])
        if cmds:
            for cmd in cmds:
                compiler = os.environ["CROSS_COMPILE"]
                cmd = cmd.replace("${compiler}", compiler)
                cmd = cmd.replace("${workdir}", self.dir_name)
                self.tools.exec(cmd, verbose=True)
        else:
            cmd = f"make {self.defconfig}"
            self.tools.exec(cmd, verbose=True)
            if self.name == "compiler":
                cmd = f"make sdk -j" + str(os.cpu_count())
            else:
                cmd = f"make -j" + str(os.cpu_count())
            self.tools.exec(cmd, verbose=True)

    def tar_files(self):
        os.chdir(self.dir_name)
        cfgs = self.cfg.get("tar", [])
        for cfg in cfgs:
            sd = SourceDest(cfg)
            src = os.path.join(self.dir_name, sd.source)
            dst = os.path.join(self.dir_name, sd.dest)
            cmd = f"tar -czf {dst} -C {src} ."
            self.tools.exec(cmd)

    def package(self):
        os.chdir(self.dir_name)
        cfgs = self.cfg.get("output", [])
        for cfg in cfgs:
            sd = SourceDest(cfg)
            sd.copy(self.dir_name, self.output, False)

    def run(self):
        if not self.cfg:
            return
        self.download()
        self.prepare_defconfig()
        self.build()
        self.tar_files()
        self.package()
        os.chdir(self.cwd)

class BuildCompiler(BuildGeneral):
    def __init__(self, config, cwd):
        super().__init__(config, cwd, "compiler", "buildroot")

    def package(self):
        super().package()
        cfgs = self.cfg.get("output", [])
        for cfg in cfgs:
            sd = SourceDest(cfg)
            dest = os.path.join(self.output, sd.dest)
            install_path = os.path.join(self.work_dir, "toolchain")
            if os.path.isdir(install_path):
                shutil.rmtree(install_path)
            os.makedirs(install_path)
            cmd = f"tar -xzf {dest} -C {install_path} --strip-components=1"
            self.tools.exec(cmd)

class BuildRootfs(BuildGeneral):
    def __init__(self, config, cwd):
        super().__init__(config, cwd, "buildroot", "buildroot")

    def build(self):
        os.chdir(self.dir_name)
        shutil.rmtree("output", ignore_errors=True)
        return super().build()

class BuildLinux(BuildGeneral):
    def __init__(self, config, cwd):
        super().__init__(config, cwd, "linux", "linux")

class BuildUBoot(BuildGeneral):
    def __init__(self, config, cwd):
        super().__init__(config, cwd, "uboot", "uboot")


class PreDownload():
    def __init__(self, config, cwd):
        self.cwd = cwd
        self.cfg = config.get("predownload", [])

    def run(self):
        if not self.cfg:
            return
        for down in self.cfg:
            url = down.get("url")
            sha256 = down.get("sha256")
            verify = down.get("verify", True)
            destfile = down.get("destfile")
            destfile = os.path.join(self.cwd, ".temp", destfile)
            destfile = os.path.realpath(destfile)
            if not destfile.startswith(self.cwd):
                raise Exception(f"dest file {destfile} not startswith {self.cwd}")
            destdir = os.path.dirname(destfile)
            if not os.path.isdir(destdir):
                os.makedirs(destdir)

            tmpfile = os.path.join(self.cwd, ".temp", os.path.basename(url))

            cfg = {
                "url": url,
                "file": tmpfile,
                "decompress": {
                    "dirname": self.cwd,
                    "strip_components": 0
                },
                "sha256": sha256,
                "verify": verify
            }
            task = DownloadTask(cfg, os.getcwd())
            task.start()
            if tmpfile != destfile:
                shutil.copyfile(tmpfile, destfile)
            decomp = down.get("decompress")
            if not decomp:
                continue
            strip_components = decomp.get("strip_components", 0)
            dirname = decomp.get("dirname")
            if not dirname:
                continue
            dirname = os.path.join(self.cwd, ".temp", dirname)
            if os.path.isdir(dirname):
                shutil.rmtree(dirname)
            os.makedirs(dirname)
            cmd = f"tar -xf {task.dst} -C {dirname}"
            if strip_components:
                cmd += f" --strip-components={strip_components}"
            tools.exec(cmd)

class UKRBuild():
    def __init__(self, env_detector: EnvDetector):
        os.chdir(env_detector.ukr.folder)
        self.env_detector = env_detector

    def run(self):
        cwd = os.getcwd()

        cfg = load_yml_with_json_schema_validate("config.yml", "/usr/share/litebmc/schema/ukr_config.v1.json")
        download = PreDownload(cfg, cwd)
        download.run()
        build = BuildCompiler(cfg, cwd)
        build.run()
        build = BuildRootfs(cfg, cwd)
        build.run()
        build = BuildLinux(cfg, cwd)
        build.run()
        build = BuildUBoot(cfg, cwd)
        build.run()
        cmd = f"tar -czf {cwd}/.temp/output/firmware.tar.gz -C {cwd}/.temp/output/images ."
        tools.exec(cmd)
