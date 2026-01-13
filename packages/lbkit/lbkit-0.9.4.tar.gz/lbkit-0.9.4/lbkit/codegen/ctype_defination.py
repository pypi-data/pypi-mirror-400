"""语言相关类型定义"""
import sys
from lbkit.errors import OdfValidateException


UNSET_MAX_ITEMS = 65536
UNSET_MIN_ITEMS = -1

class IdfValidator():
    def __init__(self, ctype):
        self.validator = {}
        self.name = ""
        self.unique = False
        self.matches = []
        self.ctype = ctype
        self.max_items = UNSET_MAX_ITEMS
        self.min_items = UNSET_MIN_ITEMS
        self.is_array = False

    def set_validator(self, value, name):
        self.validator = value
        self.name = name
        self.unique = self.validator.get("unique", False)
        self.matches = self.validator.get("matches", None)
        if self.matches == []:
            raise Exception(f"Set validate for property {name} failed because matches is empty")
        # schema已限制最多65535个成员，65536表示未配置
        self.max_items = self.validator.get("max_items", UNSET_MAX_ITEMS)
        # schema已限制至少0个成员，-1表示未配置
        self.min_items = self.validator.get("min_items", UNSET_MIN_ITEMS)
        # 设置max_items且未设置min_items时，将min_items设置为0
        if self.max_items != UNSET_MAX_ITEMS and self.min_items == UNSET_MIN_ITEMS:
            self.min_items = 0
        # min_items为零且max为UNSET_MAX_ITEMS时清空配置
        if self.min_items == 0 and self.max_items == UNSET_MAX_ITEMS:
            self.min_items = UNSET_MIN_ITEMS
        if self.max_items != UNSET_MAX_ITEMS and self.min_items != UNSET_MIN_ITEMS and self.min_items > self.max_items:
            raise Exception(f"Set validate for property {name} failed because max_items less than min_items")

    def odf_validate(self):
        return []

    def base_odf_validate(self):
        func = []
        if self.unique:
            func.append(f"validate_odf_{self.ctype}_unique_items(doc, node, prop, error_list)")
        if self.matches:
            if self.ctype == "string":
                func.append(f"validate_odf_{self.ctype}_match_items(doc, node, prop, _items, error_list)")
            else:
                func.append(f"validate_odf_{self.ctype}_match_items(doc, node, prop, {len(self.matches)}, _items, error_list)")
        if self.max_items != UNSET_MAX_ITEMS or self.min_items != UNSET_MIN_ITEMS:
            func.append(f"validate_odf_len(doc, node, prop, {self.min_items}, {self.max_items}, error_list)")
        return func

    def odf_schema(self, allow_ref):
        allow_ref = allow_ref
        return None

    def val_validate(self):
        return []

    def base_val_validate(self):
        # schema已限制只有数组能够限制max_items/min_items/unique/matches配置项
        func = []
        if self.unique and self.is_array:
            if self.ctype == "string":
                func.append(f"validate_{self.ctype}_unique_items((const gchar *const *)<arg_name>, error)")
            else:
                func.append(f"validate_{self.ctype}_unique_items(n_<arg_name>, <arg_name>, error)")
        if self.matches:
            if self.is_array:
                if self.ctype == "string":
                    func.append(f"validate_{self.ctype}_match_items((const gchar *const *)<arg_name>, _items, error)")
                else:
                    func.append(f"validate_{self.ctype}_match_items(n_<arg_name>, <arg_name>, {len(self.matches)}, _items, error)")
            else:
                if self.ctype == "string":
                    func.append(f"validate_{self.ctype}_match_item(<arg_name>, _items, error)")
                else:
                    func.append(f"validate_{self.ctype}_match_item(<arg_name>, {len(self.matches)}, _items, error)")
        if self.is_array and (self.max_items != UNSET_MAX_ITEMS or self.min_items != UNSET_MIN_ITEMS):
            if self.ctype == "string":
                func.append(f"validate_type_v_len(<arg_name> ? g_strv_length(<arg_name>) : 0, {self.min_items}, {self.max_items}, error)")
            else:
                func.append(f"validate_type_v_len(n_<arg_name>, {self.min_items}, {self.max_items}, error)")
        return func

    def match_items(self):
        if not self.matches:
            return []
        if self.ctype == "string":
            val_str = f"static const gchar *_items[] = {{"
            val_str += '"' + '", "'.join(self.matches) + '", NULL'
        else:
            if self.ctype in ["int16", "int32", "int64", "ssize"]:
                val_str = f"static gint64 _items[] = {{"
            elif self.ctype in ["uint8", "uint16", "uint32", "uint64", "size"]:
                val_str = f"static guint64 _items[] = {{"
            elif self.ctype in ["double"]:
                val_str = f"static gdouble _items[] = {{"
            else:
                return []
            val_str += ", ".join([str(i) for i in self.matches])
        val_str += "}"
        return [val_str]

