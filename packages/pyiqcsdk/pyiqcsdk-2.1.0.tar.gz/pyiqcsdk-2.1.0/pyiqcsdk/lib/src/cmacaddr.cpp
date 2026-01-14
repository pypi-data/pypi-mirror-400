#if (defined(_WIN16) || defined(_WIN32) || defined(_WIN64)) && !defined(__WINDOWS__)
#	define __WINDOWS__
#endif

#if defined(__linux__) || defined(__CYGWIN__)
#	define __LINUX__
#endif


#include "cmacaddr.h"
#if defined(__WINDOWS__)
#   include <winsock2.h> //W
#else 
#   include <arpa/inet.h>
#endif
#include "eendian.h" //W

static const char HexTbl[16] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
static const char HexTblLower[16] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};

// generate human readable debug string
const char* MACAddr::toString(char *out) const
{
    char *ptr = out;
    unsigned val, len;

    memcpy(ptr, "XX:XX:XX:XX:XX:XX", sizeof("XX:XX:XX:XX:XX:XX"));
    for(len = 0; len < 6; ptr += 6) {
        val = _mac.bytes[len++];
        ptr[0] = HexTbl[val >> 4];
        ptr[1] = HexTbl[val & 0xF];
        val = _mac.bytes[len++];
        ptr[3] = HexTbl[val >> 4];
        ptr[4] = HexTbl[val & 0xF];
    }
    return out;
}

std::string MACAddr::toString(int fmt) const
{
    std::string out;
    toStringFmt(&out, fmt);
    return out;
}

std::string MACAddr::toString() const
{
    char buf[20];
    return std::string(toString(buf), sizeof("XX:XX:XX:XX:XX:XX") - 1);
}

void MACAddr::toString(std::string *out) const
{
    char buf[20];
    out->assign(toString(buf), sizeof("XX:XX:XX:XX:XX:XX") - 1);
}

void MACAddr::toStringFmt(std::string *out, int fmt) const
{
    static const struct {
        unsigned char delta;
        char delimiter;
    } s_delmtab[6] = {
        { 0, '\0' }, /*MAC_FMT_NOSPACE*/
        { 1, ':' },  /*MAC_FMT_COLON*/
        { 1, '-' },  /*MAC_FMT_HYPHEN*/
        { 2, '.' },  /*MAC_FMT_WORD*/
        { 3, '-' },  /*MAC_FMT_HALFNHALF*/
        { 1, ' ' }   /*MAC_FMT_SPACE*/
    };
    char buf[20];
    const char *tbl = HexTbl;
    unsigned i, val, len, delta;
    char delimiter;

    if(fmt >= MAC_FMT_ATTR_LOWER) {
        fmt -= MAC_FMT_ATTR_LOWER;
        tbl = HexTblLower;
    }
    if((unsigned)--fmt >= (sizeof(s_delmtab) / sizeof(s_delmtab[0])))
        fmt = MAC_FMT_DEFAULT - 1;
    delta = s_delmtab[fmt].delta;
    delimiter = s_delmtab[fmt].delimiter;
    for(i = 0, len = 0;;) {
        val = _mac.bytes[i];
        buf[len++] = tbl[val >> 4];
        buf[len++] = tbl[val & 0xF];
        if(++i >= 6)
            break;
        if (delta != 0 && (i % delta == 0))
            buf[len++] = delimiter;
    }
    out->assign(buf, len);
}

static inline unsigned HexChar2Num(unsigned uCh)
{
    unsigned Dgt;

    if((Dgt = (uCh - '0')) > 9u)
        Dgt = ((uCh & ~('A' ^ 'a'))/*convert Latin chars to uppercase*/ - 'A' + 10u);

    return Dgt;
}

static inline int HexStr2Num(const char **str, unsigned char *pNum)
{
    const char *ptr = *str;
    unsigned Dgt, Num = 0;

    do {
        if((Dgt = HexChar2Num(*ptr)) > 15u)
            break;
        Num = (Num << 4u) + Dgt;
        ptr++;
    } while(*ptr);
    *pNum = (unsigned char)Num;
    *str = ptr;
    return *ptr;
}

void MACAddr::assignFromString(const char *macstr)
{
    for(unsigned i = 0; i < 6; i++, macstr++/*skip delimiter*/) {
        if(HexStr2Num(&macstr, &_mac.bytes[i]) == 0)
            break;
    }
}

bool MACAddr::isValid(const char *pmac)
{
    int sz = 6;
    bool valid = false;
    unsigned Dgt;

    for(;;) {
        if((Dgt = HexChar2Num(*pmac)) > 15u)
            break;
        pmac++;
        if((Dgt = HexChar2Num(*pmac)) > 15u)
            break;
        pmac++;
        if(--sz > 0) {
            if(*pmac++ != ':')
                break;
        } else {
            if(*pmac == '\0')
                valid = true;
            break;
        }
    }
    return valid;
}

MACAddr MACAddr::operator&(unsigned int prefixLen) const {
    MACAddr ret(*this);
    ret &= prefixLen;
    return ret;
}

MACAddr& MACAddr::operator&=(unsigned int prefixLen) {
    if (prefixLen >= 48) return *this;
    for (int i = 0; i < 6; i++) {
        if (prefixLen >= 8) {
            prefixLen -= 8;
            continue;
        }
        if (prefixLen == 0) {
            _mac.bytes[i] = 0;
            continue;
        }
        unsigned char mask = (unsigned char)(0xFF << (8 - prefixLen));
        _mac.bytes[i] &= mask;
        prefixLen = 0;
    }
    return *this;
}

MACAddr MACAddr::operator|(unsigned int prefixLen) const {
    MACAddr ret(*this);
    ret |= prefixLen;
    return ret;
}

MACAddr& MACAddr::operator|=(unsigned int prefixLen) {
    if (prefixLen >= 48) return *this;
    for (int i = 0; i < 6; i++) {
        if (prefixLen >= 8) {
            prefixLen -= 8;
            continue;
        }
        if (prefixLen == 0) {
            _mac.bytes[i] = 0xFF;
            continue;
        }
        unsigned char mask = (unsigned char)(0xFF >> prefixLen);
        _mac.bytes[i] |= mask;
        prefixLen = 0;
    }
    return *this;
}
