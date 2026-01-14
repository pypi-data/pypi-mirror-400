
void RegisterHstore(Oid oid);
bool IsHstore(Oid oid);
Oid GetHstoreOid();

bool IsHstoreRegistered();

PyObject* GetHstore(const char* p);

extern PyTypeObject HstoreType;

struct Hstore
{
    PyObject_HEAD
    PyObject* data;
    // The underlying dictionary.
};


#define Hstore_Check(op) PyObject_TypeCheck(op, &HstoreType)
#define Hstore_CheckExact(op) (Py_TYPE(op) == &HstoreType)
