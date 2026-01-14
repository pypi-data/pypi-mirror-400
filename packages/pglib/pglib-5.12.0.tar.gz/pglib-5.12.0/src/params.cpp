#include "pglib.h"
#include <datetime.h>
#include "connection.h"
#include "byteswap.h"
#include "params.h"
#include "datatypes.h"
#include "juliandate.h"
#include "pgarrays.h"
#include "pgtypes.h"
#include "byteswap.h"
#include "errors.h"
#include "runtime.h"
#include "debug.h"

#include "type_hstore.h"
#include "type_json.h"

#ifdef MS_WINDOWS
#include <Winsock2.h>
#else
#ifndef __APPLE__
#include <arpa/inet.h>
#endif
#endif

void Params_Init()
{
    PyDateTime_IMPORT;
};


struct Pool
{
    Pool* next;
    size_t total;
    size_t remaining;
    char buf[1];
};

void Dump(Params& params)
{
    printf("===============\n");
    printf("pools\n");
    int count = 0;
    Pool* p = (Pool*)params.pool;
    while (p != 0)
    {
        count += 1;
        printf(" [ 0x%p total=%d remaining=%d ]\n", p, (int)p->total, (int)p->remaining);
        p = p->next;
    }
    printf("---------------\n");
}

Params::Params(int _count)
{
    count = _count;
    bound = 0;

    if (count == 0)
    {
        types   = 0;
        values  = 0;
        lengths = 0;
        formats = 0;
    }
    else
    {
        types   = (Oid*)  malloc(count * sizeof(Oid));
        values  = (const char**)malloc(count * sizeof(char*));
        lengths = (int*)  malloc(count * sizeof(int));
        formats = (int*)  malloc(count * sizeof(int));
    }
    pool = 0;
}

Params::~Params()
{
    free(types);
    free(values);
    free(lengths);
    free(formats);

    Pool* p = pool;
    while (p)
    {
        Pool* tmp = p->next;
        free(p);
        p = tmp;
    }
}

bool Params::Bind(Oid type, const void* value, int length, int format)
{
    types[bound]   = type;
    values[bound]  = (const char*)value;
    lengths[bound] = length;
    formats[bound] = format;

    bound += 1;

    return true;
}

WriteBuffer Params::Allocate(size_t amount)
{
    // Returns a block of memory with at last `amount` bytes to use for binding.  The memory
    // will be freed by this object so do not free it yourself.

    // See if we have a pool that is large enough.

    Pool** pp = &pool;

    while (*pp != 0)
    {
        if ((*pp)->remaining >= amount)
            break;

        pp = &((*pp)->next);
    }

    // If we didn't find a large enough pool, make one and link it in.

    if (*pp == 0)
    {
        size_t total = amount + 1024;
        *pp = (Pool*)malloc(total + (sizeof(Pool) - 1));

        if (*pp == 0)
        {
            PyErr_NoMemory();
            return WriteBuffer(0, 0);
        }

        (*pp)->next = 0;
        (*pp)->total = (*pp)->remaining = total;
    }

    // Reserve the area and return it.

    size_t offset = (*pp)->total - (*pp)->remaining;
    char*  p      = &(*pp)->buf[offset];
    (*pp)->remaining -= amount;

    return WriteBuffer(p, amount);
}


static bool BindUnicode(Connection* cnxn, Params& params, PyObject* param)
{
    // http://www.postgresql.org/message-id/flat/CAFj8pRA14jCW8DTK4r3dYP9L0Cz+gxjE-9fmh9k=VOUVFxLuDg@mail.gmail.com#CAFj8pRA14jCW8DTK4r3dYP9L0Cz+gxjE-9fmh9k=VOUVFxLuDg@mail.gmail.com
    //
    // We are now binding as UNKNOWNOID instead of TEXTOID which lets the server figure out the
    // datatype.  Otherwise we get an error trying to insert text into XML or JSON fields.
    //
    // If this causes problems we can revert to text and provide a wrapper that we recognize
    // for the other types, but that really seems like a pain.

    // TODO: Right now we *require* the encoding to be UTF-8.
    Py_ssize_t cb;
    const char* p = PyUnicode_AsUTF8AndSize(param, &cb);
    if (p == 0)
        return false;

    return params.Bind(UNKNOWNOID, p, cb, 0);
}

