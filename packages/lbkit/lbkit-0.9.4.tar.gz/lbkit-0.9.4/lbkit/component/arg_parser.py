"""组件公共参数"""
import argparse
import os
from lbkit.misc import SmartFormatter
from lbkit.codegen.codegen import codegen_version_arg

cwd = os.getcwd()
lb_cwd = os.path.split(os.path.realpath(__file__))[0]


class ArgParser():
    @staticmethod
    def new(add_help=True):
        parser = argparse.ArgumentParser(
            description="Build component", add_help=add_help, formatter_class=SmartFormatter)
        parser.add_argument("-t", "--build_type", default="Debug",
                            help="Build type(Same as conan's settings.build_type), only Debug,Release can be accepted")
        parser.add_argument("-pr", "--profile", default="default",
                            help="Apply the specified profile to the host machine,\ndefault value: default")
        parser.add_argument("-pr:b", "--profile_build", default="default",
                            help="Apply the specified profile to the build machine,\ndefault value: default")
        parser.add_argument("-ur", "--upload_recipe", action="store_true",
                            help="Upload recipe to remote")
        parser.add_argument("-up", "--upload_package", action="store_true",
                            help="Upload package to remote")
        parser.add_argument("-s", "--from_source", action="store_true",
                            help="Build all depencencies component from source")
        parser.add_argument("--summary", action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--cov", action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument("--test", action="store_true",
                            help=argparse.SUPPRESS)
        parser.add_argument(
            "-r", "--remote", default="litebmc", help="Conan仓别名(等同conan的-r选项)")
        parser.add_argument(
            "-c", "--channel", help='Provide a channel if not specified in mds/package.yml\ndefault value: dev', default="dev")
        parser.add_argument('-o','--pkg_options', action='append', help='Define options values (host machine), e.g.: -o pkg/*:shared=True', required=False, default=[])
        # 默认的自动生成工具版本号为
        codegen_version_arg(parser)
        return parser
