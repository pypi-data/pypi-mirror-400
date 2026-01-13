import os
import argparse
import textwrap
import json
import yaml
import re
import requests
import fcntl
from string import Template
from colorama import Fore, Style
from jsonschema import validate, ValidationError
from lbkit.errors import PackageConfigException, HttpRequestException

LOG_DIR = "/tmp/lbkit/log"
TARGETS_DIR = "/usr/share/litebmc/targets"


class Color(object):
    """ Wrapper around colorama colors that are undefined in importing
    """
    RED = Fore.RED  # @UndefinedVariable
    WHITE = Fore.WHITE  # @UndefinedVariable
    CYAN = Fore.CYAN  # @UndefinedVariable
    GREEN = Fore.GREEN  # @UndefinedVariable
    MAGENTA = Fore.MAGENTA  # @UndefinedVariable
    BLUE = Fore.BLUE  # @UndefinedVariable
    YELLOW = Fore.YELLOW  # @UndefinedVariable
    BLACK = Fore.BLACK  # @UndefinedVariable
    RESET_ALL = Style.RESET_ALL

    BRIGHT_RED = Style.BRIGHT + Fore.RED  # @UndefinedVariable
    BRIGHT_BLUE = Style.BRIGHT + Fore.BLUE  # @UndefinedVariable
    BRIGHT_YELLOW = Style.BRIGHT + Fore.YELLOW  # @UndefinedVariable
    BRIGHT_GREEN = Style.BRIGHT + Fore.GREEN  # @UndefinedVariable
    BRIGHT_CYAN = Style.BRIGHT + Fore.CYAN   # @UndefinedVariable
    BRIGHT_WHITE = Style.BRIGHT + Fore.WHITE   # @UndefinedVariable
    BRIGHT_MAGENTA = Style.BRIGHT + Fore.MAGENTA   # @UndefinedVariable


if os.environ.get("COLOR_DARK", 0):
    Color.WHITE = Fore.BLACK
    Color.CYAN = Fore.BLUE
    Color.YELLOW = Fore.MAGENTA
    Color.BRIGHT_WHITE = Fore.BLACK
    Color.BRIGHT_CYAN = Fore.BLUE
    Color.BRIGHT_YELLOW = Fore.MAGENTA
    Color.BRIGHT_GREEN = Fore.GREEN

class SmartFormatter(argparse.HelpFormatter):
    """重写HelpFormatter"""
    def _fill_text(self, text, width, indent):
        """重写HelpFormatter"""
        text = textwrap.dedent(text)
        return ''.join(indent + line for line in text.splitlines(True))

    # 优化帮助文本打印：支持换行符
    def _split_lines(self, text, width):
        ret = []
        for line in text.split("\n"):
            if not line.strip():
                ret.extend(" ")
                continue
            ret.extend(super()._split_lines(line, width))
        return ret

def get_json_schema_file(yml_file, default_json_schema_file):
    """使用json schema文件校验yml_file配置文件"""
    with open(yml_file, "r") as fp:
        for line in fp:
            match = re.search(r"#[ ]*yaml-language-server:[ ]*\$schema=(.*)\n", line)
            if match is not None:
                return match.group(1)
    return default_json_schema_file

def load_json_schema(schema_file):
    """使用json schema文件校验yml_file配置文件"""
    if schema_file.startswith("https://litebmc.com/"):
        resp = requests.get(schema_file)
        if resp.status_code != 200:
            raise HttpRequestException(f"Get {schema_file} failed, status code: {resp.status_code}")
        return json.loads(resp.content)
    elif not os.path.isfile(schema_file):
        raise FileNotFoundError(f"schemafile {schema_file} not exist")
    else:
        with open(schema_file, "r") as fp:
            tmp = fp.read()
            return json.loads(tmp)

def load_yml_with_json_schema_validate(yml_file, default_json_schema_file, **kwargs):
    """使用json schema文件校验yml_file配置文件"""
    schema_file = get_json_schema_file(yml_file, default_json_schema_file)
    if schema_file is None:
        raise FileNotFoundError(f"Can't found invalid schema file in {yml_file}")

    schema = load_json_schema(schema_file)
    try:
        fp = open(yml_file, "r")
        template = Template(fp.read())
        fp.close()
        content = template.safe_substitute(kwargs)
        data = yaml.safe_load(content)
        validate(data, schema)
        return data
    except ValidationError as exc:
        raise PackageConfigException(f"validate {yml_file} failed, schema file is {schema_file}, "
                                     f"message: {exc.message}\n"
                                     "installing redhat.vscode-yaml plugin in vscode will help you write odf files")

class DownloadFlag():
    @staticmethod
    def clean(filename):
        """清理文件标记"""
        filename += ".flag"
        fp = open(filename, "a+")
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fp.truncate(0)
        fcntl.flock(fp, fcntl.F_UNLCK)
        fp.close()

    @staticmethod
    def create(filename, url, new_hash):
        """创建文件标记"""
        filename += ".flag"
        fp = open(filename, "a+")
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fp.seek(0, 0)
        fp.truncate(0)
        fp.write(url + "|" + new_hash)
        fcntl.flock(fp, fcntl.F_UNLCK)
        fp.close()

    @staticmethod
    def read(filename):
        """读取文件标记"""
        filename += ".flag"
        if not os.path.isfile(filename):
            return "", ""
        fp = open(filename, "a+")
        fcntl.flock(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fp.seek(0, 0)
        content = fp.read()
        fcntl.flock(fp, fcntl.F_UNLCK)
        fp.close()
        if len(content) == 0:
            return "", ""
        chunk = content.split("|")
        return chunk[0], chunk[1]