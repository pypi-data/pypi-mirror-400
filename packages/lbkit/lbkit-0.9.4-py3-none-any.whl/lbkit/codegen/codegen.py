"""
    DBus接口代码自动生成
"""
import os
import sys
import re
import json
import yaml
import argparse
from lbkit.codegen.idf_interface import IdfInterface

from mako.lookup import TemplateLookup
from lbkit.log import Logger
from lbkit.helper import Helper
from lbkit.errors import ArgException
from lbkit.misc import SmartFormatter

lb_cwd = os.path.split(os.path.realpath(__file__))[0]
log = Logger("codegen")


class CodeGenHistory():
    def __init__(self, lb_base: str, description: str, lb_base_compatible_required: str):
        self.lb_base = lb_base
        self.description = description
        # lb_base兼容性配置项
        self.lb_base_compatible_required = lb_base_compatible_required


class Version():
    def __init__(self, ver_str):
        if not re.match("^([0-9]|([1-9][0-9]*))\\.([0-9]|([1-9][0-9]*))$", ver_str):
            raise Exception("Version string {ver_str} not match with regex ^([0-9]|([1-9][0-9]*))\\.([0-9]|([1-9][0-9]*))$")
        self.info: CodeGenHistory = history_versions.get(ver_str)
        chunks = ver_str.split(".")
        self.major = int(chunks[0])
        self.minor = int(chunks[1])
        self.str = str(self.major) + "." + str(self.minor)

    def bt(self, next_ver):
        next = Version(next_ver)
        if self.major > next.major or (self.major == next.major and self.minor > next.minor):
            return True
        return False

    def be(self, next_ver):
        next = Version(next_ver)
        if self.major > next.major or (self.major == next.major and self.minor >= next.minor):
            return True
        return False

    def lt(self, next_ver):
        next = Version(next_ver)
        if self.major < next.major or (self.major == next.major and self.minor < next.minor):
            return True
        return False

    def le(self, next_ver):
        next = Version(next_ver)
        if self.major < next.major or (self.major == next.major and self.minor <= next.minor):
            return True
        return False

# 历史自动生成版本号，计划用于用于生成代码稳定性测试
# TODO： 支持生成代码稳定性测试，确保生成的代码一致性
history_versions = {
    "5.3": CodeGenHistory("lb_base/[>=0.8.5 <0.9.0]", "支持32位操作系统", "8004"),
    "5.4": CodeGenHistory("lb_base/[>=0.9.0 <0.10.0]", "LBInterface增加alias", "9000"),
}
__version__=Version("5.4")


def version_check(ver_str: str):
    if not re.match("^([0-9]|([1-9][0-9]*))\\.([0-9]|([1-9][0-9]*))$", ver_str):
        raise Exception(f"Version string {ver_str} not match with regex ^([0-9]|([1-9][0-9]*))\\.([0-9]|([1-9][0-9]*))$")
    if "x" not in ver_str:
        return ver_str
    if not history_versions.get(ver_str):
        log.error(f"Unkonw codegen version {ver_str}, supported versions:")
        for ver, msg in history_versions.items():
            log.error(f"    {ver}: {msg}")
        raise Exception(f"Can't found the valid version for {ver_str}")

def codegen_version_max():
    max_v = __version__
    for ver_str, _ in history_versions.items():
        next_ver = Version(ver_str)
        if next_ver.bt(max_v.str):
            max_v = next_ver
    return max_v.str

def codegen_version_arg(parser: argparse.ArgumentParser, default=__version__.str, short_arg="-cv", full_arg="--codegen_version"):
    # 默认的自动生成工具版本号为2
    help=f'''must less than or equal to {codegen_version_max()}, default: {default}

        codegen versions:
        '''
    for ver, detail in history_versions.items():
        help += f"- {ver}: compatible with {detail.lb_base}, {detail.description}\n"
    parser.add_argument(short_arg, full_arg, help=help, type=str, default=__version__.str)


