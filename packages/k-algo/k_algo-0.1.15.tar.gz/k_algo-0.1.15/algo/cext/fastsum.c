#define PY_SSIZE_T_CLEAN
#include <Python.h>

/*
 * fast_sum(iterable) -> float
 * 對可迭代的數值元素求和；元素會以 PyFloat_AsDouble() 轉成 double。
 */
static PyObject* fast_sum(PyObject* self, PyObject* args) {
    PyObject* iterable = NULL;
    if (!PyArg_ParseTuple(args, "O", &iterable)) {
        return NULL;
    }

    // 將任意可迭代轉為 sequence，便於 O(1) 索引與快速走訪
    PyObject* seq = PySequence_Fast(iterable, "argument must be iterable");
    if (!seq) {
        return NULL;  // 會帶著 TypeError
    }

    Py_ssize_t n = PySequence_Fast_GET_SIZE(seq);
    PyObject** items = PySequence_Fast_ITEMS(seq);

    double total = 0.0;
    for (Py_ssize_t i = 0; i < n; i++) {
        double v = PyFloat_AsDouble(items[i]);
        if (PyErr_Occurred()) {
            Py_DECREF(seq);
            return NULL;  // 非數值時 PyFloat_AsDouble 會設錯
        }
        total += v;
    }

    Py_DECREF(seq);
    return PyFloat_FromDouble(total);
}

static PyMethodDef FastsumMethods[] = {
    {"fast_sum", fast_sum, METH_VARARGS, "Sum numbers in an iterable as float."},
    {NULL, NULL, 0, NULL}
};

// 模組名需與最末段 "fastsum" 一致（algo.cext.fastsum）
static struct PyModuleDef fastsummodule = {
    PyModuleDef_HEAD_INIT,
    "fastsum",
    "Fast sum C extension",
    -1,
    FastsumMethods
};

PyMODINIT_FUNC PyInit_fastsum(void) {
    return PyModule_Create(&fastsummodule);
}
