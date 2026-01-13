import os
from conan import ConanFile
<% dts = pkg.get("metadata", {}).get("dts") %>

class RootfsConan(ConanFile):
    """用于构建产品的顶层rootfs包"""
    name = "rootfs_df190c"
    settings = "os", "arch", "compiler", "build_type"
    description = "build rootfs component"
    url = "https://litebmc.com"
    extension_properties = {
        "compatibility_cppstd": False,
        "compatibility_cstd": False
    }
    homepage = "https://www.litebmc.com"
    license = "BSL-1.0"
    version = "0.0.1"

% if dts:
    def build_requirements(self):
        self.tool_requires("dtc/1.7.0")

    def build(self):
        os.makedirs(self.package_folder + "/boot")
        self.run(f"dtc -I dts -O dtb ${dts["input"]} -o {self.package_folder}/boot/${dts["output"]}")

% endif