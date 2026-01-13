/*
 * signum.cpp
 * High-performance, versatile implementation of the universal 'sign' function for Python
 * Version: 1.2.1 ⊙ Gold Edition
 * Released: January 5, 2026
 * Copyright (c) 2025-2026 Alexandru Colesnicov
 * License: MIT
 */

#include <Python.h>

/* Static objects for keywords (argument names) and for Python 'int(0)' */
static PyObject *kw_if_exc     = NULL;
static PyObject *kw_preprocess = NULL;
static PyObject *kw_codeshift  = NULL;
static PyObject *Py_zero       = NULL;

/* Clearing at module  */
static void signum_free(void *m) {
    Py_XDECREF(kw_if_exc);
    Py_XDECREF(kw_preprocess);
    Py_XDECREF(kw_codeshift);
    Py_XDECREF(Py_zero);
}

static PyObject *signum_sign(PyObject *self, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames)
{
    /* Check positional arguments */
    if (nargs != 1) {
        PyErr_Format(PyExc_TypeError, "signum.sign() takes 1 positional argument but %zd were given", nargs);
        return NULL;
    }

    PyObject *x          = args[0];
    PyObject *if_exc     = Py_None;
    PyObject *preprocess = Py_None;
    int no_codeshift = 1;
    long c_codeshift = 0;

    /* Optimization: Tell the compiler that 'no_codeshift' is strictly 0 or 1 */
    #if __has_cpp_attribute(assume)
        [[assume((no_codeshift == 0) || (no_codeshift == 1))]];
    #elif defined(_MSC_VER)
        __assume((no_codeshift == 0) || (no_codeshift == 1));
    #elif defined(__GNUC__) || defined(__clang__)
        if (!((no_codeshift == 0) || (no_codeshift == 1))) __builtin_unreachable();
    #endif

    /* Parse keyword-only arguments using interned strings */
    if (kwnames != NULL) {
        Py_ssize_t nkwargs = PyTuple_GET_SIZE(kwnames);
        for (Py_ssize_t i = 0; i < nkwargs; i++) {
            PyObject *key = PyTuple_GET_ITEM(kwnames, i);
            PyObject *val = args[1 + i];

            if (key == kw_codeshift) {
                /* Convert to 'long' without checking */
                c_codeshift = PyLong_AsLong(val);
                if (c_codeshift == -1 && PyErr_Occurred()) return NULL;
                no_codeshift = 0;
            } else if (key == kw_if_exc) {
                if_exc = val;
            } else if (key == kw_preprocess) {
                preprocess = val;
            } else {
                PyErr_Format(PyExc_TypeError, "signum.sign() got an unexpected keyword argument '%U'", key);
                return NULL;
            }
        }
    }

    /* preprocess */
    PyObject *to_free = NULL;
    if (preprocess != Py_None) { /* 'preprocess' argument exists, call it without checking */
        PyObject *ppres = PyObject_CallFunctionObjArgs(preprocess, x, NULL);
        if (ppres == NULL) { /* Error inside 'preprocess(x)': ignore */
            PyErr_Clear();
        } else {
            if (PyTuple_Check(ppres)) { /* 'ppres' is a tuple */
                Py_ssize_t t_size = PyTuple_Size(ppres);

                /* Optimization: Tell the compiler that 'tsize' >= 0 */
                #if __has_cpp_attribute(assume)
                    [[assume(0 <= t_size)]];
                #elif defined(_MSC_VER)
                    __assume(0 <= t_size);
                #elif defined(__GNUC__) || defined(__clang__)
                    if (t_size < 0) __builtin_unreachable();
                #endif

                switch (t_size) {
                    case 0: break; /* Ignore the empty tuple */
                    case 1: {      /* Replace argument */
                        PyObject *item0 = PyTuple_GetItem(ppres, 0);
                        Py_INCREF(item0);
                        x = item0;
                        to_free = item0;
                        break;
                    }
                    default: {     /* 't_size' > 1: replace result */
                        PyObject *item1 = PyTuple_GetItem(ppres, 1);
                        Py_INCREF(item1);
                        Py_DECREF(ppres);
                        return item1;
                    }
                }
            }
            Py_DECREF(ppres);
        }
    }

    /* Check for numeric NaN */
    double d = PyFloat_AsDouble(x);
    if (Py_IS_NAN(d)) {
        Py_XDECREF(to_free);
        switch (no_codeshift) {
            case 0: return PyLong_FromLong(c_codeshift + 2); /* +2 is numeric code for NaN */
            case 1: return PyFloat_FromDouble(Py_NAN);
        }
    }
    /* If it is something special, we will nevertheless try comparisons */
    if (PyErr_Occurred()) PyErr_Clear();

    /* Start of the ternary logic block */
    int gt, lt, eq, stat_idx, self_eq;
    long res;

    gt = PyObject_RichCompareBool(x, Py_zero, Py_GT) + 1; /* 0: Error; 1: False; 2: True */
    stat_idx = gt;

    lt = PyObject_RichCompareBool(x, Py_zero, Py_LT) + 1;
    res = (long)gt - lt; /* Result, if nothing special */

    /* Optimization: Tell the compiler that 'lt' is strictly within [0, 2] */
    #if __has_cpp_attribute(assume)
        [[assume(0 <= lt && lt <= 2)]];
    #elif defined(_MSC_VER)
        __assume(0 <= lt && lt <= 2);
    #elif defined(__GNUC__) || defined(__clang__)
        if (!(0 <= lt && lt <= 2)) __builtin_unreachable();
    #endif

    switch (lt) {
        case 0: goto error;
        case 1: break; /* 'stat_idx == gt' is mutiplied by 'lt == 1' */
        case 2: stat_idx = (stat_idx << 1) & 3; /* 'stat_idx == gt' is shift-mutiplied by 'lt == 2'
                                                    and truncated mod 4 */
    }

    eq = PyObject_RichCompareBool(x, Py_zero, Py_EQ) + 1; /* Used only to process NaN and errors */

    #if __has_cpp_attribute(assume)
        [[assume(0 <= eq && eq <= 2)]];
    #elif defined(_MSC_VER)
        __assume(0 <= eq && eq <= 2);
    #elif defined(__GNUC__) || defined(__clang__)
        if (!(0 <= eq && eq <= 2)) __builtin_unreachable();
    #endif

    switch (eq) {
        case 0: goto error;
        case 1: break; /* 'stat_idx == (gt * lt) & 3' is mutiplied by 'eq == 1' */
        case 2: stat_idx = (stat_idx << 1) & 3; /* 'stat_idx == (gt * lt) & 3' is shift-mutiplied by 'eq == 2'
                                                   and truncated mod 4 */
    }

    /* Short Logic Overview:
       - 'stat_idx == 0': Multiple 'True' flags or an error occurred. Maps to 0, 4, 8; this is 0 mod 4.
       - 'stat_idx == 1': Triple 'False' state (1,1,1). Potential NaN; requires self-comparison.
       - 'stat_idx == 2': Exactly one 'True' flag, no errors. Valid numeric state.
    */

    /* Detailed Logic Overview:
       'gt', 'lt', 'eq' can be 0 for 'Error', 1 for 'False', 2 for 'True' (ternary logic).
       'stat_idx = (gt*lt*eq) & 3'; equivalent is '(gt*lt*eq) % 4'.
       'stat_idx' is 0:
         - if we have one, two, or three errors; then the product is 0;
           (we already processed errors in 'lt' or 'eq' directly by 'goto error;');
         - if we have two 'True' and one 'False', or three 'True'; the product is 4 or 8,
              which gives 0 (mod 4).
       'stat_idx' is 1:
         - if we have triple 'False', that indicates a potential NaN, and we perform
           an additional self-comparison;
       'stat_idx' is 2:
         - only if we have one 'True' and two 'False': it's a valid number */

    #if __has_cpp_attribute(assume)
        [[assume(0 <= stat_idx && stat_idx <= 2)]];
    #elif defined(_MSC_VER)
        __assume(0 <= stat_idx && stat_idx <= 2);
    #elif defined(__GNUC__) || defined(__clang__)
        if (!(0 <= stat_idx && stat_idx <= 2)) __builtin_unreachable();
    #endif

    switch (stat_idx) {
        case 0: goto error;
        case 1: { /* possible NaN '(False, False, False)' */
            self_eq = PyObject_RichCompareBool(x, x, Py_EQ);

            #if __has_cpp_attribute(assume)
                [[assume(-1 <= self_eq && self_eq <= 1)]];
            #elif defined(_MSC_VER)
                __assume(-1 <= self_eq && self_eq <= 1);
            #elif defined(__GNUC__) || defined(__clang__)
                if (!(-1 <= self_eq && self_eq <= 1)) __builtin_unreachable();
            #endif

            switch (self_eq) {
                case -1: { /* Error in __eq__, we keep current Python error */
                    Py_XDECREF(to_free);
                    return NULL;
                }
                case  0: { /* NaN: not equal to itself */
                    Py_XDECREF(to_free);
                    switch (no_codeshift) {
                        case 0: return PyLong_FromLong(c_codeshift + 2); /* +2 is numeric code for NaN */
                        case 1: return PyFloat_FromDouble(Py_NAN);
                    }
                }
                case  1: goto error; /* Not a NaN: equals to itself; not comparable to 0 */
            }
        }
        case 2: {
            Py_XDECREF(to_free);
            return PyLong_FromLong(res + c_codeshift);
        }
    }
    goto error;

error:

    if (if_exc != Py_None) { /* 'if_exc' argument exists, return its 0th element instead of error */
        PyErr_Clear();
        PyObject *item = PyTuple_GetItem(if_exc, 0); /* We don't check 'if_exc' that should be tuple */
        Py_INCREF(item);
        Py_XDECREF(to_free);
        return item;
    }

    switch (no_codeshift) {
        case 0: {
            PyErr_Clear();
            return PyLong_FromLong(c_codeshift - 2); /* -2 is numeric stat_idx for detectable error */
        }
        case 1: break;
    }

    if (PyErr_Occurred()) {
        PyObject *type, *value, *traceback;
        /* Extract the current error */
        PyErr_Fetch(&type, &value, &traceback);
        PyErr_NormalizeException(&type, &value, &traceback);

        /* Prepare the argument details */
        PyObject *repr = PyObject_Repr(x);
        const char *type_name = Py_TYPE(x)->tp_name;

        /* Prepare the old error as string */
        PyObject *old_msg = PyObject_Str(value);
        const char *old_msg_str = old_msg ? PyUnicode_AsUTF8(old_msg) : "unknown error";

        /* Format the new message */
        PyErr_Format(PyExc_TypeError,
            "signum.sign: invalid argument `%.160s` (type '%.80s'). "
            "Inner error: %.320s",
            repr ? PyUnicode_AsUTF8(repr) : "???",
            type_name,
            old_msg_str);

        /* Clean memory */
        Py_XDECREF(repr);
        Py_XDECREF(old_msg);
        Py_XDECREF(type);
        Py_XDECREF(value);
        Py_XDECREF(traceback);
    }
    else {
        PyObject *repr = PyObject_Repr(x);
        const char *type_name = Py_TYPE(x)->tp_name;

        if (repr) {
            PyErr_Format(PyExc_TypeError,
                "signum.sign: invalid argument `%.160s`. "
                "Type '%.80s' does not support order comparisons (>, <, ==) "
                "or NaN detection.",
                PyUnicode_AsUTF8(repr),
                type_name);
            Py_DECREF(repr);
        }
        else {
            PyErr_Format(PyExc_TypeError,
                "signum.sign: invalid argument of type '%.80s', "
                "which does not support order comparisons (>, <, ==) and printing.",
                type_name);
        }
    }
    Py_XDECREF(to_free);
    return NULL;
}

