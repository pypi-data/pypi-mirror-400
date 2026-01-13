from signum import sign
from testing import get_passes, set_high_priority, success, OutputUTF8
from testing import MyNumber as _MyNumber, ExplodingNumber as _ExplodingNumber, NotImplementedNumber as _NotImplementedNumber

from decimal import Decimal
from fractions import Fraction
from math import nan, inf
import sympy
import time

MAX_PASSES = get_passes(__file__)

# Switch sys.stdout and sys.stderr to 'utf-8' encoding
outflows = OutputUTF8()
outflows.set_utf8()

start_time = None

print(f'***** Test: {__file__}')
print(f'MAX_PASSES: {MAX_PASSES}')
print(f'*** {set_high_priority()} ***\n')
for _ in range(MAX_PASSES + 1):
    (sign(-5))
    (sign(-1))
    (sign(0))
    (sign(1))
    (sign(5))
    (sign(True))
    (sign(False))
    (sign(10**1000))
    (sign(-10**1000))
    (sign(10**1000-10**1000))
    (sign(-5.0))
    (sign(-1.0))
    (sign(0.0))
    (sign(1.0))
    (sign(5.0))
    (sign(float('-0.0')))
    (sign(float('+0.0')))
    (sign(-inf))
    (sign(inf))
    (sign(float('-nan')))
    (sign(nan))
    (sign(0.0*nan))
    (sign(Fraction(-5, 2)))
    (sign(Fraction(-1, 2)))
    (sign(Fraction(0, 2)))
    (sign(Fraction(1, 2)))
    (sign(Fraction(5, 2)))
    (sign(Decimal(-5.5)))
    (sign(Decimal(-1.5)))
    (sign(Decimal(0.0)))
    (sign(Decimal(1.5)))
    (sign(Decimal(5.5)))
    (sign(Decimal('NaN')))
    x_sym = sympy.Symbol('x')
    expr = x_sym
    val = expr.subs(x_sym, -3.14)
    (sign(val))
    (sign(sympy.Rational(3, 4)))
    (sign(sympy.nan))
    (sign(_MyNumber(-5)))
    (sign(_MyNumber(-1)))
    (sign(_MyNumber(0)))
    (sign(_MyNumber(1)))
    (sign(_MyNumber(5.1)))
    try:
        (sign(_MyNumber(nan)))
    except TypeError as e:
        (e)
    try:
        (sign())
    except TypeError as e:
        (e)
    try:
        (sign(-1, 0))
    except TypeError as e:
        (e)
    try:
        (sign(-1, 0, 1))
    except TypeError as e:
        (e)
    try:
        (sign(-1, 0, 1, 4))
    except TypeError as e:
        (e)
    try:
        (sign(-1, 0, 1, 4, 5))
    except TypeError as e:
        (e)
    try:
        (sign(5.0, code_shift=2))
    except TypeError as e:
        (e)
    try:
        (sign(_ExplodingNumber(-3.14)))
    except TypeError as e:
        (e)
    try:
        (sign(_NotImplementedNumber(-3.14)))
    except TypeError as e:
        (e)
    tests = [None, '5.0', 'nan', 'number 5', -1+1j, [-8.75], {-3.14},]
    for x in tests:
        try:
            (sign(x))
        except TypeError as e:
            (e)

    if start_time is None: # The very first pass to warm Python
        start_time = time.perf_counter()

print(f'{success(57, s_cnt=None, start_time=start_time, passes=MAX_PASSES)}\n')

# Restore stdout and stderr
outflows.reset_from_utf8()
