#include "pglib.h"
#include "connection.h"
#include "resultset.h"
#include "row.h"
#include "datatypes.h"
#include "getdata.h"
#include "byteswap.h"
#include "pgarrays.h"
#include "params.h"
#include "errors.h"
#include "enums.h"
#include "type_hstore.h"
#include "type_json.h"
#include "type_ltree.h"
#include "conninfoopt.h"

PyObject* pModule = 0;
PyObject* Error;

PyObject* strComma;
PyObject* strParens;
PyObject* strLeftParen;
PyObject* strRightParen;
PyObject* strEmpty;

static char module_doc[] = "A straightforward library for PostgreSQL";

static char connect_doc[] =
"connect(connection_string) --> Connection";

static PyObject* mod_connect(PyObject* self, PyObject* args, PyObject* kwargs)
{
    UNUSED(self);

    const char* conninfo = 0;
    if (!PyArg_ParseTuple(args, "s", &conninfo))
        return 0;

    PGconn* pgconn;
    Py_BEGIN_ALLOW_THREADS
    pgconn = PQconnectdb(conninfo);
    Py_END_ALLOW_THREADS
    if (pgconn == 0)
        return PyErr_NoMemory();

    if (PQstatus(pgconn) != CONNECTION_OK)
    {
        const char* szError = PQerrorMessage(pgconn);
        PyErr_SetString(Error, szError);
        Py_BEGIN_ALLOW_THREADS
        PQfinish(pgconn);
        Py_END_ALLOW_THREADS
        return 0;
    }

    return Connection_New(pgconn, false);
}

static PyObject* mod_async_connect(PyObject* self, PyObject* args, PyObject* kwargs)
{
    // TODO: I don't know why, but the documentation says that timeouts are not
    // enforced for an async connection.  We'll need to pick out the timeout
    // from the connection string and implement our own.
    //
    // We might be able to get the requested value from PQconninfo.

    UNUSED(self);

    const char* conninfo = 0;
    if (!PyArg_ParseTuple(args, "s", &conninfo))
        return 0;

    PGconn* pgconn = PQconnectStart(conninfo);
    if (pgconn == 0)
        return PyErr_NoMemory();

    if (PQstatus(pgconn) == CONNECTION_BAD)
    {
        SetConnectionError(pgconn);
        PQfinish(pgconn);
        return 0;
    }

    return Connection_New(pgconn, true);
}

static PyObject* mod_register_enum(PyObject* self, PyObject* args)
{
    // This is temporary while I try to figure out how to handle mapping.  I might need to keep
    // information around mapped to the hash of the connection string.  Non-system OIDs are
    // different in different databases.
    //
    // I'd also like it to be more automatic, but that would require performing connections
    // under the cover to obtain the list of types every time we see one we don't know.
    //
    // I'm also considering moving more and more from C to a Python wrapper.

    UNUSED(self);

    long oid = 0;
    if (!PyArg_ParseTuple(args, "l", &oid))
        return 0;

    if (!RegisterEnum(oid))
        return 0;

    Py_RETURN_NONE;
}

static PyObject* mod_register_type(PyObject* self, PyObject* args)
{
    UNUSED(self);

    long oid = 0;
    const char* szTypeName;
    if (!PyArg_ParseTuple(args, "ls", &oid, &szTypeName))
        return 0;

    if (PyOS_stricmp(szTypeName, "hstore") == 0)
    {
        RegisterHstore(oid);
        Py_RETURN_NONE;
    }

    if (PyOS_stricmp(szTypeName, "ltree") == 0)
    {
        RegisterLTree(oid);
        Py_RETURN_NONE;
    }

    return SetStringError(PyExc_ValueError, "register_type only supports 'hstore' and 'ltree' at this time");
}


static PyObject* mod_connection_count()
{
  return PyLong_FromLong(GetConnectionCount());
}


static char doc_defaults[] = "Returns the dictionary of default conninfo values.";

static PyObject* mod_defaults() {
    ConnInfo info(PQconndefaults());
    if (!info) {
        return PyErr_NoMemory();
    }
    return DictFromConnInfo(info);
}

