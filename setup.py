from setuptools import setup, find_packages, Extension
import os

# C++拡張モジュールの設定
cseg_renderer = Extension(
    'cseg.lib.cseg_renderer',
    sources=['cseg/cpp/cseg_renderer.cpp'],
    include_dirs=[],  # pybind11のインクルードパスは後で自動追加
    extra_compile_args=['-std=c++11', '-O3', '-march=native'],
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

setup(
    name='jbrowse-plugin-cseg',
    version='0.1.0',
    description='JBrowse 2 plugin for CSEG visualization',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(),
    ext_modules=[cseg_renderer],
    install_requires=[
        'flask',
        'pillow',
        'numpy',
        'pybind11>=2.6.0',
    ],
    entry_points={
        'console_scripts': [
            'cseg-create-db=cseg.cli.create_db:main',
            'cseg-server=cseg.cli.server:main',
        ],
    },
    python_requires='>=3.7',
    include_package_data=True,
    package_data={
        'cseg': ['cpp/*.cpp', 'cpp/*.h'],
    },
)
