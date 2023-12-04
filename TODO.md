
# ------------- Documentation -------------

[ ] Write better documentation

# ------------- Blender Interface ---------------

[ ] Add a UI list that allows to [maybe one or more] addons to test
[ ] add all pyproject.toml config to Blender UI
    collector string, keyword, -s, test_mode
[ ] 


# ------------- Test Assert System -------------

[x] Subprocess and same instance process should have the same test 
    logic inside of it, currently they are the same code but in different places.

# ------------- Test Unit System --------------

[ ] Add fixtures
[ ] Make a correct implementation of the "-s" argument, that stands for --nocapture
    Currently the implementation only stands for "-s will display output", which is not correctly implemented.
    like in pytest.


# ------------- Command Line --------------

[ ] Add command line interface

# ------------- Distribution --------------

[ ] Currently, the add-on and the package are the same things, 
    which lead to some problems like strange imports like "from bpytest.bpytest.runner import execute"
[ ] Add pip distribution




