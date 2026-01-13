"""集成构建配置项"""
import argparse
import os, sys
from lbkit.log import Logger
from lbkit.misc import load_yml_with_json_schema_validate, TARGETS_DIR

log = Logger("build_config")


class Config(object):
    """集成构建的配置项"""
    def __init__(self, args = None):
        parser = self.arg_parser()
        args = parser.parse_args(args)

        # 配置项
        self.manifest = os.path.join(os.getcwd(), args.manifest)
        self.manifest = os.path.realpath(self.manifest)
        # 配置项目录
        self.work_dir = os.path.dirname(self.manifest)
        sys.path.append(self.work_dir)
        # 是否从源码构建
        self.from_source = args.from_source
        # 是否打印详细信息
        self.verbose = True if os.environ.get("VERBOSE", False) else False
        # 编译类型
        self.build_type = args.build_type
        # conan中心仓
        self.remote = args.remote

        if not os.path.isfile(self.manifest):
            raise FileNotFoundError(f"File {args.manifest} not exist")

        # 编译主机配置项
        self.profile_build = args.profile_build
        # 待所有参数确认后会调用refresh_profile_name设置正确的profile
        self.profile_host = None

        # conan.lock options
        self.update_lockfile = args.update_lockfile
        self.target = args.target
        self.product = args.product

        # 设置并创建构建所需目录
        log.info("Work dir: %s", self.work_dir)
        self.code_path = os.getcwd()
        self.temp_path = os.path.join(self.code_path, ".temp")
        self.output_path = os.path.join(self.temp_path, "output")
        self.download_path = os.path.join(self.temp_path, "download")
        self.tool_path = os.path.join(self.temp_path, "tools")
        self.compiler_path = os.path.join(self.tool_path, "compiler")
        # conan组件打包目录
        self.conan_install = []
        self.mnt_path = os.path.join(self.temp_path, "mnt_path")
        self.rootfs_img = os.path.join(self.output_path, "rootfs.img")
        # rootfs、uboot和kernel关键文件路径
        os.makedirs(self.temp_path, exist_ok=True)
        os.makedirs(self.tool_path, exist_ok=True)
        os.makedirs(self.output_path, exist_ok=True)
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.compiler_path, exist_ok=True)
        # 制作rootfs时需要strip镜像，所以需要单独指定stip路径
        self.strip = "strip"
        self.check_product()
        # 刷新conan profile
        self.refresh_profile_name()

    @staticmethod
    def target_list():
        targets = {}
        dirname = os.path.join(TARGETS_DIR)
        for file in os.listdir(dirname):
            if not file.endswith(".yml"):
                continue
            tgt_file = os.path.join(TARGETS_DIR, file)
            targets[file] = tgt_file
        return targets

    @staticmethod
    def arg_parser():
        """返回配置项支持的参数"""
        parser = argparse.ArgumentParser(description="Build LiteBMC", formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument("-m", "--manifest", help="Specify the manifest.yml, ignored when -l is specified.", default="./manifest.yml")
        parser.add_argument("-s", "--from_source", help="Build from source", action="store_true")
        parser.add_argument("-pr:b", "--profile_build", help="Apply the specified profile to the build machine", default="default")
        parser.add_argument("-bt", "--build_type", type=str, choices=['debug', 'release', 'minsize'], help="Set the build type", default="debug")
        parser.add_argument("-r", "--remote", help="specified conan server", default="litebmc")
        parser.add_argument("-ul", "--update_lockfile", help="update conan.lock", action="store_true")
        parser.add_argument("-p", "--product", help="product name, default product is `default`", default="default")
        targets = Config.target_list()
        target_help = "build target:"
        for tgt, _ in targets.items():
            target_help += "\n* " + tgt[:-4]
        parser.add_argument("-t", "--target", help=target_help, default="default")
        return parser

    def get_manifest_config(self, key: str, default=None):
        """从manifest中读取配置"""
        manifest = self.load_manifest()
        keys = key.split("/")
        for k in keys:
            manifest = manifest.get(k, None)
            if manifest is None:
                return default
        return manifest

    @staticmethod
    def merge_cfg(dst, src):
        """合并两个配置项"""
        # 如果源为None，则返回dst
        if src is None:
            return dst
        # 如果目标是空的，直接返回src
        if not dst:
            return src
        # 如果是数组、标量的直接覆盖dst即可，所以返回src
        if not isinstance(dst, dict):
            return src
        # 如果目标非空，但源是空，直接返回目标
        if not src:
            return dst
        if not isinstance(src, dict):
            raise Exception(f"Merge configuration failed, source config {src} is not a dictionary")
        output = {}
        for key, val in src.items():
            dst_val = dst.get(key)
            output[key] = Config.merge_cfg(dst_val, val)
        for key, val in dst.items():
            # 已经合并过，即目标中存在，但源不存在，直接合并
            if key in output:
                continue
            output[key] = val
        return output

    def get_product_config(self, key: str, default=None):
        """获取产品配置，注意，key只需要基于products/[name]/即可，如 toolchain"""
        global_cfg = self.get_manifest_config(key, default)
        key = f"products/{self.product}/{key}"
        product_cfg = self.get_manifest_config(key, None)
        if not product_cfg:
            return global_cfg
        if not global_cfg:
            return product_cfg
        return Config.merge_cfg(global_cfg, product_cfg)

    def _trans_dependencies_to_dict(self, deps):
        out = {}
        for dep in deps:
            name = dep["package"]
            name = name.split("/")[0]
            out[name] = dep
        return out

    def _merge_dependencies(self, dst, src: dict[str, dict]):
        for key, val in src.items():
            dst[key] = val
        return dst

    def get_dependencies(self):
        debug_cfg = self.get_manifest_config("debug_dependencies", [])
        debug_dict = self._trans_dependencies_to_dict(debug_cfg)
        global_cfg = self.get_manifest_config("dependencies", [])
        global_dict = self._trans_dependencies_to_dict(global_cfg)
        # debug_cfg优先级更高
        tmp = self._merge_dependencies(global_dict, debug_dict)
        key = f"products/{self.product}/dependencies"
        # product_cfg优先级最高
        product_cfg = self.get_manifest_config(key, [])
        product_dict = self._trans_dependencies_to_dict(product_cfg)
        tmp = self._merge_dependencies(tmp, product_dict)
        out = []
        for _, value in tmp.items():
            out.append(value)
        return out

    def load_manifest(self):
        """加载manifest.yml并验证schema文件"""
        template = {}
        template["code_path"] = self.code_path
        template["temp_path"] = self.temp_path
        template["download_path"] = os.path.join(self.download_path)
        return load_yml_with_json_schema_validate(self.manifest, "/usr/share/litebmc/schema/pdf.v1.json", **template)

    def check_product(self):
        products = self.get_manifest_config("products", {})
        if products.get(self.product):
            return
        log.error(f"Only the following products are supported:")
        for key, _ in products.items():
            log.info("    * " + key)
        # todo: 待manifest.yml整改到位到删除下面注释
        # raise Exception(f"Unkown product {self.product}")

    def refresh_profile_name(self):
        self.profile_host = self.get_product_config("toolchain/profile/name", "litebmc")

    def set_build_type(self, value):
        self.build_type = value

    def deal_conf(self, config_dict):
        """
        处理Target级别的配置"target_config"
        当Config类有set_xxx类方法时，则可以在target文件中配置xxx
        """
        if not config_dict or not isinstance(config_dict, dict):
            return
        for key, conf in config_dict.items():
            try:
                method = getattr(self, f"set_{key}")
                method(conf)
            except Exception as e:
                raise Exception(f"目标 config 无效配置: {key}") from e
