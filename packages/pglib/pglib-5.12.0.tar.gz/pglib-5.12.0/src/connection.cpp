#include "pglib.h"
#include "connection.h"
#include "resultset.h"
#include "errors.h"
#include "byteswap.h"
#include "params.h"
#include "getdata.h"
#include "row.h"
#include "conninfoopt.h"
#include <math.h> // modf

struct ConstantDef
{
    const char* szName;
    int value;
};

#define MAKECONST(v) { #v, v }
static const ConstantDef aTxnFlags[] = {
    MAKECONST(PQTRANS_IDLE),
    MAKECONST(PQTRANS_ACTIVE),
    MAKECONST(PQTRANS_INTRANS),
    MAKECONST(PQTRANS_INERROR),
    MAKECONST(PQTRANS_UNKNOWN),
};

enum {
    REQUIRE_OPEN            = 0x01,
    REQUIRE_SYNC            = 0x02,
    REQUIRE_ASYNC           = 0x04,
    REQUIRE_ASYNC_CONNECTED = 0x08 | REQUIRE_OPEN | REQUIRE_ASYNC,
};


static volatile long connection_count = 0;
// The number of connection objects, useful for debugging leaks.  (This could be implemented
// with the PostgreSQL event system.)


long GetConnectionCount()
{
    return connection_count;
}


inline Connection* CastConnection(PyObject* self, int flags=0)
{
    // Casts the Python pointer to our Connection structure.  If flags are
    // passed and any of the requirements are not met, the appropriate exception
    // is raised and zero is returned.

    Connection* cnxn = (Connection*)self;

    if ((flags & REQUIRE_OPEN) && (!cnxn->pgconn))
    {
        SetStringError(Error, "The connection is not open");
        return 0;
    }

    if ((flags & REQUIRE_SYNC) && (cnxn->async_status != ASYNC_STATUS_SYNC))
    {
        SetStringError(Error, "The connection is not synchronous");
        return 0;
    }

    if ((flags & REQUIRE_ASYNC) && (cnxn->async_status == ASYNC_STATUS_SYNC))
    {
        SetStringError(Error, "The connection is not async");
        return 0;
    }

    if ((flags & REQUIRE_ASYNC_CONNECTED) == REQUIRE_ASYNC_CONNECTED && (cnxn->async_status == ASYNC_STATUS_CONNECTING))
    {
        SetStringError(Error, "The async connection has not yet connected");
        return 0;
    }

    return cnxn;
}

const char* NameFromTxnFlag(int flag)
{
    for (size_t i = 0; i < _countof(aTxnFlags); i++)
        if (aTxnFlags[i].value == flag)
            return aTxnFlags[i].szName;
    return "invalid";
}

static void notice_receiver(void *arg, const PGresult* res)
{
}

static void OnCompleteConnection(Connection* cnxn)
{
    // Initialization that can't happen until after the connection is complete.
    // Separated because sync and async connections complete in different code
    // paths.

    const char* szID = PQparameterStatus(cnxn->pgconn, "integer_datetimes");
    cnxn->integer_datetimes = (szID == 0) || (strcmp(szID, "on") == 0);
}

PyObject* Connection_New(PGconn* pgconn, bool async)
{
    Connection* cnxn = PyObject_NEW(Connection, &ConnectionType);

    if (cnxn == 0)
    {
        PQfinish(pgconn);
        return 0;
    }

    // TODO: Does this need to be done after connecting?
    PQsetNoticeReceiver(pgconn, notice_receiver, 0);

    cnxn->pgconn = pgconn;
    cnxn->tracefile = 0;

    cnxn->async_status = async ? ASYNC_STATUS_CONNECTING : ASYNC_STATUS_SYNC;

    if (!async)
        OnCompleteConnection(cnxn);
    else
        PQsetnonblocking(cnxn->pgconn, 1);

    connection_count++;

    return reinterpret_cast<PyObject*>(cnxn);
}

static PGresult* internal_execute(PyObject* self, PyObject* args)
{
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    // TODO: Check connection state.

    Py_ssize_t cParams = PyTuple_Size(args) - 1;
    if (cParams < 0)
    {
        PyErr_SetString(PyExc_TypeError, "Expected at least 1 argument (0 given)");
        return 0;
    }

    PyObject* pSql = PyTuple_GET_ITEM(args, 0);
    if (!PyUnicode_Check(pSql))
    {
        PyErr_SetString(PyExc_TypeError, "The first argument must be a string.");
        return 0;
    }
    const char* szSQL = PyUnicode_AsUTF8(pSql);
    if (!szSQL)
        return 0;

    Params params(cParams);
    if (!BindParams(cnxn, params, args))
        return 0;

    PGresult* result;
    Py_BEGIN_ALLOW_THREADS
    result = PQexecParams(cnxn->pgconn, szSQL,
                          cParams,
                          params.types,
                          params.values,
                          params.lengths,
                          params.formats,
                          1); // binary format
    Py_END_ALLOW_THREADS

    if (result == 0)
    {
        // Apparently this only happens for very serious errors, but the docs aren't terribly clear.
        PyErr_SetString(Error, "Fatal error");
        return 0;
    }

    return result;
}


static const char doc_script[] = "Connection.script(sql) --> None\n\n"
    "Executes a script which can contain multiple statements separated by semicolons.";

static PyObject* Connection_script(PyObject* self, PyObject* args)
{
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    PyObject* pScript;
    if (!PyArg_ParseTuple(args, "U", &pScript))
        return 0;

    const char* szScript = PyUnicode_AsUTF8(pScript);
    if (!szScript)
        return 0;

    ResultHolder result = PQexec(cnxn->pgconn, szScript);
    if (result == 0)
        return 0;

    switch (PQresultStatus(result)) {
    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
        return SetResultError(result.Detach());

    default:
        Py_RETURN_NONE;
    }
}


const char* doc_copy_from =
    "Connection.copy_from(command, source) --> int\n"
    "\n"
    "Executes the given COPY FROM command and returns the number of records copied.\n"
    "\n"
    "command\n"
    "  The copy command which must be 'from stdin'.\n"
    "\n"
    "source\n"
    "  The data to copy from.  This can be a string formatted as CSV or a file-like\n"
    "  object (anything with a read method that returns a string or bytes object).\n"
    "\n"
    "Examples:\n"
    "  cnxn.copy_from('copy from t1 from stdin csv header', open('test.csv'))\n"
    "  cnxn.copy_from('copy from t1(a, b, c) from stdin csv header', open('test.csv'))\n"
    "  cnxn.copy_from('copy from t1 from stdin csv header', gzip.open('test.csv'))\n"
    "  cnxn.copy_from('copy from t1 from stdin csv', \"1,'one'\\n2,'two'\"))\n";

