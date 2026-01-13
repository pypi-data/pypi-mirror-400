# 当工程未跟踪conanfile.py文件，lbkit构建时会自动生成conanfile.py文件。
# 如果你需要在conanfile.py中新增自己的构建业务逻辑，请参考以下步骤：
# 第一步：新增一个conanfile.py并将文件添加到git仓中，在conanfile.py中继承LiteBmcConan类，
#         并实现自己的业务逻辑，如下示例演示如何重写build方法以新增自己的业务逻辑：
# from conanbase import LiteBmcConan
# class AppConan(LiteBmcConan):
#    def build(self):
#        super(AppConan, self).build()
#        # other process
# 第二步：执行lbk启动构建，此时会新生成一个conanbase.py。建议将该文件添加到.gitignore中
import os
import time
import re
from conan import ConanFile
from conan.tools.scm import Git
from mako.lookup import TemplateLookup
from conan.tools.cmake import CMakeToolchain
from conan.tools.cmake import CMake
from conan.tools import files
from conan.errors import ConanException
from colorama import Style, Fore
<%
pkg_type = pkg["type"]
pkg_name = pkg["name"]
libs = pkg.get("package_info", {}).get("libs", [])
%>

class LiteBmcConan(ConanFile):
    name = "${pkg_name}"
    version = "${pkg["version"]}"
% if pkg["user"] != "litebmc" or pkg["channel"] != "release":
## @litebmc/release则生成的包名不带@user/channel
    user = "${pkg["user"]}"
    channel = "${pkg["channel"]}"
