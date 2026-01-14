
extern PyTypeObject JsonType;

struct Json
{
    PyObject_HEAD
    PyObject* data;
    // The underlying Python object.
};


#define Json_Check(op) PyObject_TypeCheck(op, &JsonType)
#define Json_CheckExact(op) (Py_TYPE(op) == &JsonType)
