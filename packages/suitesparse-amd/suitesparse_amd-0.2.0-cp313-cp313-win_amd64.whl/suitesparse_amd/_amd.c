#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <math.h>

#include "amd.h"


static inline int is_nonzero_finite(const Py_buffer *view, const char *ptr) {
    // Check format type, handling for NULL
    const char *fmt = view->format ? view->format : "B";
    const char type = strchr("@<>!=", fmt[0]) && fmt[1] ? fmt[1] : fmt[0];

    if (type == 'f') {
        float v;
        memcpy(&v, ptr, sizeof(v));

        if (!isfinite(v)) {
            return -1;
        }

        return v != 0.0f;
    }
    if (type == 'd') {
        double v;
        memcpy(&v, ptr, sizeof(v));

        if (!isfinite(v)) {
            return -1;
        }

        return v != 0.0;
    }

    // Handles all integer types, all integers have all-zero bytes
    const char *end = ptr + view->itemsize;
    while (ptr < end) {
        if (*ptr++) return 1;
    }

    return 0;
}

static inline int copy_array(const int32_t *array, const size_t size, PyObject *list) {
    for (size_t i = 0; i < size; i++) {
        PyObject *idx = PyLong_FromLong(array[i]);

        if (!idx) {
            return 0;
        }

        PyList_SET_ITEM(list, i, idx);
    }

    return 1;
}

static inline int copy_arrayd(const double *array, const size_t size, PyObject *list) {
    for (size_t i = 0; i < size; i++) {
        PyObject *data = PyLong_FromDouble(array[i]);

        if (!data) {
            return 0;
        }

        PyList_SET_ITEM(list, i, data);
    }

    return 1;
}

static inline PyObject *_numpy_array(PyObject *obj, int verbose, int aggressive, double dense) {
    Py_buffer view;
    if (PyObject_GetBuffer(obj, &view, PyBUF_FORMAT | PyBUF_STRIDED | PyBUF_ND) == -1) {
        return NULL;
    }

    if (view.ndim != 2) {
        PyErr_SetString(PyExc_ValueError, "Expected 2 dimensional arrays");
        PyBuffer_Release(&view);
        return NULL;
    }

    const Py_ssize_t rows = view.shape[0];
    const Py_ssize_t cols = view.shape[1];

    if (rows != cols) {
        PyErr_SetString(PyExc_ValueError, "Expected a square matrix with equal number of rows and columns");
        goto fail;
    }

    const int32_t n = (int32_t) rows;

    const char *data = view.buf;
    int32_t count = 0;

    int32_t *Ap = PyMem_Calloc(rows + 1, sizeof(int32_t));
    if (!Ap) {
        PyErr_NoMemory();
        goto fail;
    }
    Ap[0] = 0;

    for (Py_ssize_t i = 0; i < rows; i++) {
        for (Py_ssize_t j = 0; j < cols; j++) {
            const char *ptr = data + i * view.strides[0]
                              + j * view.strides[1];

            const int nonzero_flag = is_nonzero_finite(&view, ptr);

            if (nonzero_flag == -1) {
                PyErr_SetString(PyExc_ValueError, "Unsupported dtype or NaN/Inf encountered");
                goto fail;
            }

            if (nonzero_flag) {
                ++count;
            }
        }

        Ap[i + 1] = count;
    }

    int32_t *Ai = PyMem_Calloc(count, sizeof(int32_t));
    if (!Ai) {
        PyErr_NoMemory();
        goto fail;
    }

    size_t index = 0;

    for (Py_ssize_t i = 0; i < rows; i++) {
        for (Py_ssize_t j = 0; j < cols; j++) {
            const char *ptr = data + i * view.strides[0]
                              + j * view.strides[1];

            const int nonzero_flag = is_nonzero_finite(&view, ptr);

            if (nonzero_flag == -1) {
                PyErr_SetString(PyExc_ValueError, "Unsupported dtype or NaN/Inf encountered");
                goto fail;
            }

            if (nonzero_flag) {
                Ai[index++] = (int32_t) j;
            }

            if (index >= count) {
                goto loop_exit;
            }
        }
    }

loop_exit:


    int *version = PyMem_Calloc(3, sizeof(int));
    if (!version) {
        PyErr_NoMemory();
        goto fail;
    }

    if (verbose) {
        amd_version(version);
    }

    double *Control = PyMem_Calloc(AMD_CONTROL, sizeof(double));
    if (!Control) {
        PyErr_NoMemory();
        goto fail;
    }

    amd_defaults(Control);

    if (dense != AMD_DEFAULT_DENSE) {
        Control[AMD_DENSE] = dense;
    }
    if (aggressive != AMD_DEFAULT_AGGRESSIVE) {
        Control[AMD_AGGRESSIVE] = aggressive;
    }

    if (verbose) {
        amd_control(Control);
    }

    double *Info = PyMem_Calloc(AMD_INFO, sizeof(double));
    if (!Info) {
        PyErr_NoMemory();
        goto fail;
    }
    int32_t *P = PyMem_Calloc(n, sizeof(int32_t));
    if (!P) {
        PyErr_NoMemory();
        goto fail;
    }

    const int32_t result = amd_order(n, Ap, Ai, P, Control, Info);

    if (verbose) {
        amd_info(Info);
    }

    //TODO Generalize this for other function types
    if (result != AMD_OK) {
        if (result == AMD_OK_BUT_JUMBLED) {
            PyErr_WarnEx(PyExc_RuntimeWarning,
                         "Input matrix is OK for amd_order, but columns were not sorted, and/or duplicate entries were present. AMD had to do extra work before ordering the matrix. This is a warning, not an error.",
                         1);
        } else {
            if (result == AMD_OUT_OF_MEMORY) {
                PyErr_NoMemory();
            } else if (result == AMD_INFO) {
                PyErr_SetString(PyExc_ValueError, "Input arguments are not valid to the ordering");
            } else {
                PyErr_SetString(PyExc_ValueError, "Ordering failed");
            }
            goto fail;
        }
    }

    PyObject *permutation = PyList_New(n);
    if (!permutation) {
        goto fail;
    }

    if (!copy_array(P, n, permutation)) {
        goto fail;
    }

    PyObject *info = PyList_New(AMD_INFO);
    if (!info) {
        goto fail;
    }

    if (!copy_arrayd(Info, AMD_INFO, info)) {
        goto fail;
    }

    PyObject *out = PyTuple_New(2);
    if (!out) {
        goto fail;
    }

    PyTuple_SET_ITEM(out, 0, permutation);
    PyTuple_SET_ITEM(out, 1, info);

    PyMem_Free(Ap);
    PyMem_Free(Ai);

    PyMem_Free(version);
    PyMem_Free(Control);
    PyMem_Free(Info);
    PyMem_Free(P);

    PyBuffer_Release(&view);

    return out;

fail:
    PyBuffer_Release(&view);
    return NULL;
}

