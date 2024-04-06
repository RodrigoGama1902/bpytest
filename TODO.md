
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




