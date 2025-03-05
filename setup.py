from setuptools import setup, find_packages, Extension
import os
import platform
import sys

# コンパイラオプションを設定
extra_compile_args = [
    '-std=c++17',     # 最新のC++機能を使用
    '-O3',            # 最高レベルの最適化
    '-march=native',  # CPUアーキテクチャに最適化
    '-ffast-math',    # 浮動小数点演算の最適化
    '-flto',          # リンク時最適化
    '-funroll-loops', # ループ展開
    '-fopenmp',       # OpenMPによるマルチスレッド処理
    '-v',             # 詳細なコンパイル情報を表示
]

# macOSの場合は-fopenmpを除外
if platform.system() == "Darwin":
    extra_compile_args.remove('-fopenmp')

# リンカーオプションを設定
extra_link_args = ['-flto', '-v']  # リンク時最適化と詳細情報表示
if platform.system() != "Darwin":
    extra_link_args.append('-fopenmp')

# C++拡張モジュールの設定
cseg_renderer = Extension(
    'cseg.lib.cseg_renderer',
    sources=['cseg/cpp/cseg_renderer.cpp'],
    include_dirs=[],  # pybind11のインクルードパスは後で自動追加
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++',
)

# vcf2csegのビルド設定
vcf2cseg_ext = Extension(
    'cseg.bin.vcf2cseg_cpp',
    sources=['cseg/cpp/vcf2cseg.cpp'],
    include_dirs=[],  # pybind11のインクルードパスは後で自動追加
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
    language='c++',
)

def get_pybind11_include():
    try:
        import pybind11
        return pybind11.get_include()
    except ImportError:
        return None

# pybind11のインクルードパスを追加
pybind11_include = get_pybind11_include()
if pybind11_include:
    cseg_renderer.include_dirs.append(pybind11_include)
    vcf2cseg_ext.include_dirs.append(pybind11_include)

# パッケージデータファイルの設定
package_data = {
    'cseg': [
        'cpp/*.cpp',
        'cpp/*.h',
        'lib/*.so',
        'bin/*.so'
    ]
}

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
            'vcf2cseg=cseg.bin.vcf2cseg:main',
            'cseg-server=cseg.cli.server:main',
            'cseg-create-db=cseg.cli.create_db:main',
            'cseg-init=cseg.cli.init:main',
        ],
    },
    python_requires='>=3.7',
    include_package_data=True,
    package_data=package_data,
    zip_safe=False,  # C++拡張モジュールを使用するため
)