static bool BindDecimal(Connection* cnxn, Params& params, PyObject* param)
{
    // TODO: How are we going to deal with NaN, etc.?

    // This is probably wasteful, but most decimals are probably small as strings and near the size of the binary
    // format.
    //
    // We are going to allocate as UTF8 but we fully expect the results to be ASCII.

    Object s(PyObject_Str(param));
    if (!s)
        return false;

    Py_ssize_t cch;
    const char* pch = PyUnicode_AsUTF8AndSize(s, &cch);
    WriteBuffer buf(params.Allocate(cch + 1));
    if (!buf)
        return 0;

    buf.writeRawBytes(pch, cch+1);

    return params.Bind(NUMERICOID, buf.buffer(), buf.size(), FORMAT_TEXT);
}


static bool BindLong(Connection* cnxn, Params& params, PyObject* param)
{
    // Note: Integers must be in network order.

    const PY_LONG_LONG MIN_INTEGER  = -2147483648LL;
    const PY_LONG_LONG MAX_INTEGER  = 2147483647LL;

    int overflow = 0;

    PY_LONG_LONG lvalue = PyLong_AsLongAndOverflow(param, &overflow);
    if (overflow != 0)
        return false;

    if (lvalue >= MIN_INTEGER && lvalue <= MAX_INTEGER)
    {
        WriteBuffer buf(params.Allocate(4));
        if (!buf)
            return false;
        buf.writeInt32(lvalue);
        return params.Bind(INT4OID, buf, FORMAT_BINARY);
    }

    WriteBuffer buf(params.Allocate(8));
    if (!buf)
        return false;
    buf.writeUint64(lvalue);
    return params.Bind(INT8OID, buf, FORMAT_BINARY);
}


static const char FALSEBYTE = 0;
static const char TRUEBYTE  = 1;

static bool BindBool(Connection* cnxn, Params& params, PyObject* param)
{
    const char* p = (param == Py_True) ? &TRUEBYTE : &FALSEBYTE;
    return params.Bind(BOOLOID, p, 1, 1);
}

static bool BindDate(Connection* cnxn, Params& params, PyObject* param)
{
    uint32_t julian = dateToJulian(PyDateTime_GET_YEAR(param), PyDateTime_GET_MONTH(param), PyDateTime_GET_DAY(param));
    julian -= JULIAN_START;

    WriteBuffer buf = params.Allocate(sizeof(julian));
    if (!buf)
        return false;
    buf.writeUint32(julian);
    params.Bind(DATEOID, buf, FORMAT_BINARY);
    return true;
}

static bool BindDateTime(Connection* cnxn, Params& params, PyObject* param)
{
    uint64_t timestamp = dateToJulian(PyDateTime_GET_YEAR(param), PyDateTime_GET_MONTH(param), PyDateTime_GET_DAY(param)) - JULIAN_START;
    timestamp *= 24;
    timestamp += PyDateTime_DATE_GET_HOUR(param);
    timestamp *= 60;
    timestamp += PyDateTime_DATE_GET_MINUTE(param);
    timestamp *= 60;
    timestamp += PyDateTime_DATE_GET_SECOND(param);
    timestamp *= 1000000;
    timestamp += PyDateTime_DATE_GET_MICROSECOND(param);

    WriteBuffer buf = params.Allocate(8);
    if (!buf)
        return false;

    buf.writeUint64(timestamp);
    params.Bind(TIMESTAMPOID, buf, FORMAT_BINARY);
    return true;
}

static bool BindNone(Connection* cnxn, Params& params, PyObject* param)
{
    params.Bind(0,0,0,0);
    return true;
}

static bool BindTime(Connection* cnxn, Params& params, PyObject* param)
{
    uint64_t value = PyDateTime_TIME_GET_HOUR(param);
    value *= 60;
    value += PyDateTime_TIME_GET_MINUTE(param);
    value *= 60;
    value += PyDateTime_TIME_GET_SECOND(param);
    value *= 1000000;
    value += PyDateTime_TIME_GET_MICROSECOND(param);

    WriteBuffer buf = params.Allocate(8);
    if (!buf)
        return false;
    buf.writeUint64(value);
    params.Bind(TIMEOID, buf, FORMAT_BINARY);
    return true;
}

