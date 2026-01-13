<%
from inflection import underscore
%>\
#include "lb_base.h"
#include "${intf.alias}.h"

<% class_name = intf.alias + "_Cli"
properties = "_" + class_name + "_properties"
signal_processer = "_" + class_name + "_signals"
method_processer = "_" + class_name + "_methods"
%>\
static const ${intf.alias}_Methods *${method_processer} = NULL;
static ${intf.alias}_Properties ${properties};
static const ${intf.alias}_Signals *${signal_processer} = NULL;

% for prop in intf.properties:
## 私有属性或者只读属性
% if not prop.private and prop.access != "read":
    % if prop.deprecated:
__deprecated gint ${class_name}_set_${prop.name}(${class_name} obj,
    ${", ".join(prop.declare()).replace("<arg_name>", prop.name).replace("<const>", "const ")}, GError **error)
    % else:
gint ${class_name}_set_${prop.name}(${class_name} obj,
    ${", ".join(prop.declare()).replace("<arg_name>", prop.name).replace("<const>", "const ")}, GError **error)
    % endif
{
    cleanup_unref GVariant *tmp = NULL;
    % for line in prop.encode_func():
    ${line.replace("<arg_out>", "tmp").replace("n_<arg_name>", "n_" + prop.name).replace("<arg_name>", prop.name)};
    % endfor
    return lb_impl.write_property((LBO *)obj, &${properties}.${prop.name}, tmp, error);
}

% endif
## 私有或只写属性不允许读
% if not prop.private and prop.access != "write":
    % if prop.deprecated:
__deprecated gint ${class_name}_get_${prop.name}(${class_name} obj,
    ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error)
    % else:
gint ${class_name}_get_${prop.name}(${class_name} obj, ${", ".join(prop.out_declare()).replace("<arg_name>", "value").replace("<const>", "")}, GError **error)
    % endif
{
    % if "gsize n_" in prop.declare()[0]:
    g_assert(n_value && value);
    % else:
    g_assert(value);
    % endif
    % for line in prop.declare():
        % if "*" in line:
    ${line.strip().replace("<arg_name>", "tmp_value").replace("<const>", "")} = NULL;
        % else:
    ${line.strip().replace("<arg_name>", "tmp_value").replace("<const>", "")};
        % endif
    % endfor
    GVariant *out = NULL;

    gint ret = lb_impl.read_property((LBO *)obj, &${properties}.${prop.name}, &out, error);
    if (ret == 0 && out) {
    % for line in prop.decode_func():
        ${line.replace("<arg_in>", "tmp_value").replace("<arg_name>", "out")};
    % endfor
        *value = tmp_value;
    % if "gsize n_" in prop.declare()[0]:
        *n_value = n_tmp_value;
    % endif
    }
    if (out) {
        g_variant_unref(out);
    }
    return ret;
}

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
int ${class_name}_Call_${method.name}(${class_name} obj,
    ${REQ_PARA}${RSP_PARA}gint timeout,
    GError **error)
{
    if (error == NULL) {
        log_error("Emit method ${method.name} with parameter error, error is NULL");
        return -1;
    }
    if (obj == NULL) {
        *error = g_error_new(G_DBUS_ERROR, G_DBUS_ERROR_FAILED, "Call method ${method.name} with parameter error, obj is NULL");
        return -1;
    }
    % if len(method.returns.parameters) == 0:
    void **rsp = NULL;
    % endif
    % if len(method.parameters.parameters) == 0:
    void *req = NULL;
    % endif
    return lb_impl.call_method((LBO *)obj, (const LBMethod *)&${method_processer}->${method.name},
                                 (void *)req, (void **)rsp, timeout, error);
}

% endfor
static LBO *_${class_name}_create(const gchar *name, gpointer opaque);
static void _${class_name}_destroy(LBO *obj);

static LBInterface _${class_name}_interface = {
    .create = _${class_name}_create,
    .destroy = _${class_name}_destroy,
    .is_remote = 1,
    .name = "${intf.name}",
    .properties = (LBProperty *)&${properties},
    .interface = NULL, /* load from usr/share/dbus-1/interfaces/${intf.name}.xml by lb_init */
#ifdef LB_CODEGEN_BE_5_4
    .alias = "${class_name}",
    .object_template = "${intf.object_path}",
#endif
};

static LBBase *_get_real_object(LBO *obj)
{
    LBBase *real = (LBBase *)strstr((const char *)obj, LB_MAGIC);
    if ((gconstpointer)real != (gconstpointer)obj) {
        log_error("Get real object fail, Perhaps the memory has been freed, call abort() now");
        abort();
    }
    return real;
}

/**
 * @brief 销毁对象
 *
 * @param obj 待销毁的对象句柄
 */
static void _${class_name}_destroy(LBO *obj)
{
    g_assert(obj);
    struct _${intf.alias} *real_obj = (struct _${intf.alias} *)_get_real_object(obj);
    g_rec_mutex_clear(real_obj->_base.lock);
    g_free(real_obj->_base.lock);
    ${intf.alias}_clean(real_obj);
    memset(real_obj, 0, sizeof(struct _${intf.alias}));
}

/**
 * @brief 分配对象
 *
 * @param name 对象名，需要由调用者分配内存
 * @param opaque 上层应用需要写入对象的用户数据，由上层应用使用
 */
static LBO *_${class_name}_create(const gchar *name, gpointer opaque)
{
    struct _${intf.alias} *obj = g_new0(struct _${intf.alias}, 1);
    memcpy(obj->_base.magic, LB_MAGIC, strlen(LB_MAGIC) + 1);
    obj->_base.lock = g_new0(GRecMutex, 1);
    g_rec_mutex_init(obj->_base.lock);
    obj->_base.name = name;
    obj->_base.intf = &_${class_name}_interface;
    obj->_base.opaque = opaque;
    return (LBO *)obj;
}

