
#include "pglib.h"
#include <cstring>
//  #include <string.h>


PyObject* GetFunction(const char* szPath)
{
    // Returns a Python function as a PyObject.
    //
    // Pass in the path to the function like "decimal.Decimal" and it will be looked up and
    // cached.
    //
    // WARNING: Python can only load a single C extension instance so you can store a global
    // copy of items defined in one.  Because of subinterpreters, however, different threads in
    // a Python program can have different copies of modules.  You do not want to mix those.
    // We use thread-local-storage to store a copy of the json module's `loads` function so we
    // know we got the right one.
    //
    // I'd love to cache this in the connection, but at this time we don't have the connection
    // pointer everywhere.  If this becomes a performance problem, I think that's the right
    // place to put it.

    // IMPORTANT: This is for *internal* use only where we control what is passed in.  Do *not*
    // pass user strings here.

    PyObject* dict = PyThreadState_GetDict();
    if (dict == 0)
    {
        // I don't know why there wouldn't be thread state so I'm going to raise an exception
        // unless I find more info.
        return PyErr_Format(PyExc_Exception, "pglib: PyThreadState_GetDict returned NULL");
    }

    // Check the cache.  GetItemString returns a borrowed reference.

    PyObject* func = PyDict_GetItemString(dict, szPath);

    if (!func)
    {
        char szT[512];
        if (strlen(szPath) >= sizeof(szT))
        {
            PyErr_SetString(Error, "GetFunction too long");
            return 0;
        }
        strcpy(szT, szPath);
        szT[_countof(szT)-1] = '\0';

        char* szDot = strchr(szT, '.');
        if (!szDot)
        {
            PyErr_SetString(Error, "GetFunction no dot?");
            return 0;
        }

        *szDot++ = '\0';

        const char* szModule = szT;
        const char* szFunc = szDot;

        // Import the class and cache it.  GetAttrString returns a new reference.
        PyObject* mod = PyImport_ImportModule(szModule);
        if (!mod)
            return 0;

        func = PyObject_GetAttrString(mod, szFunc);
        Py_DECREF(mod);
        if (!func)
            return 0;

        // SetItemString increments the refcount (not documented)
        PyDict_SetItemString(dict, szPath, func);
    }

    return func;
}