% endif
    settings = "os", "arch", "compiler", "build_type"
    description = "${pkg["description"]}"
    url = "${pkg["url"]}"
    generators = "CMakeDeps", "PkgConfigDeps"
    package_type = "${pkg_type}"
    license = "${pkg["license"]}"
    extension_properties = {
        "compatibility_cppstd": False,
        "compatibility_cstd": False
    }
    _cmake = None
    options = {
% if pkg_type == "library":
        "shared": [False, True],
% endif
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

    def export(self):
% if conanfile_tracked:
        # files.copy(self, "conanbase.py", self.recipe_folder, self.export_folder)
        files.copy(self, "conanbase.py")
% endif
        git = Git(self, self.recipe_folder)
        if git.is_dirty():
            print(f"{Fore.YELLOW}Waring: Local repo is dirty.{Style.RESET_ALL}")
            files.update_conandata(self, {"sources": {"commit": None, "url": None, "pwd": os.getcwd()}})
            return

        scm_url = None
        scm_commit = git.get_commit()
        branches = git.run("branch -r --contains {}".format(scm_commit))
        remotes = git.run("remote")
        for remote in remotes.splitlines():
            if "{}/".format(remote) in branches:
                scm_url = git.get_remote_url(remote)
                break
        if not scm_url:
            files.update_conandata(self, {"sources": {"commit": None, "url": None, "pwd": os.getcwd()}})
            return
        files.update_conandata(self, {"sources": {"commit": scm_commit, "url": scm_url}})

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        if sources["url"] and sources["commit"]:
            git.clone(url=sources["url"], target=".")
            git.checkout(commit=sources["commit"])
        else:
            files.copy(self, "*", src=sources["pwd"], dst=".")

    def requirements(self):
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

% if len(pkg.get("requires", {})) > 0:
    def build_requirements(self):
    % for conan in pkg["requires"].get("tool", []):
        % if conan.get("when") is not None:
        if ${conan.get("when")}:
            self.tool_requires("${conan.get("conan")}")
        % else:
        self.tool_requires("${conan.get("conan")}")
        % endif
    % endfor
        pass
% endif

    def configure(self):
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

    def _append_default_flags(self):
        flags = []
        if self.options.gcov:
            flags.append("-fprofile-arcs")
            flags.append("-ftest-coverage")
        if self.settings.build_type == "Release" and self.settings.arch == "armv8":
            flags.append("-D_FORTIFY_SOURCE=2")
        return flags

    def generate(self):
        tc = CMakeToolchain(self)
% if pkg_type in ["library", "shared-library", "static-library", "header-library"]:
        tc.variables["CMAKE_INSTALL_INCLUDEDIR"] = "usr/include"
    % if pkg_type in ["library", "shared-library", "static-library"]:
        tc.variables["CMAKE_INSTALL_LIBDIR"] = "usr/lib"
    % endif
% endif
        tc.variables["CMAKE_INSTALL_DATAROOTDIR"] = "usr/share"
        tc.variables["CMAKE_PROJECT_VERSION"] = self.version
        tc.variables["CMAKE_BUILD_TYPE"] = self.settings.build_type
% if pkg_type == "static-library":
        tc.variables["BUILD_SHARED_LIBS] = False
% elif pkg_type == "shared-libraries":
        tc.variables["BUILD_SHARED_LIBS"] = True
% elif pkg_type == "library":
        if self.options.shared == False:
            tc.variables["BUILD_SHARED_LIBS"] = False
        else:
            tc.variables["BUILD_SHARED_LIBS"] = True
% endif
        if self.options.test == True:
            tc.variables["BUILD_TEST"] = True
        else:
            tc.variables["BUILD_TEST"] = False

% if len(pkg.get("options", [])) > 0:
    % for op, value in pkg["options"].items():
       % if type(value["default"]) == type(False):
        if self.options.${op}:
            value = True
        else:
            value = False
        % elif type(value["default"]) == type(""):
        value = str(self.options.${op})
        % elif type(value["default"]) == type(123):
        value = int(self.options.${op}.value)
        % elif type(value["default"]) == type(123.22):
        value = float(self.options.${op}.value)
        % endif
        tc.variables["BUILD_${op.upper()}"] = value
        tc.variables["LB_${op.upper()}"] = value
        tc.preprocessor_definitions["BUILD_${op.upper()}"] = value
        tc.preprocessor_definitions["LB_${op.upper()}"] = value
    % endfor
% endif
        tc.extra_cflags = self._append_default_flags()
        tc.extra_cxxflags = self._append_default_flags()

        tc.generate()

    def _configure_cmake(self):
        if self._cmake is not None:
            return self._cmake
        self._cmake = CMake(self)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        # files.copy(self, "LICENSE", dst=f"opt/litebmc/shared/{self.name}", src=".")
        files.copy(self, "LICENSE", dst=f"opt/litebmc/shared/{self.name}", src=".")
        # 生成package.yml
        lookup = TemplateLookup(directories=self.build_folder)
        template = lookup.get_template("metadata/package.yml")
        pkgdata = template.render(lookup=lookup, pkg=self)
        # 文件放在opt/litebmc/metadata目录，以包名命名
        metadata = os.path.join(self.package_folder, f"opt/litebmc/shared/packages")
        os.makedirs(metadata, exist_ok=True)
        package_yml = os.path.join(metadata, f"{self.name}.yml")
        # 写入内容
        fp = open(package_yml, "w")
        fp.write(pkgdata)
        fp.close()
        os.chmod(package_yml, 0o644)

    def package_info(self):
% if pkg_type in ["library", "shared-library", "static-library", "header-library"]:
        self.cpp_info.includedirs = ["usr/include"]
% endif
% if len(libs) > 0:
    % if pkg_type in ["library", "shared-library", "static-library"]:
        self.cpp_info.libdirs = ["usr/lib"]
        self.runenv_info.define("LD_LIBRARY_PATH", os.path.join(self.package_folder, "usr/lib"))
        % if pkg_type == "shared-library":
        self.cpp_info.libs = [${", ".join(("\"" + i + "\"") for i in libs)}]
        % elif pkg_type == "library":
        if self.options.shared == True:
            self.cpp_info.libs = [${", ".join(("\"" + i + "\"") for i in libs)}]
        else:
            self.cpp_info.libs = [${", ".join(("\"lib" + i + ".a\"") for i in libs)}]
        % elif pkg_type == "static-library":
        self.cpp_info.libs = [${", ".join(("\"lib" + i + ".a\"") for i in libs)}]
        % endif
        self.cpp_info.set_property("cmake_find_mode", "both")
        self.cpp_info.set_property("cmake_target_name", "${pkg_name}:${pkg_name}")
        self.cpp_info.set_property("pkg_config_name", "${pkg_name}")
    % endif
% endif
% if pkg_type == "application":
        self.cpp_info.bindirs = ["usr/bin"]
        self.runenv_info.define("PATH", os.path.join(self.package_folder, "usr/bin"))
% endif
