from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    # Include pre-built shared libraries
    package_data={
        "nncc": ["*.dll", "*.so"],
    },
    include_package_data=True,
)
