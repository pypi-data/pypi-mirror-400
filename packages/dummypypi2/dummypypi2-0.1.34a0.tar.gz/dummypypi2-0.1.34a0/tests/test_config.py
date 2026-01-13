"""Tests for global configuration of variables, algorithms, solvers, and display settings"""

import pytest

import dummypypi2 as dp


def test_set_algo_options():
    # NOTE: I like this style of testing multiple assertions in a single test function much better; cleaner and easier to read
    dp.set_algo_options('default')
    # 1: Test resetting to default
    assert dp._config.RTOL == 1E-5 and dp._config.ATOL == 1E-8, "RTOL and ATOL should be set to 1E-5 and 1E-8 by default, respectively"

    a, delta = 0.1, 1E-5; b = a + delta
    # 2: Test closeness with default tolerances
    assert not dp.is_close(a, b), f"The default tolerances (ATOL=1E-8, RTOL=1E-5) should not consider a=0.1 and b=0.10001 close"

    dp.set_algo_options(atol=1E-3)
    # 3: Test setting custom tolerances
    assert dp._config.RTOL == 1E-5 and dp._config.ATOL == 1E-3, "RTOL and ATOL should be set by the global setter to 1E-5 and 1E-3, respectively"
    
    # 4: Test closeness with updated tolerances
    assert dp.is_close(a, b), f"With ATOL=1E-3 (=0.001), a=0.1 and b=0.10001 should be considered close"


def test_algo_options_context_manager():
    # FROM: https://stackoverflow.com/questions/39896716/can-i-perform-multiple-assertions-in-pytest  # nopep8
    errors = []

    import dummypypi2._config as cfg
    dp.set_algo_options('default')  # FIXME: This does not work, because the previous test modified the global state... so we need to either modify the order, or reset the state here
    if not (cfg.RTOL == 1E-5 and cfg.ATOL == 1E-8):
        errors.append("RTOL and ATOL should be set to 1E-5 and 1E-8 by default, respectively")
    a, delta = 0.1, 1E-5; b = a + delta
    if dp.is_close(a, b):
        errors.append("With RTOL=1E-5 and ATOL=1E-8, a and b should not be considered close")
    with dp.algo_options(atol=1E-3):
        if not dp.is_close(a, b):
            errors.append("Within context manager with ATOL=1E-3, a and b should be considered close")
    if dp.is_close(a, b):
        errors.append("Outside context manager, a and b should not be considered close anymore")

    assert not errors, "errors occurred:\n{}".format("\n".join(errors))