class BoolValidator(IdfValidator):
    def odf_validate(self):
        func = ["validate_odf_as_boolean(doc, node, prop, error_list)"]
        return func

    def odf_schema(self, allow_ref):
        if allow_ref:
            return {
                "anyOf": [
                    {
                        "type": "boolean"
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
        else:
            return {
                "type": "boolean"
            }


class BoolArrayValidator(BoolValidator):
    def __init__(self, ctype):
        super().__init__(ctype)
        self.is_array = True

    def odf_validate(self):
        func = []
        func.append("validate_odf_as_boolean_v(doc, node, prop, error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        return super().base_val_validate()

    def odf_schema(self, allow_ref):
        parent_schema = super().odf_schema(False)
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "type": "array",
                        "items": parent_schema
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["anyOf"][0]["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["anyOf"][0]["minItems"] = self.min_items
        else:
            schema = {
                "type": "array",
                "items": parent_schema
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["minItems"] = self.min_items
            if self.unique:
                schema["uniqueItems"] = True

        return schema


class IntegerValidator(IdfValidator):
    def __init__(self, ctype, max, min, signed=False):
        self.maximum = max
        self.minimum = min
        self.signed = signed
        if not self.signed and self.minimum < 0:
            self.minimum = 0
        if self.maximum < self.minimum:
            raise OdfValidateException(f"The max value {self.maximum} less than or equal to {self.minimum}")
        super().__init__(ctype)

    def set_validator(self, value, name):
        super().set_validator(value, name)
        max = self.validator.get("max", self.maximum)
        if max > self.maximum:
            max = self.maximum
        min = self.validator.get("min", self.minimum)
        if min < self.minimum:
            min = self.minimum
        self.maximum = max
        self.minimum = min
        if not self.signed and self.minimum < 0:
            self.minimum = 0
        if self.maximum < self.minimum:
            raise OdfValidateException(f"The max value {self.maximum} less than or equal to {self.minimum}, property {name} validation failed")

    def odf_validate(self):
        func = []
        if self.signed:
            min_str = self.minimum
            max_str = self.maximum
            if self.minimum <= -9223372036854775808:
                min_str = "G_MININT64"
            if self.maximum >= 9223372036854775807:
                max_str = "G_MAXINT64"
            func.append(f"validate_odf_as_signed(doc, node, prop, {max_str}, {min_str}, error_list)")
        else:
            max_str = f"{self.maximum}UL"
            if self.maximum >= 18446744073709551615:
                max_str = "G_MAXUINT64"
            func.append(f"validate_odf_as_unsigned(doc, node, prop, {max_str}, {self.minimum}UL, error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        if self.signed:
            min_str = self.minimum
            max_str = self.maximum
            if self.minimum <= -9223372036854775808:
                min_str = "G_MININT64"
            if self.maximum >= 9223372036854775807:
                max_str = "G_MAXINT64"
            func.append(f"validate_{self.ctype}(<arg_name>, {min_str}, {max_str}, error)")
        else:
            max_str = f"{self.maximum}UL"
            if self.maximum >= 18446744073709551615:
                max_str = "G_MAXUINT64"
            func.append(f"validate_{self.ctype}(<arg_name>, {self.minimum}, {max_str}, error)")
        func.extend(super().base_val_validate())
        return func


    def odf_schema(self, allow_ref):
        """
            返回整数类型成员的ODF schema
            idf_validator为IDF模型中加载的数据验证器的对象
        """
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.matches:
                schema["anyOf"][0] = {
                    "enum": self.matches
                }
            else:
                schema["anyOf"][0] = {
                    "type": "integer",
                    "maximum": self.maximum,
                    "minimum": self.minimum
                }
        else:
            if self.matches:
                schema = {
                    "enum": self.matches
                }
            else:
                schema = {
                    "type": "integer",
                    "maximum": self.maximum,
                    "minimum": self.minimum
                }
        return schema


class IntegerArrayValidator(IntegerValidator):
    def __init__(self, ctype, max, min, signed=False):
        super().__init__(ctype, max, min, signed)
        self.is_array = True

    def odf_validate(self):
        func = []
        min_str = f"{self.minimum}UL"
        max_str = f"{self.maximum}UL"
        if self.signed:
            if self.minimum <= -9223372036854775808:
                min_str = "G_MININT64"
            if self.maximum >= 0x7fff_ffff_ffff_ffff:
                max_str = "G_MAXINT64"
        else:
            if self.maximum >= 0xffff_ffff_ffff_ffff:
                max_str = "G_MAXUINT64"

        if self.signed:
            func.append(f"validate_odf_as_signed_v(doc, node, prop, {max_str}, {min_str}, error_list)")
        else:
            func.append(f"validate_odf_as_unsigned_v(doc, node, prop, {max_str}, {min_str}, error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        min_str = f"{self.minimum}UL"
        max_str = f"{self.maximum}UL"
        if self.signed:
            if self.minimum <= -9223372036854775808:
                min_str = "G_MININT64"
            if self.maximum >= 0x7fff_ffff_ffff_ffff:
                max_str = "G_MAXINT64"
        else:
            if self.maximum >= 0xffff_ffff_ffff_ffff:
                max_str = "G_MAXUINT64"

        if self.signed:
            func.append(f"validate_{self.ctype}_v(n_<arg_name>, <arg_name>, {min_str}, {max_str}, error)")
        else:
            func.append(f"validate_{self.ctype}_v(n_<arg_name>, <arg_name>, {min_str}, {max_str}, error)")
        func.extend(super().base_val_validate())
        return func

    def odf_schema(self, allow_ref):
        parent_schema = super().odf_schema(False)
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "type": "array",
                        "items": parent_schema
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["anyOf"][0]["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["anyOf"][0]["minItems"] = self.min_items
            if self.unique:
                schema["anyOf"][0]["uniqueItems"] = True
        else:
            schema = {
                "type": "array",
                "items": parent_schema
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["minItems"] = self.min_items
            if self.unique:
                schema["uniqueItems"] = True

        return schema


class FloatValidator(IdfValidator):
    def __init__(self, ctype):
        self.maximum = sys.float_info.max
        self.minimum = -sys.float_info.max
        self.exclusive_max = None
        self.exclusive_min = None
        self.max_key = "maximum"
        self.max_val = self.maximum
        self.min_key = "minimum"
        self.min_val = self.minimum
        super().__init__(ctype)

    def odf_validate(self):
        func = ["validate_odf_as_double(doc, node, prop, error_list)"]
        if self.exclusive_max is not None:
            func.append(f"validate_odf_as_double_exclusive_max(doc, node, prop, {self.exclusive_max}, error_list)")
        elif self.maximum != sys.float_info.max:
            func.append(f"validate_odf_as_double_max(doc, node, prop, {self.maximum}, error_list)")

        if self.exclusive_min is not None:
            func.append(f"validate_odf_as_double_exclusive_min(doc, node, prop, {self.exclusive_min}, error_list)")
        elif self.minimum != (-sys.float_info.max):
            func.append(f"validate_odf_as_double_min(doc, node, prop, {self.minimum}, error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        if self.exclusive_max is not None:
            func.append(f"validate_double_exclusive_max(<arg_name>, {self.exclusive_max}, error)")
        elif self.maximum != sys.float_info.max:
            func.append(f"validate_double_max(<arg_name>, {self.maximum}, error)")

        if self.exclusive_min is not None:
            func.append(f"validate_double_exclusive_min(<arg_name>, {self.exclusive_min}, error)")
        elif self.minimum != (-sys.float_info.max):
            func.append(f"validate_double_min(<arg_name>, {self.minimum}, error)")
        func.extend(super().base_val_validate())
        return func

    def set_validator(self, value, name):
        super().set_validator(value, name)
        self.maximum = self.validator.get("max", self.maximum)
        self.minimum = self.validator.get("min", self.minimum)
        self.exclusive_max = self.validator.get("exclusive_max", None)
        self.exclusive_min = self.validator.get("exclusive_min", None)
        self.max_key = "maximum"
        self.min_key = "minimum"
        self.max_val = self.maximum
        self.min_val = self.minimum
        if self.exclusive_max is not None:
            self.max_key = "exclusiveMaximum"
            self.max_val = self.exclusive_max
        if self.exclusive_min is not None:
            self.max_key = "exclusiveMinimum"
            self.min_val = self.exclusive_min

    def odf_schema(self, allow_ref):
        """
            返回整数类型成员的ODF schema
            idf_validator为IDF模型中加载的数据验证器的对象
        """
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.matches:
                schema["anyOf"][0] = {
                    "enum": self.matches
                }
            else:
                schema["anyOf"][0] = {
                    "type": "number",
                    self.max_key: self.max_val,
                    self.min_key: self.min_val
                }
        else:
            if self.matches:
                schema = {
                    "enum": self.matches
                }
            else:
                schema = {
                    "type": "number",
                    self.max_key: self.max_val,
                    self.min_key: self.min_val
                }
        return schema


class FloatArrayValidator(FloatValidator):
    def __init__(self, ctype):
        super().__init__(ctype)
        self.is_array = True

    def odf_validate(self):
        func = []
        func.append("validate_odf_as_double_v(doc, node, prop, error_list)")
        if self.exclusive_max is not None:
            func.append(f"validate_odf_as_double_exclusive_max_v(doc, node, prop, {self.exclusive_max}, error_list)")
        elif self.maximum != sys.float_info.max:
            func.append(f"validate_odf_as_double_max_v(doc, node, prop, {self.maximum}, error_list)")

        if self.exclusive_min is not None:
            func.append(f"validate_odf_as_double_exclusive_min_v(doc, node, prop, {self.exclusive_min}, error_list)")
        elif self.minimum != (-sys.float_info.max):
            func.append(f"validate_odf_as_double_min_v(doc, node, prop, {self.minimum}, error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        if self.exclusive_max is not None:
            func.append(f"validate_double_exclusive_max_v(n_<arg_name>, <arg_name>, {self.exclusive_max}, error)")
        elif self.maximum != sys.float_info.max:
            func.append(f"validate_double_max_v(n_<arg_name>, <arg_name>, {self.maximum}, error)")

        if self.exclusive_min is not None:
            func.append(f"validate_double_exclusive_min_v(n_<arg_name>, <arg_name>, {self.exclusive_min}, error)")
        elif self.minimum != (-sys.float_info.max):
            func.append(f"validate_double_min_v(n_<arg_name>, <arg_name>, {self.minimum}, error)")
        func.extend(super().base_val_validate())
        return func

    def odf_schema(self, allow_ref):
        parent_schema = super().odf_schema(False)
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "type": "array",
                        "items": parent_schema
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["anyOf"][0]["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["anyOf"][0]["minItems"] = self.min_items
            if self.unique:
                schema["anyOf"][0]["uniqueItems"] = True
        else:
            schema = {
                "type": "array",
                "items": parent_schema
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["minItems"] = self.min_items
            if self.unique:
                schema["uniqueItems"] = True
        return schema


class StringValidator(IdfValidator):
    def __init__(self, ctype, pattern):
        self.pattern = pattern
        super().__init__(ctype)

    def set_validator(self, value, name):
        super().set_validator(value, name)
        self.pattern = self.validator.get("pattern", self.pattern)

    def odf_validate(self):
        func = []
        if self.pattern:
            func.append(f"validate_odf_as_string(doc, node, prop, \"{self.pattern}\", error_list)")
        else:
            pattern = "^()|(((\\\\$)|[^$]).*)$"
            func.append(f"validate_odf_as_string(doc, node, prop, \"{pattern}\", error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        if self.pattern:
            func.append(f"validate_string(<arg_name>, \"{self.pattern}\", error)")
        func.extend(super().base_val_validate())
        return func

    def odf_schema(self, allow_ref):
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "pattern": "^()|(((\\\\$)|[^$]).*)$"
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.pattern:
                schema["anyOf"][0]["pattern"] = self.pattern
            if self.matches:
                schema["anyOf"][0]["enum"] = self.matches
            else:
                schema["anyOf"][0]["type"] = "string"
        else:
            schema = {
            }
            if self.pattern:
                schema["pattern"] = self.pattern
            if self.matches:
                schema["enum"] = self.matches
            else:
                schema["type"] = "string"
        return schema


class StringArrayValidator(StringValidator):
    def __init__(self, ctype, pattern):
        super().__init__(ctype, pattern)
        self.is_array = True

    def odf_validate(self):
        func = []
        if self.pattern:
            func.append(f"validate_odf_as_string_v(doc, node, prop, \"{self.pattern}\", error_list)")
        else:
            pattern = "^()|(((\\\\$)|[^$]).*)$"
            func.append(f"validate_odf_as_string_v(doc, node, prop, \"{pattern}\", error_list)")
        func.extend(super().base_odf_validate())
        return func

    def val_validate(self):
        func = []
        if self.pattern:
            func.append(f"validate_string_v((const gchar *const *)<arg_name>, \"{self.pattern}\", error)")
        func.extend(super().base_val_validate())
        return func

    def odf_schema(self, allow_ref):
        parent_schema = super().odf_schema(False)
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "type": "array",
                        "items": parent_schema
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["anyOf"][0]["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["anyOf"][0]["minItems"] = self.min_items
            if self.unique:
                schema["anyOf"][0]["uniqueItems"] = True
        else:
            schema = {
                "type": "array",
                "items": parent_schema
            }
            if self.max_items != UNSET_MAX_ITEMS:
                schema["maxItems"] = self.max_items
            if self.min_items != UNSET_MIN_ITEMS:
                schema["minItems"] = self.min_items
            if self.unique:
                schema["uniqueItems"] = True
        return schema


class RefObjValidator(IdfValidator):
    def __init__(self, ctype=None):
        super().__init__(ctype)

    def odf_validate(self):
        func = ["validate_odf_as_ref_obj(doc, node, prop, error_list)"]
        return func

    def odf_schema(self, allow_ref):
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "$ref": "#/$defs/ref_obj"
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
        else:
            schema = {
                "$ref": "#/$defs/ref_obj"
            }
        return schema


class RefObjArrayValidator(RefObjValidator):
    def __init__(self, ctype=None):
        super().__init__(ctype)
        self.is_array = True

    def odf_validate(self):
        func = ["validate_odf_as_ref_obj_v(doc, node, prop, error_list)"]
        return func

    def odf_schema(self, allow_ref):
        if allow_ref:
            schema = {
                "anyOf": [
                    {
                        "$ref": "#/$defs/ref_obj_array"
                    },
                    {
                        "$ref": "#/$defs/ref_value"
                    }
                ]
            }
        else:
            schema = {
                "$ref": "#/$defs/ref_obj_array"
            }
        return schema


class CTypeBase(object):
    """C语言相关的操作函数＆类型定义"""
    def __init__(self, declare, out_declare, free_func, encode_func, decode_func,
                 validator: IdfValidator = None,
                 const_declare = None,
                 const_free_func = None,
                 const_decode_func = None):
        self.declare = declare
        # 作为函数出参时的变量申明
        self.out_declare = out_declare
        self.free_func = free_func
        self.encode_func = encode_func
        self.decode_func = decode_func
        self.validator = validator
        # Req消息顶层数据结构的释放和解码函数，注意顶层的(string/signature/object_path)数据可以是const的
        self.const_declare = const_declare
        self.const_free_func = const_free_func
        self.const_decode_func = const_decode_func
        if const_declare is None:
            self.const_declare = self.declare
        if const_free_func is None:
            self.const_free_func = self.free_func
        if const_decode_func is None:
            self.const_decode_func = self.decode_func


"""定义支持的C语言类型"""
CTYPE_OBJS = {
    "boolean": CTypeBase(
        ["gboolean <arg_name>"],
        ["gboolean *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_boolean(<arg_name>)"],
        ["<arg_in> = g_variant_get_boolean(<arg_name>)"],
        BoolValidator("boolean")
    ),
    "byte": CTypeBase(
        ["guint8 <arg_name>"],
        ["guint8 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_byte(<arg_name>)"],
        ["<arg_in> = g_variant_get_byte(<arg_name>)"],
        IntegerValidator("uint8", 0xff, 0)
    ),
    "int16": CTypeBase(
        ["gint16 <arg_name>"],
        ["gint16 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_int16(<arg_name>)"],
        ["<arg_in> = g_variant_get_int16(<arg_name>)"],
        IntegerValidator("int16", 0x7fff, -(0x8000), True)
    ),
    "uint16": CTypeBase(
        ["guint16 <arg_name>"],
        ["guint16 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_uint16(<arg_name>)"],
        ["<arg_in> = g_variant_get_uint16(<arg_name>)"],
        IntegerValidator("uint16", 0xffff, 0)
    ),
    "int32": CTypeBase(
        ["gint32 <arg_name>"],
        ["gint32 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_int32(<arg_name>)"],
        ["<arg_in> = g_variant_get_int32(<arg_name>)"],
        IntegerValidator("int32", 0x7fff_ffff, -(0x8000_0000), True)
    ),
    "uint32": CTypeBase(
        ["guint32 <arg_name>"],
        ["guint32 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_uint32(<arg_name>)"],
        ["<arg_in> = g_variant_get_uint32(<arg_name>)"],
        IntegerValidator("uint32", 0xffff_ffff, 0)
    ),
    "int64": CTypeBase(
        ["gint64 <arg_name>"],
        ["gint64 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_int64(<arg_name>)"],
        ["<arg_in> = g_variant_get_int64(<arg_name>)"],
        IntegerValidator("int64", 0x7fff_ffff_ffff_ffff, -(0x8000_0000_0000_0000), True)
    ),
    "uint64": CTypeBase(
        ["guint64 <arg_name>"],
        ["guint64 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_uint64(<arg_name>)"],
        ["<arg_in> = g_variant_get_uint64(<arg_name>)"],
        IntegerValidator("uint64", 0xffff_ffff_ffff_ffff, 0)
    ),
    "size": CTypeBase(
        ["gsize <arg_name>"],
        ["gsize *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_tsize(<arg_name>)"],
        ["<arg_in> = g_variant_get_tsize(<arg_name>)"],
        IntegerValidator("size", 0xffff_ffff_ffff_ffff, 0)
    ),
    "ssize": CTypeBase(
        ["gssize <arg_name>"],
        ["gssize *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_tssize(<arg_name>)"],
        ["<arg_in> = g_variant_get_tssize(<arg_name>)"],
        IntegerValidator("ssize", 0x7fff_ffff_ffff_ffff, -(0x8000_0000_0000_0000), True)
    ),
    "double": CTypeBase(
        ["gdouble <arg_name>"],
        ["gdouble *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_double(<arg_name>)"],
        ["<arg_in> = g_variant_get_double(<arg_name>)"],
        FloatValidator("double")
    ),
    "unixfd": CTypeBase(
        ["gint32 <arg_name>"],
        ["gint32 *<arg_name>"],
        [],
        ["<arg_out> = g_variant_new_handle(<arg_name>)"],
        ["<arg_in> = g_variant_get_handle(<arg_name>)"],
        IntegerValidator("int32", 0x7fff_ffff_ffff_ffff, 0, True)
    ),
    "string": CTypeBase(
        ["<const>gchar *<arg_name>"],
        ["gchar **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_string_encode(<arg_name>)"],
        ["<arg_in> = g_strdup(g_variant_get_string(<arg_name>, NULL))"],
        StringValidator("string", "^.*$"),
        ["const gchar *<arg_name>"],
        [],
        ["<arg_in> = g_variant_get_string(<arg_name>, NULL)"],
    ),
    "object_path": CTypeBase(
        ["<const>gchar *<arg_name>"],
        ["gchar **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_object_path_encode(<arg_name>)"],
        ["<arg_in> = g_strdup(g_variant_get_string(<arg_name>, NULL))"],
        StringValidator("string", "^(/[A-Z0-9a-z_]+)*$"),
        ["const gchar *<arg_name>"],
        [],
        ["<arg_in> = g_variant_get_string(<arg_name>, NULL)"],
    ),
    "signature": CTypeBase(
        ["<const>gchar *<arg_name>"],
        ["gchar **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_signature_encode(<arg_name>)"],
        ["<arg_in> = g_strdup(g_variant_get_string(<arg_name>, NULL))"],
        StringValidator("string", "^([abynqiuxtdsogvh\\\\{\\\\}\\\\(\\\\)])+$"),
        ["const gchar *<arg_name>"],
        [],
        ["<arg_in> = g_variant_get_string(<arg_name>, NULL)"],
    ),
    "variant": CTypeBase(
        ["GVariant *<arg_name>"],
        ["GVariant **<arg_name>"],
        ["lb_unref_p((GVariant **)&<arg_name>)"],
        ["g_variant_take_ref(<arg_name>)", "<arg_out> = g_variant_new_variant(<arg_name>)"],
        ["<arg_in> = g_variant_get_variant(<arg_name>)"],
        IdfValidator(None)
    ),
    "array[boolean]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gboolean *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gboolean **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_boolean_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_boolean_decode(<arg_name>, &n_<arg_in>)"],
        BoolArrayValidator("boolean")
    ),
    "array[byte]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>guint8 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"guint8 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_byte_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_byte_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("uint8", 0xff, 0)
    ),
    "array[int16]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gint16 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gint16 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_int16_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_int16_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("int16", 0x7fff, -(0x8000), True)
    ),
    "array[uint16]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>guint16 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"guint16 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_uint16_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_uint16_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("uint16", 0xffff, 0)
    ),
    "array[int32]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gint32 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gint32 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_int32_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_int32_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("int32", 0x7fff_ffff, -(0x80000000), True)
    ),
    "array[uint32]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>guint32 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"guint32 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_uint32_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_uint32_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("uint32", 0xffff_ffff, 0)
    ),
    "array[int64]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gint64 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gint64 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_int64_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_int64_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("int64", 0x7fff_ffff_ffff_ffff, -(0x8000_0000_0000_0000), True)
    ),
    "array[uint64]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>guint64 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"guint64 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_uint64_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_uint64_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("uint64",0xffff_ffff_ffff_ffff, 0)
    ),
    "array[ssize]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gssize *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gssize **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_ssize_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_ssize_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("ssize",0x7fff_ffff_ffff_ffff, -(0x8000_0000_0000_0000), True)
    ),
    "array[size]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gsize *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gsize **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_size_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_size_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("size", 0xffff_ffff_ffff_ffff, 0)
    ),
    "array[double]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gdouble *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gdouble **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_double_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_double_decode(<arg_name>, &n_<arg_in>)"],
        FloatArrayValidator("double")
    ),
    "array[unixfd]": CTypeBase(
        ["gsize n_<arg_name>" ,"<const>gint32 *<arg_name>"],
        ["gsize *n_<arg_name>" ,"gint32 **<arg_name>"],
        ["lb_free_p((void **)&<arg_name>)"],
        ["<arg_out> = lb_array_handle_encode(<arg_name>, n_<arg_name>)"],
        ["<arg_in> = lb_array_handle_decode(<arg_name>, &n_<arg_in>)"],
        IntegerArrayValidator("int32", 0x7fff_ffff_ffff_ffff, 0, True)
    ),
    "array[string]": CTypeBase(
        ["gchar *<const>*<arg_name>"],
        ["gchar ***<arg_name>"],
        ["lb_strfreev_p(&<arg_name>)"],
        ["<arg_out> = lb_array_string_encode(<arg_name>)"],
        ["<arg_in> = lb_array_string_decode(<arg_name>)"],
        StringArrayValidator("string", "")
    ),
    "array[object_path]": CTypeBase(
        ["gchar *<const>*<arg_name>"],
        ["gchar ***<arg_name>"],
        ["lb_strfreev_p(&<arg_name>)"],
        ["<arg_out> = lb_array_object_path_encode(<arg_name>)"],
        ["<arg_in> = lb_array_object_path_decode(<arg_name>)"],
        StringArrayValidator("string", "^(/[A-Z0-9a-z_]+)*$")
    ),
    "array[signature]": CTypeBase(
        ["gchar *<const>*<arg_name>"],
        ["gchar ***<arg_name>"],
        ["lb_strfreev_p(&<arg_name>)"],
        ["<arg_out> = lb_array_signature_encode(<arg_name>)"],
        ["<arg_in> = lb_array_signature_decode(<arg_name>)"],
        StringArrayValidator("string", "^([abynqiuxtdsogvh\\\\{\\\\}\\\\(\\\\)])+$")
    )
}