static inline PyObject *_list_array(PyObject *obj, int verbose, int aggressive, double dense) {
    const Py_ssize_t rows = PyList_Size(obj);

    const int32_t n = (int32_t) rows;
    int32_t count = 0;

    int32_t *Ap = PyMem_Calloc(rows + 1, sizeof(int32_t));
    if (!Ap) {
        PyErr_NoMemory();
        goto fail;
    }
    Ap[0] = 0;

    for (Py_ssize_t i = 0; i < rows; ++i) {
        PyObject *py_inner_list = PyList_GetItem(obj, i);

        if (!PyList_Check(py_inner_list)) {
            PyErr_SetString(PyExc_TypeError, "list must contain only lists");
            goto fail;
        }

        const Py_ssize_t cols = PyList_Size(py_inner_list);

        if (rows != cols) {
            PyErr_SetString(PyExc_TypeError, "lists must have the same length, to be a square matrix");
            goto fail;
        }

        for (Py_ssize_t j = 0; j < cols; ++j) {
            PyObject *py_value = PyList_GetItem(py_inner_list, j);
            double val;

            if (PyLong_Check(py_value)) {
                val = (double) PyLong_AsLong(py_value);
            } else if (PyFloat_Check(py_value)) {
                val = PyFloat_AsDouble(py_value);
            } else if (PyUnicode_Check(py_value)) {
                // Check for non-zero string values
                val = (double) PyUnicode_GET_LENGTH(py_value);
            } else {
                PyErr_SetString(PyExc_TypeError, "inner lists must contain only numbers");
                goto fail;
            }

            if (val != 0) {
                ++count;
            }
        }

        Ap[i + 1] = count;
    }


    int32_t *Ai = PyMem_Calloc(count, sizeof(int32_t));
    if (!Ai) {
        PyErr_NoMemory();
        goto fail;
    }

    size_t index = 0;

    for (Py_ssize_t i = 0; i < rows; ++i) {
        PyObject *py_inner_list = PyList_GetItem(obj, i);

        const Py_ssize_t cols = PyList_Size(py_inner_list);

        for (Py_ssize_t j = 0; j < cols; ++j) {
            PyObject *py_value = PyList_GetItem(py_inner_list, j);
            double val;

            if (PyLong_Check(py_value)) {
                val = (double) PyLong_AsLong(py_value);
            } else if (PyFloat_Check(py_value)) {
                val = PyFloat_AsDouble(py_value);
            } else {
                continue;
            }

            if (val != 0) {
                Ai[index++] = (int32_t) j;
            }

            if (index >= count) {
                goto loop_exit;
            }
        }
    }

loop_exit:


    int *version = PyMem_Calloc(3, sizeof(int));
    if (!version) {
        PyErr_NoMemory();
        goto fail;
    }

    if (verbose) {
        amd_version(version);
    }

    double *Control = PyMem_Calloc(AMD_CONTROL, sizeof(double));
    if (!Control) {
        PyErr_NoMemory();
        goto fail;
    }

    amd_defaults(Control);

    if (dense != AMD_DEFAULT_DENSE) {
        Control[AMD_DENSE] = dense;
    }
    if (aggressive != AMD_DEFAULT_AGGRESSIVE) {
        Control[AMD_AGGRESSIVE] = aggressive;
    }

    if (verbose) {
        amd_control(Control);
    }

    double *Info = PyMem_Calloc(AMD_INFO, sizeof(double));
    if (!Info) {
        PyErr_NoMemory();
        goto fail;
    }
    int32_t *P = PyMem_Calloc(n, sizeof(int32_t));
    if (!P) {
        PyErr_NoMemory();
        goto fail;
    }

    const int32_t result = amd_order(n, Ap, Ai, P, Control, Info);

    if (verbose) {
        amd_info(Info);
    }

    //TODO Generalize this for other function types
    if (result != AMD_OK) {
        if (result == AMD_OK_BUT_JUMBLED) {
            PyErr_WarnEx(PyExc_RuntimeWarning,
                         "Input matrix is OK for amd_order, but columns were not sorted, and/or duplicate entries were present. AMD had to do extra work before ordering the matrix. This is a warning, not an error.",
                         1);
        } else {
            if (result == AMD_OUT_OF_MEMORY) {
                PyErr_NoMemory();
            } else if (result == AMD_INFO) {
                PyErr_SetString(PyExc_ValueError, "Input arguments are not valid to the ordering");
            } else {
                PyErr_SetString(PyExc_ValueError, "Ordering failed");
            }
            goto fail;
        }
    }

    PyObject *permutation = PyList_New(n);
    if (!permutation) {
        goto fail;
    }

    if (!copy_array(P, n, permutation)) {
        goto fail;
    }

    PyObject *info = PyList_New(AMD_INFO);
    if (!info) {
        goto fail;
    }

    if (!copy_arrayd(Info, AMD_INFO, info)) {
        goto fail;
    }

    PyObject *out = PyTuple_New(2);
    if (!out) {
        goto fail;
    }

    PyTuple_SET_ITEM(out, 0, permutation);
    PyTuple_SET_ITEM(out, 1, info);

    PyMem_Free(Ap);
    PyMem_Free(Ai);

    PyMem_Free(version);
    PyMem_Free(Control);
    PyMem_Free(Info);
    PyMem_Free(P);

    return out;

fail:
    return NULL;
}

static PyObject *_sparse_system(PyObject *self, PyObject *args, PyObject *kwargs) {
    PyObject *obj;
    int verbose = 0;
    int aggressive = AMD_DEFAULT_AGGRESSIVE;
    double dense = AMD_DEFAULT_DENSE;

    static char *kwlist[] = {"matrix", "dense", "aggressive", "verbose", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|dpp", kwlist, &obj, &dense, &aggressive, &verbose)) {
        return NULL;
    }

    if (PyList_Check(obj)) {
        return _list_array(obj, verbose, aggressive, dense);
    } else {
        return _numpy_array(obj, verbose, aggressive, dense);
    }
}

static PyObject *_amd(PyObject *self, PyObject *args, PyObject *kwargs) {
    return _sparse_system(self, args, kwargs);
}


static struct PyMethodDef methods[] = {
    {
        "amd", (PyCFunction) _amd, METH_VARARGS | METH_KEYWORDS,
        "Converts a dense symmetric matrix to CSC format and then performs AMD ( Approximate Minimum Degree ), returns the permutation matrix P."
    },
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "_amd",
    NULL,
    -1,
    methods
};


PyMODINIT_FUNC PyInit__amd(void) {
    return PyModule_Create(&module);
}
