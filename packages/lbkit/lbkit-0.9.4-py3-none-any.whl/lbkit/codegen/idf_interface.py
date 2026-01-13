import os
import re
import copy
import logging
import hashlib
from functools import cached_property
from lbkit.log import Logger
from lbkit.codegen.renderer import Renderer
from lbkit.codegen.ctype_defination import CTYPE_OBJS, RefObjArrayValidator, RefObjValidator
from lbkit.misc import load_yml_with_json_schema_validate, get_json_schema_file
from lbkit.errors import OdfValidateException, LiteBmcException
from lbkit.helper import SigInvalidException, validate_glib_signature

log = Logger("gen_interface")
alias = None

class IDFException(Exception):
    pass

class IdfInterfacePlugin(Renderer):
    def __init__(self):
        super().__init__()
        self.install_dir = None
        self.actions = []

class IdfInterfaceBase(Renderer):
    def __init__(self) -> None:
        super(Renderer, self).__init__()
        self.file: str = None
        self.properties = []
        self.methods = []
        self.signals = []
        self.structures = {}
        self.dictionaries = {}
        self.enumerations = {}
        self.annotations = []
        self.plugin: IdfInterfacePlugin = None
        self.description = None
        self.version = None
        self.alias = None
        self.name = None
        self.object_path = None
        self.codegen_version = None

class IdfAnnotation():
    def __init__(self, name, value):
        self.name = name
        if isinstance(value, str):
            self.value = value
        else:
            raise IDFException(f"the value of {name} with type error, must be a string or bool, but real type is {type(value)}")

            #   "pattern": "^(readwrite|readonly|writeonly|deprecated|hidden|emits_change|emits_invalidation|refval|refobj)(,(readwrite|readonly|writeonly|deprecated|hidden|emits_change|emits_invalidation|refobj|refval))*$"
ANNOTATION_MAP = {
    "deprecated": IdfAnnotation("org.freedesktop.DBus.Deprecated", "true"),
    "emits_change": IdfAnnotation("org.freedesktop.DBus.Property.EmitsChangedSignal", "true"),
    "emits_invalidation": IdfAnnotation("org.freedesktop.DBus.Property.EmitsChangedSignal", "invalidates"),
    "const": IdfAnnotation("org.freedesktop.DBus.Property.EmitsChangedSignal", "const"),
    "emits_false": IdfAnnotation("org.freedesktop.DBus.Property.EmitsChangedSignal", "false"),
    "hidden": IdfAnnotation("com.litebmc.Dbus.Property.Private", "const"),
    "refobj": IdfAnnotation("com.litebmc.Dbus.Property.RefObject", "true"),
    "required": IdfAnnotation("com.litebmc.Dbus.Property.Required", "true"),
}

ACCESS_MAP = {
    "readonly": "read",
    "writeonly": "write",
    "readwrite": "readwrite"
}
ACCESS_FLAG_MAP = {
    "read": "G_DBUS_PROPERTY_INFO_FLAGS_READABLE",
    "write": "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE",
    "readwrite": "G_DBUS_PROPERTY_INFO_FLAGS_WRITABLE | G_DBUS_PROPERTY_INFO_FLAGS_READABLE"
}

# 简单类型的格式化符号
PRINT_FORMATTER_MAP = {
    "byte": "%u",
    "uint16": "G_GUINT16_FORMAT",
    "uint32": "G_GUINT32_FORMAT",
    "uint64": "G_GUINT64_FORMAT",
    "int16": "G_GINT16_FORMAT",
    "int32": "G_GINT32_FORMAT",
    "int64": "G_GINT64_FORMAT",
    "size": "G_GSIZE_FORMAT",
    "ssize": "G_GSSIZE_FORMAT",
    "double": "%d",
    "boolean": "%i",
    "string": "%s",
    "object_path": "%s",
    "signature": "%s"
}

# ^(byte|uint16|uint32|uint64|int16|int32|int64|double|boolean|string|object_path|signature|unixfd|(array\\[(byte|uint16|uint32|uint64|int16|int32|int64|double|boolean|string|object_path|signature|unixfd)\\])|((struct|enum|dict)\\[[a-zA-Z][A-Za-z0-9.]*\\])|(array\\[(struct|enum|dict)\\[[a-zA-Z][A-Za-z0-9.]*\\]\\]))$"

METHOD_NAME_REGEX = "[A-Z][a-zA-Z0-9_]*"
SIGNAL_NAME_REGEX = METHOD_NAME_REGEX
STRU_NAME_REGEX = METHOD_NAME_REGEX
ENUM_NAME_REGEX = METHOD_NAME_REGEX
DICT_NAME_REGEX = METHOD_NAME_REGEX

CTYPE_BASE_REG = "boolean|byte|int16|uint16|int32|uint32|int64|uint64|size|ssize|double|string|object_path|signature|unixfd"
CTYPE_REGEX = CTYPE_BASE_REG + "|variant"

CTYPE_SIGNATURE_MAP = {
    "boolean": "b",
    "byte": "y",
    "int16": "n",
    "uint16": "q",
    "int32": "i",
    "uint32": "u",
    "int64": "x",
    "uint64": "t",
    "ssize": "x",
    "size": "t",
    "double": "d",
    "string": "s",
    "object_path": "o",
    "signature": "g",
    "unixfd": "h",
    "variant": "v",
    # 只有枚举的ctype可能为None，其对外呈现的是字符串，C语言绑定为uint32
    None: "s"
}

