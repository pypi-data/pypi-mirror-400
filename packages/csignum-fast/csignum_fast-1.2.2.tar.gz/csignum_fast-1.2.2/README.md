# csignum-fast
![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/release-Gold%20Edition-gold.svg)
![Performance](https://img.shields.io/badge/performance-+16%25%20faster-orange.svg)
![Tests](https://img.shields.io/badge/tests-121%20passed-brightgreen.svg)
![PyPI Version](https://img.shields.io/pypi/v/csignum-fast.svg)

**High-performance, versatile implementation of the universal 'sign' function for Python**

*Released on January 5, 2026* ⊙ *Gold Edition*

Version **1.2.2**: Maximum speed (**+7.1%** vs v.1.0.2 and **+15.9%** vs 1.1.5), and the third keyword argument.

## Key Features

1.  **Uniform Results**: Always returns only `-1`, `0`, or `1` as an `int` for valid numeric comparisons.
2.  **Correct Edge Case Handling**:
    * `sign(+0.0)` and `sign(-0.0)` return `0`.
    * `sign(inf)` returns `1`, `sign(-inf)` returns `-1`.
    * For any **NaN** (float NaN, Decimal NaN, etc.), it returns `math.nan` (float).
3.  **Comprehensive Duck Typing**: Delegates comparisons to the argument's class. Works seamlessly with:
    * Built-in `int` (including arbitrary-precision), `bool`, and `float`.
    * `fractions.Fraction` and `decimal.Decimal`.
    * Any existing and future objects that support rich comparisons with numbers.
4.  **Informative Error Handling for Easy Debugging**: Provides clear, descriptive `TypeError` messages when passed non-numeric, non-scalar, or incomparable arguments.
5.  **⚡ High Performance**: Branch-optimized C++20 core; `METH_FASTCALL` argument scan; static module-level constants. The speed is near maximum for a C++ extension for Python: since v1.0.0 all possibilities to increase performance have been systematically searched and applied.
6.  **✅ Thoroughly Tested**: Tested on 121 cases including different types, edge cases, new custom class, keyword and inappropriate arguments. Also tested: memory leaks, and benchmarking against older versions.
7.  **✨ Pre-processing Engine**: Use the `preprocess` keyword argument to transform input before calculation or trigger an **Early Exit** (recursion permitted).
8.  **🛡️ Exception safety**: The `if_exc` keyword argument allows to define a fallback value (like `None`, `math.nan`, or `-2`) instead of crashing on invalid types.
9.  **✨ 5-way uniform result**: Use the `codeshift` keyword argument to encode all 5 possible `sign` exits (`TypeError`, -1, 0, 1, `NaN`) by subsequent integers for switching or indexing.

## Installation

```bash
pip install csignum-fast
```

## Standard Usage

```python
from signum import sign # Obligatory for all examples

print(sign(-10**100))       # -1
print(sign(3.14))           #  1
print(sign(float('-nan')))  # math.nan

from decimal import Decimal
print(sign(Decimal("0.0"))) #  0
```

## Advanced Usage (New features since v1.1.0)

### ☢️ Attention: Contract Programming!
For Performance reasons, keyword argument values are **not checked** by the `sign` function. **Your** responsibility is:
* To pass a **`callable`** for `preprocess` (accepts one argument, returns `None` or a `tuple`).
* To pass a **`tuple`** for `if_exc`.
* To pass an **`int`** for `codeshift`.
* To guarantee that **all** calculations implied by these arguments do not result in additional exceptions or crashes.

*Passing incorrect values to these parameters may result in **unpredictable behavior** or **segmentation faults**.*

### ⚡ Custom Pre-processing with `preprocess`
With `preprocess` keyword argument, you can pass a `callable` to transform the input. (Default: `preprocess=None` without preprocessing).

The `callable` will be called with the positional argument of `sign`. It must support a special return protocol:
- Return `None`: `sign` proceed with usual calculation.
- Return `(value,)`: `sign` proceed with calculation using `value` as an argument. Why a `tuple`? Use `(None,)` to return `None` as a `value` (usually raises `TypeError`).
- Return `(any, result)`: **Early Exit**. Immediately return `result` as the final answer of `sign`; `any` is ignored.

```python
from signum import sign # Obligatory for all examples

# Convert str to float; uses lambda as callable
sign('5.0', preprocess=lambda a: (float(a),)) # Returns 1 instead of `TypeError` exception

# Treat small number as zero through argument replacement only
EPS = 1e-9
sign(-.187e-17, preprocess=lambda a: (0 if abs(a) < EPS else a,)) # Returns 0 (instead of -1)

# Treat small number as zero through argument or result replacement; uses variable as callable
ppf1 = lambda x: (x, 0) if abs(x) < EPS else (x,)
sign(-.187e-17, preprocess=ppf1) # Returns 0 (instead of -1)

# Extract the first number from string, replacing only string argument; supplies function as callable
import re
numeric_finder = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")

def n_extract(s):
    if isinstance(s, str):
        match = numeric_finder.search(s)
        return (float(match.group()),) if match else None
    return None

sign("☠️15 men on the dead man's chest☠️", preprocess=n_extract) # Returns sign(15) == 1

# Do you want sign(complex) instead of `TypeError` exception?
def c_prep(z):
    if z == 0 or not isinstance(z, complex): return None
    # complex z != 0
    return (0, z/abs(z))

sign(-1+1j, preprocess=c_prep) # Returns (-0.7071067811865475+0.7071067811865475j)

# numpy flavor: float result for float or Decimal argument; uses recursive call of sign
from decimal import Decimal
ppf2 = lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None
sign(-5.0, preprocess=ppf2) # Returns -1.0 instead of -1
```

### 🛡️ Exception Safety with `if_exc`
With this keyword, you can avoid try-except blocks. If `sign()` encounters an incompatible type, it will return your fallback value instead of raising a `TypeError`. `if_exc` should be a tuple that permits you to pass `None` as the fallback value through `if_exc=(None,)`. (Default `if_exc=None` is totally different).
```python
from signum import sign # Obligatory for all examples

sign("not a number", if_exc=(-2,)) # Returns -2 instead of `TypeError` exception
```

### You can use two keyword arguments at once
With `preprocess`, you replace arguments (or even results) in specific cases, while `if_exc` prevents exceptions for all that remains.

### Comfortable 5-way processing with `codeshift` keyword argument
When innocent people lived in the heavenly world of pure mathematics, the `sign` function was **ternary**. The results were -1, 0, +1.

In the meantime, people entered the real world and started programming. In the real world, there is the IEEE 754 standard, which describes the tricky number `NaN`, that is, **‘Not a Number’**. Any function of `NaN`, according to the rules of good taste, should return `NaN`.

In the real world, programmers make **mistakes**. Worse, completely **inappropriate data** can be caught in endless streams of those. Then the function — alas — stops calculating with an error message.

In the real world of confusing standards and distorted data, our divine ternary `sign` function has become **quinary** (5-way).

You cannot process the five possible results of `sign` **uniformly**.

To catch an error, you need to write an indecently multi-layered construction `try: ... sign(...) ... except TypeError as e: ...`.

To catch NaN, you need to write `if isnan(sign(...)):`.

Only the usual results `-1, 0, 1` do not cause any trouble: a cascade of `if ... elif ... else` with checks for `==`, or `match ... case ...` solve the problem.

The keyword argument `codeshift` converts `sign` into a **uniform 5-way switch**. All 5 possible `sign` results are **encoded as integers**: `TypeError` becomes -2; -1, 0, 1 remain unchanged; `NaN` is encoded by 2. The value of the `codeshift` argument, which must be an integer, is added to this code, and the resulting number is returned as the result. (Default is `codeshift=None`: usual processing).

The easiest way to continue is to use the **`match ... case ...`** operator. You can also use the result as an **index**.

Everything aforementioned is summarized in the table:

#### Quinary way of `signum.sign()` through `codeshift`
| Argument | Std result | `codeshift=0` | `codeshift=2` |
| :--- | :--- | :--- | :--- |
| Invalid | `TypeError` | -2 | 0 |
| Negative | -1 | -1 | 1 |
| Zero | 0 | 0 | 2 |
| Positive | 1 | 1 | 3 |
| NaN | math.nan | 2 | 4 |

#### Code Patterns: One ~~Ring~~ Switch to Rule Them All
```python
# The golden match
from signum import sign # Obligatory for all examples

match sign((d := data_input), codeshift=2):
    case 0: handle_error(d)
    case 1: handle_negative(d)
    case 2: handle_zero(d)
    case 3: handle_positive(d)
    case 4: handle_nan(d)

# Indexing pattern
function_list = [handle_error, handle_negative, handle_zero, handle_positive, handle_nan]
function_list[sign((d := data_input), codeshift=2)](d)
```

### Interaction with other keyword arguments
If there is the `if_exc` argument, it takes precedence over `codeshift`: instead of an exception, the `if_exc` value is returned unchanged. `codeshift` is applied in the remaining four cases (the results -1, 0, 1, and `NaN`).

The interaction between `preprocess` and `codeshift` is similar. If `preprocess` returns `None` or a tuple with one element `(x,)`, then everything goes as usual: `codeshift` is not about the argument, but about the result. If `preprocess` returns a tuple with two elements `(x, y)`, it takes precedence over `codeshift`, and unchanged `y` is returned as the result.

The general principle is “an explicitly specified **special** case **overrides** a **more general** option”. `if_exc` is only applicable to exceptions, while `codeshift` is applicable to all results in general, so `codeshift` has a lower priority. The same applies to `preprocess` returning a tuple of length 2: it defines a single specific outcome, which takes precedence over what intercepts and shifts all results and even “no-results”.

## Why Gold Edition? (v1.2.2)

### The Quinary Revolution
-  **New `codeshift` Argument:** The headliner of v1.2.0+. It enables effortless 5-way logic (`TypeError`, -1, 0, 1, `NaN`) without extra Python-level overhead.

### Evolution of Speed (**15.9%** faster than v1.1.5, **7.1%** faster than v1.0.2)
-  **New in v1.2.2: CPython FastCall.** Migration to `METH_FASTCALL`. This eliminated the overhead of using temporary tuple and dictionary for argument parsing.
-  **New in v1.2.2: Static Object Caching.** The comparison base (Python `int(0)`) and all keyword names are now static C-objects, pre-allocated at module load time.
-  **Since v1.1.0: Branchless Logic Remastered.** The optimized cascade of ternary switches replaced the bulky 27-way switch.
-  **Since v1.0.0: Branchless Logic.** Our state index allows the CPU to execute core logic in a linear pipeline without conditional branching even when handling edge cases and type errors.

## 📊 Performance & Quality Assurance

### Benchmark Results
**Gold Edition v1.2.2** delivers a **15.9%** performance boost over v1.1.5 and is **7.1%** faster than the original v1.0.2, despite the significantly expanded feature set. Detailed metrics are available in the “Benchmarking” section in [README for tests](https://github.com/acolesnicov/signum/tree/main/tests/README.md).

**Note:** Benchmarking scripts require `psutil` (for priority management) and `sympy` (for `sympy` numeric types and `NaN` validation).

### Reliability
-  **Memory Safety:** Verified with rigorous stress test (**0 bytes leaked over 7M iterations**).
-  **Expanded Test Coverage:** 121 validation cases (vs 57 for  v1.0.2 and 94 for v1.1.0+).

## License
This project is licensed under the **MIT License**. See the [LICENSE](https://github.com/acolesnicov/signum/blob/main/LICENSE) file for details.

## Author
**Alexandru Colesnicov**: [GitHub Profile](https://github.com/acolesnicov)
