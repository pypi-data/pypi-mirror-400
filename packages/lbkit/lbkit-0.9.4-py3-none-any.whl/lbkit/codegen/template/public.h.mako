#ifndef __${"_".join(intf.name.upper().split(".", -1))}_PUB_H__
#define __${"_".join(intf.name.upper().split(".", -1))}_PUB_H__

#include <glib-2.0/glib.h>
#include <glib-2.0/gio/gio.h>
#include "lb_base.h"
% for dep_intf in intf.dependency_interface:
#include "public/${dep_intf}.h"
% endfor

#ifdef __cplusplus
extern "C" {
#endif

/* Interface ${intf.alias} codegen start */

<% class_name = intf.alias %>\
### 生成Errors错误 START >>>>>
% if len(intf.errors):
### 定义枚举类型
typedef enum {
% for name, stru in intf.errors.items():
    ${class_name}_Error_${name},
% endfor
} ${class_name}_Error;

%endif
### 生成Errors错误 END <<<<<
% for name, stru in intf.structures.items():
/*
 * structure: ${name}
% if len(stru.description.strip()) > 0:
 *
 % for line in stru.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
% if name != class_name:
typedef struct _${name} ${name};
% else:
typedef const struct _${name} * ${name};
% endif
% endfor
% for name, enum in intf.enumerations.items():
/*
 * enumeration: ${name}
% if len(enum.description.strip()) > 0:
 *
 % for line in enum.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
typedef enum {
    % for value in enum.values.parameters:
    ${name}_${value.name},
    % endfor
    _${name}_Invalid,
} ${name};
const gchar *${name}_as_string(${name} value);

% endfor
### 生成Errors错误 START
% if len(intf.errors):
% for name, stru in intf.errors.items():
<% proto_str="" %>\
        % for prop in stru.values.parameters:
            % for dec in prop.declare():
<% proto_str += dec.replace("<arg_name>", prop.name).replace("<const>", "const ") + ", " %>\
            % endfor
        % endfor
/*
 * Error: ${stru.description.strip()}
 */
% if len(proto_str):
GError *${intf.alias}_Error_${name}_new(${proto_str[:-2]});
% else:
GError *${intf.alias}_Error_${name}_new(void);
%endif
%endfor

%endif
### 生成Errors错误 END
% for name, dictionary in intf.dictionaries.items():
/*
 * dictionary: ${name}
% if len(dictionary.description.strip()) > 0:
 *
 % for line in dictionary.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
typedef struct _${name}${dictionary.key} ${name}${dictionary.key};
typedef struct _${name} ${name};

% endfor
% for name, stru in intf.structures.items():
    % if name != class_name:
/*
 * structure: ${name}
% if len(stru.description.strip()) > 0:
 *
 % for line in stru.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
struct _${name} {
        % for prop in stru.values.parameters:
            % for dec in prop.declare():
    ${dec.replace("<arg_name>", prop.name).replace("<const>", "")};
            % endfor
        % endfor
};

    % endif
%endfor
% for name, dictionary in intf.dictionaries.items():
struct _${name}${dictionary.key} {
    % for value in dictionary.values.parameters:
        % for line in value.declare():
    ${line.replace("<arg_name>", value.name).replace("<const>", "")};
        % endfor
    % endfor
};
/* Drop ${name}${dictionary.key} and the memory contained within it */
void ${name}${dictionary.key}_free(${name}${dictionary.key} **obj);
<% key_declare = ", ".join(dictionary.key_obj.declare()).replace("<arg_name>", "key").replace("<const>", "const ") %>
typedef void (*${name}_func)(${key_declare}, ${name}${dictionary.key} *value, gpointer user_data);
struct _${name} {
    /* the ownership NOT transferred */
    ${name}${dictionary.key} *(*lookup)(const ${name} *dict, ${key_declare});
    /* if return TRUE, ownership of `value` is transferred to the dict */
    gboolean (*insert)(const ${name} *dict, ${key_declare}, ${name}${dictionary.key} **value);
    gboolean (*remove)(const ${name} *dict, ${key_declare});
    gboolean (*contains)(const ${name} *dict, ${key_declare});
    void (*clear)(const ${name} *dict);
    void (*foreach)(const ${name} *dict, ${name}_func func, gpointer user_data);
};
/* Create a new ${name} object */
${name} *${name}_new(void);

% endfor
## 定义结构体编解码和释放函数
% for name, stru in intf.structures.items():
/* ${name} structure object */
/* START: 结构体${name}及其数组类型的序列化、反序列化、释放函数 */
GVariant *${name}_encode(const struct _${name} *value);
struct _${name} *${name}_decode(GVariant *in);
// Clean up the memory of structure and it's all members, `*value` will to NULL
void ${name}_free(struct _${name} **value);
// Clean up the memory of members managed by structure ${name}
void ${name}_clean(struct _${name} *value);

struct _${name} **${name}_decode_v(GVariant *in);
GVariant *${name}_encode_v(struct _${name} * const *value);
// Clean up the memory of structure array and it's all members, `*value` will to NULL
void ${name}_free_v(struct _${name} ***value);
/* END: 结构体struct _${name}及其数组类型的序列化、反序列化、释放函数 */

% endfor
## 定义枚举编解码函数
% for name, enum in intf.enumerations.items():
/* START: 枚举${name}及其数组类型的序列化、反序列化、释放函数 */
GVariant *${name}_encode(${name} value);
${name} ${name}_decode(GVariant *in);

GVariant *${name}_encode_v(const ${name} *value, gsize n);
${name} *${name}_decode_v(GVariant *in, gsize *n);
/* END: 枚举${name}及其数组类型的序列化、反序列化、释放函数 */

## 校验枚举变量有效性
gboolean ${name}_check_enum_variant(LBO *obj, GVariant *value, GError **error);
gboolean ${name}_check_enum_variant_v(LBO *obj, GVariant *value, GError **error);

% endfor
## 定义字典编解码和释放函数
% for name, dictionary in intf.dictionaries.items():
/* START: 字典${name}及其数组类型的序列化、反序列化、释放函数 */
GVariant *${name}_encode(const ${name} *value);
${name} *${name}_decode(GVariant *in);
void ${name}_free(${name} **value);

GVariant *${name}_encode_v(${name} * const *value);
${name} **${name}_decode_v(GVariant *in);
void ${name}_free_v(${name} ***value);
/* END: 字典${name}及其数组类型的序列化、反序列化、释放函数 */

% endfor
### 生成Errors错误 END
## 定义结构体ODF加载函数
% for name, stru in intf.structures.items():
/* ${name} structure object */
/* START: 结构体${name}及其数组类型的ODF校验函数 */
gboolean ${name}_validate_odf(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);
gboolean ${name}_validate_odf_v(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);

% endfor
## 定义枚举ODF加载函数
% for name, enum in intf.enumerations.items():
/* START: 枚举${name}及其数组类型的ODF校验函数 */
gboolean ${name}_validate_odf(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);
gboolean ${name}_validate_odf_v(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);

% endfor
## 定义字典ODF加载函数
% for name, dictionary in intf.dictionaries.items():
gboolean ${name}_validate_odf(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);
gboolean ${name}_validate_odf_v(yaml_document_t *doc, yaml_node_t *node, GString *prop, GSList **error_list);

% endfor
## 定义结构体ODF加载函数
% for name, stru in intf.structures.items():
/* ${name} structure object */
/* START: 结构体${name}及其数组类型的ODF加载函数 */
struct _${name} *${name}_load_from_odf(yaml_document_t *doc, yaml_node_t *node);
struct _${name} **${name}_load_from_odf_v(yaml_document_t *doc, yaml_node_t *node);

% endfor
## 定义枚举ODF加载函数
% for name, enum in intf.enumerations.items():
/* START: 枚举${name}及其数组类型的ODF加载函数 */
${name} ${name}_load_from_odf(yaml_document_t *doc, yaml_node_t *node);
${name} *${name}_load_from_odf_v(yaml_document_t *doc, yaml_node_t *node, gsize *n);

% endfor
## 定义字典ODF加载函数
% for name, dictionary in intf.dictionaries.items():
/* START: 字典${name}及其数组类型的ODF加载函数 */
${name} *${name}_load_from_odf(yaml_document_t *doc, yaml_node_t *node);
${name} **${name}_load_from_odf_v(yaml_document_t *doc, yaml_node_t *node);

% endfor
### 开始生成方法的请求体、响应体和处理函数
% for method in intf.fake_methods:
    % if method.parameters.parameters:
/* ${method.name}方法的请求体 */
typedef struct {
        % for arg in method.parameters.parameters:
            % for dec in arg.const_declare():
    ${dec.replace("<arg_name>", arg.name).replace("<const>", "")};
            % endfor
        % endfor
} ${class_name}_${method.name}_Req;
    % else:
typedef void ${class_name}_${method.name}_Req;
    % endif

    % if method.returns.parameters:
/* ${method.name}方法的响应体 */
typedef struct {
        % for arg in method.returns.parameters:
            % for dec in arg.declare():
    ${dec.replace("<arg_name>", arg.name).replace("<const>", "")};
            % endfor
        % endfor
} ${class_name}_${method.name}_Rsp;
    % else:
typedef void ${class_name}_${method.name}_Rsp;
    % endif

void ${class_name}_${method.name}_Rsp_free(${class_name}_${method.name}_Rsp **value);

% if not method.is_plugin:
int ${class_name}_${method.name}(${class_name} obj, const ${class_name}_${method.name}_Req *req,
    ${class_name}_${method.name}_Rsp **rsp, GError **error, LBMethodExtData *ext_data);
% endif

%endfor
/* ${intf.name}的方法集合 */
typedef struct {
% for method in intf.methods:
    struct {
        const gchar *const name;
        const gchar *const req_signature;
    % if method.parameters.parameters:
        ${class_name}_${method.name}_Req *(*req_decode)(GVariant *in);
        GVariant *(*req_encode)(${class_name}_${method.name}_Req *value);
        void (*req_free)(${class_name}_${method.name}_Req **value);
    % else:
        lbo_message_decode_handler req_decode;
        lbo_message_encode_handler req_encode;
        lbo_message_free_handler req_free;
    % endif
        const gchar *const rsp_signature;
    % if method.returns.parameters:
        ${class_name}_${method.name}_Rsp *(*rsp_decode)(GVariant *in);
        GVariant *(*rsp_encode)(${class_name}_${method.name}_Rsp *value);
        void (*rsp_free)(${class_name}_${method.name}_Rsp **value);
    % else:
        lbo_message_decode_handler rsp_decode;
        lbo_message_encode_handler rsp_encode;
        lbo_message_free_handler rsp_free;
    % endif
        int (*handler)(${class_name} obj, const ${class_name}_${method.name}_Req *req,
            ${class_name}_${method.name}_Rsp **rsp, GError **error, LBMethodExtData *ext_data);
        guint8 reserved[16];
    } ${method.name};
% endfor
    LBMethod __reserved__;
} ${class_name}_Methods;

% if len(intf.plugin.actions) > 0:
% for action in intf.plugin.actions:
<% RSP_PARA = f'' %>\
<% REQ_PARA = f'' %>\
    % if len(action.returns.parameters) > 0:
<% RSP_PARA = f', {class_name}_{action.name}_Rsp **rsp' %>\
    % endif
    % if len(action.parameters.parameters) > 0:
<% REQ_PARA = f', const {class_name}_{action.name}_Req *req' %>\
    % endif
    % if action.policy == "continue_always":
typedef void (*${class_name}_${action.name}_action)(${class_name} obj${REQ_PARA}${RSP_PARA}, gpointer user_data);
    % else:
typedef int (*${class_name}_${action.name}_action)(${class_name} obj${REQ_PARA}${RSP_PARA}, gpointer user_data);
    % endif

/* Register a new plugin action, can't register repeated with same action and user_data */
int ${class_name}_${action.name}_register(const gchar *req_signature, const gchar *rsp_signature,
    ${class_name}_${action.name}_action action, gpointer user_data);
void ${class_name}_${action.name}_unregister(${class_name}_${action.name}_action action);
    % if action.policy == "continue_always":
void ${class_name}_${action.name}_run(${class_name} obj${REQ_PARA}${RSP_PARA});
    % else:
int ${class_name}_${action.name}_run(${class_name} obj${REQ_PARA}${RSP_PARA});
    % endif

% endfor
% endif
### 开始生成方法的请求体、响应体和处理函数
% for signal in intf.signals:
/* ${signal.name}信号的消息体 */
    % if signal.properties.parameters:
typedef struct {
        % for arg in signal.properties.parameters:
            % for dec in arg.const_declare():
    ${dec.replace("<arg_name>", arg.name).replace("<const>", "")};
            % endfor
        % endfor
} ${class_name}_${signal.name}_Msg;
    % else:
typedef void ${class_name}_${signal.name}_Msg;
    % endif

%endfor
typedef struct {
% for signal in intf.signals:
    struct {
        const gchar *const name;
        const gchar *const msg_signature;
    % if signal.properties.parameters:
        ${class_name}_${signal.name}_Msg *(*msg_decode)(GVariant *in);
        GVariant *(*msg_encode)(${class_name}_${signal.name}_Msg *value);
        void (*msg_free)(${class_name}_${signal.name}_Msg **value);
    % else:
        lbo_message_decode_handler msg_decode;
        lbo_message_encode_handler msg_encode;
        lbo_message_free_handler msg_free;
    % endif
        guint8 reserved[16];
    } ${signal.name};
% endfor
    LBSignal __reserved__;
} ${class_name}_Signals;

% for name, stru in intf.structures.items():
    % if name == class_name:
struct _${name} {
    LBBase _base;        /* Notice: property name can't be _base */
    char __reserved__[8]; /* 8bytes reserved space, can't be modified */
        % for prop in stru.values.parameters:
            % for dec in prop.declare():
    ${dec.replace("<arg_name>", prop.name).replace("<const>", "")};
            % endfor
        % endfor
};

    % endif
%endfor
typedef struct {
% for prop in intf.properties:
    LBProperty ${prop.name};
% endfor
    LBProperty __reserved__;
} ${class_name}_Properties;

gboolean ${intf.alias}_validate_odf_file(yaml_document_t *doc, yaml_node_t *node,
    const gchar *object_name, GSList **error_list);
// 不要使用此函数返回的对象，需要使用${class_name}_properties() 或${class_name}_Cli_properties()
const ${class_name}_Properties *${class_name}_properties_const(void);
// 同时加载客户端和服务端时Processer是共享的，因此可以直接调用Processer定义的handler函数
${class_name}_Signals *${class_name}_signals(void);
${class_name}_Methods *${class_name}_methods(void);
/* Interface ${intf.name} codegen finish */

#ifdef __cplusplus
}
#endif

#endif /* __${"_".join(intf.alias.upper().split(".", -1))}_PUB_H__ */
