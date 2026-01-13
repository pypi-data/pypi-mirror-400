"""环境准备"""
import os
import tempfile
from lbkit.tasks.config import Config
from lbkit.log import Logger
from lbkit.utils.images.emmc import MakeImage as MekeEmmcImage
from lbkit.tasks.image_maker.make_image import TaskMakeImage

log = Logger("build_image")

src_cwd = os.path.split(os.path.realpath(__file__))[0]

class TaskMakeQemuImage(TaskMakeImage):
    def __init__(self, config, name):
        super().__init__(config, name)
        self.chip_model = None
        chip_model = self.config.get_product_config("chip_model")
        if chip_model not in ["qemu_arm64"]:
            return
        self.chip_model = chip_model
        self.uboot = self.config.get_product_config("flash/uboot")
        self.kernel = self.config.get_product_config("flash/kernel")
        self.rootfs = self.config.rootfs_img

    @staticmethod
    def _trans_to_blk_1m(cfg: str):
        if cfg.endswith("K"):
            return int(cfg[:-1]) / 1024
        elif cfg.endswith("M"):
            return int(cfg[:-1])
        elif cfg.endswith("G"):
            return int(cfg[:-1]) * 1024

    def available(self):
        if not self.chip_model:
            return False
        if self.config.get_product_config("flash/type") != "emmc":
            return False
        return True

    def run(self):
        """任务入口"""
        """检查manifest文件是否满足schema格式描述"""
        os.chdir(self.config.output_path)

        mk = MekeEmmcImage(os.path.join(self.config.temp_path, "emmc_tmp_dir"))
        rootfs_size = self.config.get_product_config("rootfs/size")
        if rootfs_size:
            mk.rootfs_blk_1m = self._trans_to_blk_1m(rootfs_size)
        emmc_size = self.config.get_product_config("flash/size")
        if emmc_size:
            mk.size_1m = self._trans_to_blk_1m(emmc_size)
        tmpdir = tempfile.TemporaryDirectory()
        cmd = f"fuse2fs {self.rootfs} {tmpdir.name} -o fakeroot"
        self.exec(cmd)
        # 复制内核文件到boot/extlinux/Image
        cmd = f"cp {self.kernel} {tmpdir.name}/boot/Image"
        self.exec(cmd)
        cmd = f"chown 0:0 {tmpdir.name}/boot/Image"
        self.exec(cmd)
        cmd = f"umount {tmpdir.name}"
        self.exec(cmd)
        mk.run(self.config.rootfs_img, "qemu.img")
        cmd = 'cp /usr/share/litebmc/qemu.conf qemu.conf'
        self.exec(cmd)
        cmd = f'cp {self.uboot} u-boot.bin'
        self.exec(cmd)
        output_img = os.path.join(self.config.output_path, "litebmc_qemu.tar.gz")
        cmd = f'tar -czf {output_img} -C . qemu.img u-boot.bin qemu.conf'
        self.exec(cmd)
        log.success(f"Create litebmc image {output_img} successfully")
        return 0

if __name__ == "__main__":
    config = Config()
    build = TaskMakeQemuImage(config, "test")
    build.run()