def get_intfname_and_ctype(class_alias: str, ctype: str):
    match = re.findall(r"([\w][\w\d]*)", ctype)
    intf = ".".join(match[:-1])
    ctype = match[-1]
    if intf == "self":
        return class_alias, class_alias + "_" + ctype
    return intf, intf + "_" + ctype

def ctype_to_variant_signature(intf: IdfInterfaceBase, ctype: str):
    sig_prefix = ""
    match = re.match(f"^array\[(.*)\]$", ctype)
    if match is not None:
        sig_prefix = "a"
        ctype = match.group(1)
    match = re.match(f"^({CTYPE_REGEX})$", ctype)
    if match is not None:
        return sig_prefix + CTYPE_SIGNATURE_MAP.get(ctype)
    match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)

    match_intf, match_ctype = get_intfname_and_ctype(intf.alias, match.group(2))
    if match_intf != intf.alias:
        intf = intf.dependency_idf_interface[match_intf]
    if match.group(1) == "struct":
        stru = intf.structures.get(match_ctype)
        if stru is None:
            raise IDFException(f"Unknown structure {match_ctype} get")
        return sig_prefix + stru.signature
    elif match.group(1) == "enum":
        return sig_prefix + "s"
    else:
        dictionary = intf.dictionaries.get(match_ctype)
        if dictionary is None:
            raise IDFException(f"Unknown structure {match_ctype} get")
        return sig_prefix + dictionary.signature

def ctype_to_dependency_interface(class_alias: str, ctype: str):
    match = re.match(f"^array\[(.*)\]$", ctype)
    if match is not None:
        ctype = match.group(1)
    match = re.match(f"^({CTYPE_REGEX})$", ctype)
    if match is not None:
        return []
    match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)

    match_intf, _ = get_intfname_and_ctype(class_alias, match.group(2))
    if match_intf == class_alias:
        return []
    return [match_intf]


