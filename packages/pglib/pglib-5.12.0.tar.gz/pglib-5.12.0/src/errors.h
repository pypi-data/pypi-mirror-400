
#ifndef ERRORS_H
#define ERRORS_H

#include "connection.h"

PyObject* SetConnectionError(PGconn* pgconn);

inline PyObject* SetConnectionError(Connection* cnxn)
{
    return SetConnectionError(cnxn->pgconn);
}

PyObject* SetResultError(PGresult* result);

PyObject* SetStringError(PyObject* type, const char* szFormat, ...);

#endif // ERRORS_H

