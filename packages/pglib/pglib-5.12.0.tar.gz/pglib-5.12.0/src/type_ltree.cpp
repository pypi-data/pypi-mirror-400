
#include "pglib.h"
#include "byteswap.h"
#include "type_ltree.h"

static Oid oidLTree = 0;


Oid GetLTreeOid() {
    return oidLTree;
}

void RegisterLTree(Oid oid)
{
    oidLTree = oid;
}

bool IsLTreeRegistered()
{
    return oidLTree != 0;
}

bool IsLTree(Oid oid)
{
    return oid == oidLTree;
}

PyObject* GetLTree(const char* p)
{
  // Pretty simple: A 1-byte version, which only supported 1 when I wrote this, followed by the
  // UTF8 (ASCII?) path.

  if (*p != 0x01) {
    PyErr_SetString(PyExc_RuntimeError, "Only ltree v1 is supported");
    return 0;
  }

  p++;
  return PyUnicode_DecodeUTF8(p, strlen(p), 0);
}
