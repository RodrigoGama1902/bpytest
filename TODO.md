
# Documentation

- [ ] Create a readme.md file
- [ ] Write better documentation

# Blender Interface

- [ ] Add a UI list that allows to [maybe one or more] addons to test
- [ ] add all pyproject.toml config to Blender UI
    collector string, keyword, -s, runner_type

# CLI

- [x] Add command line interface
- [ ] #parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
- [ ] #parser.add_argument('-x', '--exitfirst', action='store_true', help='Exit instantly on first error or failed test')

# Test Assert System

- [x] Subprocess and same instance process should have the same test 
    logic inside of it, currently they are the same code but in different places.
- [] When running from blender 3.3 octane all tests passes

# Unit Test System

- [ ] Add fixtures (Maybe the collector will collect all fixtures first)
- [ ] Implement classes grouping

# Distribution

- [ ] Currently, the add-on and the package are the same things, 
    which lead to some problems like strange imports like "from bpytest.bpytest.runner import execute"
- [ ] Add pip distribution