static PyObject* Connection_copy_from(PyObject* self, PyObject* args)
{
    PyObject* command;
    PyObject* source;
    if (!PyArg_ParseTuple(args, "UO", &command, &source))
        return 0;

    // If source is a string (Unicode), store the UTF-encoded value in buffer. If a byte
    // object, store directly in buffer.  Otherwise, buffer will be zero and `source` must be
    // an object with a read method (e.g. file).
    const char* buffer = 0;
    Py_ssize_t buffer_size = 0;
    Object read_method;

    if (PyUnicode_Check(source))
    {
        buffer = PyUnicode_AsUTF8AndSize(source, &buffer_size);
        if (buffer == 0)
            return 0;
    }
    else
    {
        if (!PyObject_HasAttrString(source, "read"))
            return PyErr_Format(Error, "CSV source must be a string or file-like object.");
        read_method.Attach(PyObject_GetAttrString(source, "read"));
    }

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    const char* szSQL = PyUnicode_AsUTF8(command);
    if (!szSQL)
        return 0;

    ResultHolder result;
    Py_BEGIN_ALLOW_THREADS
    result = PQexec(cnxn->pgconn, szSQL);
    Py_END_ALLOW_THREADS

    if (result == 0)
        return 0;

    switch (PQresultStatus(result)) {
    case PGRES_COPY_IN:
        // This is what we are expecting.
        break;

    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
        return SetResultError(result.Detach());

    default:
        return PyErr_Format(Error, "Result was not PGRES_COPY_IN: %d", (int)PQresultStatus(result));
    }

    if (buffer != 0)
    {
        int copyStatus = 0;
        Py_BEGIN_ALLOW_THREADS
        copyStatus = PQputCopyData(cnxn->pgconn, buffer, (int)buffer_size);
        Py_END_ALLOW_THREADS
        if (copyStatus != 1)
            return SetConnectionError(cnxn);
    }
    else
    {
        Object read_args(Py_BuildValue("(l)", 200 * 1024));
        if (read_args == 0)
            return 0;

        for (;;)
        {
            Object s(PyObject_CallObject(read_method, read_args));
            if (s == 0)
                return 0;
            if (PyBytes_Check(s))
            {
                buffer = PyBytes_AS_STRING(s.Get());
                buffer_size = PyBytes_GET_SIZE(s.Get());
            }
            else if (PyUnicode_Check(s.Get()))
            {
                buffer = PyUnicode_AsUTF8AndSize(s.Get(), &buffer_size);
            }
            else
            {
                return PyErr_Format(Error, "Result of reading is not a bytes object: %R", s.Get());
            }
            if (buffer == 0)
                return 0;
            if (buffer_size == 0)
                break;
            int copyStatus = 0;
            Py_BEGIN_ALLOW_THREADS
            copyStatus = PQputCopyData(cnxn->pgconn, buffer, (int)buffer_size);
            Py_END_ALLOW_THREADS
            if (copyStatus != 1)
                return SetConnectionError(cnxn);
        }
    }

    if (PQputCopyEnd(cnxn->pgconn, 0) != 1)
        return SetConnectionError(cnxn);

    // After a copy, you have to get another result to know if it was successful.

    ResultHolder final_result;
    ExecStatusType status = PGRES_COMMAND_OK;
    Py_BEGIN_ALLOW_THREADS
    final_result = PQgetResult(cnxn->pgconn);
    status = PQresultStatus(final_result);

    // You must call PQgetResult until it returns NULL at the end of each command.
    for (;;) {
      PGresult* res = PQgetResult(cnxn->pgconn);
      if (res == 0)
        break;
      PQclear(res);
    }
    Py_END_ALLOW_THREADS

    if (status != PGRES_COMMAND_OK) {
      // SetResultError will take ownership of `result`.
      return SetResultError(final_result.Detach());
    }

    const char* sz = PQcmdTuples(final_result);
    if (sz == 0 || *sz == 0)
      Py_RETURN_NONE;
    return PyLong_FromLong(atoi(sz));
}


const char* doc_copy_to =
    "Connection.copy_to(command, dest) --> int\n"
    "\n"
    "Executes the given COPY TO command and returns the number of records copied.\n"
    "\n"
    "command\n"
    "  The copy command which must be 'to stdout'.\n"
    "\n"
    "dest\n"
    "  The file-like object to write to.  Strings will be written, not bytes, so\n"
    "  open in text mode.\n"
    "\n"
    "Examples:\n"
    "  cnxn.copy_to('copy t1 to stdout csv header', open('test.csv', 'w'))\n"
    "  cnxn.copy_to('copy t1(a, b, c) to stdout csv header', open('test.csv', 'w'))\n"
    "  cnxn.copy_to('copy (select * from t1 where id > 10) to stdout csv', f)\n";

static PyObject* Connection_copy_to(PyObject* self, PyObject* args)
{
    PyObject* command;
    PyObject* dest;
    if (!PyArg_ParseTuple(args, "UO", &command, &dest))
        return 0;

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (!PyObject_HasAttrString(dest, "write"))
        return PyErr_Format(Error, "Destination must be a file-like object.");
    Object write_method(PyObject_GetAttrString(dest, "write"));

    const char* szSQL = PyUnicode_AsUTF8(command);
    if (!szSQL)
        return 0;

    ResultHolder result;
    Py_BEGIN_ALLOW_THREADS
    result = PQexec(cnxn->pgconn, szSQL);
    Py_END_ALLOW_THREADS

    if (result == 0)
        return 0;

    switch (PQresultStatus(result)) {
    case PGRES_COPY_OUT:
        // This is what we are expecting.
        break;

    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
        return SetResultError(result.Detach());

    default:
        return PyErr_Format(Error, "Result was not PGRES_COPY_OUT: %d", (int)PQresultStatus(result));
    }


    for (;;) {
        int cb = 0;
        char* buffer;
        Py_BEGIN_ALLOW_THREADS
        cb = PQgetCopyData(cnxn->pgconn, &buffer, 0);
        Py_END_ALLOW_THREADS

        if (cb == -2) {
            return SetResultError(result.Detach());
        }

        if (cb == -1) {
            // The copy is complete.
            break;
        }

        // We have a buffer of byte data.  We have the length (`cb`), but the libpq docs say
        // that the string is also zero terminated, so we're going to try not calling 'write'.

        int err = PyFile_WriteString(buffer, dest);

        PQfreemem(buffer);
        if (err) {
            return 0;
        }
    }

    // After a copy, you have to get another result to know if it was successful.

    ResultHolder final_result;
    ExecStatusType status = PGRES_COMMAND_OK;
    Py_BEGIN_ALLOW_THREADS
    final_result = PQgetResult(cnxn->pgconn);
    status = PQresultStatus(final_result);
    Py_END_ALLOW_THREADS

    if (status != PGRES_COMMAND_OK) {
      // SetResultError will take ownership of `result`.
      return SetResultError(final_result.Detach());
    }

    const char* sz = PQcmdTuples(final_result);
    if (sz == 0 || *sz == 0)
      Py_RETURN_NONE;
    return PyLong_FromLong(atoi(sz));
}