class CodeGen(object):
    def __init__(self, args):
        self.args = args
        self.codegen_version = __version__
        self.log_level = "NOTSET"

    def _gen(self, idf_file, directory=".", code_type="all"):
        directory = os.path.realpath(directory)
        interface = self.get_interface(idf_file)
        code_types = ["server", "client", "public"]
        if code_type != "all":
            code_types = [code_type]
        log.info(f"Codegen version: {self.codegen_version.str}")
        for ct in code_types:
            os.makedirs(os.path.join(directory, ct), exist_ok=True)
            out_file = os.path.join(directory, ct, interface.name + ".xml")
            interface.render_dbus_xml("interface.introspect.xml.mako", out_file)
            out_file = os.path.join(directory, ct, interface.alias + ".h")
            interface.render_c_source(ct + ".h.mako", out_file)
            out_file = os.path.join(directory, ct, interface.alias + ".c")
            interface.render_c_source(ct + ".c.mako", out_file)
            if "server" == ct:
                # 生成接口schema文件
                odf_file = os.path.join(directory, "server", "schema", f"{interface.alias}.json")
                os.makedirs(os.path.dirname(odf_file), exist_ok=True)
                odf_data = interface.odf_schema
                with open(odf_file, "w", encoding="utf-8") as fp:
                    json.dump(odf_data, fp, sort_keys=False, indent=4)
        json_file = os.path.join(directory, "package.yml")
        data = {
            "version": interface.version,
            "name": interface.name,
            "alias": interface.alias
        }
        with open(json_file, "w", encoding="utf-8") as fp:
            yaml.dump(data, fp, encoding='utf-8', allow_unicode=True)

    def get_interface(self, idf_file):
        lookup = TemplateLookup(directories=os.path.join(lb_cwd, "template"))
        return IdfInterface(lookup, idf_file, self.codegen_version, self.log_level)

    def run(self):
        """
        代码自动生成.

        支持自动生成服务端和客户端C代码
        """
        parser = argparse.ArgumentParser(description=self.run.__doc__,
                                         prog="lbkit gen",
                                         formatter_class=SmartFormatter)
        codegen_version_arg(parser)
        parser.add_argument("-d", "--directory", help='generate code directory', default=".")
        parser.add_argument("-l", "--log_level", help='show log level',
                            choices=[
                                "CRITICAL", "FATAL", "ERROR", "WARN",
                                "WARNING", "INFO", "DEBUG", "NOTSET",
                            ], default=None)
        parser.add_argument("-t", "--codetype", help='code type, default: all', default="all", choices=["public", "server", "client", "all"])
        group2 = parser.add_argument_group('cdf file', 'Generate code using the specified CDF file')
        group2.add_argument("-c", "--cdf_file", help='component description file, default metadata/package.yml', default=None)
        group1 = parser.add_argument_group('idf file', 'Generate code using the specified IDF file')
        group1.add_argument("-i", "--idf_file", help='A IDF file to be processed e.g.: com.litebmc.Upgrade.xml', default=None)

        args = parser.parse_args(self.args)
        if args.log_level:
            self.log_level = args.log_level
            log.setLevel(self.log_level)

        if args.cdf_file:
            if not os.path.isfile(args.cdf_file):
                raise ArgException(f"argument -c/--cdf_file: {args.cdf_file} not exist")
            configs = Helper.read_yaml(args.cdf_file, "codegen", [])
            # 为保障兼容，package.yml未指定版本号的，默认使用2，该版本配套lb_base/0.6.0版本，其LBProperty无set/get成员
            ver_str = os.environ.get("CODEGEN_VERSION")
            if ver_str is None:
                ver_str = Helper.read_yaml(args.cdf_file, "codegen_version", args.codegen_version)
            version_check(ver_str)
            self.codegen_version = Version(ver_str)
            for cfg in configs:
                file = cfg.get("file")
                if file is None:
                    log.error("%s的自动代码生成配置不正确, 缺少file元素指定描述文件", args.cdf_file)
                    sys.exit(-1)
                if not file.endswith(".yaml") :
                    log.error("%s的自动代码生成配置不正确, %s的文件名不是以.yaml结束", args.cdf_file, file)
                    sys.exit(-1)
                if not os.path.isfile(file):
                    log.error("%s的自动代码生成配置不正确, %s不是一个文件", args.cdf_file, file)
                    sys.exit(-1)
                outdir = cfg.get("outdir", os.getcwd())
                self._gen(file, outdir)
            return
        else:
            ver_str = os.environ.get("CODEGEN_VERSION")
            if ver_str is None:
                ver_str = args.codegen_version
            version_check(ver_str)
            self.codegen_version = Version(ver_str)

        intf_file = args.idf_file
        if not intf_file:
            raise ArgException(f"argument error, arguments -c/--cdf_file and -i/--idf_file are not set")
        if not os.path.isfile(intf_file):
            raise ArgException(f"argument -i/--idf_file: {args.idf_file} not exist")
        if self.codegen_version.bt(codegen_version_max()):
            raise ArgException(f"argument -cv/--codegen_version: validate failed, must less than or equal to {__version__.str}")
        out_dir = os.path.join(os.getcwd(), args.directory)
        if not intf_file.endswith(".yaml"):
            raise ArgException(f"The IDF file ({intf_file}) not endswith .yaml")
        if  not os.path.isfile(intf_file):
            raise ArgException(f"The IDF file ({intf_file}) not exist")
        if not os.path.isdir(out_dir):
            log.warning(f"Directory {args.directory} not exist, try create")
            os.makedirs(out_dir)
        self._gen(intf_file, out_dir, args.codetype)

if __name__ == "__main__":
    gen = CodeGen(sys.argv)
    gen._gen("com.litebmc.test.xml", ".")
