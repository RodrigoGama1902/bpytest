from setuptools import setup, find_packages

setup(
    name='bpytest',
    version='0.1',
    packages=find_packages(),
    package_dir={'bpytest': 'bpytest'},
    entry_points={
        'console_scripts': [
            'bpytest = bpytest.__main__:main',
        ],
    },
    install_requires=[
        'colorama==0.4.6',
        'toml==0.10.2',
    ],
)