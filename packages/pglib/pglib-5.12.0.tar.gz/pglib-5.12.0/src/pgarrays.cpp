// Sending and receiving arrays.  Right now we only support strings and integers, but there is
// no reason we can't add more types.
//
// I'm not sure what to do when the array is empty or all NULLs.  I'm sending as TEXT but this
// can't be written into an int[] column.
//
// Array Wire Format
// -----------------
//
// The format was determined from array_recv in src/backend/utils/adt/arrayfuncs.c
//
// The array starts with a header which I've created a struct for below: ArrayHeader.
//
// Each item is written after the header.  Each starts with a 4-byte length.  If the item is
// NULL, set the length to -1 and do not write any data.  Otherwise write the length followed
// by the data.  There does not appear to be any padding after elements (possibly because the
// header is already 32-bit aligned).
//
// Remember that all integers are in network order, so use ntohl and htonl appropriately.  All
// OSs don't seem to have an 8-byte version of this, so there are some equivalent macros in
// byteswap.h

#include "pglib.h"
#include <datetime.h>
#include "connection.h"
#include "byteswap.h"
#include "params.h"
#include "juliandate.h"
#include "errors.h"
#include "runtime.h"
#include "debug.h"


void Arrays_Init()
{
    PyDateTime_IMPORT;
};


struct ArrayHeader
{
    // The fields in a PostgreSQL array.  We use this when writing an array.  All int fields
    // will be in host / big endian, so use ntohl and htonl.
    //
    // Technically an array header only includes the first 3 fields.  Each dimension then has a
    // count and lbound.  Since we only support one dimension right now, I've put them together.

    uint32_t ndim;   // number of dimensions - we support 1
    uint32_t flags;  // binary format? 0 or 1, but unused by the server?
    Oid oid;         // type of elements
    uint32_t dim;    // length of array
    uint32_t lbound; // lower bound - set to 1
    char buffer[0];
};


struct ArrayInfo {
    // The important array fields, copied and converted to native endianess (so don't use ntohl
    // or htonl).
    Oid oid;                    // type of elements
    uint32_t len;               // number of elements
    const char* data;           // pointer to first element
};


inline uint8_t ReadU8(const char ** pp) {
    // Reads an unsigned int from `pp` *and* increments the pointer *pp.
    uint8_t n = **(uint8_t**)pp;
    *pp += sizeof(char);
    return n;
}

inline int64_t Read64(const char ** pp) {
    // Reads an int64 from `pp` *and* increments the pointer *pp.
    uint64_t n = **(uint64_t**)pp;
    *pp += sizeof(uint64_t);
    return swaps8(n);
}

inline int32_t Read32(const char ** pp) {
    // Reads an int from `pp` *and* increments the pointer *pp.
    uint32_t n = **(uint32_t**)pp;
    *pp += sizeof(uint32_t);
    return (int32_t)htonl(n);
}

inline uint32_t ReadU32(const char ** pp) {
    // Reads an unsigned int from `pp` *and* increments the pointer *pp.
    uint32_t n = **(uint32_t**)pp;
    *pp += sizeof(uint32_t);
    return htonl(n);
}

inline double ReadDouble(const char ** pp) {
    double n = **(double**)pp;
    *pp += sizeof(double);
    return swapdouble(n);
}


static PyObject* FindFirstParam(Object& seq)
{
    // Returns a *borrowed* reference to the first non-None parameter in the sequence.  Returns
    // zero if the list is empty or all are None.

    Py_ssize_t cItems = PySequence_Length(seq);
    for (int i = 0; i < cItems; i++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), i);
        if (item != Py_None)
            return item;
    }
    return 0;
}


static bool ReadArrayInfo(const char* p, ArrayInfo &info, Oid expected_type) {
    // Read the array header from `p` into `info` and return true if valid and something pglib
    // can handle.  If there is an error, an exception will be set and false will be returned.
    
    uint32_t ndim = ReadU32(&p);
    if (ndim > 1) {
        SetStringError(Error, "pglib can only read single dimensional arrays (ndim=%d)", (int)ndim);
        return false;
    }

    ReadU32(&p);  // format: 0 or 1.  Not used right now.

    info.oid = (Oid)ReadU32(&p);
    if (info.oid != expected_type) {
        SetStringError(Error, "Unable to read array.  Expected element type %u not %u",
                       (uint)expected_type, (uint)info.oid);
        return false;
    }

    // The length is within the dimension header, which we don't have if there are no dimensions.

    if (ndim != 0) {
        info.len = ReadU32(&p);
        ReadU32(&p);  // lower bound
    } else {
        info.len = 0;
    }

    info.data = p;

    return true;
}


