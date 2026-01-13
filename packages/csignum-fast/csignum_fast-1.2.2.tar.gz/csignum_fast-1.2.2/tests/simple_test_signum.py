from signum import sign

from testing import SHORT_SIMPLE_TEST, SST_DICT, get_passes, set_high_priority, detect_version, success, \
                    open_devnull, close_devnull, OutputUTF8, \
                    EPS as _EPS, PIRATES as _PIRATES, n_extract as _n_extract, c_prep as _c_prep, \
                    MyNumber as _MyNumber, ExplodingNumber as _ExplodingNumber, \
                    NotImplementedNumber as _NotImplementedNumber, trace as _trace

from decimal import Decimal
from fractions import Fraction
from math import nan, inf
import sympy
import sys
import time

MAX_PASSES = get_passes(__file__)
_SST = min(SHORT_SIMPLE_TEST, SST_DICT.get(detect_version(), 'default'))

outflows = OutputUTF8()
outflows.set_utf8()

start_time = None
out_test   = None

print(f'***** Test: {__file__}')
print(f'MAX_PASSES: {MAX_PASSES}')
print(f'*** {set_high_priority()} ***\n')
for _ in range(MAX_PASSES + 1):
    s_cnt = 0
    counter = 0

    s_cnt += 1; prev_counter = counter
    print(f'{s_cnt:2} --- int', file=out_test)
    print("sign(-5):", sign(-5), file=out_test); counter += 1
    print("sign(-1):", sign(-1), file=out_test); counter += 1
    print("sign(0):", sign(0), file=out_test); counter += 1
    print("sign(1):", sign(1), file=out_test); counter += 1
    print("sign(5):", sign(5), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- bool', file=out_test)
    print("sign(True):", sign(True), file=out_test); counter += 1
    print("sign(False):", sign(False), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- big numbers', file=out_test)
    print('sign(10**1000):', sign(10**1000), file=out_test); counter += 1
    print('sign(-10**1000):', sign(-10**1000), file=out_test); counter += 1
    print('sign(10**1000-10**1000):', sign(10**1000-10**1000), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- float', file=out_test)
    print("sign(-5.0):", sign(-5.0), file=out_test); counter += 1
    print("sign(-1.0):", sign(-1.0), file=out_test); counter += 1
    print("sign(0.0):", sign(0.0), file=out_test); counter += 1
    print("sign(1.0):", sign(1.0), file=out_test); counter += 1
    print("sign(5.0):", sign(5.0), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- -0.0 and +0.0', file=out_test)
    print("sign(float('-0.0')):", sign(float('-0.0')), file=out_test); counter += 1
    print("sign(float('+0.0')):", sign(float('+0.0')), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- -inf and inf', file=out_test)
    print("sign(-inf):", sign(-inf), file=out_test); counter += 1
    print("sign(inf):", sign(inf), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- -nan and nan', file=out_test)
    print("sign(float('-nan')):", sign(float('-nan')), file=out_test); counter += 1
    print("sign(nan):", sign(nan), file=out_test); counter += 1
    print("sign(0.0*nan):", sign(0.0*nan), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- Fraction', file=out_test)
    print("sign(Fraction(-5, 2)):", sign(Fraction(-5, 2)), file=out_test); counter += 1
    print("sign(Fraction(-1, 2)):", sign(Fraction(-1, 2)), file=out_test); counter += 1
    print("sign(Fraction(0, 2)):", sign(Fraction(0, 2)), file=out_test); counter += 1
    print("sign(Fraction(1, 2)):", sign(Fraction(1, 2)), file=out_test); counter += 1
    print("sign(Fraction(5, 2)):", sign(Fraction(5, 2)), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- Decimal', file=out_test)
    print("sign(Decimal(-5.5)):", sign(Decimal(-5.5)), file=out_test); counter += 1
    print("sign(Decimal(-1.5)):", sign(Decimal(-1.5)), file=out_test); counter += 1
    print("sign(Decimal(0.0)):", sign(Decimal(0.0)), file=out_test); counter += 1
    print("sign(Decimal(1.5)):", sign(Decimal(1.5)), file=out_test); counter += 1
    print("sign(Decimal(5.5)):", sign(Decimal(5.5)), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f"\n{s_cnt:2} --- Decimal('NaN')", file=out_test)
    print("sign(Decimal('NaN')):", sign(Decimal('NaN')), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- sympy (substitution and Rational)', file=out_test)
    x_sym = sympy.Symbol('x')
    expr = x_sym
    val = expr.subs(x_sym, -3.14)
    print(f"val: {repr(val)}; type(val): {type(val)}", file=out_test)
    print(f"type(val > 0): {type(val > 0)}", file=out_test)
    print("sign(val):", sign(val), file=out_test); counter += 1
    print("sign(sympy.Rational(3, 4)):", sign(sympy.Rational(3, 4)), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- sympy.nan', file=out_test)
    print("sign(sympy.nan):", sign(sympy.nan), file=out_test); counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- My Custom Class That Have >, <, == With Numbers But Nothing Else', file=out_test)
    print("sign(_MyNumber(-5)):",  sign(_MyNumber(-5)), file=out_test); counter += 1
    print("sign(_MyNumber(-1)):",  sign(_MyNumber(-1)), file=out_test); counter += 1
    print("sign(_MyNumber(0)):",   sign(_MyNumber(0)), file=out_test); counter += 1
    print("sign(_MyNumber(1)):",   sign(_MyNumber(1)), file=out_test); counter += 1
    print("sign(_MyNumber(5.1)):", sign(_MyNumber(5.1)), file=out_test); counter += 1
    try:
        print("sign(_MyNumber(nan)):", sign(_MyNumber(nan)), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    new_test = '0 with keys, ' if _SST > 0 else ''
    print(f"\n{s_cnt:2} --- invalid number of positional arguments (0, {new_test}2, 3, 4)", file=out_test)
    try:
        print("sign():", sign(), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    if _SST > 0: # This test is for v1.1.0+ only
        try:
            print("sign(preprocess=lambda a: (float(a),), if_exc=None):",
                  sign(preprocess=lambda a: (float(a),), if_exc=None), file=out_test)
        except TypeError as e:
            print(f"- {e}", file=out_test)
        finally:
            counter += 1

    try:
        print("sign(-1, 0):", sign(-1, 0), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    try:
        print("sign(-1, 0, 1):", sign(-1, 0, 1), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    try:
        print("sign(-1, 0, 1, 4):", sign(-1, 0, 1, 4), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    try:
        print("sign(-1, 0, 1, 4, 5):", sign(-1, 0, 1, 4, 5), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    try:
        print("sign(5.0, code_shift=2):", sign(5.0, code_shift=2), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f'\n{s_cnt:2} --- ExplodingNumber, NotImplementedNumber', file=out_test)
    try:
        print("sign(_ExplodingNumber(-3.14):", sign(_ExplodingNumber(-3.14)), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    try:
        print("sign(_NotImplementedNumber(-3.14):", sign(_NotImplementedNumber(-3.14)), file=out_test)
    except TypeError as e:
        print(f"- {e}", file=out_test)
    finally:
        counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    s_cnt += 1; prev_counter = counter
    print(f"\n{s_cnt:2} --- inappropriate argument types (None, str, complex, list, set)", file=out_test)
    tests = [None, '5.0', 'nan', 'number 5', -1+1j, [-8.75], {-3.14},]
    for x in tests:
        try:
            print("sign({repr(x)}):", sign(x), file=out_test)
        except TypeError as e:
            print(f"- {e}", file=out_test)
        finally:
            counter += 1

    print(_trace(prev_counter, counter, s_cnt), file=out_test)

    # New options since version 1.1.0; skip these tests for v1.0.2

    if _SST > 0: # v1.1.0+
        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- preprocess key, simple argument replacement, string conversion', file=out_test)
        tests = ['5.0', 'nan', -18]
        for x in tests:
            try:
                print(f"sign({repr(x)}, "
                      f"preprocess=lambda a: (float(a),)):", sign(x, preprocess=lambda a: (float(a),)), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- preprocess key, argument replacement, treat small number as zero', file=out_test)
        tests = [-1, 0, -.187e-17, 5.0]
        for x in tests:
            print(f"sign({x}, "
                  f"preprocess=lambda a: (0 if abs(a) < _EPS else a,)):",
                  sign(x, preprocess=lambda a: (0 if abs(a) < _EPS else a,)), file=out_test); counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- preprocess key, replace only string argument, extract number from string', file=out_test)

        tests = [_PIRATES, 'Temperature is -.12e+02 °C', 'error', 123]
        for x in tests:
            try:
                print(f"sign({repr(x)}, "
                      f"preprocess=n_extract):", sign(x, preprocess=_n_extract), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- preprocess key, replace result, permits complex arguments', file=out_test)
        tests = [-1+1j, -18.4]

        for x in tests:
            try:
                print(f"sign({repr(x)}, "
                      f"preprocess=c_prep):", sign(x, preprocess=_c_prep), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f"\n{s_cnt:2} --- preprocess key, replace result, float result for 'float' and 'Decimal', sign recursion", file=out_test)
        tests = [-5, -5.0, Decimal(-5.5)]
        for x in tests:
            try:
                print(f"sign({repr(x)}, "
                      f"preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None):",
                      sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- preprocess key, replace result or argument, treat small number as zero differently', file=out_test)
        tests = [-1, 0, -.187e-17, 5.0]
        ppl = lambda x: (x, 0) if abs(x) < _EPS else (x,)
        for x in tests:
            print(f"sign({x}, preprocess=ppl):", sign(x, preprocess=ppl), file=out_test); counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f'\n{s_cnt:2} --- if_exc key (exception safety)', file=out_test)
        tests = [(None, '?'), ('5.0', '?'), ('nan', '?'), ('number 5', '?'),
                 (-1+1j, '?'), ([-8.75], '?'), ({-3.14}, '?'), # blocking exception, marked '?'
                 (-1, '!'), (31.4, '!'), (nan, '!'), (Fraction(-99, 19), '!'), (Decimal('101.78'), '!'),]                                              # valid nuneric types, marked '!'
        flag = 0
        repl = [None, -2, nan, None,]
        nrepl = len(repl)
        sp = ' '; quo = "'"
        for x, mark in tests:
            try:
                print(f"Type: {quo + type(x).__name__ + quo:10} {mark} "
                      f"sign({repr(x)}, "
                      f"if_exc=({repl[flag]},)):",
                      sign(x, if_exc=(repl[flag],)), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1
            flag = (flag + 1) % nrepl

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

        s_cnt += 1; prev_counter = counter
        print(f"\n{s_cnt:2} --- both preprocess and if_exc key", file=out_test)
        tests = [-5, -5.0, Decimal(-5.5), 'error']
        for x in tests:
            try:
                print(f"sign({repr(x)}, "
                      f"preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None, "
                      f"if_exc=(None,)):",
                      sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None, if_exc=(None,)), file=out_test)
            except TypeError as e:
                print(f"- {e}", file=out_test)
            finally:
                counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)

    # New options since version 1.2.0; skip these tests for v1.0.2, v1.1.0+

    if _SST > 1: # v1.2.0+
        s_cnt += 1; prev_counter = counter
        print(f"\n{s_cnt:2} --- codeshift and key combinations", file=out_test)
        tests = ['error', -5, 0, 5, nan]
        for x in tests:
            print(f"sign({repr(x)}, codeshift=2):",
                  sign(x, codeshift=2), file=out_test); counter += 1
        print('   ---', file=out_test)
        for x in tests:
            print(f"sign({repr(x)}, if_exc=(13,), codeshift=2):",
                  sign(x, if_exc=(13,), codeshift=2), file=out_test); counter += 1
        print('   ---', file=out_test)
        tests = ['error', -1, 0, -.187e-17, 5.0]
        for x in tests:
            print(f"sign({repr(x)}, "
                  f"preprocess=lambda a: (0 if abs(a) < _EPS else a,), codeshift=2):",
                  sign(x, preprocess=lambda a: (0 if abs(a) < _EPS else a,), codeshift=2),
                  file=out_test); counter += 1
        print('   ---', file=out_test)
        tests = ['error', -5.0, 0.0, 0, 5, nan]
        for x in tests:
            print(f"sign({repr(x)}, "
                  f"preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, "
                  f"codeshift=1):",
                  sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1), file=out_test); counter += 1
        print('   ---', file=out_test)
        for x in tests:
            print(f"sign({repr(x)}, "
                  f"preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, "
                  f"if_exc=(13,), codeshift=1):",
                  sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1), file=out_test); counter += 1

        print(_trace(prev_counter, counter, s_cnt), file=out_test)


    if start_time is None: # The very first pass to warm Python
        start_time = time.perf_counter()
        # Block printing
        out_test = open_devnull()

# Finalize out_test
close_devnull(out_test)
out_test = None

print(f'\n{success(counter, s_cnt=s_cnt, start_time=start_time, passes=MAX_PASSES)}')

# Restore stdout and stderr
outflows.reset_from_utf8()
