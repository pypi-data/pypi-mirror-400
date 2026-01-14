
#ifndef PGARRAYS_H
#define PGARRAYS_H

struct Params;

void Arrays_Init();

bool BindArray(Params& params, PyObject* param);

PyObject* GetInt4Array(const char* p);
// Reads an INT4ARRAYOID array result and returns a list of integers.

PyObject* GetInt8Array(const char* p);
PyObject* GetTextArray(const char* p);
PyObject* GetDateArray(const char* p);
PyObject* GetJSONBArray(const char* p);
PyObject* GetFloat8Array(const char* p);

#endif
