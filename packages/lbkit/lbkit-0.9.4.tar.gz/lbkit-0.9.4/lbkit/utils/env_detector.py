#!/usr/bin/env python3

import os
import configparser
from lbkit.tools import Tools
from lbkit.misc import load_yml_with_json_schema_validate

tools = Tools("EnvDetector")
log = tools.log


class LbkitComponent(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config


class LbkitManifest(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config

class UKR(object):
    def __init__(self, folder, config: configparser.ConfigParser):
        self.folder = os.path.realpath(folder)
        self.config = config


class EnvDetector(object):
    def __init__(self):
        """初始化"""
        self.component: LbkitComponent = None
        self.manifest: LbkitManifest = None
        self.ukr: UKR = None
        self.cwd = os.getcwd()
        """探测环境"""
        cwd = self.cwd
        while cwd != "/":
            conf_file = os.path.join(cwd, ".lbkit.yml")
            if os.path.isfile(conf_file):
                conf = load_yml_with_json_schema_validate(conf_file, "/usr/share/litebmc/schema/lbk_config.v1.json")
                ukr_conf = conf.get("uboot_kernel_rootfs")
                if ukr_conf:
                    folder = ukr_conf.get("folder")
                    self.ukr = UKR(os.path.join(cwd, folder), ukr_conf)
                    return
            if os.path.isfile(os.path.join(cwd, "manifest.yml")):
                self.manifest = LbkitManifest(cwd, None)
                return
            if os.path.isfile(os.path.join(cwd, "metadata/package.yml")):
                self.component = LbkitComponent(cwd, None)
                return
            cwd = os.path.dirname(cwd)
