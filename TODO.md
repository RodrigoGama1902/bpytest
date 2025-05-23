
# Documentation

- [ ] Create a readme.md file
- [ ] Write better documentation

# General codebase

- [ ] Fix all type issues

# Blender Add-on

- [ ] Automatic install bpytest addon if not installed
- [ ] Re-design the UI
- [ ] Restore the possibility to run the tests from the Blender UI
- [ ] Allow it test to be runned individually
- [x] add all pyproject.toml config to Blender UI
    collector string, keyword, -s

# CLI

- [x] Add command line interface
- [ ] Fix the CLI output, even with -s it is still showing print lines on saving a blender file
- [ ] #parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
- [ ] #parser.add_argument('-x', '--exitfirst', action='store_true', help='Exit instantly on first error or failed test')

# Test Assert System

- [x] Subprocess and same instance process should have the same test 
    logic inside of it, currently they are the same code but in different places.
- [ ] When running from blender 3.3 octane all tests passes

# Unit Test System

- [x] Implement simple fixture registering from conftest.py
- [x] Implement fixtures yield behavior
- [ ] Implement declaration scope of fixtures (module, package (fixtures defined in the conftest.py) )
- [ ] Implement fixtures scope:
    - [x] function
    - [ ] class
    - [x] module
    - [ ] package
    - [x] session
- [x] Add fixtures (Maybe the collector will collect all fixtures first)
- [x] Allow add fixtures to receive a fixture name

# Future

- [ ] Implement classes grouping
- [ ] Implement @bpytest.mark.parametrize
- [ ] Implement @pytest.mark.skipif
- [ ] Implement exception context ex: with pytest.raises(ValueError) as exc_info:, to except a specific exception

# Distribution

- [ ] Currently, the add-on and the package are the same things, 
    which lead to some problems like strange imports like "from bpytest.bpytest.runner import execute"
- [ ] Add pip distribution

# Code

- [ ] Currently, the config module is separated in a understandable way, but in the main.py of the package, the data
from the config file is not relating to any of the ConfigFile classes, find I way to relate the data to the classes, maybe
using composition in the main BpyTestConfig class, and creating each instance of each config class than 
    passing the data to the BpyTestConfig
- [ ] Currently its not clear if the test failed because of the test it self, or because some not handled exception or
blender crash. Find a way to resolve this.
- [ ] rename blender_exe_id_list > blender_exe_env_list. make sure the cli arg and the class attr will be updated and isntead of combining strings to get the env variable
the user should specify the full env variable name
- [ ] Create a print module in the common/ dir, to be used to print info, warning and error messages from bpytest
- [ ] Inside the bpytest blender module print() is used for test info, which is not the best way to do it since can be confused with the debug output or 
not relevant messages. these messages should be printed from a special function so anyone knows that this is important print
- [ ] Create a class to represent th PyProject.toml file, so its easier to read and write, and document
- [ ] Implement auto Blender download and install

# python_dependencies

- [x] If python_dependencies are used, it will be good to create a temp duplicate the blender installation
so the dependency installation dont break the current installation

# Pytests

- [ ] Test enable_addons parameter
- [ ] Test link_addons parameter
- [ ] Test configuration file load
- [ ] Add tests for python_dependencies