/* --- FORMALITIES --- */

/* List of implemented methods */
static PyMethodDef SignumMethods[] = {
    {"sign", (PyCFunction)signum_sign, METH_FASTCALL | METH_KEYWORDS, "Return the sign of x: -1, 0, 1, or NaN."},
    {NULL, NULL, 0, NULL} /* Stop-string */
};

/* Module description */
static struct PyModuleDef signummodule = {
    PyModuleDef_HEAD_INIT,
    "signum",
    "High-performance sign function for Python.",
    -1,
    SignumMethods,
    NULL, NULL, NULL,
    signum_free
};

/* Module initialization */
PyMODINIT_FUNC PyInit_signum(void) {
    PyObject *m = PyModule_Create(&signummodule);
    if (m == NULL) return NULL;

    /* Create interned strings */
    kw_if_exc     = PyUnicode_InternFromString("if_exc");
    kw_preprocess = PyUnicode_InternFromString("preprocess");
    kw_codeshift  = PyUnicode_InternFromString("codeshift");

    /* Create static Pyhtonic int(0) */
    Py_zero = PyLong_FromLong(0);

    if (!kw_if_exc || !kw_preprocess || !kw_codeshift || !Py_zero) {
        return NULL; /* No memory */
    }

    /* Adding attribute 'signum.__version__' */
    PyModule_AddStringConstant(m, "__version__", "1.2.1");
    return m;
}