class IdfCtypeRender():
    intf: IdfInterfaceBase = None
    ctype: str = None
    name: str = ""
    idf_data = None
    default = None
    flags: list[str] = []

    def __init__(self):
        # 非基础类型
        match = re.match(f"^set\[enum\[(.*)\]\]$", self.ctype)
        # 如果set类型由转换成数组，当前不具备对set类型独立处理能力
        if match:
            self.ctype = f"array[enum[{match.group(1)}]]"

    def odf_validate(self, allow_ref):
        log.debug(f"Get odf validate info, name: {self.name}, ctype: {self.ctype}")
        if "variant" == self.ctype:
            return []
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        validator_cfg = self.validator_cfg
        if match:
            if "refobj" in self.flags:
                valiator = RefObjArrayValidator()
                return valiator.odf_validate()
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.odf_validate()
        match = re.match(f"^({CTYPE_BASE_REG})$", self.ctype)
        if match:
            if "refobj" in self.flags:
                valiator = RefObjValidator()
                return valiator.odf_validate()
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.odf_validate()
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if is_array:
            return [f"{stru_name}_validate_odf_v(doc, node, prop, error_list)"]
        else:
            return [f"{stru_name}_validate_odf(doc, node, prop, error_list)"]

    def odf_match_items(self):
        log.debug(f"Get odf validate info, name: {self.name}, ctype: {self.ctype}")
        if "variant" == self.ctype:
            return []
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        validator_cfg = self.validator_cfg
        if match:
            if "refobj" in self.flags:
                valiator = RefObjArrayValidator()
                return valiator.match_items()
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.match_items()
        match = re.match(f"^({CTYPE_BASE_REG})$", self.ctype)
        if match:
            if "refobj" in self.flags:
                valiator = RefObjValidator()
                return valiator.match_items()
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.match_items()
        return []

    def val_validate(self):
        log.debug(f"Get val validate info, name: {self.name}, ctype: {self.ctype}")
        if "variant" == self.ctype:
            return []
        if "refobj" in self.flags:
            return []
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        validator_cfg = self.validator_cfg
        if match:
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.val_validate()

        match = re.match(f"^({CTYPE_BASE_REG})$", self.ctype)
        if not match:
            return []
        ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
        validator = ctype_obj.validator
        if validator_cfg:
            validator.set_validator(validator_cfg, self.name)
        return validator.val_validate()

    def odf_schema(self, allow_ref):
        log.debug(f"Get odf schema info, name: {self.name}, ctype: {self.ctype}")
        if "variant" == self.ctype:
            return None
        validator_cfg = self.validator_cfg
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            if "refobj" in self.flags:
                valiator = RefObjArrayValidator()
                return valiator.odf_schema(allow_ref)
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.odf_schema(allow_ref)
        match = re.match(f"^({CTYPE_BASE_REG})$", self.ctype)
        if match:
            if "refobj" in self.flags:
                valiator = RefObjValidator()
                return valiator.odf_schema(allow_ref)
            ctype_obj = copy.deepcopy(CTYPE_OBJS.get(self.ctype))
            validator = ctype_obj.validator
            if validator_cfg:
                validator.set_validator(validator_cfg, self.name)
            return validator.odf_schema(allow_ref)
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        intf_name, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if intf_name == self.intf.alias:
            intf = self.intf
        else:
            intf = self.intf.dependency_idf_interface[intf_name]
        if match.group(1) == "struct":
            stru = intf.structures.get(stru_name)
            if stru is None:
                raise IDFException(f"Structurer {stru_name} is not found, generate odf for {self.name} failed")
            schema = stru.odf_schema()
        elif match.group(1) == "enum":
            enum = intf.enumerations.get(stru_name)
            if enum is None:
                raise IDFException(f"Enumerate {stru_name} is not found, generate odf for {self.name} failed")
            schema = enum.odf_schema()
        else:
            dict_cls = intf.dictionaries.get(stru_name)
            if dict_cls is None:
                raise IDFException(f"Dictionary {stru_name} is not found, generate odf for {self.name} failed")
            schema = dict_cls.odf_schema()
        if is_array:
            # 结构体数组初始化时为二级空指针，以空指针结束
            if allow_ref:
                return {
                        "type": "array",
                        "item": schema
                    }
            return  {
                "oneOf": [
                    {
                        "$ref": "#/$defs/ref_value"
                    },
                    {
                        "type": "array",
                        "item": schema
                    }
                ]
            }
        else:
            # 结构体成员初始化时为空结构体，由反序列化时填充内容
            if allow_ref:
                return {
                    "oneOf": [
                        {
                            "$ref": "#/$defs/ref_value"
                        },
                        schema
                    ]
                }
            return schema

    def out_declare(self):
        """输出变量申明，用于结构体（接口类、方法请求和响应、信号消息等）申明"""
        log.debug(f"Get out_declare info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.out_declare
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.out_declare
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "struct":
            if is_array:
                # 结构体数组初始化时为二级空指针，以空指针结束
                return [f"{stru_name} ***<arg_name>"]
            else:
                # 结构体成员初始化时为空结构体，由反序列化时填充内容
                return [f"{stru_name} **<arg_name>"]
        elif match.group(1) == "enum":
            if is_array:
                # 枚举数组初始化时为数组空指针
                return [f"gsize *n_<arg_name>", f"{stru_name} **<arg_name>"]
            else:
                return [f"{stru_name} *<arg_name>"]
        else:
            if is_array:
                # 字典数组初始化为二级空指针，以空指针
                return [f"{stru_name} ***<arg_name>"]
            else:
                return [f"{stru_name} **<arg_name>"]

    def declare(self):
        """变量申明，用于结构体（接口类、方法请求和响应、信号消息等）申明"""
        log.debug(f"Get declare info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.declare
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.declare
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "struct":
            if is_array:
                # 结构体数组初始化时为二级空指针，以空指针结束
                return [f"{stru_name} *<const>*<arg_name>"]
            else:
                # 结构体成员初始化时为空结构体，由反序列化时填充内容
                return [f"<const>{stru_name} *<arg_name>"]
        elif match.group(1) == "enum":
            if is_array:
                # 枚举数组初始化时为数组空指针
                return [f"gsize n_<arg_name>", f"<const>{stru_name} *<arg_name>"]
            else:
                return [f"{stru_name} <arg_name>"]
        else:
            if is_array:
                # 字典数组初始化为二级空指针，以空指针
                return [f"{stru_name} *<const>*<arg_name>"]
            else:
                return [f"<const>{stru_name} *<arg_name>"]

    def free_func(self):
        """生成释放数据的C函数，如果是结构体、字典需要生成对象的释放函数"""
        log.debug(f"Get free function info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.free_func
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.free_func
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "enum":
            if is_array:
                return [f"lb_free_p((void **)&<arg_name>)"]
            return []
        else:
            if is_array:
                return [f"{stru_name}_free_v(&<arg_name>)"]
            else:
                return [f"{stru_name}_free(&<arg_name>)"]

    def encode_func(self):
        log.debug(f"Get encode function info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.encode_func
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.encode_func
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "enum":
            if is_array:
                # 入参为二级指针
                return [f"<arg_out> = {stru_name}_encode_v(<arg_name>, n_<arg_name>)"]
            else:
                return [f"<arg_out> = {stru_name}_encode(<arg_name>)"]
        else:
            if is_array:
                # 入参为二级指针
                return [f"<arg_out> = {stru_name}_encode_v(<arg_name>)"]
            else:
                return [f"<arg_out> = {stru_name}_encode(<arg_name>)"]


    def decode_func(self):
        log.debug(f"Get decode info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.decode_func
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.decode_func
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "enum":
            if is_array:
                # 入参为二级指针
                return [f"<arg_in> = {stru_name}_decode_v(<arg_name>, &n_<arg_in>)"]
            else:
                return [f"<arg_in> = {stru_name}_decode(<arg_name>)"]
        else:
            if is_array:
                # 入参为二级指针
                return [f"<arg_in> = {stru_name}_decode_v(<arg_name>)"]
            else:
                return [f"<arg_in> = {stru_name}_decode(<arg_name>)"]

    def const_declare(self):
        """常量申明，用于方法请求和信号消息结构体顶层成员申明"""
        log.debug(f"Get const_declare info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_declare
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_declare
        return self.declare()

    def const_decode_func(self):
        """常量反序列化申明，用于方法请求和信号消息结构体顶层成员反序列化"""
        log.debug(f"Get const_declare_func info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_decode_func
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_decode_func
        return self.decode_func()

    def const_free_func(self):
        """常量释放申明，用于方法请求和信号消息结构体顶层成员反序列化"""
        log.debug(f"Get const_free_func info, name: {self.name}, ctype: {self.ctype}")
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_free_func
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            ctype_obj = CTYPE_OBJS.get(self.ctype)
            return ctype_obj.const_free_func
        return self.free_func()

    def odf_load_func(self):
        log.debug(f"Get odf_load function, name: {self.name}, ctype: {self.ctype}")
        # odf不支持gariant
        match = re.match(f"^array\[(variant)\]$", self.ctype)
        if match:
            return None
        match = re.match(f"^variant$", self.ctype)
        if match:
            return None
        # 字符串数组由结束NULL表示，不需要长度
        match = re.match(f"^array\[(string|object_path|signature)\]$", self.ctype)
        if match:
            return "<arg_name> = load_odf_as_" + match.group(1) + "_v(doc, <node>)"
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if match:
            return "<arg_name> = load_odf_as_" + match.group(1) + "_v(doc, <node>, &n_<arg_name>)"
        match = re.match(f"^({CTYPE_REGEX})$", self.ctype)
        if match:
            return "<arg_name> = load_odf_as_" + match.group(1) + "(doc, <node>)"
        # 非基础类型
        is_array = False
        ctype = self.ctype
        match = re.match(f"^array\[(.*)\]$", ctype)
        if match:
            is_array = True
            ctype = match.group(1)
        match = re.match(f"^(struct|enum|dict)\[(.*)\]$", ctype)
        _, stru_name = get_intfname_and_ctype(self.intf.alias, match.group(2))
        if match.group(1) == "enum":
            if is_array:
                # 入参为二级指针
                return f"<arg_name> = {stru_name}_load_from_odf_v(doc, <node>, &n_<arg_name>)"
            else:
                return f"<arg_name> = {stru_name}_load_from_odf(doc, <node>)"
        else:
            if is_array:
                # 入参为二级指针
                return f"<arg_name> = {stru_name}_load_from_odf_v(doc, <node>)"
            else:
                return f"<arg_name> = {stru_name}_load_from_odf(doc, <node>)"

    @property
    def validator_cfg(self):
        cfg = {}
        if (self.ctype == "string" or self.ctype == "array[string]" or
            self.ctype == "object_path" or self.ctype == "array[object_path]" or
            self.ctype == "signature" or self.ctype == "array[signature]"):
            value = self.idf_data.get("pattern")
            if value:
                cfg["pattern"] = value
        elif self.ctype in ["byte", "array[byte]", "int16", "array[int16]",
                            "uint16", "array[uint16]", "int32", "array[int32]",
                            "uint32", "array[uint32]","int64", "array[int64]",
                            "uint64", "array[uint64]", "size", "array[size]",
                            "ssize", "array[ssize]"]:
            value = self.idf_data.get("max")
            if value:
                cfg["max"] = value
            value = self.idf_data.get("min")
            if value:
                cfg["min"] = value
        if self.ctype == "double" or self.ctype == "array[double]":
            emin = self.idf_data.get("exclusive_min")
            if emin:
                cfg["exclusive_min"] = emin
            emax = self.idf_data.get("exclusive_max")
            if emax:
                cfg["exclusive_max"] = emax
            mmin = self.idf_data.get("min")
            if mmin:
                cfg["min"] = mmin
            mmax = self.idf_data.get("max")
            if mmax:
                cfg["max"] = mmax
            if mmax is not None and emax is not None:
                raise OdfValidateException(f"Cannot set max and exclusive_max at the same time, property {self.name} validation failed")
            if mmin is not None and emin is not None:
                raise OdfValidateException(f"Cannot set min and exclusive_min at the same time, property {self.name} validation failed")
        unique = self.idf_data.get("unique")
        if unique:
            cfg["unique"] = unique
        max_items = self.idf_data.get("max_items")
        if max_items:
            cfg["max_items"] = max_items
        min_items = self.idf_data.get("min_items")
        if min_items:
            cfg["min_items"] = min_items
        matches = self.idf_data.get("matches")
        if matches:
            cfg["matches"] = matches
        return cfg


class IdfProperty(IdfCtypeRender):
    def __init__(self, intf: IdfInterfaceBase, prop_data):
        self.intf = intf
        self.idf_data = prop_data
        self.ctype = prop_data.get("type", "")
        super().__init__()
        self.name = prop_data.get("name")
        self.access = "readwrite"
        self.annotations: list[IdfAnnotation] = []
        self.description = prop_data.get("description", "")
        flags = prop_data.get("flags", "").split(",")
        self.flags = flags
        self.private = True if ("hidden" in flags) else False
        self.deprecated = True if ("deprecated" in flags) else False
        # refobj的ctype只能是s或as
        if "refobj" in flags and self.ctype != "string" and self.ctype != "array[string]":
                raise IDFException(f"property {self.name} with refobj flag but type is neither s nor as")
        for k, v in ACCESS_MAP.items():
            if k in flags:
                self.access = v
                break
        self.access_flag = ACCESS_FLAG_MAP.get(self.access)
        for k, v in ANNOTATION_MAP.items():
            if k in flags:
                self.annotations.append(v)

        c_flags = []
        if self.private:
            c_flags.append("LB_FLAGS_PROPERTY_PRIVATE")
        elif "const" in flags:
            c_flags.append("LB_FLAGS_PROPERTY_EMIT_CONST")
        elif "emits_false" in flags:
            c_flags.append("LB_FLAGS_PROPERTY_EMIT_FALSE")
        elif "emits_invalidation" in flags:
            c_flags.append("LB_FLAGS_PROPERTY_EMIT_INVALIDATES")
        else:
            c_flags.append("LB_FLAGS_PROPERTY_EMIT_TRUE")
        if self.deprecated:
            c_flags.append("LB_FLAGS_PROPERTY_DEPRECATED")
        if len(c_flags) == 0:
            self.desc_flags = "0"
        else:
            self.desc_flags = " | ".join(c_flags)

        self._load_default()

    def _load_default(self):
        # 只有基础类型有default值
        match = re.match(f"^array\[({CTYPE_BASE_REG})\]$", self.ctype)
        if not match:
            match = re.match(f"^({CTYPE_BASE_REG})$", self.ctype)
        if not match:
            return
        self.default = self.idf_data.get("default")
        if self.default is None:
            return

        if self.ctype in ["boolean", "array[boolean]"]:
            return
        pattern = self.idf_data.get("pattern")
        if self.ctype == "string":
            if pattern:
                match = re.match(pattern, self.default)
                if not match:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {self.default}")
            return
        if self.ctype == "array[string]":
            if pattern:
                for val in self.default:
                    match = re.match(pattern, val)
                    if not match:
                        raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {val}")
            return
        if self.ctype == "object_path":
            if pattern:
                match = re.match(pattern, self.default)
                if not match:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {self.default}")
            match = re.match(f"^(/[A-Z0-9a-z_]+)+$", self.default)
            if not match:
                raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"^(/[A-Z0-9a-z_]+)+$\", get default: {self.default}")
            return
        if self.ctype == "array[object_path]":
            for val in self.default:
                if pattern:
                    match = re.match(pattern, val)
                    if not match:
                        raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {val}")
                match = re.match(f"^(/[A-Z0-9a-z_]+)+$", val)
                if not match:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"^(/[A-Z0-9a-z_]+)+$\", get default: {val}")
            return

        if self.ctype == "signature":
            try:
                validate_glib_signature(self.default)
                if pattern:
                    match = re.match(pattern, self.default)
                    if not match:
                        raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {self.default}")
            except SigInvalidException:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}")
            return
        if self.ctype == "array[signature]":
            try:
                for val in self.default:
                    validate_glib_signature(val)
                    if pattern:
                        match = re.match(pattern, self.default)
                        if not match:
                            raise OdfValidateException(f"Fail to validation default value of property {self.name} with pattern \"{pattern}\", get default: {self.default}")
            except SigInvalidException:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}")
            return

        cfg = self.validator_cfg
        if self.ctype in ["byte", "int16", "uint16", "int32", "uint32", "size", "ssize",
                          "int64", "uint64"]:
            mmax = cfg.get("max")
            if mmax is not None and mmax < self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, max: {mmax}")
            mmin = cfg.get("min")
            if mmin is not None and mmin > self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, min: {mmin}")
            return
        if self.ctype in ["array[byte]", "array[int16]", "array[uint16]", "array[int32]", "array[uint32]", "array[size]",
                          "array[ssize]", "array[int64]", "array[uint64]"]:
            for val in self.default:
                mmax = cfg.get("max")
                if mmax is not None and mmax < val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, max: {mmax}")
                mmin = cfg.get("min")
                if mmin is not None and mmin > val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, min: {mmin}")
            return

        if self.ctype == "double":
            emax = cfg.get("exclusive_max")
            mmax = cfg.get("max")
            if emax is not None and emax <= self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, eclusive_max: {emax}")
            if mmax is not None and mmax < self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, max: {mmax}")
            emin = cfg.get("exclusive_min")
            mmin = cfg.get("min")
            if emin is not None and emin >= self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, exclusive_min: {emin}")
            if mmin is not None and mmin > self.default:
                raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {self.default}, min: {emin}")
            return
        if self.ctype == "array[double]":
            for val in self.default:
                emax = cfg.get("exclusive_max")
                mmax = cfg.get("max")
                if emax is not None and emax <= val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, eclusive_max: {emax}")
                if mmax is not None and mmax < val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, max: {mmax}")
                emin = cfg.get("exclusive_min")
                mmin = cfg.get("min")
                if emin is not None and emin >= val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, exclusive_min: {emin}")
                if mmin is not None and mmin > val:
                    raise OdfValidateException(f"Fail to validation default value of property {self.name}, get default: {val}, min: {emin}")
            return
        raise OdfValidateException(f"Only basic type(byaqiuxtdsog) support default value, Property {self.name} type is {self.ctype}")

    @property
    def signature(self):
        return ctype_to_variant_signature(self.intf, self.ctype)

    @cached_property
    def dependency_interface(self):
        return ctype_to_dependency_interface(self.intf.alias, self.ctype)


class IdfParameter(IdfCtypeRender):
    def __init__(self, intf: IdfInterfaceBase, para_data):
        self.idf_data = para_data
        self.intf = intf
        self.name = para_data.get("name")
        self.ctype = para_data.get("type", "")
        self.description = para_data.get("description", "")
        super().__init__()

    @property
    def signature(self):
        return ctype_to_variant_signature(self.intf, self.ctype)

    @cached_property
    def dependency_interface(self):
        return ctype_to_dependency_interface(self.intf.alias, self.ctype)


class IdfParameters():
    def __init__(self, intf: IdfInterfaceBase, para_data):
        self.intf = intf
        self.parameters: list[IdfParameter] = []
        # 是否存在Variant类型的成员
        self.has_variant_value = False
        for ret in para_data:
            para = IdfParameter(intf, ret)
            if para.ctype == "variant":
                self.has_variant_value = True
            self.parameters.append(para)

    @property
    def signature(self):
        sig = ""
        for para in self.parameters:
            sig += para.signature
        return sig

    @cached_property
    def dependency_interface(self):
        deps = []
        for para in self.parameters:
            deps.extend(para.dependency_interface)
        return list(set(deps))


class IdfBase():
    def __init__(self, intf: IdfInterfaceBase, data):
        self.intf = intf
        self.annotations: list[IdfAnnotation] = []
        self.name = data.get("name")
        self.description = data.get("description", "")
        flags = data.get("flags", "").split(",")
        self.deprecated = True if ("deprecated" in flags) else False
        for k, v in ANNOTATION_MAP.items():
            if k in flags:
                self.annotations.append(v)

    @property
    def signature(self):
        return ""


class IdfMethod(IdfBase):
    def __init__(self, intf: IdfInterfaceBase, method_data):
        self.is_plugin = False
        super().__init__(intf, method_data)
        self.parameters: IdfParameters = IdfParameters(intf, method_data.get("parameters", []))
        self.returns: IdfParameters = IdfParameters(intf, method_data.get("returns", []))
        self.errors: list[str] = method_data.get("errors", [])

    @property
    def in_signature(self):
        return "(" + self.parameters.signature + ")"

    @property
    def out_signature(self):
        return "(" + self.returns.signature + ")"

    @cached_property
    def dependency_interface(self):
        deps = []
        deps.extend(self.parameters.dependency_interface)
        deps.extend(self.returns.dependency_interface)
        deps.extend(self.errors_dependency())
        return list(set(deps))

    def errors_dependency(self):
        deps = []
        for error in self.errors:
            pos = error.rfind(".Error.")
            if pos > 0:
                deps.append(error[0:pos])
        return deps

class IdfSignal(IdfBase):
    def __init__(self, intf: IdfInterfaceBase, signal_data):
        super().__init__(intf, signal_data)
        self.properties: IdfParameters = IdfParameters(intf, signal_data.get("properties", []))

    @property
    def signature(self):
        return "(" + self.properties.signature + ")"

    @cached_property
    def dependency_interface(self):
        return self.properties.dependency_interface

class IdfStructure(IdfBase):
    def __init__(self, intf: IdfInterfaceBase, stru_data, propety_key = "values"):
        super().__init__(intf, stru_data)
        self.values: IdfParameters = IdfParameters(intf, stru_data.get(propety_key, []))

    @property
    def signature(self):
        return "(" + self.values.signature+ ")"

    @cached_property
    def dependency_interface(self):
        return self.values.dependency_interface

    def odf_schema(self):
        schema = {}
        for prop in self.values.parameters:
            odf = prop.odf_schema(False)
            if odf is not None:
                schema[prop.name] = odf
            else:
                log.warning(f"the schema of prop {prop.name} is None")
        odf = {
            "type": "object",
            "additionalProperties": False,
            # "required": [],
            "properties": schema
        }
        return odf


class IdfPluginAction(IdfMethod):
    def __init__(self, intf: IdfInterfaceBase, method_data):
        self.policy = method_data.get("policy", "continue_always")
        super().__init__(intf, method_data)
        self.is_plugin = True
        if self.policy == "continue_always" and method_data.get("returns", []):
            raise Exception(f"The policy of plugin {self.name} is 'continue_always', does't supported 'returns' property, interface {self.intf.name} failed to generate code")


class IdfEnumeration(IdfBase):
    def __init__(self, intf: IdfInterfaceBase, enum_data):
        super().__init__(intf, enum_data)
        self.values: list[IdfParameter] = IdfParameters(intf, enum_data.get("values", []))

    @property
    def signature(self):
        return "s"

    def odf_schema(self):
        values = []
        for prop in self.values.parameters:
            val = prop.name
            values.append(val)

        odf = {
            "enum": values
        }
        return odf


class IdfDictionary():
    def __init__(self, intf: IdfInterfaceBase, dict_data):
        self.intf = intf
        self.annotations: list[IdfAnnotation] = []
        self.name = dict_data.get("name")
        self.key = dict_data.get("key")
        self.key_type = dict_data.get("key_type", "string")
        self.description = dict_data.get("description", "")
        flags = dict_data.get("flags", "").split(",")
        for k, v in ANNOTATION_MAP.items():
            if k in flags:
                self.annotations.append(v)
        self.values: IdfParameters = IdfParameters(intf, dict_data.get("values", []))

        key = {
            "name": self.key,
            "type": self.key_type,
            "description": f"the key of {self.name}"
        }
        self.key_obj = IdfParameter(intf, key)
        if "->n_" in self.key_obj.declare():
            raise IDFException(f"The key type of dictinary {self.name} can't be an array, get: {self.key_type}")

    @property
    def signature(self):
        if (len(self.values.parameters) > 1):
            return "a{" + self.key_obj.signature + "(" + self.values.signature + ")}"
        else:
            return "a{" + self.key_obj.signature + self.values.signature + "}"

    @cached_property
    def dependency_interface(self):
        return self.values.dependency_interface

    @property
    def key_is_string(self):
        return self.key_type in ["string", "signature", "object_path"]

    @property
    def hash_func(self):
        if self.key_is_string:
            return "g_str_hash"
        else:
            return "g_direct_hash"

    @property
    def equal_func(self):
        if self.key_is_string:
            return "g_str_equal"
        else:
            return "g_direct_equal"

    @property
    def key_free(self):
        if self.key_is_string:
            return "g_free"
        else:
            return "NULL"

    def odf_schema(self):
        schema = {}
        for prop in self.values.parameters:
            odf = prop.odf_schema(False)
            if odf is not None:
                schema[prop.name] = odf
            else:
                log.warning(f"the schema of prop {prop.name} is None")
        key_schema = self.key_obj.odf_schema(False)
        odf = {
            "type": "array",
            "description": "dictionary schema#",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "key",
                    "properties"
                ],
                "properties": {
                    "key": key_schema,
                    "properties": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": schema
                    }
                }
            }
        }
        return odf


