#define PY_SSIZE_T_CLEAN
#include "jonesum.h"
#include <Python.h>
#include <stdlib.h>

typedef struct {
  PyObject_HEAD jonesum_context_t *ctx;
} JonesumObject;

static void JonesumObject_dealloc(JonesumObject *self) {
  if (self->ctx != NULL) {
    jonesum_free(self->ctx);
    self->ctx = NULL;
  }
  Py_TYPE(self)->tp_free((PyObject *)self);
}

static PyObject *JonesumObject_new(PyTypeObject *type, PyObject *args,
                                   PyObject *kwds) {
  JonesumObject *self = (JonesumObject *)type->tp_alloc(type, 0);
  if (self == NULL) {
    return NULL;
  }
  self->ctx = NULL;
  return (PyObject *)self;
}

static int JonesumObject_init(JonesumObject *self, PyObject *args,
                              PyObject *kwds) {
  PyObject *vocabulary_list;
  if (!PyArg_ParseTuple(args, "O", &vocabulary_list)) {
    return -1;
  }

  if (!PyList_Check(vocabulary_list)) {
    PyErr_SetString(PyExc_TypeError, "Expected a list of strings");
    return -1;
  }

  Py_ssize_t count = PyList_Size(vocabulary_list);
  if (count == 0) {
    PyErr_SetString(PyExc_ValueError, "Vocabulary list cannot be empty");
    return -1;
  }

  const char **vocabulary = (const char **)malloc(sizeof(const char *) * count);
  if (vocabulary == NULL) {
    PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory");
    return -1;
  }

  for (Py_ssize_t i = 0; i < count; i++) {
    PyObject *item = PyList_GetItem(vocabulary_list, i);
    if (!PyUnicode_Check(item)) {
      free(vocabulary);
      PyErr_SetString(PyExc_TypeError, "All items must be strings");
      return -1;
    }
    const char *str = PyUnicode_AsUTF8(item);
    if (str == NULL) {
      free(vocabulary);
      return -1;
    }
    vocabulary[i] = str;
  }

  self->ctx = jonesum_init(vocabulary, (size_t)count);
  free(vocabulary);

  if (self->ctx == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to initialize jonesum context");
    return -1;
  }

  return 0;
}

static PyObject *JonesumObject_rant(JonesumObject *self, PyObject *args,
                                    PyObject *kwds) {
  int count = 0;

  static char *kwlist[] = {"count", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist, &count)) {
    return NULL;
  }

  if (self->ctx == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Context not initialized");
    return NULL;
  }

  char *result = jonesum_rant(self->ctx, count);
  if (result == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "Failed to generate rant");
    return NULL;
  }

  PyObject *py_result = PyUnicode_FromString(result);
  free(result);
  return py_result;
}

static PyMethodDef JonesumObject_methods[] = {
    {"rant", (PyCFunction)JonesumObject_rant, METH_VARARGS | METH_KEYWORDS,
     "Generate multiple pontification sentences"},
    {NULL}};

static PyTypeObject JonesumType = {
    PyVarObject_HEAD_INIT(NULL, 0).tp_name = "_jonesum.Jonesum",
    .tp_doc = "Alex Jones Ipsum generator",
    .tp_basicsize = sizeof(JonesumObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = JonesumObject_new,
    .tp_init = (initproc)JonesumObject_init,
    .tp_dealloc = (destructor)JonesumObject_dealloc,
    .tp_methods = JonesumObject_methods,
};

static PyModuleDef jonesum_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_jonesum",
    .m_doc = "Alex Jones Ipsum C extension module",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__jonesum(void) {
  PyObject *m;

  if (PyType_Ready(&JonesumType) < 0) {
    return NULL;
  }

  m = PyModule_Create(&jonesum_module);
  if (m == NULL) {
    return NULL;
  }

  Py_INCREF(&JonesumType);
  if (PyModule_AddObject(m, "Jonesum", (PyObject *)&JonesumType) < 0) {
    Py_DECREF(&JonesumType);
    Py_DECREF(m);
    return NULL;
  }

  return m;
}
