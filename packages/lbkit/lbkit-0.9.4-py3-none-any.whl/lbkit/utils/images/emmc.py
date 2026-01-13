"""环境准备"""
import os
import tempfile
from lbkit import errors
from lbkit.tools import Tools


src_cwd = os.path.split(os.path.realpath(__file__))[0]

class MakeImage():
    def __init__(self, tmp_dir):
        self.tools = Tools("make emmc_image")
        self.log = self.tools.log
        self.size_1m = 4096
        self.misc_blk_1k = 1024
        self.ubootenv_blk_1k = 1024
        self.vbmeta_blk_1k = 1024
        # 会创建3个rootfs镜像
        self.rootfs_blk_1m = 1024
        # 用户数据区，默认使用剩余的磁盘空间
        self.userdata_blk_1m = 0
        self.tmp_dir = tmp_dir
        if not os.path.isdir(tmp_dir):
            os.makedirs(self.tmp_dir)
        else:
            cmd = "umount " + tmp_dir
            self.tools.exec(cmd, ignore_error=True, echo_cmd=False)

    def run(self, rootfs, output="emmc.img"):
        if self.userdata_blk_1m < 128 and self.userdata_blk_1m != 0:
            raise errors.LiteBmcException(f"参数检测错误，userdata分区至少需要128M，实际为{self.userdata_blk_1m}M大小")

        blk_1k = self.misc_blk_1k + self.ubootenv_blk_1k + self.vbmeta_blk_1k
        blk_1k += self.rootfs_blk_1m * 1024 * 3
        if self.userdata_blk_1m == 0:
            blk_1k += 128 * 1024
        else:
            blk_1k += self.userdata_blk_1m * 1024
        if self.size_1m * 1024 < blk_1k:
            raise errors.LiteBmcException(f"参数检测错误，镜像文件{self.size_1m}M小于需要的{int(blk_1k / 1024)}M大小")
        if self.userdata_blk_1m == 0:
            self.userdata_blk_1m = int(self.size_1m - blk_1k / 1024) - 128
            self.log.info(f"重置userdata大小为{self.userdata_blk_1m}M")
        if os.path.isfile(output):
            os.unlink(output)
        self.log.info(f"创建一个{self.size_1m}M大小的镜像")
        self.tools.exec(f"dd if=/dev/zero of={output} bs=1M count=1 seek={self.size_1m -1}")
        self.tools.exec(f"parted {output} mktable gpt")
        start = 4096
        end = start + self.misc_blk_1k * 2
        self.log.info(f"创建misc区")
        self.tools.exec(f"parted {output} mkpart misc {start}s {end - 1}s")
        start = end
        end += self.ubootenv_blk_1k * 2
        self.log.info(f"创建ubootenv区")
        self.tools.exec(f"parted -s -a none {output} mkpart ubootenv {start}s {end - 1}s")
        start = end
        end += self.vbmeta_blk_1k * 2
        self.log.info(f"创建vbmeta区")
        self.tools.exec(f"parted -s -a none {output} mkpart vbmeta {start}s {end - 1}s")
        start = end
        end += self.rootfs_blk_1m * 1024 * 2
        self.log.info("创建rootfs镜像区")
        self.tools.exec(f"parted -s -a none {output} mkpart rootfs_a {start}s {end - 1}s")
        self.log.info("复制镜像文件到rootfs_a区域")
        self.tools.exec(f"dd if={rootfs} of={output} bs=512 seek={start} conv=notrunc")
        self.log.info("制作rootfs_b")
        start = end
        end += self.rootfs_blk_1m * 1024 * 2
        self.tools.exec(f"parted -s -a none {output} mkpart rootfs_b {start}s {end - 1}s")
        # self.log.info("复制镜像文件到rootfs_b")
        # self.tools.exec(f"dd if={rootfs} of={output} bs=512 seek={start} conv=notrunc")
        self.log.info("制作rootfs_c")
        start = end
        end += self.rootfs_blk_1m * 1024 * 2
        self.tools.exec(f"parted -s -a none {output} mkpart rootfs_c {start}s {end - 1}s")
        # self.log.info("复制镜像文件到rootfs_c")
        # self.tools.exec(f"dd if={rootfs} of={output} bs=512 seek={start} conv=notrunc")
        start = end
        self.log.info("制作userdata区")
        end += self.userdata_blk_1m * 1024 * 2
        self.tools.exec(f"parted -s -a none {output} mkpart userdata ext4 {start}s {end - 1}s")
        self.log.info("为userdata区创建一个空镜像")
        tmpfile = tempfile.NamedTemporaryFile()
        empty_img = tmpfile.name
        self.tools.exec(f"dd if=/dev/zero of={empty_img} bs=1M seek={self.userdata_blk_1m - 1} count=1")
        self.tools.exec(f"mkfs.ext4 {empty_img}")
        self.log.info("复制空镜像到userdata区")
        self.tools.exec(f"dd if={empty_img} of={output} bs=512 seek={start} conv=notrunc")
        self.tools.exec(f"parted {output} set 4 boot on")

if __name__ == "__main__":
    mk = MakeImage()
    mk.run("./rootfs.img", "./qemu.img")