// IMPORTANT: These are not exposed in the Python API!
#define GET_TD_DAYS(o)          (((PyDateTime_Delta *)(o))->days)
#define GET_TD_SECONDS(o)       (((PyDateTime_Delta *)(o))->seconds)
#define GET_TD_MICROSECONDS(o)  (((PyDateTime_Delta *)(o))->microseconds)

static bool BindDelta(Connection* cnxn, Params& params, PyObject* param)
{
    if (GET_TD_MICROSECONDS(param))
        return PyErr_Format(Error, "Microseconds are not supported in intervals.");

    WriteBuffer buf = params.Allocate(sizeof(Interval));
    if (!buf)
        return false;

    Interval* p = (Interval*)buf.writeStruct();
    p->time  = swaps8((uint64_t)GET_TD_SECONDS(param) * 1000000);
    p->day   = swaps4(GET_TD_DAYS(param));
    p->month = 0;

    return params.Bind(INTERVALOID, buf, FORMAT_BINARY);
}

static bool BindBytes(Connection* cnxn, Params& params, PyObject* param)
{
    char* p = PyBytes_AS_STRING(param);
    Py_ssize_t cb = PyBytes_GET_SIZE(param);
    params.Bind(BYTEAOID, p, cb, 1);
    return true;
}


static bool BindByteArray(Connection* cnxn, Params& params, PyObject* param)
{
    char* p = PyByteArray_AS_STRING(param);
    Py_ssize_t cb = PyByteArray_GET_SIZE(param);
    params.Bind(BYTEAOID, p, cb, 1);
    return true;
}


static bool BindFloat(Connection* cnxn, Params& params, PyObject* param)
{
    double value = PyFloat_AS_DOUBLE(param);

    WriteBuffer buf = params.Allocate(8);
    if (!buf)
        return false;
    buf.writeDouble(value);
    params.Bind(FLOAT8OID, buf, FORMAT_BINARY);
    return true;
}


static bool BindHstore(Params& params, PyObject* param)
{
    // Bind a pglib.hstore, which is a wrapper around a dictionary.
    //
    // The wire format is:
    //
    // - 32-bit count of key, value pairs.
    // - Each pair - key then value
    //   - If a string, 32-bit length followed by chars with no null terminator.
    //   - The value can be null, which is simply the length -1 with no chars.
    //
    // As usual, the network byte order is used.

    // We were passed an hstore.  Get the dictionary.
    PyObject* dict = ((Hstore*)param)->data;

    int32_t count = PyDict_Size(dict);

    if (count == 0) {
        // Handle the zero case just to keep the code simple.  (It might be simple to wrap all
        // of the code below in an if, but it is so long the top and bottom of the if wouldn't
        // fit on screen.  I'd rather duplicate a bit and keep it readable.)
        WriteBuffer buf = params.Allocate(4);
        if (!buf)
            return false;
        buf.writeInt32(count);
        params.Bind(GetHstoreOid(), buf, FORMAT_BINARY);
        return true;
    }

    // We'll bind into a single buf, so we need to determine the size.  (`cb` is "count of
    // bytes").
    //
    // If I understand correctly, Python 3 strings cache their UTF-8 representation so it is
    // okay to call PyUnicode_AsUTF8 twice on each value.  (Research this.)  If the value is
    // already in UTF8 internally, it is definitely ok.

    size_t cb = (
        4 +                     // count of pairs
        4 * 2 * count           // length indicators for each key and value
    );

    Py_ssize_t pos = 0;
    PyObject *pkey, *pval;
    while (PyDict_Next(dict, &pos, &pkey, &pval)) {
        // The key must be a string.
        const char* pszKey = PyUnicode_AsUTF8(pkey);
        if (!pszKey)
            return false;
        cb += strlen(pszKey);

        // The value can be a string or null.
        if (pval != Py_None) {
            const char* pszVal = PyUnicode_AsUTF8(pval);
            if (!pszVal)
                return false;
            cb += strlen(pszVal);
        }
    }

    WriteBuffer buf = params.Allocate(cb);
    if (!buf)
        return false;

    buf.writeInt32(count);

    pos = 0;
    while (PyDict_Next(dict, &pos, &pkey, &pval)) {

        buf.writeString(pkey);

        if (pval == Py_None) {
            buf.writeInt32(-1);
        } else  {
            buf.writeString(pval);
        }
    }

    I(buf.isFull());

    params.Bind(GetHstoreOid(), buf, FORMAT_BINARY);
    return true;
}


