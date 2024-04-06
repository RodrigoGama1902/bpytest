from setuptools import find_packages, setup

setup(
    name="bpytest",
    version="0.1",
    packages=find_packages(),
    package_dir={"bpytest": "bpytest"},
    entry_points={
        "console_scripts": [
            "bpytest = bpytest.main:main",
        ],
    },
    install_requires=[
        "toml==0.10.2",
    ],
)
