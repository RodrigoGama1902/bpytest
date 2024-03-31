from setuptools import find_packages, setup

setup(
    name="bpytest",
    version="0.1",
    packages=find_packages(),
    package_dir={"core": "core"},
    entry_points={
        "console_scripts": [
            "bpytest = core.main:main",
        ],
    },
    install_requires=[
        "colorama==0.4.6",
        "toml==0.10.2",
    ],
)
