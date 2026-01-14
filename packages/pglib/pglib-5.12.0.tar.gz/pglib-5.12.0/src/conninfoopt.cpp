
#include "pglib.h"
#include "conninfoopt.h"

PyObject* DictFromConnInfo(const ConnInfo& info) {

    Object result(PyDict_New());
    if (!result)
        return 0;

    const PQconninfoOption* p = info;

    for (; p->keyword; ++p) {
      if (p->val) {
          Object val(PyUnicode_DecodeUTF8((const char*)p->val, strlen(p->val), 0));
          if (!val)
            return 0;
          if (PyDict_SetItemString(result, p->keyword, val) == -1)
            return 0;
          val.Detach();
      }
    }

    return result.Detach();
}
