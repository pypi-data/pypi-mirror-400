# Signum Test Suite

This directory contains validation and benchmarking tools for the `csignum-fast` library (`*.py`), and test results (`*.txt`).

## Test Files

* `testing.py`: An auxiliary module. Contains things common for all tests, for example, the `detect_version` function.
* `simple_test_signum.py`: The prototype that prints test results for visual check; does not use assertions. 121 cases. Works for all versions: for older versions, passes only the corresponding subset of tests.
* `test_signum.py`: The same 121 cases with assertions and `unittest`. Current version only.
* `leak_test.py`: seven million-repeating loops for memory leak detection. Current version only.
* `57_tests_signum.py`: 57 tests from the whole 121-tests set, which are common for all versions. Repeats 100,000 times to estimate execution time. Includes tests that raise exceptions.
* `41_tests_signum.py` (**Pure Math**): 41 tests from 57 that do not raise exceptions. Repeats 100,000 times to estimate execution time. Our base for benchmarking.

## Benchmarking

Results (`*.txt`) were obtained with **Python 3.13.5 (AMD64)** on a **Lenovo ThinkPad** (processor 11th Gen Intel(R) Core(TM) i7-1165G7 @ 2.80GHz, RAM 32.0 GB) running **Windows 11 Pro 25H2** under the **"Best performance"** power plan.

For consistent results, all benchmarking scripts (except `test_signum.py`) automatically set **High Process Priority** via `psutil`.

Benchmarks were conducted using the **Best-of-N** method with the `41_tests_signum.py` **Pure Math** suite. This eliminates jitter from background OS activities (antivirus, network tasks, system updates, notifications, etc.), capturing the true peak performance of the extension.

| Version | 4.1M calls (s) | Speedup vs v1.0.2 (%) | Edition | Features | Status |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1.0.2 | 6.6877 | - | Christmas | Base `sign(x)` | Legacy, 7.1% slower  |
| 1.1.0+ | 7.2759 | -8.8% | New Year | preprocess=, if_exc= | Intermediate, 15.9% slower |
| 1.2.0 | 6.2133 | +7.1% | Gold | codeshift=, max optimization | The Recommended Champion |

**Efficiency Note:** The transition from v1.1.0+ to v1.2.0 resolved previous performance regressions, resulting in a 15.9% internal throughput improvement because of refined optimizations in C++ code.

## How to run tests

1.  Ensure the library and dependencies are installed:
```bash
pip install csignum-fast psutil sympy
```

2.  Run the desired test under Linux/macOS:
```bash
python tests/test_signum.py
python tests/test_signum.py >> tests/test_signum.txt 2>&1
```
or under Windows:
```bash
python tests\test_signum.py
python tests\test_signum.py >> tests\test_signum.txt 2>&1
```
`test_signum.py` is unique: the result is printed both through `sys.stdout` (test header, section trace, final result) and `sys.stderr` (the `unittest` module output), so you need `2>&1` to catch all that in a file.

## Building from Source

To build and test the library locally:

1.  Install build tools and dependencies:
```bash
pip install build setuptools psutil sympy
```

2.  Build from the project root:
```bash
python -m build
```

3.  Install from the project root:
```bash
pip install .
```

4.  Run any test file from the `tests` directory as shown above.

[**Back to Main README**](../README.md)