const char* doc_copy_to_csv =
    "Connection.copy_to_csv(table, dest, header=0, delimiter=',', quote='\"')\n"
    "\n"
    "Execute a COPY TO command and return the number of records copied.\n"
    "\n"
    "table\n"
    "  The table to copy from.\n"
    "\n"
    "dest\n"
    "  The file-like object to write to.  Strings will be written, not bytes, so\n"
    "  open in text mode.\n"
    "\n"
    "header\n"
    "  If non-zero, a CSV header will be written.\n";


static PyObject* Connection_copy_to_csv(PyObject* self, PyObject* args, PyObject* kwargs)
{
    // This is not nearly as efficient as I'd like since newer Python versions no longer give
    // us access to underlying file objects.  We have to write strings through a write method
    // since there are io layers involved.
    //
    // For maximum performance, we should probably offer an option where we open the file given
    // a filename.  We can either check the parameter type here or we could make a separate
    // method with "file" in the name like copy_to_file.

    static const char* kwlist[] = {"table", "dest", "header", "delimiter", "quote", 0};

    PyObject* table;
    PyObject* dest;
    int header = 0;
    char* szDelimiter = 0;
    char* szQuote = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "UO|pzz", (char**)kwlist, &table, &dest, &header,
                                     &szDelimiter, &szQuote)) {
        return 0;
    }

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (!PyObject_HasAttrString(dest, "write"))
        return PyErr_Format(Error, "CSV destination must be a file-like object.");
    Object write_method(PyObject_GetAttrString(dest, "write"));

    char header_token[] = "header";
    if (header == 0) {
        header_token[0] = 0;
    }

    const char* pszDelimiter = szDelimiter ? szDelimiter : ",";
    const char* pszQuote = szQuote ? szQuote : "\"";

    Object sql(PyUnicode_FromFormat("copy %U to stdout with csv %s delimiter '%s' quote '%s'",
                                    table, header_token, pszDelimiter, pszQuote));
    if (!sql)
        return 0;

    const char* szSQL = PyUnicode_AsUTF8(sql);
    if (!szSQL)
        return 0;

    ResultHolder result;
    Py_BEGIN_ALLOW_THREADS
    result = PQexec(cnxn->pgconn, szSQL);
    Py_END_ALLOW_THREADS

    if (result == 0)
        return 0;

    switch (PQresultStatus(result)) {
    case PGRES_COPY_OUT:
        // This is what we are expecting.
        break;

    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
        return SetResultError(result.Detach());

    default:
        return PyErr_Format(Error, "Result was not PGRES_COPY_IN: %d", (int)PQresultStatus(result));
    }


    for (;;) {
        int cb = 0;
        char* buffer;
        Py_BEGIN_ALLOW_THREADS
        cb = PQgetCopyData(cnxn->pgconn, &buffer, 0);
        Py_END_ALLOW_THREADS

        if (cb == -2) {
            return SetResultError(result.Detach());
        }

        if (cb == -1) {
            // The copy is complete.
            break;
        }

        // We have a buffer of byte data.  We have the length, but the libpq docs say that the
        // string is also zero terminated, so we're going to try not calling 'write'.

        int err = PyFile_WriteString(buffer, dest);

        //  while (cb > 0) {
        //      PyObject* res = PyObject_CallObject(write_method)
        //  }

        PQfreemem(buffer);
        if (err) {
            return 0;
        }
    }

    // After a copy, you have to get another result to know if it was successful.

    ResultHolder final_result;
    ExecStatusType status = PGRES_COMMAND_OK;
    Py_BEGIN_ALLOW_THREADS
    final_result = PQgetResult(cnxn->pgconn);
    status = PQresultStatus(final_result);
    Py_END_ALLOW_THREADS

    if (status != PGRES_COMMAND_OK) {
      // SetResultError will take ownership of `result`.
      return SetResultError(final_result.Detach());
    }

    const char* sz = PQcmdTuples(final_result);
    if (sz == 0 || *sz == 0)
      Py_RETURN_NONE;
    return PyLong_FromLong(atoi(sz));
}


const char* doc_copy_from_csv =
    "Connection.copy_from_csv(table, source, header=0) --> int\n"
    "\n"
    "Executes a COPY FROM command and returns the number of records copied.\n"
    "\n"
    "table\n"
    "  The table to copy to.  This can also contain the columns to populate.\n"
    "\n"
    "source\n"
    "  The data to copy from.  This can be a string formatted as CSV or a file-like\n"
    "  object (anything with a read method that returns a string or bytes object).\n"
    "\n"
    "Examples:\n"
    "  cnxn.copy_from_csv('t1', open('test.csv'), header=1)\n"
    "  cnxn.copy_from_csv('t1(a,b,c)', open('test.csv'), header=1)\n"
    "  cnxn.copy_from_csv('t1', gzip.open('test.csv'), header=1)\n"
    "  cnxn.copy_from_csv('t1', \"1,'one'\\n2,'two'\")\n";

