<!DOCTYPE node PUBLIC
"-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd">
<node>
% for text in intf.description.split("\n"):
  <!-- ${text} -->
% endfor
  <interface name="${intf.name}">
    ### 接口注释
% for anno in intf.annotations:
    <annotation name="${anno.name}" value="${anno.value}" />
% endfor
### 属性
% for prop in intf.properties:
    % if not prop.private:
        % for text in prop.description.split("\n"):
    <!-- ${text} -->
        % endfor
        % if len(prop.annotations) > 0:
    <property name="${prop.name}" type="${prop.signature}" access="${prop.access}">
            % for anno in prop.annotations:
      <annotation name="${anno.name}" value="${anno.value}" />
            % endfor
    </property>
        % else:
    <property name="${prop.name}" type="${prop.signature}" access="${prop.access}"></property>
        % endif
    % endif
% endfor
### 方法
% for method in intf.methods:
    % for text in method.description.split("\n"):
    <!-- ${text} -->
    % endfor
    <method name="${method.name}">
        % for anno in method.annotations:
      <annotation name="${anno.name}" value="${anno.value}" />
        % endfor
        % for arg in method.parameters.parameters:
            % for text in arg.description.split("\n"):
      <!-- ${text} -->
            % endfor
      <arg name="${arg.name}" direction="in" type="${arg.signature}"></arg>
        % endfor
        % for arg in method.returns.parameters:
            % for text in arg.description.split("\n"):
      <!-- ${text} -->
            % endfor
      <arg name="${arg.name}" direction="out" type="${arg.signature}"></arg>
        % endfor
    </method>
% endfor
### 方法
% for signal in intf.signals:
    % for text in signal.description.split("\n"):
    <!-- ${text} -->
    % endfor
    <signal name="${signal.name}">
        % for anno in signal.annotations:
      <annotation name="${anno.name}" value="${anno.value}" />
        % endfor
        % for arg in signal.properties.parameters:
            % for text in arg.description.split("\n"):
      <!-- ${text} -->
            % endfor
      <arg name="${arg.name}" type="${arg.signature}"></arg>
        % endfor
    </signal>
%endfor
  </interface>
</node>