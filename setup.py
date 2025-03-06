from setuptools import setup, find_packages, Extension
import os
import platform
import sys
import sysconfig
import pybind11

# コンパイラオプションを設定
extra_compile_args = [
    '-std=c++17',     # 最新のC++機能を使用
    '-O3',            # 最高レベルの最適化
    '-march=x86-64',  # 基本的なx86-64アーキテクチャ向けに最適化
    '-mtune=generic', # 一般的なプロセッサ向けに最適化
    '-ffast-math',    # 浮動小数点演算の最適化
    '-flto',          # リンク時最適化
    '-funroll-loops', # ループ展開
    '-fopenmp',       # OpenMPによるマルチスレッド処理
]

# macOSの場合は-fopenmpを除外
if platform.system() == "Darwin":
    extra_compile_args.remove('-fopenmp')

# リンカーオプションを設定
extra_link_args = ['-flto']  # リンク時最適化
if platform.system() != "Darwin":
    extra_link_args.append('-fopenmp')

# Python.hのインクルードパスを取得
python_include = sysconfig.get_path('include')
print(f"Python include path: {python_include}")

# pybind11のインクルードパスを取得
pybind11_include = pybind11.get_include()
print(f"pybind11 include path: {pybind11_include}")

include_dirs = [python_include, pybind11_include]
print(f"Using include directories: {include_dirs}")

# C++拡張モジュールの設定
cseg_renderer = Extension(
    'cseg.lib.cseg_renderer',  # フルパスで指定
    sources=['cseg/cpp/cseg_renderer.cpp'],
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++',
)

# vcf2csegのビルド設定
vcf2cseg_ext = Extension(
    'cseg.bin.vcf2cseg_cpp',  # フルパスで指定
    sources=['cseg/cpp/vcf2cseg.cpp'],
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++',
)

print("Setting up package...")
setup(
    name='jbrowse-plugin-cseg',
    version='0.1.0',
    description='JBrowse 2 plugin for CSEG visualization',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    ext_modules=[cseg_renderer, vcf2cseg_ext],
    install_requires=[
        'flask',
        'pillow',
        'numpy',
        'pybind11>=2.6.0',
    ],
    entry_points={
        'console_scripts': [
            'vcf2cseg=cseg.bin.vcf2cseg_cpp:main',  # C++モジュールのmain関数を直接使用
            'cseg-server=cseg.cli.server:main',
            'cseg-create-db=cseg.cli.create_db:main',
            'cseg-init=cseg.cli.init:main',
        ],
    },
    python_requires='>=3.7',
    include_package_data=True,
    package_data={
        'cseg': [
            'lib/*.so',
            'bin/*.so',
        ],
    },
)