static PyObject* Connection_copy_from_csv(PyObject* self, PyObject* args, PyObject* kwargs)
{
    static const char *kwlist[] = { "table", "source", "header", "delimiter", "quote", 0 };

    PyObject* table;
    PyObject* source;
    int header = 0;
    char* szDelimiter = 0;
    char* szQuote = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "UO|pzz", (char**)kwlist, &table, &source, &header, &szDelimiter, &szQuote))
        return 0;

    char header_token[] = "header";
    if (header == 0)
        header_token[0] = 0;

    const char* pszDelimiter = szDelimiter ? szDelimiter : ",";
    const char* pszQuote = szQuote ? szQuote : "\"";
    Object sql(PyUnicode_FromFormat("copy %U from stdin with csv %s delimiter '%s' quote '%s'",
                                    table, header_token, pszDelimiter, pszQuote));

    // If source is a string (Unicode), store the UTF-encoded value in buffer. If a byte
    // object, store directly in buffer.  Otherwise, buffer will be zero and `source` must be
    // an object with a read method (e.g. file).
    const char* buffer = 0;
    Py_ssize_t buffer_size = 0;
    Object read_method;
    //  PyObject* read_method = 0;

    if (PyUnicode_Check(source))
    {
        buffer = PyUnicode_AsUTF8AndSize(source, &buffer_size);
        if (buffer == 0)
            return 0;
    }
    else
    {
        if (!PyObject_HasAttrString(source, "read"))
            return PyErr_Format(Error, "CSV source must be a string or file-like object.");
        read_method.Attach(PyObject_GetAttrString(source, "read"));
    }

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    const char* szSQL = PyUnicode_AsUTF8(sql);
    if (!szSQL)
        return 0;

    ResultHolder result;
    Py_BEGIN_ALLOW_THREADS
    result = PQexec(cnxn->pgconn, szSQL);
    Py_END_ALLOW_THREADS

    if (result == 0)
        return 0;

    switch (PQresultStatus(result)) {
    case PGRES_COPY_IN:
        // This is what we are expecting.
        break;

    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
        return SetResultError(result.Detach());

    default:
        return PyErr_Format(Error, "Result was not PGRES_COPY_IN: %d", (int)PQresultStatus(result));
    }

    if (buffer != 0)
    {
        int copyStatus = 0;
        Py_BEGIN_ALLOW_THREADS
        copyStatus = PQputCopyData(cnxn->pgconn, buffer, (int)buffer_size);
        Py_END_ALLOW_THREADS
        if (copyStatus != 1)
            return SetConnectionError(cnxn);
    }
    else
    {
        Object read_args(Py_BuildValue("(l)", 200 * 1024));
        if (read_args == 0)
            return 0;

        for (;;)
        {
            Object s(PyObject_CallObject(read_method, read_args));
            if (s == 0)
                return 0;
            if (PyBytes_Check(s))
            {
                buffer = PyBytes_AS_STRING(s.Get());
                buffer_size = PyBytes_GET_SIZE(s.Get());
            }
            else if (PyUnicode_Check(s.Get()))
            {
                buffer = PyUnicode_AsUTF8AndSize(s.Get(), &buffer_size);
            }
            else
            {
                return PyErr_Format(Error, "Result of reading is not a bytes object: %R", s.Get());
            }
            if (buffer == 0)
                return 0;
            if (buffer_size == 0)
                break;
            int copyStatus = 0;
            Py_BEGIN_ALLOW_THREADS
            copyStatus = PQputCopyData(cnxn->pgconn, buffer, (int)buffer_size);
            Py_END_ALLOW_THREADS
            if (copyStatus != 1)
                return SetConnectionError(cnxn);
        }
    }

    if (PQputCopyEnd(cnxn->pgconn, 0) != 1)
        return SetConnectionError(cnxn);

    // After a copy, you have to get another result to know if it was successful.

    ResultHolder final_result;
    ExecStatusType status = PGRES_COMMAND_OK;
    Py_BEGIN_ALLOW_THREADS
    final_result = PQgetResult(cnxn->pgconn);
    status = PQresultStatus(final_result);

    // You must call PQgetResult until it returns NULL at the end of each command.
    for (;;) {
      PGresult* res = PQgetResult(cnxn->pgconn);
      if (res == 0)
        break;
      PQclear(res);
    }
    Py_END_ALLOW_THREADS

    if (status != PGRES_COMMAND_OK) {
      // SetResultError will take ownership of `result`.
      return SetResultError(final_result.Detach());
    }

    const char* sz = PQcmdTuples(final_result);
    if (sz == 0 || *sz == 0)
      Py_RETURN_NONE;
    return PyLong_FromLong(atoi(sz));
}

static PyObject* ReturnResult(Connection* cnxn, ResultHolder& result)
{
    // An internal function for handling a result set so we can share the sync
    // and async implementations.

    ExecStatusType status = PQresultStatus(result);

    switch (status)
    {
    case PGRES_TUPLES_OK:
        return ResultSet_New(cnxn, result.Detach());

    case PGRES_COMMAND_OK:
    {
        const char* sz = PQcmdTuples(result);
        if (sz == 0 || *sz == 0)
            Py_RETURN_NONE;
        return PyLong_FromLong(atoi(sz));
    }

    case PGRES_EMPTY_QUERY:
        // This means an empty string was passed, but we check that already so we should never get here.
        Py_RETURN_NONE;

    case PGRES_COPY_OUT:
    case PGRES_COPY_IN:
    case PGRES_COPY_BOTH:
        Py_RETURN_NONE;

    case PGRES_BAD_RESPONSE:
    case PGRES_NONFATAL_ERROR:
    case PGRES_FATAL_ERROR:
    default:
        // Fall through and return an error.
        break;
    }

    // SetResultError will take ownership of `result`.
    return SetResultError(result.Detach());
}

static PyObject* Connection_execute(PyObject* self, PyObject* args)
{
    Connection* cnxn = (Connection*)self;

    ResultHolder result = internal_execute(self, args);
    if (result == 0)
        return 0;

    return ReturnResult(cnxn, result);
}

static PyObject* Connection_row(PyObject* self, PyObject* args)
{
    Connection* cnxn = (Connection*)self;

    ResultHolder result = internal_execute(self, args);
    if (result == 0)
        return 0;

    ExecStatusType status = PQresultStatus(result);

    if (status != PGRES_TUPLES_OK)
    {
        switch (status)
        {
            case PGRES_COMMAND_OK:
            case PGRES_EMPTY_QUERY:
            case PGRES_COPY_OUT:
            case PGRES_COPY_IN:
            // case PGRES_COPY_BOTH:
                PyErr_SetString(Error, "SQL wasn't a query");
                return 0;

            case PGRES_BAD_RESPONSE:
            case PGRES_NONFATAL_ERROR:
            case PGRES_FATAL_ERROR:
            default:
                // SetResultError will take ownership of `result`.
                return SetResultError(result.Detach());
        }
    }

    int cRows = PQntuples(result);
    if (cRows == 0)
    {
        Py_RETURN_NONE;
    }

    if (cRows != 1)
        return PyErr_Format(Error, "row query returned %d rows, not 1", cRows);

    Object rset = ResultSet_New(cnxn, result);
    if (rset == 0)
        return 0;

    result.Detach();

    return Row_New((ResultSet*)rset.Get(), 0);
}

static PyObject* Connection_info(PyObject* self, PyObject* args) {

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    ConnInfo info(PQconninfo(cnxn->pgconn));
    if (!info) {
        return PyErr_NoMemory();
    }

    return DictFromConnInfo(info);
}


static PyObject* Connection_reset(PyObject* self, PyObject* args)
{
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    PQreset(cnxn->pgconn);
    Py_RETURN_NONE;
}

