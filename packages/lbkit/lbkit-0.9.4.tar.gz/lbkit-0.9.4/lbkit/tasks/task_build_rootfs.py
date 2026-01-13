"""完成rootfs镜像打包."""
import os
import shutil
from lbkit.tasks.config import Config
from lbkit.tasks.task import Task
from lbkit.log import Logger
from lbkit import errors

log = Logger("build_rootfs")

src_cwd = os.path.split(os.path.realpath(__file__))[0]
IMG_FILE = "rootfs.img"

class TaskClass(Task):
    def __init__(self, config, name):
        super().__init__(config, name)
        # 基础rootfs镜像
        self.rootfs = self.config.get_product_config("rootfs/file")
        # 原始文件系统格式
        self.ori_fstype = self.config.get_manifest_config("rootfs/fstype")
        # 目标文件系统格式
        self.fstype = self.config.get_product_config("rootfs/fstype")
        self.append_files = self.config.get_product_config("rootfs/append_files", [])
        # 目标文件系统大小
        size = self.config.get_product_config("rootfs/size")
        self.size = int(size[:-1])
        if size.endswith("G"):
            self.size *= 1024

        self.work_dir = os.path.join(self.config.temp_path, "make_rootfs")
        os.makedirs(self.work_dir, exist_ok=True)

    """构建rootfs镜像"""
    def do_permission(self, per_file: str):
        """完成组件制品赋权"""
        if not os.path.isfile(per_file):
            return
        log.info("Do permission, file: %s", per_file)
        with open(per_file, "r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if line.startswith("#") or len(line) == 0:
                    continue
                log.debug("Permission line: %s", line)
                chunk = line.split()
                if len(chunk) < 5:
                    raise errors.PermissionFormatError(f"Permission format with error, line: {line}")
                if not chunk[0].startswith("/"):
                    raise errors.PermissionFormatError(f"Permission file error, must begin with \"/\", get: {chunk[0]}")
                if not chunk[3].isnumeric() or not chunk[4].isnumeric():
                    raise errors.PermissionFormatError(f"Permission uid or gid error, must is numeric, uid({chunk[3]}), gid({chunk[4]})")
                chunk[0] = chunk[0].lstrip("/")
                if chunk[1] != "f" and chunk[1] != "d" and chunk[1] != "s" and chunk[1] != "r":
                    raise errors.PermissionFormatError(f"Permission type error, only support 'f' 's' 'd' 'r', get({chunk[1]}), ignore")
                if chunk[1] == "d" and not os.path.isdir(chunk[0]):
                    log.error("Permission error, %s is not directory", chunk[0])
                if chunk[1] == "s" and not os.path.islink(chunk[0]):
                    log.error("Permission error, %s is not directory", chunk[0])
                uid = int(chunk[3])
                gid = int(chunk[4])
                pri = chunk[2]
                if (chunk[1] == "f" and os.path.isdir(chunk[0])) or chunk[1] == "r":
                    for subf in os.listdir(chunk[0]):
                        file_path = os.path.join(chunk[0], subf)
                        if not os.path.isfile(file_path):
                            continue
                        log.debug("chmod %s", file_path)
                        cmd = f"chmod {pri} {file_path}"
                        self.exec(cmd)
                        cmd = f"chown {uid}:{gid} {file_path}"
                        self.exec(cmd)
                else:
                    cmd = f"chmod {pri} {chunk[0]}"
                    self.exec(cmd)
                    cmd = f"chown {uid}:{gid} {chunk[0]}"
                    self.exec(cmd)

    def copy_conan_install(self, src_dir, mnt_path):
        src_dir += "/"
        cmd = f"rsync -aHK --exclude '*.hpp' --exclude '*.h'"
        cmd += f" --exclude 'rootfs.tar' --exclude 'u-boot.bin'"
        cmd += f" --exclude 'conanmanifest.txt' --exclude 'conaninfo.txt'"
        cmd += f" --exclude '*.a' --chown=0:0 {src_dir} {mnt_path}"
        log.info("copy %s to %s", src_dir, mnt_path)
        self.exec(cmd, echo_cmd=False)
        strip = self.get_manifest_config("metadata/strip")
        for root, dirs, files in os.walk(src_dir):
            root = root.replace(src_dir, "")
            for dir in dirs:
                name = os.path.join(mnt_path, root, dir)
                if not os.path.isdir(name):
                    continue
                cmd = f"chown 0:0 {name}"
                self.exec(cmd, echo_cmd=False)
            for file in files:
                name = os.path.join(mnt_path, root, file)
                cmd = f"chown -h 0:0 {name}"
                if not os.path.isfile(name):
                    continue
                self.exec(cmd, echo_cmd=False)
                if name.find("usr/share") > 0 and name.find("bin") == -1:
                    continue
                suffix = name.split(".")[-1]
                no_need_strip = ["json", "html", "md", "txt", "yaml", "xml"]
                no_need_strip.extend(["yml", "mo", "conf", "gz", "inc", "service", "py"])
                no_need_strip.extend(["m4", "pc", "cmake", "rules", "ts", "js", "png"])
                no_need_strip.extend(["jpg", "jpeg", "mpeg", "c", "h", "hpp", "ko"])
                if suffix != name and suffix in no_need_strip:
                    continue
                strip = self.get_manifest_config("metadata/strip")
                if strip:
                    cmds = [f"file {name}", "grep \"not stripped\"", f"{self.config.strip} -s {name}"]
                    self.pipe(cmds, error_log="", ignore_error=True)
        per_file = os.path.join(src_dir, "permissions")
        self.do_permission(per_file)

    def apply_permission(self, file, permission):
        chunks = permission.split(" ")
        owner = chunks[0]
        perm = chunks[1]
        cmd = f"chmod {perm} {file}"
        self.exec(cmd)
        cmd = f"chown {owner} {file}"
        self.exec(cmd)

    def append_files_to_rootfs(self, mnt_path):
        for file in self.append_files:
            source = file.get("source")
            source = os.path.realpath(source)
            dest = file.get("dest")
            dest = os.path.join(mnt_path, dest)
            file_perm = file.get("files_permission", "0:0 640")
            dir_perm = file.get("dirs_permission", "0:0 750")
            if os.path.isfile(source):
                dirname = os.path.dirname(dest)
                if dirname and not os.path.isdir(dirname):
                    os.makedirs(dirname, exist_ok=True)
                cmd = f"cp {source} {dest}"
                self.exec(cmd)
                self.apply_permission(dest, file_perm)
            elif os.path.isdir(source):
                os.makedirs(dest, exist_ok=True)
                for file in os.listdir(source):
                    file = os.path.join(source, file)
                    if os.path.isfile(file):
                        cmd = f"cp {file} {dest}/"
                    else:
                        cmd = f"cp {file} {dest}/ -rf"
                    self.exec(cmd)
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file = os.path.join(root, file)
                        name = file[len(source) + 1:]
                        dest_name = os.path.join(dest, name)
                        self.apply_permission(dest_name, file_perm)
                    for dir in dirs:
                        dir = os.path.join(root, dir)
                        name = dir[len(source) + 1:]
                        dest_name = os.path.join(dest, name)
                        self.apply_permission(dest_name, dir_perm)
            else:
                raise Exception(f"Copy append_files to {dest} failed because source file {source} does not exist")

    def merge_rootfs(self):
        """将产品依赖的所有组件安装到rootfs镜像中"""
        mnt_path = self.config.mnt_path
        self.exec("umount " + mnt_path, ignore_error=True)
        shutil.rmtree(mnt_path, ignore_errors=True)
        os.makedirs(mnt_path)

        # 挂载rootfs镜像
        self.exec(f"fuse2fs {self.rootfs} {mnt_path} -o fakeroot")
        # 将镜像大小设置为目标大小的1.5倍，预留一部分空间
        new_size = int(self.size * 1.5)
        tmp_img = os.path.join(self.work_dir, "rootfs.img")
        cmd = f"mkfs.ext4 -d {mnt_path} -r 1 -N 0 -m 5 -L \"rootfs\" -O ^64bit {tmp_img} \"{new_size}M\""
        self.exec(cmd)
        self.exec(f"umount {mnt_path}")
        # 重新挂载临时文件
        self.exec(f"fuse2fs {tmp_img} {mnt_path} -o fakeroot")
        # 切换到rootfs挂载目录
        os.chdir(mnt_path)
        log.info("Copy customization rootfs......")
        for src_dir in self.config.conan_install:
            self.copy_conan_install(src_dir, mnt_path)

        # copy product self-owned rootfs
        product_rootfs = os.path.join(self.config.work_dir, "rootfs")
        if os.path.isdir(product_rootfs):
            self.copy_conan_install(product_rootfs, mnt_path)

        # 设置boot目录权限
        log.info("设置boot目录权限")
        self.exec(f"chown 0:0 boot/ -R")
        self.exec(f"chmod 600 boot/ -R")
        if os.path.isdir("extlinux"):
            self.exec(f"chmod 700 boot/extlinux/")
        # 执行rootfs定制化脚本
        os.chdir(self.config.work_dir)
        hook_name = "hook.post_rootfs"
        self.do_hook(hook_name)

        # 清理冗余文件
        inc_dir = os.path.join(self.config.mnt_path, "include")
        if os.path.isdir(inc_dir):
            cmd = "rm -rf " + inc_dir
            self.exec(cmd)
        cmd = "rm " + os.path.join(self.config.mnt_path, "permissions")
        self.exec(cmd)

        log.info("remove all .fuse_hiddeng* files")
        cmds = [f"find {self.config.mnt_path} -name .fuse_hidden*", "xargs -i{} rm {}"]
        self.pipe(cmds)

        self.append_files_to_rootfs(mnt_path)

        os.chdir(self.config.output_path)

        if self.fstype == "ext4":
            cmd = f"mkfs.ext4 -d {mnt_path} -r 1 -N 0 -m 5 -L \"rootfs\" -O ^64bit {self.config.rootfs_img} \"{self.size}M\""
            self.exec(cmd)
        elif self.fstype == "ubi":
            min_io_size = self.config.get_product_config("rootfs/min_io_size", 2048)
            leb_size = self.config.get_product_config("rootfs/leb_size", 126976)
            max_leb_cnt = self.config.get_product_config("rootfs/leb_size", 1024)
            cmd = f"mkfs.ubifs -r {mnt_path} -m {min_io_size} -e {leb_size} -c {max_leb_cnt} -o {self.config.rootfs_img} -v"
            self.exec(cmd, verbose=True)
            with open("ubinize.cfg", "w+") as fp:
                fp.write(f"[ubifs]\n")
                fp.write(f"mode=ubi\n")
                fp.write(f"image={self.config.rootfs_img}\n")
                fp.write(f"vol_id=0\n")
                fp.write(f"vol_size={self.size * 0x100000}\n")
                fp.write(f"vol_type=dynamic\n")
                fp.write(f"vol_name=rootfs\n")
                fp.write(f"vol_flags=autoresize\n")
            blk_size = 1
            tmp_size = leb_size
            while True:
                blk_size <<= 1
                tmp_size >>= 1
                if tmp_size == 0:
                    break
            cmd = f"ubinize -o ubi.img -m {min_io_size} -p {blk_size} -s 2048 ubinize.cfg -v"
            self.exec(cmd, verbose=True)
            cmd = f"mv ubi.img {self.config.rootfs_img}"
            self.exec(cmd)
            stat = os.stat(self.config.rootfs_img)
            if stat.st_size > self.size * 1024 * 1024:
                raise Exception(f"The size of {self.config.rootfs_img} is {stat.st_size}Bytes, bigger than limit size {self.size * 1024 * 1024}Bytes")

        self.exec("umount " + mnt_path)
        os.unlink(tmp_img)

    def run(self):
        # 任务入口
        self.merge_rootfs()
        log.success(f"Create image {self.config.rootfs_img} successfully")
        return 0

if __name__ == "__main__":
    config = Config()
    build = TaskClass(config, "test")
    build.run()