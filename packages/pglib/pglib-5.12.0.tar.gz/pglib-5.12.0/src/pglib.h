#ifndef PGLIB_H
#define PGLIB_H

#ifdef _MSC_VER
#define _CRT_SECURE_NO_WARNINGS
#endif

#ifdef __APPLE__
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wnullability-completeness"
#endif

extern "C"
{
#include <libpq-fe.h>
}

#include <stdint.h>

#define PY_SSIZE_T_CLEAN 1

#include <Python.h>
#include <floatobject.h>
#include <longobject.h>
#include <boolobject.h>
#include <unicodeobject.h>
#include <structmember.h>

#ifdef _MSC_VER
#include <winsock2.h> // ntohl, etc.
#define PRIi64 "%I64d"
#else
#include <arpa/inet.h> // ntohl, etc.
#endif

#if PY_VERSION_HEX < 0x03030000
#error This branch is for Python 3.3+
#endif

#ifdef __APPLE__
// Turn up clang compiler warnings.
#endif

#ifndef _countof
#define _countof(a) (sizeof(a) / sizeof(a[0]))
#endif

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#ifdef UNUSED
#undef UNUSED
#endif
inline void UNUSED(...) { }

#define MAX(a,b) (((a)>(b))?(a):(b))

extern PyObject* Error;

// From src/include/catalog/pg_type.dat

#define ANYARRAYOID    2277
#define ANYOID         2276
#define BOOLOID        16
#define BPCHAROID      1042
#define BYTEAOID       17
#define CASHOID        790
#define DATEOID        1082
#define DATEARRAYOID   1182
#define FLOAT4OID      700
#define FLOAT8OID      701
#define FLOAT8ARRAYOID 1022
#define INT2ARRAYOID   1005
#define INT2OID        21
#define INT4ARRAYOID   1007
#define INT4OID        23
#define INT8ARRAYOID   1016
#define INT8OID        20
#define INTERVALOID    1186
#define NAMEOID        19
#define NUMERICOID     1700
#define OIDOID         26
#define TEXTARRAYOID   1009
#define TEXTOID        25
#define TIMEOID        1083
#define TIMESTAMPOID   1114
#define TIMESTAMPTZOID 1184
#define UNKNOWNOID     705
#define UUIDOID        2950
#define VARCHAROID     1043
#define JSONOID        114
#define JSONBOID       3802
#define JSONBARRAYOID  3807

//  #define TIMESTAMPARRAYOID 1115
//  #define TIMEARRAYOID 1183
//  #define TIMESTAMPTZOID 1184
//  #define TIMESTAMPTZARRAYOID 1185


enum
{
    FORMAT_TEXT = 0,
    FORMAT_BINARY = 1
};


// -----------------------------------------------------------------------------------------------
// Debug

#if defined(PGLIB_ASSERT)
#if _MSC_VER
  #include <crtdbg.h>
#endif
  inline void FailAssert(const char* szFile, int line, const char* szExpr)
  {
      printf("assertion failed: %s(%d)\n%s\n", szFile, line, szExpr);
#if _MSC_VER
      __debugbreak(); // _CrtDbgBreak();
#else
      assert(0);
#endif
  }
  #define I(expr) if (!(expr)) FailAssert(__FILE__, __LINE__, #expr);
  #define N(expr) if (expr) FailAssert(__FILE__, __LINE__, #expr);
#else
  #define I(expr)
  #define N(expr)
#endif



// -----------------------------------------------------------------------------------------------
// C++ wrappers for objects.  No exceptions.

struct Object
{
    PyObject* p;

    // Borrows the reference (takes ownership without adding a new reference).
    Object(PyObject* _p = 0) { p = _p; }

    // If it still has the pointer, it dereferences it.
    ~Object() { Py_XDECREF(p); }

    operator PyObject*() { return p; }
    PyObject* Get() { return p; }

    void Attach(PyObject* _p)
    {
        // I(p == 0);
        p = _p;
    }

    void AttachAndIncrement(PyObject* _p)
    {
        // I(p == 0);
        p = _p;
        Py_INCREF(p);
    }

    PyObject* Detach()
    {
        PyObject* _p = p;
        p = 0;
        return _p;
    }
};

struct Tuple : public Object
{
    Tuple(Py_ssize_t len)
        : Object(PyTuple_New(len))
    {
    }

    void BorrowItem(Py_ssize_t i, PyObject* item)
    {
        // Sets the item at the given index and borrows the reference (i.e. does not increment
        // item's reference count).
        PyTuple_SET_ITEM(p, i, item);
    }

    void IncItem(Py_ssize_t i, PyObject* item)
    {
        // Sets the item at the given index and increments its reference count.
        PyTuple_SET_ITEM(p, i, item);
        Py_XINCREF(item);
    }

    PyObject* GetItem(Py_ssize_t i)
    {
        return PyTuple_GET_ITEM(p, i);
    }

    operator bool() { return p != 0; }

    operator PyTupleObject*() { return (PyTupleObject*)p; }
};

struct List : public Object
{
    List() {}

    List(Py_ssize_t len)
        : Object(PyList_New(len))
    {
    }

    PyObject* Join(PyObject* sep)
    {
        return PyUnicode_Join(sep, p);
    }

    bool AppendAndIncrement(PyObject* o)
    {
        if (PyList_Append(p, o) == -1)
            return false;
        Py_INCREF(o);
        return true;
    }

    bool AppendAndBorrow(PyObject* o)
    {
        return PyList_Append(p, o) == 0;
    }

    void SET_ITEM(int i, PyObject* o)
    {
        PyList_SET_ITEM(p, i, o);
    }
};

struct ResultHolder
{
    // Designed to hold a result on the stack.

    PGresult* p;
    ResultHolder(PGresult* _p = 0) { p = _p; }
    ~ResultHolder()
    {
        if (p)
            PQclear(p);
    }

    void operator=(PGresult* _p) { p = _p; }

    operator PGresult*() { return p; }

    PGresult* Detach()
    {
        PGresult* tmp = p;
        p = 0;
        return tmp;
    }
};

template <class T>
struct MemHolder
{
    T* p;
    MemHolder(T* _p = 0)
    {
        p = _p;
    }

    ~MemHolder()
    {
        if (p)
            PQfreemem(p);
    }

    void operator=(T* _p) { p = _p; }

    operator T*()
    {
        return p;
    }

    T* Detach()
    {
        T* tmp = p;
        p = 0;
        return tmp;
    }
};

extern PyObject* strComma;
extern PyObject* strParens;
extern PyObject* strLeftParen;
extern PyObject* strRightParen;
extern PyObject* strEmpty;

#endif // PGLIB_H