static PyObject* Connection_trace(PyObject* self, PyObject* args)
{
    const char* filename;
    const char* mode = 0;
    if (!PyArg_ParseTuple(args, "z|z", &filename, &mode))
        return 0;

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (cnxn->tracefile)
    {
        PQuntrace(cnxn->pgconn);
        fclose(cnxn->tracefile);
        cnxn->tracefile = 0;
    }

    if (filename)
    {
        cnxn->tracefile = fopen(filename, mode ? mode : "w");
        if (cnxn->tracefile == 0)
            return PyErr_SetFromErrnoWithFilename(Error, filename);
        PQtrace(cnxn->pgconn, cnxn->tracefile);
    }

    Py_RETURN_NONE;
}

static const char doc_fetchvals[] = "Connection.fetchvals(sql, ...) --> List\n\n"
    "Returns an array with the first column of each resulting row.  If there are no\n"
    " rows, an empty array is returned.";

static PyObject* Connection_fetchvals(PyObject* self, PyObject* args)
{
    Connection* cnxn = (Connection*)self;
    ResultHolder result = internal_execute(self, args);
    if (result == 0)
        return 0;

    ExecStatusType status = PQresultStatus(result);

    if (status != PGRES_TUPLES_OK)
    {
        switch (status)
        {
        case PGRES_COMMAND_OK:
        case PGRES_EMPTY_QUERY:
        case PGRES_COPY_OUT:
        case PGRES_COPY_IN:
            // case PGRES_COPY_BOTH:
            PyErr_SetString(Error, "SQL wasn't a query");
            return 0;

        case PGRES_BAD_RESPONSE:
        case PGRES_NONFATAL_ERROR:
        case PGRES_FATAL_ERROR:
        default:
            // SetResultError will take ownership of `result`.
            return SetResultError(result.Detach());
        }
    }

    int cRows = PQntuples(result);

    List list(cRows);
    if (!list)
        return 0;

    for (int i = 0; i < cRows; i++)
    {
        PyObject* p = ConvertValue(result, i, 0, cnxn->integer_datetimes, PQfformat(result, 0));
        if (p == 0)
            return 0;
        list.SET_ITEM(i, p);
    }

    return list.Detach();
}

static PyObject* Connection_fetchval(PyObject* self, PyObject* args)
{
    Connection* cnxn = (Connection*)self;

    ResultHolder result = internal_execute(self, args);
    if (result == 0)
        return 0;

    ExecStatusType status = PQresultStatus(result);

    if (status != PGRES_TUPLES_OK)
    {
        switch (status)
        {
            case PGRES_COMMAND_OK:
            case PGRES_EMPTY_QUERY:
            case PGRES_COPY_OUT:
            case PGRES_COPY_IN:
            // case PGRES_COPY_BOTH:
                PyErr_SetString(Error, "SQL wasn't a query");
                return 0;

            case PGRES_BAD_RESPONSE:
            case PGRES_NONFATAL_ERROR:
            case PGRES_FATAL_ERROR:
            default:
                // SetResultError will take ownership of `result`.
                return SetResultError(result.Detach());
        }
    }

    int cRows = PQntuples(result);

    if (cRows == 0)
    {
        Py_RETURN_NONE;
    }

    if (cRows != 1)
        return PyErr_Format(Error, "scalar query returned %d rows, not 1", cRows);

    return ConvertValue(result, 0, 0, cnxn->integer_datetimes, PQfformat(result, 0));
}

static const char doc_begin[] = "Connection.begin() --> None\n\n"
    "Begins a transaction.  Raises an error if already in a transaction.";

static PyObject* Connection_begin(PyObject* self, PyObject* args)
{
    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    PGTransactionStatusType txnstatus;
    ExecStatusType status = PGRES_COMMAND_OK;
    ResultHolder result;

    Py_BEGIN_ALLOW_THREADS
    txnstatus = PQtransactionStatus(cnxn->pgconn);
    if (txnstatus == PQTRANS_IDLE)
    {
        result = PQexec(cnxn->pgconn, "BEGIN");
        status = PQresultStatus(result);
    }
    Py_END_ALLOW_THREADS

    if (txnstatus != PQTRANS_IDLE)
        return PyErr_Format(Error, "Connection transaction status is not idle: %s", NameFromTxnFlag(txnstatus));

    if (status != PGRES_COMMAND_OK)
        return SetResultError(result);

    Py_RETURN_NONE;
}

static const char doc_commit[] = "Connection.commit() --> None\n\n"
    "Commits a transaction if one is active.  It is not an error to call outside of a transaction.";

static PyObject* Connection_commit(PyObject* self, PyObject* args)
{
    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    PGTransactionStatusType txnstatus;
    ExecStatusType status = PGRES_COMMAND_OK;
    ResultHolder result;

    Py_BEGIN_ALLOW_THREADS
    txnstatus = PQtransactionStatus(cnxn->pgconn);
    if (txnstatus == PQTRANS_INTRANS)
    {
        result = PQexec(cnxn->pgconn, "COMMIT");
        status = PQresultStatus(result);
    }
    Py_END_ALLOW_THREADS

    if (txnstatus != PQTRANS_IDLE && txnstatus != PQTRANS_INTRANS)
        return PyErr_Format(Error, "Connection transaction status is invalid: %s", NameFromTxnFlag(txnstatus));

    if (status != PGRES_COMMAND_OK)
        return SetResultError(result);

    Py_RETURN_NONE;
}

static const char doc_rollback[] = "Connection.rollback() --> None\n\n"
    "Rolls back a transaction if one is active.  It is not an error to call outside of a transaction.";

static PyObject* Connection_rollback(PyObject* self, PyObject* args)
{
    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    ExecStatusType status = PGRES_COMMAND_OK;
    ResultHolder result;

    Py_BEGIN_ALLOW_THREADS
    result = PQexec(cnxn->pgconn, "ROLLBACK");
    status = PQresultStatus(result);
    Py_END_ALLOW_THREADS

    if (status != PGRES_COMMAND_OK)
        return SetResultError(result);

    Py_RETURN_NONE;
}

static void Connection_close_impl(Connection* cnxn)
{
    // Called by the close() method and the destructor.  This should be safe if called multiple
    // times.  (It will be called twice if close() is used since the destructor is always
    // called.)

    Py_BEGIN_ALLOW_THREADS
    if (cnxn->pgconn)
    {
        connection_count--;
        PQfinish(cnxn->pgconn);
        cnxn->pgconn = 0;
    }
    if (cnxn->tracefile)
    {
        fclose(cnxn->tracefile);
        cnxn->tracefile = 0;
    }
    Py_END_ALLOW_THREADS
}

