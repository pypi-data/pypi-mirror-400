from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup, find_packages
import sys

# Compiler flags
extra_compile_args = [
    '-std=c++17',
    '-O3',
    '-march=native',
    '-fopenmp',
    '-mavx2',
    '-mfma',
    '-DNDEBUG'
]

# Linker flags
extra_link_args = ['-fopenmp']

# Define extension
ext_modules = [
    Pybind11Extension(
        "industrial_matrix",
        [
            "src/industrial_matrix.cpp",
            "src/python_binding.cpp"
        ],
        include_dirs=['include'],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
        cxx_std=17,
        language='c++'
    ),
]

setup(
    name="industrial-matrix",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Industrial-grade matrix computing engine with SIMD and OpenMP optimization",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/industrial-matrix",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: C++",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pybind11>=2.6.0"
    ],
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
