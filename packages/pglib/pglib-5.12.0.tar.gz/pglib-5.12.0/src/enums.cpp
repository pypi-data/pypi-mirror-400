
#include "pglib.h"
#include "enums.h"

static int countOIDs = 0;
static Oid* enumOIDs = 0;

bool RegisterEnum(Oid oid)
{
    Oid* newa = (Oid*)malloc(sizeof(Oid) * (countOIDs + 1));
    if (!newa)
    {
        PyErr_NoMemory();
        return false;
    }

    if (countOIDs)
    {
        memcpy(newa, enumOIDs, sizeof(Oid) * countOIDs);
        free(enumOIDs);
    }

    enumOIDs = newa;
    enumOIDs[countOIDs++] = oid;

    return true;
}

bool IsEnum(Oid oid)
{
    for (int i = 0; i < countOIDs; i++)
        if (enumOIDs[i] == oid)
            return true;
    return false;
}