static const char doc_close[] = "Connection.close() -> None\n\n"
    "Closes the connection to the database.  It is safe to call if already closed.";

static PyObject* Connection_close(PyObject* self, PyObject* args)
{
    UNUSED(args);
    Connection* cnxn = (Connection*)self;
    Connection_close_impl(cnxn);
    Py_RETURN_NONE;
}

static void Connection_dealloc(PyObject* self)
{
    Connection* cnxn = (Connection*)self;
    Connection_close_impl(cnxn);
    PyObject_Del(self);
}

static PyObject* Connection_repr(PyObject* self)
{
    Connection* cnxn = (Connection*)self;
    if (cnxn->pgconn == 0)
        return PyUnicode_FromString("Connection { closed }");
    return PyUnicode_FromFormat("Connection { dbname=%s user=%s }", PQdb(cnxn->pgconn), PQuser(cnxn->pgconn));
}

static PyObject* Connection_server_version(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    return PyLong_FromLong(PQserverVersion(cnxn->pgconn));
}

static PyObject* Connection_protocol_version(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    return PyLong_FromLong(PQprotocolVersion(cnxn->pgconn));
}

static PyObject* Connection_server_encoding(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    const char* sz = PQparameterStatus(cnxn->pgconn, "server_encoding");
    if (sz == 0)
        return PyErr_NoMemory();
    return PyUnicode_DecodeUTF8(sz, strlen(sz), 0);
}

static PyObject* Connection_client_encoding(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    const char* sz = PQparameterStatus(cnxn->pgconn, "client_encoding");
    if (sz == 0)
        return PyErr_NoMemory();
    return PyUnicode_DecodeUTF8(sz, strlen(sz), 0);
}

static PyObject* Connection_status(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    return PyBool_FromLong(PQstatus(cnxn->pgconn) == CONNECTION_OK);
}

static PyObject* Connection_socket(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self);
    if (!cnxn->pgconn)
        return PyLong_FromLong(-1);

    return PyLong_FromLong(PQsocket(cnxn->pgconn));
}

static PyObject* Connection_pid(Connection* cnxn, void*)
{
    if (!cnxn->pgconn)
        return PyLong_FromLong(0);
    return PyLong_FromLong((long)PQbackendPID(cnxn->pgconn));
}

static PyObject* Connection_transaction_status(PyObject* self, void* closure)
{
    UNUSED(closure);
    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    return PyLong_FromLong(PQtransactionStatus(cnxn->pgconn));
}

static PyObject* Connection_sendQuery(PyObject* self, PyObject* args)
{
    PyObject* pScript;
    if (!PyArg_ParseTuple(args, "U", &pScript))
        return 0;

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC_CONNECTED);
    if (!cnxn)
        return 0;

    int sent;
    const char* szSQL = PyUnicode_AsUTF8(pScript);
    if (!szSQL)
        return 0;

    Py_BEGIN_ALLOW_THREADS
    sent = PQsendQuery(cnxn->pgconn, szSQL);
    Py_END_ALLOW_THREADS

    if (!sent)
        return SetConnectionError(cnxn->pgconn);

    int result = PQflush(cnxn->pgconn);

    if (result == -1)
        return SetConnectionError(cnxn->pgconn);

    return PyLong_FromLong(result);
}

static PyObject* Connection_sendQueryParams(PyObject* self, PyObject* args)
{
    // An async function to send a query.
    //
    // Returns True if all data was successfully sent and False if the caller needs to wait for
    // the socket to become writable again and call flush.

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC_CONNECTED);
    if (!cnxn)
        return 0;

    Py_ssize_t cParams = PyTuple_Size(args) - 1;
    if (cParams < 0)
    {
        PyErr_SetString(PyExc_TypeError, "Expected at least 1 argument (0 given)");
        return 0;
    }

    PyObject* pSql = PyTuple_GET_ITEM(args, 0);
    if (!PyUnicode_Check(pSql))
    {
        PyErr_SetString(PyExc_TypeError, "The first argument must be the SQL string.");
        return 0;
    }

    const char* szSQL = PyUnicode_AsUTF8(pSql);
    if (!szSQL)
        return 0;

    Params params(cParams);
    if (!BindParams(cnxn, params, args))
        return 0;

    const int BINARY_RESULTS = 1;
    bool error = false;
    int needs_flush = -1;

    Py_BEGIN_ALLOW_THREADS
    error = PQsendQueryParams(cnxn->pgconn, szSQL,
                              cParams,
                              params.types,
                              params.values,
                              params.lengths,
                              params.formats,
                              BINARY_RESULTS) == 0;

    if (!error)
    {
        needs_flush = PQflush(cnxn->pgconn);
        if (needs_flush == -1)
            error = true;
    }
    Py_END_ALLOW_THREADS

    if (error)
        return SetConnectionError(cnxn->pgconn);

    return PyBool_FromLong(needs_flush == 0);
}

static PyObject* Connection_flush(PyObject* self, PyObject* args)
{
    // An async function called when the socket has become writable.  Returns True if all data
    // was sent and False if another call to flush is required when the socket becomes writable
    // again.

    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    int result = PQflush(cnxn->pgconn);

    if (result == -1)
        return SetConnectionError(cnxn->pgconn);

    return PyBool_FromLong(result == 0);
}

static PyObject* Connection_consumeInput(PyObject* self, PyObject* args)
{
    // Consumes input (obviously) and returns True if data is ready to be read
    // with _getResult and False if data is not ready.  If an error occurs an
    // exception is raised.

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    int result = PQconsumeInput(cnxn->pgconn);
    if (result == 0)
        return SetConnectionError(cnxn->pgconn);

    return PyBool_FromLong(PQisBusy(cnxn->pgconn) == 0);
}

static PyObject* ConvertNotification(PGnotify* pn)
{
    // Converts a single notification to a tuple containing (channel, extra).
    //
    // This takes ownership of pn and frees it, even if there is an error.

    MemHolder<PGnotify> n(pn);

    Tuple tuple(2);
    if (!tuple)
        return 0;
    tuple.BorrowItem(0, PyUnicode_FromString(pn->relname));
    if (!tuple.GetItem(0))
        return 0;

    if (pn->extra)
    {
        tuple.BorrowItem(1, PyUnicode_FromString(pn->extra));
    }
    else
    {
        tuple.IncItem(1, Py_None);
    }

    return tuple.Detach();
}


