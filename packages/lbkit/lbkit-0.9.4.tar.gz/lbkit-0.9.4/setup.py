import os
import re
from setuptools import setup, find_packages

def load_version():
    """ Loads a file content """
    filename = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "lbkit", "__init__.py"))
    with open(filename, "rt") as version_file:
        litebmc_init = version_file.read()
        version = re.search(r"__version__ = '([0-9a-z.-]+)'", litebmc_init).group(1)
        return version

setup(
    name="lbkit",
    version=load_version(),
    author="xuhj@litebmc.com",
    author_email="xuhj@litebmc.com",
    description="Tools provided by litebmc.com",
    long_description="build and code generate tools",
    long_description_content_type="text/markdown",
    install_requires=["pyyaml", "colorama", "mako", "node-semver>=0.6.1", "jsonschema", "conan", "requests", "gitpython", "inflection", "meson>=1.4.0", "psutil"],
    url="https://www.litebmc.com",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'lbk=lbkit.lbkit:run',
            'lbkit=lbkit.lbkit:run',
        ],
    },
)
