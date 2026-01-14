
#ifndef PARAMS_H
#define PARAMS_H

void Params_Init();

struct Pool;


struct WriteBuffer
{
    // Wraps a *borrowed* parameter buffer with methods for encoding values.

    char* pbStart;              // The start of the buf
    char* pbWrite;              // The current write position
    char* pbMax;                // The end of the buf (1 byte after the buf)

    WriteBuffer(char* pb, size_t cb) {
        pbStart = pb;
        pbWrite = pb;
        pbMax   = pb + cb;
    }

    WriteBuffer(const WriteBuffer& other) {
        pbStart = other.pbStart;
        pbWrite = other.pbWrite;
        pbMax   = other.pbMax;
    }

    WriteBuffer& operator=(const WriteBuffer& other) {
        pbStart = other.pbStart;
        pbWrite = other.pbWrite;
        pbMax   = other.pbMax;
        return *this;
    }

    operator bool() const { return pbStart != 0; }

    const char* buffer() const {
        // Returns a pointer to the beginning of the buf.
        return pbStart;
    }

    size_t size() const {
        return (pbMax - pbStart);
    }

    bool available(int cb) const {
        // Are at least `cb` bytes available?
        return (pbMax - pbWrite) >= cb;
    }

    char* writeStruct() {
        // Return the rest of the buffer for writing a structure.  (You'll have to cast the
        // result.)
        char* tmp = pbWrite;
        pbWrite = pbMax;
        return tmp;
    }

    void writeOid(Oid oid) {
        writeUint32(swaps4((uint32_t)oid));
    }

    void writeUint32(uint32_t n) {
        I(available(4));
        *(uint32_t*)pbWrite = swapu4(n);
        pbWrite += 4;
    }

    void writeInt32(int32_t n) {
        I(available(4));
        *(int32_t*)pbWrite = swaps4(n);
        pbWrite += 4;
    }

    void writeUint64(uint64_t n) {
        I(available(8));
        *(uint64_t*)pbWrite = swapu8(n);
        pbWrite += 8;
    }

    void writeString(PyObject* str) {
        Py_ssize_t cch;
        const char* sz = PyUnicode_AsUTF8AndSize(str, &cch);
        I(available(4 + cch));
        writeInt32(cch);
        memcpy(pbWrite, sz, cch);
        pbWrite += cch;
    }

    void writeDouble(double n) {
        *(double*)pbWrite = swapdouble(n);
        pbWrite += 8;
    }

    void writeRawBytes(const char* pb, size_t cb) {
        I(available(cb));
        memcpy(pbWrite, pb, cb);
        pbWrite += cb;
    }

    void writeByte(uint8_t b) {
        I(available(1));
        *pbWrite++ = b;
    }

    bool isFull() const {
        return pbWrite == pbMax;
    }
};


struct Params
{
    Oid*   types;
    const char** values;
    int*   lengths;
    int*   formats;

    int count; // How many are we going to bind?
    int bound; // How many have we bound?

    Pool* pool;

    Params(int count);
    ~Params();

    bool valid() const
    {
        return types && values && lengths && formats;
    }

    WriteBuffer Allocate(size_t amount);

    bool Bind(Oid type, const void* value, int length, int format);
    bool Bind(Oid type, const WriteBuffer& buf, int format);
};


inline bool Params::Bind(Oid type, const WriteBuffer& buf, int format)
{
    return Bind(type, buf.buffer(), buf.size(), format);
}

bool BindParams(Connection* cnxn, Params& params, PyObject* args);

#endif // PARAMS_H
