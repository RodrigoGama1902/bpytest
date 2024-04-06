from setuptools import setup

setup(
    name="bpytest",
    version="0.1",
    packages=["bpytest"],
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
