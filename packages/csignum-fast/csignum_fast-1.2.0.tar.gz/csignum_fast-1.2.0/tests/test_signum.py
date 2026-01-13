from signum import sign

from testing import EPS, PIRATES, n_extract, c_prep, \
                    MyNumber, ExplodingNumber, NotImplementedNumber, trace, success, OutputUTF8

from decimal import Decimal
from fractions import Fraction
from math import nan, isnan, inf
import sympy
import unittest

class TestSignum(unittest.TestCase):

    def test_sign(self):
        self.buffer = []
        s_cnt = 0
        counter = 0
        # --- int
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(-5), -1); counter += 1
        self.assertEqual(sign(-1), -1); counter += 1
        self.assertEqual(sign(0), 0); counter += 1
        self.assertEqual(sign(1), 1); counter += 1
        self.assertEqual(sign(5), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="'int'"))

        # ------ bool
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(True), 1); counter += 1
        self.assertEqual(sign(False), 0); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="'bool'"))

        # ------ big numbers
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(10**1000), 1); counter += 1
        self.assertEqual(sign(-10**1000), -1); counter += 1
        self.assertEqual(sign(10**1000-10**1000), 0); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="big 'int'"))

        # --- float
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(-5.0), -1); counter += 1
        self.assertEqual(sign(-1.0), -1); counter += 1
        self.assertEqual(sign(0.0), 0); counter += 1
        self.assertEqual(sign(1.0), 1); counter += 1
        self.assertEqual(sign(5.0), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="'float'"))

        # ------ -0.0 and +0.0
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(float('-0.0')), 0); counter += 1
        self.assertEqual(sign(float('+0.0')), 0); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="±0.0"))

        # ------ -inf and inf
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(-inf), -1); counter += 1
        self.assertEqual(sign(inf), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="infinity"))

        # ------ -nan (the same as nan), nan
        s_cnt += 1; prev_counter = counter
        self.assertTrue(isnan(sign(float('-nan')))); counter += 1
        self.assertTrue(isnan(sign(nan))); counter += 1
        self.assertTrue(isnan(sign(0.0*nan))); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="NaN"))

        # --- Fraction
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(Fraction(-5, 2)), -1); counter += 1
        self.assertEqual(sign(Fraction(-1, 2)), -1); counter += 1
        self.assertEqual(sign(Fraction(0, 2)), 0); counter += 1
        self.assertEqual(sign(Fraction(1, 2)), 1); counter += 1
        self.assertEqual(sign(Fraction(5, 2)), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="'Fraction'"))

        # --- Decimal
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(Decimal(-5.5)), -1); counter += 1
        self.assertEqual(sign(Decimal(-1.5)), -1); counter += 1
        self.assertEqual(sign(Decimal(0.0)), 0); counter += 1
        self.assertEqual(sign(Decimal(1.5)), 1); counter += 1
        self.assertEqual(sign(Decimal(5.5)), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="'Decimal'"))

        # ------ Decimal NaN
        s_cnt += 1; prev_counter = counter
        self.assertTrue(isnan(sign(Decimal('NaN')))); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="Decimal NaN"))

        # --- sympy
        x_sym = sympy.Symbol('x')
        expr = x_sym
        val = expr.subs(x_sym, -3.14)
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(val), -1); counter += 1
        self.assertEqual(sign(sympy.Rational(3, 4)), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="sympy"))

        # ------ sympy.nan
        s_cnt += 1; prev_counter = counter
        self.assertTrue(isnan(sign(sympy.nan))); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="sympy.nan"))

        # --- New custom class (testing possible future extentions)
        #     This class has no __float__ that tests one subtle branch in the C++ code
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(MyNumber(-5)), -1); counter += 1
        self.assertEqual(sign(MyNumber(-1)), -1); counter += 1
        self.assertEqual(sign(MyNumber(0)), 0); counter += 1
        self.assertEqual(sign(MyNumber(1)), 1); counter += 1
        self.assertEqual(sign(MyNumber(5)), 1); counter += 1
        with self.assertRaisesRegex(TypeError, r'signum\.sign: invalid argument `MyNumber\(nan\)`'):
            sign(MyNumber(nan))
        counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="new custom class"))

        # Testing inappropriate arguments and types (non-scalar, non-comparable, etc.)

        # --- Invalid number of positional arguments (0, 0 with keys, 2, 3, 4, 5); invalid keyword
        s_cnt += 1; prev_counter = counter
        with self.assertRaisesRegex(TypeError, r"signum.sign\(\) takes 1 positional argument but 0 were given"):
            sign()
        counter += 1
        with self.assertRaisesRegex(TypeError, r"signum.sign\(\) takes 1 positional argument but 0 were given"):
            sign(preprocess=lambda a: (float(a),), if_exc=None)
        counter += 1
        with self.assertRaisesRegex(TypeError, r'signum.sign\(\) takes 1 positional argument but 2 were given'):
            sign(-1, 0)
        counter += 1
        with self.assertRaisesRegex(TypeError, r'signum.sign\(\) takes 1 positional argument but 3 were given'):
            sign(-1, 0, 1)
        counter += 1
        with self.assertRaisesRegex(TypeError, r'signum.sign\(\) takes 1 positional argument but 4 were given'):
            sign(-1, 0, 1, 4)
        counter += 1
        with self.assertRaisesRegex(TypeError, r'signum.sign\(\) takes 1 positional argument but 5 were given'):
            sign(-1, 0, 1, 4, 5)
        counter += 1
        with self.assertRaisesRegex(TypeError, r"signum.sign\(\) got an unexpected keyword argument 'code_shift'"):
            sign(5.0, code_shift=2)
        counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="invalid number of arguments"))

        # --- ExplodingNumber, NotImplementedNumber
        s_cnt += 1; prev_counter = counter
        with self.assertRaisesRegex(TypeError, r'signum.sign: invalid argument `ExplodingNumber\(-3\.14\)`'):
            sign(ExplodingNumber(-3.14))
        counter += 1
        with self.assertRaisesRegex(TypeError, r'signum.sign: invalid argument `NotImplementedNumber\(-3\.14\)`'):
            sign(NotImplementedNumber(-3.14))
        counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="Exploding and Not Implemented numbers"))

        # --- None, str, complex, list, set
        tests = [(r"`None`", None), (r"`'5\.0'`", '5.0'), (r"`'nan'`", 'nan'),
                 (r"`'number 5'`", 'number 5'), (r"`\(-1\+1j\)`", -1+1j), (r"`\[-8\.75\]`", [-8.75]),
                 (r"`\{-3\.14\}`", {-3.14}),
                ]

        s_cnt += 1; prev_counter = counter
        for msg, obj in tests:
            with self.subTest(obj=obj):
                with self.assertRaisesRegex(TypeError,
                                            r'signum\.sign: invalid argument ' + msg):
                    sign(obj)
                counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="inappropriate types"))

        ## Testing additional key arguments (preprocess=, is_exc=, both, codeshift=, combinations)

        # --- preprocess key, simple argument replacement, string conversion
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign('5.0', preprocess=lambda a: (float(a),)), 1); counter += 1
        self.assertTrue(isnan(sign('nan', preprocess=lambda a: (float(a),)))); counter += 1
        self.assertEqual(sign(-18, preprocess=lambda a: (float(a),)), -1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess with simple str replacement"))

        # --- preprocess key, argument replacement, treat small number as zero
        s_cnt += 1; prev_counter = counter
        tests = [(-1, -1), (0, 0), (-.187e-17, 0), (5.0, 1)]
        for x, y in tests:
            self.assertEqual(sign(x, preprocess=lambda a: (0 if abs(a) < EPS else a,)), y);  counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess treating small number as zero"))

        # --- preprocess key, replace only string argument, extract number from string
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign(PIRATES, preprocess=n_extract), 1); counter += 1
        self.assertEqual(sign('Temperature is -.12e+02 °C', preprocess=n_extract), -1); counter += 1
        with self.assertRaisesRegex(TypeError, r"signum.sign: invalid argument `'error'` \(type 'str'\)"):
            sign('error', preprocess=n_extract)
        counter += 1
        self.assertEqual(sign(123, preprocess=n_extract), 1); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess extracting numbers from str"))

        # --- preprocess key, replace result, permits complex arguments
        s_cnt += 1; prev_counter = counter
        tests = [(-1+1j, '(-0.7071067811865475+0.7071067811865475j)'), (-18.4, '-1')]
        for x, y in tests:
            self.assertEqual(str(sign(x, preprocess=c_prep)), y); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess permitting complex arguments"))

        # --- preprocess key, replace result, float result for 'float' and 'Decimal', sign recursion
        s_cnt += 1; prev_counter = counter
        tests = [(-5, -1, int), (-5.0, -1.0, float), (Decimal(-5.5), -1.0, float)]
        for x, y, t in tests:
            self.assertEqual((s := sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None)), y)
            self.assertIsInstance(s, t); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess with float result and sign recursion"))

        # --- preprocess key, replace result or argument, treat small number as zero differently
        s_cnt += 1; prev_counter = counter
        tests = [(-1, -1), (0, 0), (-.187e-17, 0), (5.0, 1)]
        ppl = lambda x: (x, 0) if abs(x) < EPS else (x,)
        for x, y in tests:
            self.assertEqual(sign(x, preprocess=ppl), y); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="preprocess replacing result or argument"))

        # --- if_exc key (exception safety)
        s_cnt += 1; prev_counter = counter
        tests = [(None, 'None'), ('5.0', '-2'), ('nan', 'nan'), ('number 5', 'None'),
                 (-1+1j, 'None'), ([-8.75], '-2'), ({-3.14}, 'nan'), # blocking exceptions
                 (-1, '-1'), (31.4, '1'), (nan, 'nan'), (Fraction(-99, 19), '-1'), (Decimal('101.78'), '1'),]                                              # valid nuneric types
        flag = 0
        repl = [None, -2, nan, None,]
        nrepl = len(repl)
        for x, y in tests:
            self.assertEqual(repr(sign(x, if_exc=(repl[flag],))), y); counter += 1
            flag = (flag + 1) % nrepl
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="if_exc key"))

        # --- both preprocess and if_exc key
        s_cnt += 1; prev_counter = counter
        tests = [(-5, '-1', int), (-5.0, '-1.0', float),
                 (Decimal(-5.5), '-1.0', float), ('error', 'None', type(None))]
        for x, y, t in tests:
            self.assertEqual(str(s := sign(x, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, (float, Decimal)) else None, if_exc=(None,))), y)
            self.assertIsInstance(s, t); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="both preprocess and if_exc"))

        # codeshift and combinations
        s_cnt += 1; prev_counter = counter
        self.assertEqual(sign('error', codeshift=2), 0); counter += 1
        self.assertEqual(sign(-5, codeshift=2), 1); counter += 1
        self.assertEqual(sign(0, codeshift=2), 2); counter += 1
        self.assertEqual(sign(5, codeshift=2), 3); counter += 1
        self.assertEqual(sign(nan, codeshift=2), 4); counter += 1
        self.assertEqual(sign('error', if_exc=(13,), codeshift=2), 13); counter += 1
        self.assertEqual(sign(-5, if_exc=(13,), codeshift=2), 1); counter += 1
        self.assertEqual(sign(0, if_exc=(13,), codeshift=2), 2); counter += 1
        self.assertEqual(sign(5, if_exc=(13,), codeshift=2), 3); counter += 1
        self.assertEqual(sign(nan, if_exc=(13,), codeshift=2), 4); counter += 1
        self.assertEqual(sign('error', preprocess=lambda a: (0 if abs(a) < EPS else a,), codeshift=2), 0); counter += 1
        self.assertEqual(sign(-1, preprocess=lambda a: (0 if abs(a) < EPS else a,), codeshift=2), 1); counter += 1
        self.assertEqual(sign(0, preprocess=lambda a: (0 if abs(a) < EPS else a,), codeshift=2), 2); counter += 1
        self.assertEqual(sign(-1.87e-18, preprocess=lambda a: (0 if abs(a) < EPS else a,), codeshift=2), 2); counter += 1
        self.assertEqual(sign(5.0, preprocess=lambda a: (0 if abs(a) < EPS else a,), codeshift=2), 3); counter += 1
        self.assertEqual(sign('error', preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1), -1); counter += 1
        self.assertEqual((s := sign(-5.0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1)), -1.0)
        self.assertIsInstance(s, float); counter += 1
        self.assertEqual((s := sign(0.0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1)), 0.0)
        self.assertIsInstance(s, float); counter += 1
        self.assertEqual(sign(0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1), 1); counter += 1
        self.assertEqual(sign(5, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1), 2); counter += 1
        self.assertTrue(isnan(sign(nan, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, codeshift=1))); counter += 1
        self.assertEqual(sign('error', preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1), 13); counter += 1
        self.assertEqual((s := sign(-5.0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1)), -1.0)
        self.assertIsInstance(s, float); counter += 1
        self.assertEqual((s := sign(0.0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1)), 0.0)
        self.assertIsInstance(s, float); counter += 1
        self.assertEqual(sign(0, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1), 1); counter += 1
        self.assertEqual(sign(5, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1), 2); counter += 1
        self.assertTrue(isnan(sign(nan, preprocess=lambda a: (a, float(sign(a))) if isinstance(a, float) else None, if_exc=(13,), codeshift=1))); counter += 1
        self.buffer.append(trace(prev_counter, counter, s_cnt, what="codeshift and key combinations"))

        self.buffer.append(f'\n{success(counter, s_cnt=s_cnt)}\n')
        print('\n'.join(self.buffer), flush=True)

if __name__ == '__main__':
    # Switch sys.stdout and sys.stderr to 'utf-8' encoding
    outflows = OutputUTF8()
    outflows.set_utf8()

    print(f'***** Test: {__file__}\n', flush=True)
    unittest.main()

    # Restore stdout and stderr
    outflows.reset_from_utf8()