// static PyObject* mod_test(PyObject* self, PyObject* args)
// {
//     return 0;
// }

static PyMethodDef pglib_methods[] =
{
    // { "test",  (PyCFunction)mod_test,  METH_VARARGS, 0 },
    { "connect",  (PyCFunction)mod_connect,  METH_VARARGS, connect_doc },
    { "register_enum",  (PyCFunction)mod_register_enum,  METH_VARARGS, 0 },
    { "register_type",  (PyCFunction)mod_register_type,  METH_VARARGS, 0 },
    { "async_connect",  (PyCFunction)mod_async_connect,  METH_VARARGS, connect_doc },
    { "defaults", (PyCFunction)mod_defaults, METH_NOARGS,  doc_defaults },
    { "connection_count", (PyCFunction)mod_connection_count, METH_NOARGS, 0 },
    { 0, 0, 0, 0 }
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "pglib",                    // m_name
    module_doc,
    -1,                         // m_size
    pglib_methods,              // m_methods
    0,                          // m_reload
    0,                          // m_traverse
    0,                          // m_clear
    0,                          // m_free
};

static bool InitStringConstants()
{
    strComma = PyUnicode_FromString(",");
    strParens = PyUnicode_FromString("()");
    strLeftParen = PyUnicode_FromString("(");
    strRightParen = PyUnicode_FromString(")");
    strEmpty = PyUnicode_FromString("");

    return (
        strComma != 0 &&
        strParens != 0 &&
        strLeftParen != 0 &&
        strRightParen != 0 &&
        strEmpty
    );
}

struct ConstantDef
{
    const char* szName;
    int value;
};

#define MAKECONST(v) { #v, v }
static const ConstantDef aConstants[] = {
    MAKECONST(PQTRANS_IDLE),
    MAKECONST(PQTRANS_ACTIVE),
    MAKECONST(PQTRANS_INTRANS),
    MAKECONST(PQTRANS_INERROR),
    MAKECONST(PQTRANS_UNKNOWN),
    MAKECONST(PGRES_POLLING_READING),
    MAKECONST(PGRES_POLLING_WRITING),
    MAKECONST(PGRES_POLLING_FAILED),
    MAKECONST(PGRES_POLLING_OK),
};

PyMODINIT_FUNC PyInit__pglib()
{
    if (PQisthreadsafe() == 0)
    {
        PyErr_SetString(PyExc_RuntimeError, "Postgres libpq is not multithreaded");
        return 0;
    }

    if (PyType_Ready(&ConnectionType) < 0 || PyType_Ready(&ResultSetType) < 0
        || PyType_Ready(&RowType) < 0 || PyType_Ready(&HstoreType) < 0
        || PyType_Ready(&JsonType) < 0)
    {
        return 0;
    }

    if (!DataTypes_Init())
        return 0;

    if (!GetData_Init())
        return 0;

    Arrays_Init();
    Params_Init();
    if (!ResultSet_Init())
        return 0;

    if (!InitStringConstants())
        return 0;

    Error = PyErr_NewException("_pglib.Error", 0, 0);
    if (!Error)
        return 0;

    Object module(PyModule_Create(&moduledef));

    if (!module)
        return 0;

    for (unsigned int i = 0; i < _countof(aConstants); i++)
        PyModule_AddIntConstant(module, (char*)aConstants[i].szName, aConstants[i].value);

    PyModule_AddObject(module, "Error", Error);

    PyModule_AddObject(module, "Connection", (PyObject*)&ConnectionType);
    Py_INCREF((PyObject*)&ConnectionType);
    PyModule_AddObject(module, "Row", (PyObject*)&RowType);
    Py_INCREF((PyObject*)&RowType);
    PyModule_AddObject(module, "ResultSet", (PyObject*)&ResultSetType);
    Py_INCREF((PyObject*)&ResultSetType);

    PyModule_AddObject(module, "hstore", (PyObject*)&HstoreType);
    Py_INCREF((PyObject*)&HstoreType);

    PyModule_AddObject(module, "json", (PyObject*)&JsonType);
    Py_INCREF((PyObject*)&JsonType);

    return module.Detach();
}
