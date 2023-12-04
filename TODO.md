
# ------------- Documentation -------------

[ ] Write better documentation

# ------------- Test Assert System -------------

[x] Subprocess and same instance process should have the same test 
    logic inside of it, currently they are the same code but in different places.

# ------------- Test Unit System --------------

[ ] Add fixtures
[ ] Make a correct implementation of the "-s" argument, that stands for --nocapture
    Currently the implementation only stands for "-s will display output", which is not correctly implemented.
    like in pytest.
[ ] Create a better test collection system, so the -k flag can be used correctly.
    Make it so that all collected functions can be filtered

# ------------- Command Line --------------

[ ] Add command line interface

# ------------- Distribution --------------

[ ] Currently, the add-on and the package are the same things, 
    which lead to some problems like strange imports like "from bpytest.bpytest.runner import execute"
[ ] Add pip distribution




