from setuptools import setup, find_packages

setup(
    name='bpytest',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bpytest = bpytest.__main__:main',
        ],
    },
)