static bool BindDateArray(Params& params, Object& seq, Py_ssize_t cItems)
{
    // Loop through the array and make sure each entry is a date.

    int cNonNull = 0;           // count of non-null items

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            if (!PyDate_Check(item))
            {
                SetStringError(Error, "array parameters must all be the same type");
                return false;
            }

            cNonNull += 1;
        }
    }

    int cbItem = sizeof(uint32_t);

    Py_ssize_t cb = sizeof(ArrayHeader) +
        (4 * cItems) +          // length indicators
        (cbItem * cNonNull);    // values


    WriteBuffer buf = params.Allocate(cb);
    if (!buf)
        return false;

    ArrayHeader* phdr = (ArrayHeader*)buf.pbStart;
    phdr->ndim   = htonl(1);
    phdr->flags  = htonl(1);
    phdr->oid    = htonl(DATEOID);
    phdr->dim    = htonl(cItems);
    phdr->lbound = htonl(1);

    char* pT = &phdr->buffer[0];

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            (*(uint32_t*)pT) = htonl(cbItem); // could be swapped and cached
            pT += 4;

            uint32_t julian = dateToJulian(PyDateTime_GET_YEAR(item), PyDateTime_GET_MONTH(item), PyDateTime_GET_DAY(item));
            julian -= JULIAN_START;

            (*(uint32_t*)pT) = htonl(julian);
            pT += cbItem;
        }
        else
        {
            (*(uint32_t*)pT) = htonl(-1);
            pT += 4;
        }
    }

    return params.Bind(DATEARRAYOID, buf, FORMAT_BINARY);
}


bool BindUnicodeArray(Params& params, Object& seq, Py_ssize_t cItems)
{
    // First loop through the array and add up the memory we'll need.  This isn't quite as
    // inefficient as it looks since the string objects will cache the UTF8 version.

    Py_ssize_t cb = sizeof(ArrayHeader);
    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        cb += 4;                // length indicator
        if (item != Py_None)
        {
            if (!PyUnicode_Check(item))
            {
                SetStringError(Error, "array parameters elements must all be the same type");
                return false;
            }

            Py_ssize_t len = 0;
            if (!PyUnicode_AsUTF8AndSize(item, &len))
                return false;
            cb += len;
        }
    }

    WriteBuffer buf = params.Allocate(cb);
    if (!buf)
        return false;

    ArrayHeader* phdr = (ArrayHeader*)buf.pbStart;
    phdr->ndim   = htonl(1);
    phdr->flags  = htonl(1);
    phdr->oid    = htonl(TEXTOID);
    phdr->dim    = htonl(cItems);
    phdr->lbound = htonl(1);

    char* pT = &phdr->buffer[0];

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            Py_ssize_t len;
            const char* sz = PyUnicode_AsUTF8AndSize(item, &len);
            if (!sz)
                return false;

            (*(uint32_t*)pT) = htonl(len);
            pT += 4;

            memcpy(pT, sz, len);
            pT += len;
        }
        else
        {
            (*(uint32_t*)pT) = htonl(-1);
            pT += 4;
        }
    }

    return params.Bind(TEXTARRAYOID, buf, FORMAT_BINARY);
}

const long MIN_SMALLINT = -32768;
const long MAX_SMALLINT = 32767;
const PY_LONG_LONG MIN_INTEGER = -2147483648LL;
const PY_LONG_LONG MAX_INTEGER = 2147483647LL;

inline int MinLongSize(PyObject* item)
{
    // Returns the number of bytes required to hold this value.  Will return 2, 4, or 8.

    int overflow;
    PY_LONG_LONG lvalue = PyLong_AsLongLongAndOverflow(item, &overflow);
    if (overflow != 0)
        return 0;

    if (lvalue < MIN_INTEGER || lvalue > MAX_INTEGER)
        return 8;
    if (lvalue < MIN_SMALLINT || lvalue > MAX_SMALLINT)
        return 4;
    return 2;
}

static const Oid MAP_INTSIZE_TO_OID[] = { 0, 0, INT2OID, 0, INT4OID, 0, 0, 0, INT8OID };
static const Oid MAP_INTSIZE_TO_ARRAYOID[] = { 0, 0, INT2ARRAYOID, 0, INT4ARRAYOID, 0, 0, 0, INT8ARRAYOID };