static bool BindUUID(Connection* cnxn, Params& params, PyObject* param)
{
    Object bytes(PyObject_GetAttrString(param, "bytes"));
    if (!bytes)
        return false;

    Py_ssize_t cb = PyBytes_GET_SIZE(bytes.Get());
    WriteBuffer buf(params.Allocate(cb));
    if (!buf)
        return false;
    buf.writeRawBytes(PyBytes_AS_STRING(bytes.Get()), cb);
    return params.Bind(UUIDOID, buf.buffer(), buf.size(), FORMAT_BINARY);
}


static bool BindJSON(Params& params, PyObject* param)
{
    PyObject* func = GetFunction("json.dumps");
    if (!func)
        return 0;
    Object text(PyObject_CallFunctionObjArgs(func, param, 0));
    if (!text)
        return false;

    Py_ssize_t cb;
    const char* pb = PyUnicode_AsUTF8AndSize(text.Get(), &cb);
    if (!pb)
        return false;

    // I'm going to copy the data for now.  We might want to consider having a version of Bind
    // that hangs onto a temporary object.
    WriteBuffer buf(params.Allocate(cb + 1));
    buf.writeRawBytes(pb, cb + 1);  // +1 for null terminator
    return params.Bind(JSONOID, buf.buffer(), buf.size(), FORMAT_TEXT);
}


static bool BindJSONWrapper(Params& params, PyObject* param) {
  // Used when an object is wrapped in a pglib.Json object.  This is used when writing
  // something other than a dictionary to a JSON column.

  Json* json = (Json*)param;
  return BindJSON(params, json->data);
}


bool BindParams(Connection* cnxn, Params& params, PyObject* args)
{
    // Binds arguments 1-n.  Argument zero is expected to be the SQL statement itself.

    if (params.count == 0)
        return true;

    if (!params.valid())
    {
        PyErr_NoMemory();
        return false;
    }

    for (int i = 0, c = PyTuple_GET_SIZE(args)-1; i < c; i++)
    {
        // Remember that a bool is a long, a datetime is a date, etc, so the order we check them in is important.

        PyObject* param = PyTuple_GET_ITEM(args, i+1);
        if (param == Py_None)
        {
            if (!BindNone(cnxn, params, param))
                return false;
        }
        else if (PyBool_Check(param))
        {
            if (!BindBool(cnxn, params, param))
                return false;
        }
        else if (PyLong_Check(param))
        {
            if (!BindLong(cnxn, params, param))
                return false;
        }
        else if (PyUnicode_Check(param))
        {
            if (!BindUnicode(cnxn, params, param))
                return false;
        }
        else if (Decimal_Check(param))
        {
            if (!BindDecimal(cnxn, params, param))
                return false;
        }
        else if (PyDateTime_Check(param))
        {
            if (!BindDateTime(cnxn, params, param))
                return false;
        }
        else if (PyDate_Check(param))
        {
            if (!BindDate(cnxn, params, param))
                return false;
        }
        else if (PyTime_Check(param))
        {
            if (!BindTime(cnxn, params, param))
                return false;
        }
        else if (PyDelta_Check(param))
        {
            if (!BindDelta(cnxn, params, param))
                return false;
        }
        else if (PyFloat_Check(param))
        {
            if (!BindFloat(cnxn, params, param))
                return false;
        }
        else if (PyBytes_Check(param))
        {
            if (!BindBytes(cnxn, params, param))
                return false;
        }
        else if (PyByteArray_Check(param))
        {
            if (!BindByteArray(cnxn, params, param))
                return false;
        }
        else if (UUID_Check(param))
        {
            if (!BindUUID(cnxn, params, param))
                return false;
        }
        else if (PyList_Check(param) || PyTuple_Check(param))
        {
            if (!BindArray(params, param))
                return false;
        }
        else if (Json_Check(param))
        {
            if (!BindJSONWrapper(params, param))
                return false;
        }
        else if (PyDict_Check(param))
        {
            if (!BindJSON(params, param))
                return false;
        }
        else if (Hstore_Check(param) && IsHstoreRegistered())
        {
            if (!BindHstore(params, param))
                return false;
        }
        else
        {
            PyErr_Format(Error, "Unable to bind parameter %d: unhandled object type %R", (i+1), param);
            return false;
        }
    }

    return true;
}
