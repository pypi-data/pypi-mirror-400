"""环境准备"""
import os
import shutil
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger

log = Logger("build_image")

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class TaskMakeRockchipImage(Task):
    def __init__(self, config, name):
        super().__init__(config, name)
        self.chip_model = None
        chip_model = self.config.get_product_config("chip_model")
        if chip_model not in ["rk3506"]:
            return
        self.chip_model = chip_model
        self.uboot = self.config.get_product_config("flash/uboot")
        self.kernel = self.config.get_product_config("flash/kernel")
        self.loader = self.config.get_product_config("flash/loader")
        self.parameter = self.config.get_product_config("flash/parameter")
        self.package_file = self.config.get_product_config("flash/package-file")
        self.rootfs = self.config.rootfs_img

    def available(self):
        if not self.chip_model:
            return False
        if self.config.get_product_config("flash/type") != "spi_nand":
            return False
        return True

    def run(self):
        """任务入口"""
        if not self.available():
            return -1
        cwd = os.getcwd()
        tmpdir = os.path.join(self.config.output_path, "temp_files")
        if os.path.isdir(tmpdir):
            shutil.rmtree(tmpdir)
        os.makedirs(tmpdir)
        os.chdir(tmpdir)
        self.copyfile(self.uboot, os.path.basename(self.uboot))
        self.copyfile(self.kernel, os.path.basename(self.kernel))
        self.copyfile(self.loader, os.path.basename(self.loader))
        self.copyfile(self.parameter, "parameter.txt")
        self.copyfile(self.package_file, "package-file")
        self.copyfile(self.rootfs, os.path.basename(self.rootfs))
        with open(self.package_file) as fp:
            lines = fp.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                continue
            infos = line.split("\t")
            if len(infos) != 2:
                raise Exception("the package-file with format error, each line of text must be in the format of `name\tfile\n`")
            filename = infos[1]
            if not os.path.isfile(filename):
                cmd = f"dd if=/dev/zero of={filename} bs=1K count=1"
                self.exec(cmd)
        cmd = "rk_afptool -pack . firmware.img.raw"
        self.exec(cmd, verbose=True)
        cmds = [f"hexdump -s 21 -n 4 -e '4 \"%c\"' {self.loader}", "rev"]
        tag = "RK" + self.pipe(cmds).decode("utf-8")
        cmd = f"rk_image_maker -{tag} {self.loader} firmware.img.raw firmware.img -os_type:androidos"
        self.exec(cmd, verbose=True)
        cmd = f"mv firmware.img " + os.path.join(self.config.output_path, "firmware.img")
        self.exec(cmd)
        os.chdir(cwd)
        return 0


if __name__ == "__main__":
    config = Config()
    build = TaskMakeRockchipImage(config, "test")
    build.run()