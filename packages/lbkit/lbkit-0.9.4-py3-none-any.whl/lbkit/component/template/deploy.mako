from conan import ConanFile


class DeployConan(ConanFile):
    name = "deploy"
    settings = "os", "arch", "compiler", "build_type"
    description = "部署组件"
    url = "https://litebmc.com"
    homepage = ""
    generators = "CMakeDeps"
    package_type = "application"
    version = "0.0.1"
    license = "MulanPSL v2"
    extension_properties = {
        "compatibility_cppstd": False,
        "compatibility_cstd": False
    }
    options = {
        "gcov": [False, True],
        "test": [False, True],
% if len(pkg.get("options", [])) > 0:
    % for op, ctx in pkg["options"].items():
        "${op}": [${", ".join(("\"" + i + "\"") if isinstance(i, str) else str(i) for i in ctx["option"])}],
    % endfor
% endif
    }
    default_options = {
% if pkg_type == "library":
        "shared": True,
% endif
        "gcov": False,
        "test": False,
% if len(pkg.get("options", [])) > 0:
    % for op, ctx in pkg["options"].items():
        "${op}": ${("\"" + ctx["default"] + "\"") if isinstance(ctx["default"], str) else str(ctx["default"])},
    % endfor
% endif
    }

    def requirements(self):
% for package in packages:
        self.requires("${package}")
% endfor
% if len(pkg.get("requires", {})) > 0:
    % for conan in pkg["requires"].get("compile", []):
        % if conan.get("when") is not None:
        if ${conan.get("when")}:
            self.requires("${conan.get("conan")}")
        % else:
        self.requires("${conan.get("conan")}")
        % endif
    % endfor
<%test_requires=pkg["requires"].get("test", [])%>\
    % if len(test_requires):
        if self.options.test == True:
        % for conan in test_requires:
            % if conan.get("when") is not None:
            if ${conan.get("when")}:
                self.requires("${conan.get("conan")}")
            % else:
            self.requires("${conan.get("conan")}")
            % endif
        % endfor
    % endif
% endif
        pass

    def configure(self):
        self.options["lb_base"].compatible_required = "${codegen_version.info.lb_base_compatible_required}"
% if len(pkg.get("requires", {})) > 0:
    % for conan in pkg["requires"].get("compile", []):
        % if conan.get("option") is not None:
            % for k, v in conan.get("option").items():
        self.options["${conan.get("conan").split("/")[0]}"].${k} = ${("\"" + v + "\"") if isinstance(v, str) else str(v)}
            % endfor
        % endif
    % endfor
        if self.options.test == True:
<%test_requires=pkg["requires"].get("test", [])%>\
    % if len(test_requires):
        % for conan in test_requires:
            % if conan.get("option") is not None:
                % for k, v in conan.get("option").items():
            self.options["${conan.get("conan").split("/")[0]}"].${k} = ${("\"" + v + "\"") if isinstance(v, str) else str(v)}
                % endfor
            % endif
        % endfor
    % endif
% endif
            pass