bool BindLongArray(Params& params, Object& seq, Py_ssize_t cItems)
{
    // Loop through the array to determine the size of integers we'll need (we send the
    // smallest possible) and how many NULLs there are so we can determine the memory needed.

    int cNonNull = 0;           // count of non-null items
    int cbItem  = 0;            // byte-size of each item

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            if (!PyLong_Check(item))
            {
                SetStringError(Error, "array parameters elements must all be the same type");
                return false;
            }

            cNonNull += 1;
            cbItem = MAX(cbItem, MinLongSize(item));
        }
    }

    Py_ssize_t cb = sizeof(ArrayHeader) +
        (4 * cItems) +          // length indicators
        (cbItem * cNonNull);    // values

    WriteBuffer buf = params.Allocate(cb);
    if (!buf)
        return false;

    ArrayHeader* phdr = (ArrayHeader*)buf.pbStart;
    phdr->ndim   = htonl(1);
    phdr->flags  = htonl(1);
    phdr->oid    = htonl(MAP_INTSIZE_TO_OID[cbItem]);
    phdr->dim    = htonl(cItems);
    phdr->lbound = htonl(1);

    char* pT = &phdr->buffer[0];

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            (*(uint32_t*)pT) = htonl(cbItem); // could be swapped and cached
            pT += 4;

            PY_LONG_LONG lvalue = PyLong_AsLongLong(item);

            if (cbItem == 2)
            {
                (*(uint16_t*)pT) = htons((uint16_t)lvalue);
            }
            else if (cbItem == 4)
            {
                (*(uint32_t*)pT) = htonl((uint32_t)lvalue);
            }
            else
            {
                (*(uint64_t*)pT) = swapu8((uint64_t)lvalue);
            }

            pT += cbItem;
        }
        else
        {
            (*(uint32_t*)pT) = htonl(-1);
            pT += 4;
        }
    }

    return params.Bind(MAP_INTSIZE_TO_ARRAYOID[cbItem], buf, FORMAT_BINARY);
}


static bool BindFloatArray(Params& params, Object& seq, Py_ssize_t cItems)
{
    // Loop through the array and make sure each entry is a float (or None).

    int cNonNull = 0;           // count of non-null items

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            if (!PyFloat_Check(item))
            {
                SetStringError(Error, "array parameters must all be the same type");
                return false;
            }

            cNonNull += 1;
        }
    }

    int cbItem = sizeof(double);

    Py_ssize_t cb = sizeof(ArrayHeader) +
        (4 * cItems) +          // length indicators
        (cbItem * cNonNull);    // values


    WriteBuffer buf = params.Allocate(cb);
    if (!buf)
        return false;

    ArrayHeader* phdr = (ArrayHeader*)buf.pbStart;
    phdr->ndim   = htonl(1);
    phdr->flags  = htonl(1);
    phdr->oid    = htonl(FLOAT8OID);
    phdr->dim    = htonl(cItems);
    phdr->lbound = htonl(1);

    char* pT = &phdr->buffer[0];

    for (Py_ssize_t iItem = 0; iItem < cItems; iItem++)
    {
        PyObject* item = PySequence_Fast_GET_ITEM(seq.Get(), iItem);
        if (item != Py_None)
        {
            (*(uint32_t*)pT) = htonl(cbItem); // could be swapped and cached
            pT += 4;

            (*(double*)pT) = swapdouble(PyFloat_AS_DOUBLE(item));
            pT += cbItem;
        }
        else
        {
            (*(uint32_t*)pT) = htonl(-1);
            pT += 4;
        }
    }

    return params.Bind(FLOAT8ARRAYOID, buf, FORMAT_BINARY);
}


bool BindArray(Params& params, PyObject* param)
{
    // Binds a list or tuple as an array.  All elements must be of the same type, though None
    // (NULL) is supported.

    Object seq = PySequence_Fast(param, "a list or tuple is required");
    if (!seq)
        return 0;

    Py_ssize_t cItems = PySequence_Length(param);

    // Figure out what kind of elements are in the array.  Find the first non-None item.

    PyObject* first = FindFirstParam(seq);

    if (!first || PyUnicode_Check(first))
        return BindUnicodeArray(params, seq, cItems);

    if (PyLong_Check(first))
        return BindLongArray(params, seq, cItems);

    if (PyDate_Check(first))
        return BindDateArray(params, seq, cItems);

    if (PyFloat_Check(first))
        return BindFloatArray(params, seq, cItems);

    SetStringError(Error, "Unhandled type in array parameter");

    return false;
}