static bool ParseDoubleKeyword(const char* name, PyObject* o, double defval, double& result)
{
    // Accepts either a Python number or None.  If None, `defval` is returned.
    if (o == Py_None)
    {
        result = defval;
        return true;
    }

    if (!PyNumber_Check(o))
    {
        SetStringError(PyExc_TypeError, "%s must be a number or None", name);
        return false;
    }

    // I'm kind of surprised there isn't a PyNumber_AsDouble.

    Object f(PyNumber_Float(o));
    if (!f)
        return false;

    result = PyFloat_AsDouble(f);
    return true;
}


static PyObject* Connection_notifications(PyObject* self, PyObject* args, PyObject* kwargs)
{
    // A synchronous function that waits for the next notification.

    // TODO: This doesn't handle signals.

    // TODO: This doesn't loop in case the select data is for something else.  On the other
    // hand, perhaps it shouldn't.  The data isn't going to get read unless we return.

    // The timeout is optional and can be None, but there doesn't seem to be an easy way to do
    // that.  It would be nice if you could indicate that like you can get string lengths,
    // etc.  Since we can't we'll get the timeout as a PyObject

    static const char* kwlist[] = { "timeout", 0 };
    PyObject* oTimeout;
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", (char**)kwlist, &oTimeout))
        return 0;

    double timeout = INFINITY;
    if (!ParseDoubleKeyword("timeout", oTimeout, INFINITY, timeout))
        return 0;

    Connection* cnxn = CastConnection(self, REQUIRE_SYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (PQconsumeInput(cnxn->pgconn) == 0)
        return SetConnectionError(cnxn->pgconn);

    PGnotify* pn = PQnotifies(cnxn->pgconn);
    if (pn)
        return ConvertNotification(pn);

    int sock = PQsocket(cnxn->pgconn);

    fd_set rfds;
    FD_ZERO(&rfds);
    FD_SET(sock, &rfds);

    struct timeval tv;
    if (timeout != INFINITY)
    {
        // TODO: Set a maximum to deal with overflow issues.
        double integral, fractional;
        fractional = modf(timeout, &integral);
        tv.tv_sec  = (int)timeout;
        tv.tv_usec = ((int)(fractional * 1000000) % 1000000);
    }

    int retval;
    Py_BEGIN_ALLOW_THREADS
    retval = select(sock + 1, &rfds, 0, 0, (timeout != INFINITY) ? &tv : 0);
    Py_END_ALLOW_THREADS

    if (retval == -1) {
        // Allow the Python (or application) signal handler deal with Ctrl-C.  If it raises an
        // exception, -1 is returned.  This only works on the main Python thread, but it is
        // just a convenience for command line utilities to raise a KeyboardInterrupt instead a
        // pglib error that *then* raises a KeyboardInterrupt.  So it is OK if we call on
        // another thread and it is a no-op.

        if (PyErr_CheckSignals() != -1) {
            SetStringError(Error, "An error occurred waiting for notifications");
        }

        return 0;
    }

    if (retval) {
        if (PQconsumeInput(cnxn->pgconn) == 0)
            return SetConnectionError(cnxn->pgconn);

        pn = PQnotifies(cnxn->pgconn);
        if (pn)
            return ConvertNotification(pn);
    }

    Py_RETURN_NONE;
}


static PyObject* Connection_asyncNotifications(PyObject* self, PyObject* args)
{
    // Used by the asynchronous connection wrapper to return notifications.

    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    bool error;
    Py_BEGIN_ALLOW_THREADS
    error = (PQconsumeInput(cnxn->pgconn) == 0);
    Py_END_ALLOW_THREADS;

    if (error)
        return SetConnectionError(cnxn);

    // Since PQnotifies does not read from the socket and is just returning the first item from
    // a linked list, we don't release the GIL.
    //
    // If this is only called when there is data on the socket, there probably is a
    // notification available, but I'm not going to allocate a list until we read it to be
    // sure.

    MemHolder<PGnotify> n(PQnotifies(cnxn->pgconn));
    if (!n)
    {
        Py_RETURN_NONE;
    }

    List list(0);
    if (!list)
        return 0;

    do
    {
        PyObject* p = ConvertNotification(n.Detach());
        if (!p)
            return 0;
        list.AppendAndBorrow(p); // could fail
        n = PQnotifies(cnxn->pgconn);
    }
    while (n.p);

    return list.Detach();
}


static PyObject* Connection_asyncGetResult(PyObject* self, PyObject* args)
{
    // Used by the asyncio code to read results (and notifications) when the socket has
    // data.
    //
    // The caller needs to know if we actually received results or not, but we can't use None
    // as an indication since it is a valid result.  (We return None when a DDL statement is
    // executed.)  We use the value False in the result slot to indicate no results have been
    // received.

    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    bool error = false;
    // MemHolder<PGnotify> n;
    ResultHolder r1;
    ResultHolder r2;

    // TODO: Need to use PQresultStatus.  Also need to continue calling PQgetResult even when
    // an error occurs until it returns NULL.

    Py_BEGIN_ALLOW_THREADS
    error = (PQconsumeInput(cnxn->pgconn) == 0);
    if (!error && !PQisBusy(cnxn->pgconn))
    {
        // The PostgreSQL async docs say you have to keep calling PQgetResult until it returns
        // NULL.  What I've noticed is about 2/3 of the calls return no results, and the other
        // 1/3 returns 1 result followed by NULL.  We'll optimize for those two cases.

        r1 = PQgetResult(cnxn->pgconn);
        r2 = r1 ? PQgetResult(cnxn->pgconn) : 0;
    }
    Py_END_ALLOW_THREADS;

    if (error)
        return SetConnectionError(cnxn);

    if (r2)
    {
        // This wouldn't be too hard to handle with a simple loop, but I haven't reproduced it
        // yet.
        return SetStringError(Error, "statement returned multiple results");
    }

    if (!r1)
    {
        Py_INCREF(Py_False);
        return Py_False;
    }

    return ReturnResult(cnxn, r1);
}

static PyObject* Connection_getResult(PyObject* self, PyObject* args)
{
    UNUSED(args);

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    ResultHolder result;
    Py_BEGIN_ALLOW_THREADS
    result = PQgetResult(cnxn->pgconn);
    Py_END_ALLOW_THREADS

    if (result.p == 0)
    {
        // This is normal and is how libpq tells us we've retrieved all of the
        // results.
        PyErr_SetNone(PyExc_StopIteration);
        return 0;
    }

    return ReturnResult(cnxn, result);
}

static PyObject* pg_notify = 0;

static PyObject* Connection_notify(PyObject* self, PyObject* args)
{
    PyObject* channel;
    PyObject* payload = 0;
    if (!PyArg_ParseTuple(args, "U|U", &channel, &payload))
        return 0;

    Connection* cnxn = CastConnection(self, REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (!pg_notify)
    {
        pg_notify = PyUnicode_FromString("select pg_notify($1, $2)");
        if (!pg_notify)
            return 0;
    }

    Tuple newArgs(3);
    if (!newArgs)
        return 0;

    newArgs.IncItem(0, pg_notify);

    newArgs.IncItem(1, channel);

    if (!payload)
        payload = Py_None;

    newArgs.IncItem(2, payload);

    ResultHolder result = internal_execute(self, newArgs);
    if (result == 0)
        return 0;
    return ReturnResult(cnxn, result);
}


static PyObject* Connection_connectPoll(PyObject* self, PyObject* args)
{
    // A wrapper around PQconnectPoll.
    //
    // Returns the polling constants OK, READING, and WRITING.  If an error
    // occurs it will be raised.

    Connection* cnxn = CastConnection(self, REQUIRE_ASYNC | REQUIRE_OPEN);
    if (!cnxn)
        return 0;

    if (cnxn->async_status != ASYNC_STATUS_CONNECTING)
        return SetStringError(Error, "Already connected");

    PostgresPollingStatusType status = PQconnectPoll(cnxn->pgconn);
    if (status == PGRES_POLLING_OK)
    {
        cnxn->async_status = ASYNC_STATUS_IDLE;
        OnCompleteConnection(cnxn);
    }

    if (status == PGRES_POLLING_READING || status == PGRES_POLLING_WRITING || status == PGRES_POLLING_OK)
        return PyLong_FromLong(status);

    SetConnectionError(cnxn);

    PQfinish(cnxn->pgconn);
    cnxn->pgconn = 0;

    return 0;
}

static PyGetSetDef Connection_getset[] = {
    { (char*)"server_version",     (getter)Connection_server_version,     0, (char*)"The server version", 0 },
    { (char*)"protocol_version",   (getter)Connection_protocol_version,   0, (char*)"The protocol version", 0 },
    { (char*)"server_encoding",    (getter)Connection_server_encoding,    0, (char*)0, 0 },
    { (char*)"client_encoding",    (getter)Connection_client_encoding,    0, (char*)0, 0 },
    { (char*)"status",             (getter)Connection_status,             0, (char*)"True if status is CONNECTION_OK, False otherwise", 0 },
    { (char*)"transaction_status", (getter)Connection_transaction_status, 0, (char*)"Returns PQtransactionStatus constants", 0 },
    { (char*)"socket",             (getter)Connection_socket,             0, (char*)"Returns the socket fileno", 0 },
    { (char*)"pid", (getter)Connection_pid, 0, (char*)"Returns the backend PID", 0 },
    { 0 }
};

static struct PyMethodDef Connection_methods[] =
{
    { "execute", Connection_execute, METH_VARARGS, 0 },
    { "fetchall", Connection_execute, METH_VARARGS, 0 },
    { "fetchrow", Connection_row,     METH_VARARGS, 0 },
    { "fetchval", Connection_fetchval,  METH_VARARGS, 0 },
    { "fetchvals", Connection_fetchvals, METH_VARARGS, doc_fetchvals },
    { "row",     Connection_row,     METH_VARARGS, 0 },
    { "scalar",  Connection_fetchval,  METH_VARARGS, 0 }, // deprecated
    { "trace",   Connection_trace,   METH_VARARGS, 0 },
    { "reset",   Connection_reset,   METH_NOARGS,  0 },
    { "script",  Connection_script,  METH_VARARGS, doc_script },
    { "copy_from", (PyCFunction) Connection_copy_from, METH_VARARGS | METH_KEYWORDS, doc_copy_from },
    { "copy_from_csv", (PyCFunction) Connection_copy_from_csv, METH_VARARGS | METH_KEYWORDS, doc_copy_from_csv },
    { "copy_to", (PyCFunction) Connection_copy_to, METH_VARARGS, doc_copy_to },
    { "copy_to_csv", (PyCFunction) Connection_copy_to_csv, METH_VARARGS | METH_KEYWORDS, doc_copy_to_csv},
    { "begin",    Connection_begin,   METH_NOARGS, doc_begin },
    { "commit",   Connection_commit,   METH_NOARGS, doc_commit },
    { "rollback", Connection_rollback,   METH_NOARGS, doc_rollback },
    { "close", Connection_close,   METH_NOARGS, doc_close },
    { "_connectPoll", Connection_connectPoll, METH_NOARGS, 0 },
    { "_sendQuery", Connection_sendQuery, METH_VARARGS, 0 },
    { "_sendQueryParams", Connection_sendQueryParams, METH_VARARGS, 0 },
    { "_consumeInput", Connection_consumeInput, METH_VARARGS, 0 },
    { "_getResult", Connection_getResult, METH_VARARGS, 0 },
    { "_flush", Connection_flush, METH_VARARGS, 0 },
    { "notifications", (PyCFunction)Connection_notifications, METH_VARARGS | METH_KEYWORDS, 0 },
    { "notify", Connection_notify, METH_VARARGS | METH_KEYWORDS, 0 },
    { "_asyncGetResult", Connection_asyncGetResult, METH_NOARGS, 0 },
    { "_asyncNotifications", Connection_asyncNotifications, METH_NOARGS, 0 },
    { "info", Connection_info, METH_NOARGS, 0 },
    { 0, 0, 0, 0 }
};

PyTypeObject ConnectionType =
{
    PyVarObject_HEAD_INIT(0, 0)
    "pglib.Connection",         // tp_name
    sizeof(Connection),         // tp_basicsize
    0,                          // tp_itemsize
    Connection_dealloc,         // destructor tp_dealloc
    0,                          // tp_print
    0,                          // tp_getattr
    0,                          // tp_setattr
    0,                          // tp_compare
    Connection_repr,            // tp_repr
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
    0, //connection_doc,             // tp_doc
    0,                          // tp_traverse
    0,                          // tp_clear
    0,                          // tp_richcompare
    0,                          // tp_weaklistoffset
    0,                          // tp_iter
    0,                          // tp_iternext
    Connection_methods,         // tp_methods
    0,                          // tp_members
    Connection_getset,          // tp_getset
    0,                          // tp_base
    0,                          // tp_dict
    0,                          // tp_descr_get
    0,                          // tp_descr_set
    0,                          // tp_dictoffset
    0,                          // tp_init
    0,                          // tp_alloc
    0,                          // tp_new
    0,                          // tp_free
    0,                          // tp_is_gc
    0,                          // tp_bases
    0,                          // tp_mro
    0,                          // tp_cache
    0,                          // tp_subclasses
    0,                          // tp_weaklist
};