% for signal in intf.signals:
% if signal.deprecated:
__deprecated guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Callback handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data)
% else:
guint ${class_name}_Subscribe_${signal.name}(${class_name}_${signal.name}_Callback handler,
    const gchar *bus_name, const gchar *object_path, const gchar *arg0, gpointer user_data)
% endif
{
    return lb_impl.subscribe_signal(&_${class_name}_interface, bus_name,
        (const LBSignal *)&${signal_processer}->${signal.name},
        object_path, arg0, (lbo_signal_handler)handler, user_data);
}

% if signal.deprecated:
__deprecated void ${class_name}_Unsubscribe_${signal.name}(guint *id)
% else:
void ${class_name}_Unsubscribe_${signal.name}(guint *id)
% endif
{
    return lb_impl.unsubscribe_signal(id);
}

% endfor
LBInterface *${class_name}_interface(void)
{
    return &_${class_name}_interface;
}

${class_name}_Properties *${class_name}_properties(void)
{
    return &${properties};
}

${class_name} ${class_name}_get(const gchar *well_known, const gchar *name)
{
    return lb_impl._cli_get(&_${class_name}_interface, well_known, name);
}

${class_name} ${class_name}_new(const gchar *well_known, const gchar *name)
{
    LBO *obj = lb_impl._cli_new(&_${class_name}_interface, well_known, name);
    return (${class_name} )obj;
}

/* 减对象引用计数 */
void ${class_name}_unref(${class_name} *obj)
{
    lb_impl._unref((LBO **)obj);
}

/* 加对象引用计数 */
${class_name} ${class_name}_ref(${class_name} obj)
{
    return (${class_name} )lb_impl._ref((LBO *)obj);
}

/* 设置在位状态 */
void ${class_name}_present_set(${class_name} obj, gboolean present)
{
    lb_impl._present_set((LBO *)obj, present);
}

/* 获取在位状态 */
gboolean ${class_name}_present(${class_name} obj)
{
    return lb_impl._present((LBO *)obj);
}

/* 绑定数据 */
void ${class_name}_bind(${class_name} obj, gpointer data, GDestroyNotify destroy_func)
{
    lb_impl._bind((LBO *)obj, data, destroy_func);
}

/* 获取绑定数据 */
gpointer ${class_name}_data(${class_name} obj)
{
    return lb_impl._data((LBO *)obj);
}

/* @notes 属性对象属性值变更(后)事件 */
gint ${class_name}_on_prop_changed(${class_name} obj, const gchar *prop, ${class_name}_after_changed_hook pc, gpointer user_data, GDestroyNotify destroy)
{
    return lb_impl._on_prop_changed((LBO *)obj, prop, (lbo_after_changed_hook)pc, user_data, destroy);
}

/* 取消监听，成功取消监听时会调用监听时设置的destroy回调清除注册时的user_data */
void ${class_name}_on_prop_changed_cancel(${class_name} obj, const gchar *prop, ${class_name}_after_changed_hook pc, gconstpointer user_data)
{
    lb_impl._on_prop_changed_cancel((LBO *)obj, prop, (lbo_after_changed_hook)pc, user_data);
}

/* 对象变更事件 */
void ${class_name}_on_changed(${class_name}_on_changed_hook cb, gpointer user_data, GDestroyNotify destroy)
{
    lb_impl._on_changed(&_${class_name}_interface, (LbObjectHook)cb, user_data, destroy);
}

/* 注册对象释放回调 */
void ${class_name}_before_destroy(${class_name} obj, GHookFunc cb, gpointer user_data)
{
    lb_impl._before_destroy((LBO *)obj, cb, user_data);
}

/* 查询第n个对象 */
${class_name} ${class_name}_nth(int nth)
{
    return (${class_name} )lb_impl._nth(&_${class_name}_interface, nth);
}

/* 查询对象名称 */
const gchar *${class_name}_name(${class_name} obj)
{
    return lbo_name((LBO *)obj);
}

/* 对象加锁 */
void ${class_name}_lock(${class_name} obj)
{
    lbo_lock((LBO *)obj);
}

/* 对象解锁 */
void ${class_name}_unlock(${class_name} obj)
{
    lbo_unlock((LBO *)obj);
}

/* 对象列表查询接口 */
GSList *${class_name}_list(void)
{
    return lb_impl._list(&_${class_name}_interface);
}

% for prop in intf.properties:
/* 监听属性${prop.name}变更 */
void ${class_name}_${prop.name}_hook(${class_name}_after_changed_hook after, gpointer user_data)
{
    LBPropertyHook hook = {
        .after = (lbo_after_changed_hook)after,
        .user_data = user_data
    };
    lb_impl._prop_hook(&${properties}.${prop.name}, &hook);
}

% endfor
static void __constructor(150) ${class_name}_register(void)
{
    // 从公共库中复制信号处理函数
    ${signal_processer} = ${intf.alias}_signals();

    // 从公共库中复制方法处理函数
    _${class_name}_interface.methods = (LBMethod *)${intf.alias}_methods();
    _${class_name}_interface.signals = (LBSignal *)${intf.alias}_signals();
    ${method_processer} = ${intf.alias}_methods();

    // 从公共库中复制属性信息
    memcpy(&${properties}, ${intf.alias}_properties_const(), sizeof(${properties}));
    lb_interface_register(&_${class_name}_interface,
                           "${intf.introspect_xml_sha256}",
                           "/usr/share/dbus-1/interfaces/${intf.name}.xml");
}