PyObject* GetDateArray(const char* p)
{
    // Reads a DATEARRAYOID array result and returns a list of datetime.date objects.
    ArrayInfo info;
    if (!ReadArrayInfo(p, info, DATEOID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len) {
        const char* data = info.data;

        for (uint32_t i = 0; i < info.len; i++)
        {
            int32_t len = Read32(&data);

            if (len == -1)
            {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(list.Get(), i, Py_None);
            }
            else
            {
                uint32_t value = Read32(&data) + JULIAN_START;
                int year, month, date;
                julianToDate(value, year, month, date);
                PyObject* d = PyDate_FromDate(year, month, date);
                if (!d)
                    return 0;
                PyList_SET_ITEM(list.Get(), i, d);
            }
        }
    }

    return list.Detach();
}


PyObject* GetInt4Array(const char* p)
{
    // Reads an INT4ARRAYOID array result and returns a list of integers.

    ArrayInfo info;
    if (!ReadArrayInfo(p, info, INT4OID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len) {
        const char* data = info.data;

        for (uint32_t i = 0; i < info.len; i++)
        {
            int32_t len = Read32(&data);

            if (len == -1)
            {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(list.Get(), i, Py_None);
            }
            else
            {
                int32_t val = Read32(&data);
                PyObject* l = PyLong_FromLong(val);
                if (!l)
                    return 0;

                PyList_SET_ITEM(list.Get(), i, l);
            }
        }
    }

    return list.Detach();
}

PyObject* GetInt8Array(const char* p)
{
    // Reads an INT4ARRAYOID array result and returns a list of integers.

    ArrayInfo info;
    if (!ReadArrayInfo(p, info, INT8OID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len) {
        const char* data = info.data;

        for (uint32_t i = 0; i < info.len; i++)
        {
            int32_t len = Read32(&data);

            if (len == -1)
            {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(list.Get(), i, Py_None);
            }
            else
            {
                int64_t val = Read64(&data);
                PyObject* l = PyLong_FromLongLong(val);
                if (!l)
                    return 0;

                PyList_SET_ITEM(list.Get(), i, l);
            }
        }
    }

    return list.Detach();
}


PyObject* GetFloat8Array(const char* p)
{
    // Reads an FLOAT8ARRAYOID array result and returns a list of floats.

    ArrayInfo info;
    if (!ReadArrayInfo(p, info, FLOAT8OID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len) {
        const char* data = info.data;

        for (uint32_t i = 0; i < info.len; i++)
        {
            int32_t len = Read32(&data);

            if (len == -1)
            {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(list.Get(), i, Py_None);
            }
            else
            {
                double val = ReadDouble(&data);
                PyObject* o = PyFloat_FromDouble(val);
                if (!o)
                    return 0;

                PyList_SET_ITEM(list.Get(), i, o);
            }
        }
    }

    return list.Detach();
}

PyObject* GetTextArray(const char* p)
{
    ArrayInfo info;
    if (!ReadArrayInfo(p, info, TEXTOID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len > 0)
    {
        const char* pT = info.data;

        for (uint32_t i = 0; i < info.len; i++)
        {
            int32_t len = Read32(&pT);

            if (len == -1)
            {
                Py_INCREF(Py_None);
                PyList_SET_ITEM(list.Get(), i, Py_None);
            }
            else
            {
                PyObject* str = PyUnicode_DecodeUTF8(pT, len, "strict");
                if (!str)
                    return 0;
                pT += len;
                PyList_SET_ITEM(list.Get(), i, str);
            }
        }
    }

    return list.Detach();
}


PyObject* GetJSONBArray(const char* p) {
    ArrayInfo info;
    if (!ReadArrayInfo(p, info, JSONBOID)) {
        return 0;
    }

    Object list(PyList_New(info.len));
    if (!list)
        return 0;

    if (info.len > 0) {
        PyObject* func = GetFunction("json.loads");
        if (!func)
            return 0;

        const char* data = info.data;

        for (uint32_t i = 0; i < info.len; i++) {
            // Each element is (len, version (1), cstr)

            int32_t len = Read32(&data);

            PyObject* value = 0;
            if (len == -1) {
                value = Py_None;
                Py_INCREF(Py_None);
            } else {
                uint8_t version = ReadU8(&data);

                if (version != 1) {
                    return SetStringError(Error, "Unexpected JSONB version %u in array", (uint32_t)version);
                }

                value = PyObject_CallFunction(func, "s", data);
                if (!value)
                    return 0;
                data += len - 1;  // -1 because we already incremented past version
            }

            PyList_SET_ITEM(list.Get(), i, value);
        }
    }

    return list.Detach();
}
