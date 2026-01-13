from setuptools import setup, Extension, find_packages
import os

# Define the C extension (Source compatibility for Linux/macOS)
# On Windows, we prefer the pre-built DLL to avoid MSVC requirement for users
ext_modules = []
if os.name != 'nt':
    ext_modules.append(Extension(
        "nncc._libnncc",
        sources=[
            "src/libnncc.c",
            "src/loader.c",
            "src/codegen.c",
            "src/model.c"
        ],
        include_dirs=["src"],
        extra_compile_args=["-O3", "-Wall", "-fPIC", "-shared"],
    ))

setup(
    packages=find_packages(),
    # Include pre-built shared libraries (for Windows wheel)
    package_data={
        "nncc": ["*.dll", "*.so"],
    },
    ext_modules=ext_modules,
    include_package_data=True,
)
