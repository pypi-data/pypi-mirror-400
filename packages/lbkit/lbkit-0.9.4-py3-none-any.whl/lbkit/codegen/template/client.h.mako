<% from lbkit.tools import hump2underline %>\
#ifndef __${"_".join(intf.name.upper().split(".", -1))}_CLI_H__
#define __${"_".join(intf.name.upper().split(".", -1))}_CLI_H__

#include <glib-2.0/glib.h>
#include <glib-2.0/gio/gio.h>
#include "lb_base.h"
#include "public/${intf.alias}.h"

#ifdef __cplusplus
extern "C" {
#endif
<% class_name = intf.alias + "_Cli"%>
typedef ${intf.alias} ${class_name};
typedef ${intf.alias}_Properties ${class_name}_Properties;

% for prop in intf.properties:
% if not prop.private:
/*
 * property: ${prop.name}
% if len(prop.description.strip()) > 0:
 *
 % for line in prop.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
## 私有属性或者只读属性不允许写
% if not prop.private and prop.access != "read":
    % if prop.deprecated:
__deprecated gint ${class_name}_set_${prop.name}(${class_name} obj, ${", ".join(prop.declare()).replace("<arg_name>", "value").replace("<const>", "const ")}, GError **error);
    % else:
gint ${class_name}_set_${prop.name}(${class_name} obj, ${", ".join(prop.declare()).replace("<arg_name>", "value").replace("<const>", "const ")}, GError **error);
    % endif
% endif
% if not prop.private and prop.access != "write":
    % if prop.deprecated:
__deprecated gint ${class_name}_get_${prop.name}(${class_name} obj, ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error);
    % else:
gint ${class_name}_get_${prop.name}(${class_name} obj, ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error);
    % endif
% endif
% endif
% endfor

% for method in intf.methods:
<% RSP_PARA = f'' %>\
<% REQ_PARA = f'' %>\
    % if len(method.returns.parameters) > 0:
<% RSP_PARA = f'{intf.alias}_{method.name}_Rsp **rsp, ' %>\
    % endif
    % if len(method.parameters.parameters) > 0:
<% REQ_PARA = f'const {intf.alias}_{method.name}_Req *req, ' %>\
    % endif
/*
 * method: ${method.name}
% if len(method.description.strip()) > 0:
 *
 % for line in method.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
    % if method.deprecated:
__deprecated int ${class_name}_Call_${method.name}(${class_name} obj,
    ${REQ_PARA}${RSP_PARA}gint timeout,
    GError **error);
    % else:
int ${class_name}_Call_${method.name}(${class_name} obj,
    ${REQ_PARA}${RSP_PARA}gint timeout,
    GError **error);
    % endif
% endfor

% for signal in intf.signals:
/*
 * signal: ${signal.name}
% if len(signal.description.strip()) > 0:
 *
 % for line in signal.description.split("\n"):
   % if len(line.strip()) > 0:
 * ${line.strip()}
   % endif
 % endfor
% endif
 */
typedef void (*${class_name}_${signal.name}_Callback)(${class_name} obj, const gchar *destination,
    const ${intf.alias}_${signal.name}_Msg *req, gpointer user_data, const LBSignalExtData *ext_data);
/**/
        % if signal.deprecated:
__deprecated guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Callback handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data);
        % else:
guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Callback handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data);
        % endif
    % if signal.deprecated:
__deprecated void ${class_name}_Unsubscribe_${signal.name}(guint *id);
    % else:
void ${class_name}_Unsubscribe_${signal.name}(guint *id);
    % endif

% endfor

${class_name}_Properties *${class_name}_properties(void);
LBInterface *${class_name}_interface(void);
#define ${hump2underline(class_name).upper()}    ${class_name}_interface()

