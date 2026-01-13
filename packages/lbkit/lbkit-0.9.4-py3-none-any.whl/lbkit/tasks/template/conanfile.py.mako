from conan import ConanFile

class LitebmcConan(ConanFile):
    """用于构建产品的顶层conan包，该包只是用于集成组件，无需要推送到conan中心仓"""
    name = "litebmc"
    settings = "os", "arch", "compiler", "build_type"
    description = "${pkg["metadata"]["description"]}"
    url = "https://litebmc.com"
    extension_properties = {
        "compatibility_cppstd": False,
        "compatibility_cstd": False
    }
    homepage = ""
    generators = "CMakeDeps"
    license = "BSL-1.0"
    version = "${pkg["metadata"]["version"]}"

    def requirements(self):
        """从manifest.yml文件中提取的依赖组件"""
    % for dep in real_dependencies:
        self.requires("${dep["package"]}")
    % endfor
        self.requires("rootfs_df190c/0.0.1")

    def configure(self):
    % for dep in real_dependencies:
        % if len(dep.get("options", [])) > 0:
<% name = dep["package"].split("/")[0] %>\
            % for op, ctx in dep["options"].items():
                % if op.find(":") == -1:
        self.options["${name}"].${op} = ${("\"" + ctx + "\"") if isinstance(ctx, str) else str(ctx)}
                % else:
<% name = op.split(":")[0] %>\
<% option = op.split(":")[1] %>\
        self.options["${name}"].${option} = ${("\"" + ctx + "\"") if isinstance(ctx, str) else str(ctx)}
                % endif
            % endfor
        % endif
    % endfor
        pass
