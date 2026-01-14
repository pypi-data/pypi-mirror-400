
// Common code for pglib.defaults and Connection.info

struct ConnInfo {
  PQconninfoOption* info;

  ConnInfo(PQconninfoOption* _info) {
    this->info = _info;
  }

  ~ConnInfo() {
    if (info)
      PQconninfoFree(info);
  }

  operator const PQconninfoOption* () const { return this->info; }
};


PyObject* DictFromConnInfo(const ConnInfo& info);