/* notes: 对象变更加回调函数 */
typedef void (*${class_name}_on_changed_hook)(${class_name} obj, gpointer user_data);
/* notes: 属性变更后回调，远程对象或本地对象变更后都会调用 */
typedef void (*${class_name}_after_changed_hook)(${class_name} obj, const LBProperty *prop, GVariant *value, gpointer user_data);
/* notes: 属性变更前回调，返回-1表示阻止值变更，一般用于值合法性校验，只在被远程操作时才会生效，本地变更值不会回调 */
typedef gint (*${class_name}_before_change_hook)(${class_name} obj, const LBProperty *prop, GVariant *value, gpointer user_data, GError **error);

/* 查询对象 */
${class_name} ${class_name}_get(const gchar *well_known, const gchar *name);
/* 创建对象 */
${class_name} ${class_name}_new(const gchar *well_known, const gchar *name);
/* 减对象引用计数 */
void ${class_name}_unref(${class_name} *obj);
/* 加对象引用计数 */
${class_name} ${class_name}_ref(${class_name} obj);
/* 设置在位状态 */
void ${class_name}_present_set(${class_name} obj, gboolean present);
/* 获取在位状态 */
gboolean ${class_name}_present(${class_name} obj);
/* 绑定数据 */
void ${class_name}_bind(${class_name} obj, gpointer data, GDestroyNotify destroy_func);
/* 获取绑定数据 */
gpointer ${class_name}_data(${class_name} obj);
/* @notes 属性对象属性值变更(后)事件 */
gint ${class_name}_on_prop_changed(${class_name} obj, const gchar *prop, ${class_name}_after_changed_hook pc, gpointer user_data, GDestroyNotify destroy);
/* 取消监听，成功取消监听时会调用监听时设置的destroy回调清除注册时的user_data */
void ${class_name}_on_prop_changed_cancel(${class_name} obj, const gchar *prop, ${class_name}_after_changed_hook pc, gconstpointer user_data);
/* 对象变更事件 */
void ${class_name}_on_changed(${class_name}_on_changed_hook cb, gpointer user_data, GDestroyNotify destroy);
/* 注册对象释放回调 */
void ${class_name}_before_destroy(${class_name} obj, GHookFunc cb, gpointer user_data);
/*
 * 查询第n个对象
 * @notes: 支持正逆向查询第n个对象，返回的对象需要使用lbo_unref减引用计数
 *     正向查找传入非负n，以0开始计数，表示查找最早创建的第n个对象;
 *     逆向查找传入负数n，以-1开始计数，依次为-2、-3等，表示查找最后创建的第n个对象。
 */
${class_name} ${class_name}_nth(int nth);
/* 查询对象名称 */
const gchar *${class_name}_name(${class_name} obj);
/* 对象加锁 */
void ${class_name}_lock(${class_name} obj);
/* 对象解锁 */
void ${class_name}_unlock(${class_name} obj);
/* 对象列表查询接口 */
GSList *${class_name}_list(void);
/* 监听属性 */
% for prop in intf.properties:
void ${class_name}_${prop.name}_hook(${class_name}_after_changed_hook after, gpointer user_data);
% endfor

static inline void ${class_name}_unref_p(${class_name} obj)
{
    ${class_name}_unref(&obj);
}

static inline void _cleanup_${class_name}_(${class_name} *ptr)
{
    if (ptr && *ptr) {
        ${class_name}_unref(ptr);
    }
}

static inline void ${class_name}_list_free(GSList **list)
{
    g_assert(list);
    g_slist_free_full(*list, (GDestroyNotify)${class_name}_unref_p);
    *list = NULL;
}

static inline void _cleanup_${class_name}_list(GSList **ptr)
{
    if (ptr && *ptr) {
        ${class_name}_list_free(ptr);
    }
}

#define cleanup_${class_name} __attribute__((cleanup(_cleanup_${class_name}_)))
#define cleanup_${class_name}_list __attribute__((cleanup(_cleanup_${class_name}_list)))
#ifdef __cplusplus
}
#endif

#endif /* __${"_".join(intf.name.upper().split(".", -1))}_CLI_H__ */
