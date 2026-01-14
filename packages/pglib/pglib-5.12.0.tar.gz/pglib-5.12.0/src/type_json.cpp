
#include "pglib.h"
#include "byteswap.h"
#include "type_json.h"

static PyObject* Json_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    PyObject* arg;
    if (!PyArg_ParseTuple(args, "O", &arg))
    {
        PyErr_SetString(Error, "json constructor requires a single object");
        return 0;
    }

    Json* self = (Json*)type->tp_alloc(type, 0);
    if (self == 0)
        return 0;

    self->data = arg;
    Py_INCREF(self->data);

    return (PyObject*)self;
}


static void Json_dealloc(PyObject* self)
{
    Json* json = (Json*)self;
    Py_XDECREF(json->data);
    Py_TYPE(self)->tp_free(self);
}


PyTypeObject JsonType =
{
    PyVarObject_HEAD_INIT(0, 0)
    "pglib.Json",               // tp_name
    sizeof(Json),               // tp_basicsize
    0,                          // tp_itemsize
    Json_dealloc,               // destructor tp_dealloc
    0,                          // tp_print
    0,                          // tp_getattr
    0,                          // tp_setattr
    0,                          // tp_compare
    0,                          // tp_repr
    0,                          // tp_as_number
    0,                          // tp_as_sequence
    0,                          // tp_as_mapping
    0,                          // tp_hash
    0,                          // tp_call
    0,                          // tp_str
    0,                          // tp_getattro
    0,                          // tp_setattro
    0,                          // tp_as_buffer
    Py_TPFLAGS_DEFAULT,         // tp_flags
    0,                          // tp_doc
    0,                          // tp_traverse
    0,                          // tp_clear
    0,                          // tp_richcompare
    0,                          // tp_weaklistoffset
    0,                          // tp_iter
    0,                          // tp_iternext
    0,                          // tp_methods
    0,                          // tp_members
    0,                          // tp_getset
    0,                          // tp_base
    0,                          // tp_dict
    0,                          // tp_descr_get
    0,                          // tp_descr_set
    0,                          // tp_dictoffset
    0,                          // tp_init
    0,                          // tp_alloc
    Json_new,                   // tp_new
    0,                          // tp_free
    0,                          // tp_is_gc
    0,                          // tp_bases
    0,                          // tp_mro
    0,                          // tp_cache
    0,                          // tp_subclasses
    0,                          // tp_weaklist
};
