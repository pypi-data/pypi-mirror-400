# -*- coding: utf-8 -*-
# Copyright (C) 2018-2025 Connet Information Technology Company, Shanghai.

from setuptools import find_packages, setup, Extension
import os
import os.path as osp
import sys
import typing
import pathlib
from setup_config import PACKAGE_NAME, PROJECT_NAME, VERSION, EXTLIST, REQUIREMENTS_FILE

v = sys.version_info
if v[0] >= 3 and v[:2] < (3, 6):
    error = "ERROR: qSide requires Python version 3.6 and above."
    print(error, file=sys.stderr)
    sys.exit(1)


here = osp.abspath(osp.dirname(__file__))


def get_package_data(name, extlist):
    """
    收集包目录中的资源文件。

    :param name: 包目录路径
    :param extlist: 匹配条件列表，可以包含文件名或扩展名，例如
                    ['.svg', '.png', 'LICENSE']
    :return: 相对路径列表（相对于 name）
    """
    files = []
    extlist_lower = {e.lower() for e in extlist}

    for dirpath, __dirnames, filenames in os.walk(name):
        if 'tests' in dirpath:  # 跳过测试目录
            continue

        for fname in filenames:
            if fname.startswith('.'):
                continue

            ext = osp.splitext(fname)[1].lower()
            if fname.lower() in extlist_lower or ext in extlist_lower:
                relpath = osp.relpath(osp.join(dirpath, fname), name)
                files.append(relpath)

    return files


def get_description() -> str:
    """Get long description."""
    with open(osp.join(here, 'README.md'), 'r') as f:
        data = f.read()
    return data


def get_requirements() -> typing.List[str]:
    """Get installation requirements"""
    if pathlib.Path(REQUIREMENTS_FILE).is_file():
        with open(osp.join(here, REQUIREMENTS_FILE), 'r') as f:
            requirements = f.readlines()
        return requirements
    else:
        return []


def get_extensions() -> typing.List[Extension]:
    ext_modules = []
    package_dir = pathlib.Path(here, PACKAGE_NAME)
    if sys.platform == 'darwin':
        ext = "*.so"
    elif sys.platform == 'win32':
        ext = '*.pyd'
    else:
        ext = '.so'

    for so_file in package_dir.rglob(ext):
        # 生成 Python 导入路径
        rel_path = so_file.relative_to(package_dir)
        module_name = PACKAGE_NAME + "." + ".".join(rel_path.with_suffix("").parts)

        ext_modules.append(
            Extension(
                name=module_name,
                sources=[],  # 已经编译好的二进制文件，不需要重新编译
            )
        )
    return ext_modules




# 告诉 setuptools：这是一个 二进制分发包，即使不用编译
# 1. 不需要写 Extension，不会触发 build_ext。
# 2. wheel 会正确生成 cp311-cp311-win_amd64.whl 或 macosx_11_0_arm64.whl。
# 3. .so/.pyd 会被直接打进 wheel。
from setuptools.dist import Distribution
class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True  # 强制认为有二进制模块

setup(
    name=PROJECT_NAME,
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    package_data={PACKAGE_NAME: get_package_data(PACKAGE_NAME, EXTLIST)},
    distclass=BinaryDistribution,
    author="Connet Information Technology Company Ltd, Shanghai.",
    author_email="tech_support@shconnet.com.cn",
    description="X Qt framework.",
    long_description="",
    long_description_content_type="text/markdown",
    keywords="Qt Python",
    url="",
    project_urls={
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Interpreters",
    ],
    install_requires=get_requirements(),
)