class IdfInterface(IdfInterfaceBase):
    def __init__(self, lookup, idf_file, codegen_version, log_level="NOTSET"):
        if not idf_file.endswith(".yaml") and not idf_file.endswith(".yml"):
            raise IDFException(f"IDF file {idf_file} neither endswith .yaml nor endswith .yml")
        super().__init__()
        self.lookup = lookup
        self.file = idf_file
        self.properties: list[IdfProperty] = []
        self.methods: list[IdfMethod] = []
        self.signals: list[IdfSignal] = []
        self.structures: dict[str, IdfStructure] = {}
        self.errors: dict[str, IdfStructure] = {}
        self.dictionaries: dict[str, IdfDictionary] = {}
        self.enumerations: dict[str, IdfEnumeration] = {}
        self.annotations: list[IdfAnnotation] = []
        self.plugin: IdfInterfacePlugin = None
        self.description = None
        self.version = None
        self.alias = None
        self.codegen_version = codegen_version
        self.load_elements()
        if log_level != "NOTSET":
            log.setLevel(logging.WARN)

    @cached_property
    def dependency_idf_interface(self):
        deps: dict[str, IdfInterface] = {}
        intfs = self.dependency_interface
        for intf in intfs:
            intf_path = intf + ".yaml"
            cwd = os.getcwd()
            realpath = None
            while cwd != "/":
                tmp_path = os.path.join(cwd, intf_path)
                if os.path.isfile(tmp_path):
                    realpath = tmp_path
                    break
                tmp_path = os.path.join(cwd, intf + ".yaml")
                if os.path.isfile(tmp_path):
                    realpath = tmp_path
                    break
                cwd = os.path.dirname(cwd)

            if not realpath:
                raise FileNotFoundError(f"Dependency interface {intf} not exist, cwd: {os.getcwd()}")
            log.debug(f"Found dependency interface: {realpath}")
            deps[intf] = (IdfInterface(self.lookup, realpath, self.codegen_version))
        return deps

    @cached_property
    def signature(self):
        sig = ""
        for prop in self.properties:
            sig += prop.signature
        return "(" + sig + ")"

    @cached_property
    def dependency_interface(self):
        deps = []
        for prop in self.properties:
            deps.extend(prop.dependency_interface)
        for _, dicti in self.dictionaries.items():
            deps.extend(dicti.dependency_interface)
        for _, strct in self.structures.items():
            deps.extend(strct.dependency_interface)
        for action in self.plugin.actions:
            deps.extend(action.dependency_interface)
        for signal in self.signals:
            deps.extend(signal.dependency_interface)
        for method in self.methods:
            deps.extend(method.dependency_interface)
        for _, error in self.errors.items():
            deps.extend(error.dependency_interface)
        return list(set(deps))

    @property
    def odf_schema(self):
        schema = {}
        with_schema_prop_cnt = 0
        required = []
        for prop in self.properties:
            if "required" in prop.flags:
                required.append(prop.name)
            odf = prop.odf_schema(True)
            if odf is not None:
                schema[prop.name] = odf
                with_schema_prop_cnt += 1
            else:
                log.warning(f"the schema of prop {prop.name} is None")
            # 顶层属性可以有一个flags标记属性
            schema[f"_{prop.name}_flags"] =  {
                "enum": ["per_save", "per_power_off", "per_reboot"]
            }
        odf = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": self.name + " schema#",
            "description": f"schema of the interface " + self.name,
            "type": "object",
            "additionalProperties": False
        }
        if len(required) > 0:
            odf["required"] = required
        if with_schema_prop_cnt > 0:
            odf["properties"] = schema
            odf["$defs"] = {
                "ref_value": {
                    "type": "string",
                    "description": "Property reference syntax. The format must be `\\$\\{([<]*|:)<object>.<property name>\\}`, for example: Test_Obj.Prop",
                    "pattern": "^\\$\\{([<]*|:)\\.?[a-zA-Z][a-z0-9A-Z]+_[a-zA-Z0-9][a-z0-9A-Z_]*\\.[a-zA-Z][A-Za-z0-9_-]*\\}$"
                },
                "ref_obj": {
                    "type": "string",
                    "description": "Property reference syntax. The format must be `\\$\\{([<]*|:)<object>.<property name>\\}`, for example: Test_Obj",
                    "pattern": "^\\$\\{([<]*|:)\\.?[a-zA-Z][a-z0-9A-Z]+_[a-zA-Z0-9][a-z0-9A-Z_]*\\}$"
                },
                "ref_obj_array": {
                    "type": "array",
                    "description": "String array, each item is described using the object reference syntax",
                    "items": {
                        "anyOf": [
                            {
                                "type": "string",
                                "description": "Object reference syntax. The format must be `\\$\\{([<]*|:)<object>\\}`, for example: Test_Obj",
                                "pattern": "^\\$\\{([<]*|:)\\.?[a-zA-Z][a-z0-9A-Z]+_[a-zA-Z0-9][a-z0-9A-Z_]*\\}$"
                            },
                            {
                                "type": "string",
                                "description": "Plain string format, if the string start with `$` must add `\\` before `$` to escape; If the string is empty it must be surrounded by `\"`",
                                "pattern": "^/?[A-Z0-9a-z_]+(/[A-Z0-9a-z_]+)*$"
                            }
                        ]
                    }
                }
            }
        return odf

    @property
    def fake_methods(self):
        methods = []
        for method in self.methods:
            methods.append(method)
        for action in self.plugin.actions:
            methods.append(action)
        return methods

    def load_elements(self):
        # 使用schema校验数据，确保IDF文件符合格式要求，减少程序处理过程中的异常处理
        # 验证失败时抛异常，此处不用处理，由外层处理
        idf = load_yml_with_json_schema_validate(self.file, "/usr/share/litebmc/schema/idf.v2.json")
        schema = get_json_schema_file(self.file, "/usr/share/litebmc/schema/idf.v2.json")
        if schema.endswith("idf.v1.json"):
            self.name = os.path.basename(self.file)[:-5]
            self.alias = idf.get("alias")
            self.object_path = ""
        else:
            self.alias = os.path.basename(self.file)[:-5]
            self.name = idf.get("interface")
            # 别名
            self.object_path = idf.get("object_path", "")

        log.debug(f"validate {self.file} successfully")
        self.version = idf.get("version")
        self.description = idf.get("description", "")
        global alias
        alias = self.alias
        # 注释
        flags = idf.get("flags", "").split(",")
        for k, v in ANNOTATION_MAP.items():
            if k in flags:
                self.annotations.append(v)

        items = idf.get("properties", [])
        for item in items:
            self.properties.append(IdfProperty(self, item))
        items = idf.get("signals", [])
        for item in items:
            self.signals.append(IdfSignal(self, item))
        items = idf.get("methods", [])
        self.methods = []
        for item in items:
            self.methods.append(IdfMethod(self, item))
        items = idf.get("structures", [])
        for item in items:
            obj = IdfStructure(self, item)
            obj.name = alias + "_" + obj.name
            self.structures[obj.name] = obj
        items = idf.get("errors", [])
        for item in items:
            obj = IdfStructure(self, item, "parameters")
            self.errors[obj.name] = obj
        self._check_errors_format()
        items = idf.get("dictionaries", [])
        for item in items:
            obj = IdfDictionary(self, item)
            obj.name = alias + "_" + obj.name
            self.dictionaries[obj.name] = obj
        items = idf.get("enumerations", [])
        for item in items:
            obj = IdfEnumeration(self, item)
            obj.name = alias + "_" + obj.name
            self.enumerations[obj.name] = obj
        plugin = idf.get("plugin", None)
        self.plugin = IdfInterfacePlugin()
        if plugin is not None:
            items = plugin.get("actions", [])
            self.plugin.install_dir = plugin.get("install_dir")
            for item in items:
                obj = IdfPluginAction(self, item)
                self.plugin.actions.append(obj)
        log.debug("interface signature: " + self.signature)
        for signal in self.signals:
            log.debug(f"{signal.name} signature: " + signal.signature)
        for method in self.methods:
            log.debug(f"{method.name} in signature: " + method.in_signature + ", out signature: " + method.out_signature)
        # for name, stru in self.structures.items():
        #     log.debug(f"{name} signature: " + stru.signature)
        # for name, enum in self.enumerations.items():
        #     log.debug(f"{name} signature: " + enum.signature)
        # for name, dictionary in self.dictionaries.items():
        #     log.debug(f"{name} signature: " + dictionary.signature)
        # 接口本身也是一个结构体
        intf_stru = IdfStructure(self, idf, propety_key="properties")
        self.structures[self.alias] = intf_stru

    def render_dbus_xml(self, template, out_file):
        out = self.render(self.lookup, template, intf=self, codegen_version=self.codegen_version)
        hash = hashlib.sha256()
        hash.update(out.encode('utf-8'))
        self.introspect_xml_sha256 = hash.hexdigest()
        log.info("The sha256sum of interface {} is {}".format(out_file, self.introspect_xml_sha256))
        with open(out_file, "w") as fd:
            fd.write(out)

    def render_c_source(self, template, out_file):

        out = self.render(self.lookup, template, intf=self, codegen_version=self.codegen_version)
        with open(out_file, "w") as fd:
            fd.write(out)

    def _check_errors_format(self):
        for name, error in self.errors.items():
            desc = error.description
            chunks = []
            prev_line = ""
            for chunk in desc.split("$?"):
                if prev_line:
                    chunks.append(prev_line + chunk)
                    prev_line = ""
                elif chunk[-1:] == "\\":
                    prev_line = chunk[:-1] + "$?"
                else:
                    chunks.append(chunk)
            # 如果剩余prev_line示处理，表示纯粹剩余一个\
            if prev_line:
                chunks.append(prev_line[:-2] + "\\")
            # 参数个数检验
            if len(chunks) != len(error.values.parameters) + 1:
                raise LiteBmcException(f"The number({len(chunks) - 1}) of $? in the description string(Error: ${name}) does not match the number({len(error.values.parameters)}) of parameters")
            new_desc = chunks[0]
            id = 1
            for param in error.values.parameters:
                formatter = PRINT_FORMATTER_MAP[param.ctype]
                if formatter.startswith("%"):
                    new_desc += formatter
                else:
                    new_desc += f"%\"{formatter}\""
                new_desc += chunks[id]
                id += 1
            error.description = new_desc
