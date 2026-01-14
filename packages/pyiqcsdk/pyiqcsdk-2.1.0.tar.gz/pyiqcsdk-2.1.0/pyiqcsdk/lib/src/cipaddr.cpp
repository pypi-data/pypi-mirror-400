#if (defined(_WIN16) || defined(_WIN32) || defined(_WIN64)) && !defined(__WINDOWS__)
#	define __WINDOWS__
#endif

#if defined(__linux__) || defined(__CYGWIN__)
#	define __LINUX__
#endif


#include <stdio.h>
#if defined(__WINDOWS__)
#   include <winsock2.h> //W
#else 
#   include <arpa/inet.h>
#endif
#include "eendian.h" //W
#include "cipaddr.h"
#include "bitalgs.h"

const uint8_t IPAddr::ipv6_addr_unspec[IPADDR_IPV6_SZ] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

IPAddr& IPAddr::operator=(const IPAddr& rhs) {
    if(this != &rhs)
        memcpy(&_view, &rhs._view, sizeof(_view));
    return *this;
}

bool IPAddr::operator==(const IPAddr& rhs) const {
    bool v4 = isV4();
    if (v4 != rhs.isV4()) return false;
    if (v4) return _view._address.v4 == rhs._view._address.v4;
    return ((_view._address.v6_64[0] == rhs._view._address.v6_64[0]) && (_view._address.v6_64[1] == rhs._view._address.v6_64[1]));
}

bool IPAddr::operator<(const IPAddr& rhs) const {
    if (isV4()) return _view._address.v4 < rhs._view._address.v4;
    return memcmp(_view._address.v6, rhs._view._address.v6, sizeof(_view._address.v6)) < 0;
}

IPAddr IPAddr::operator ~() const {
    if (isV4()) return ~_view._address.v4;
    return *this; // "~" does not apply to IPv6
}

const IPAddr& IPAddr::operator ++() {
    if (isV4()) ++_view._address.v4; // "~" does not apply to IPv6
    return *this;
}

IPAddr IPAddr::operator+(int offset) const {
    if (isV4()) return _view._address.v4 + offset;
    return *this;
}

void IPAddr::assignV4(const unsigned char* const bytes) {
    _view.displayFlags = CIPADDR_IPV4;
    memcpy(&_view._address.v4, bytes, sizeof(_view._address.v4));
}

void IPAddr::assignV6NtwkOrder(const unsigned char *const bytes) {
    unsigned ui, lz, fl, dist, maxdist = 2;
    unsigned dispFlgs[8];
    unsigned dispDist[8];
    int zidx = -1;

    memcpy(&_view._address.v6, bytes, sizeof(_view._address.v6));

    /* IPv6 display canonization (RFC5952) */
    memset(dispDist, 0, sizeof(dispDist));
    for(ui = 0; ui < (sizeof(dispFlgs) / sizeof(dispFlgs[0])); ui++) {
        lz = clz_byte(bytes[2 * ui]);
        if(lz == 8)
            lz += clz_byte(bytes[2 * ui + 1]);
        lz >>= 2; /*leading zero quadbits*/
        if((dispFlgs[ui] = 4 - lz) == 0) {
            if(zidx < 0)
                zidx = (int)ui;
        } else if(zidx >= 0) { /*zero sequence ended*/
            dispDist[zidx] = dist = ui - (unsigned)zidx;
            if(dist > maxdist)
                maxdist = dist;
            zidx = -1;
        }
    }
    if(zidx >= 0) { /*terminate last sequence of zeros*/
        dispDist[zidx] = dist = ui - (unsigned)zidx;
        if(dist > maxdist)
            maxdist = dist;
    }

    _view.displayFlags = 0;
    for(ui = 0; ui < (sizeof(dispDist) / sizeof(dispDist[0]));) {
        if((dist = dispDist[ui]) == 0) {
            _view.displayFlags = (_view.displayFlags >> 3u) | (dispFlgs[ui] << 21u);
            ui++;
            continue;
        }
        fl = 1u << 21u; /*shorter sequences of zeroes have to be displayed*/
        if(dist >= maxdist) {
            fl = 0;
            maxdist = ~0u; /*only one :: collapsed sequence*/
        }
        ui += dist;
        do {
            _view.displayFlags = (_view.displayFlags >> 3u) | fl;
        }while(--dist > 0);
    }
}

void IPAddr::unserialize(const unsigned char* const bytes) {
    memset(&_view, 0, sizeof(_view));
    memcpy(&_view, bytes, serializedSize());
}

bool IPAddr::isZero() const {
    if (isV4()) return _view._address.v4 == 0;
    return ((_view._address.v6_64[0] == 0) && (_view._address.v6_64[1] == 0));
}

std::string IPAddr::toString() const {
    static const char lowHexTbl[16] = {'0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f'};
    char buf[40];
    unsigned remains = sizeof(buf);

    if (isV4()) {
        remains -= snprintf(buf, sizeof(buf), "%d.%d.%d.%d",
                 (_view._address.v4 >> 24) & 0xff,
                 (_view._address.v4 >> 16) & 0xff,
                 (_view._address.v4 >> 8) & 0xff,
                 _view._address.v4 & 0xff
                 );
    }
    else {
        char *wpos = buf;
        unsigned int i, df, displayFlags = _view.displayFlags;
        bool gapExists = false;

        for (i = 0, remains++/*offset first : char*/; (i < (IPADDR_IPV6_SZ / 2)) && (remains > 0); i++, displayFlags >>= 3) {
            df = displayFlags & 7;
            if (df > 0) {
                unsigned char ch;

                if (df > 4)
                    df = 4;

                if (df >= 3) {
                    ch = _view._address.v6[2 * i];
                    if (df > 3)
                        *wpos++ = lowHexTbl[(ch >> 4) & 0x0F];
                    *wpos++ = lowHexTbl[ch & 0x0F];
                }
                ch = _view._address.v6[2 * i + 1];
                if (df > 1)
                    *wpos++ = lowHexTbl[(ch >> 4) & 0x0F];
                *wpos++ = lowHexTbl[ch & 0x0F];

                remains -= df + 1/*takes care about previous : char*/;
                *wpos++ = ':';
            }
            else {
                if (!gapExists && remains > 2) {
                    if (i == 0) {
                        *wpos++ = ':';
                        remains--;
                    }
                    *wpos++ = ':';
                    remains--;
                    gapExists = true;
                }
            }
        }
        if (df == 0) /*terminate properly when double colon is at the end*/
            remains--;
    }
    return std::string(buf, sizeof(buf) - remains);
}

void IPAddr::assignFromString(const char* const ipAddress) {
    unsigned int v41, v42, v43, v44;
    memset(&_view, 0, sizeof(_view));
    _view.displayFlags = CIPADDR_IPV4; // V4 by default

    if (ipAddress == NULL || *ipAddress == '\0') return;
    if (addrchk(ipAddress, ADDRCHK_IPV4 | ADDRCHK_IPV6) != 0) return;

    if (sscanf(ipAddress, "%3u.%3u.%3u.%3u", &v41, &v42, &v43, &v44) == 4) {
        _view._address.v4 = (v41 << 24) | (v42 << 16) | (v43 << 8) | v44;
        return;
    }

    // IPv6
    _view.displayFlags = 0;
    addrchk_ipv6_assign_from_str(ipAddress, _view._address.v6, &_view.displayFlags);
}

IPAddr IPAddr::operator | (const IPAddr& p) const {
    if (isV4()) {
        if (!p.isV4()) return IPAddr();
        return IPAddr(get() | p.get());
    }
    IPAddr ret(*this);
    ret._view._address.v6_64[0] |= p._view._address.v6_64[0];
    ret._view._address.v6_64[1] |= p._view._address.v6_64[1];
    ret._view.displayFlags = ~CIPADDR_IPV4;
    return ret;
}

IPAddr IPAddr::operator & (const IPAddr& p) const {
    if (isV4()) {
        if (!p.isV4()) return IPAddr();
        return IPAddr(get() & p.get());
    }
    IPAddr ret(*this);
    ret._view._address.v6_64[0] &= p._view._address.v6_64[0];
    ret._view._address.v6_64[1] &= p._view._address.v6_64[1];
    return ret;
}

IPAddr IPAddr::mask(unsigned int prefixLen) const {
    if (isV4()) {
        if (prefixLen == 0) return IPAddr();
        if (prefixLen >= 32) return *this;
        int mask = (0xFFFFFFFF << (32 - prefixLen));
        return IPAddr(get() & mask);
    }
    if (prefixLen >= 128) return *this;
    IPAddr ret(*this);
    for (unsigned i = 0; i < (sizeof(_view._address.v6) / sizeof(_view._address.v6[0])); i++) {
        if (prefixLen >= 8) {
            prefixLen -= 8;
            continue;
        }
        if (prefixLen == 0) {
            ret._view._address.v6[i] = 0;
            continue;
        }
        unsigned char mask = (unsigned char)(0xFF << (8 - prefixLen));
        ret._view._address.v6[i] &= mask;
        prefixLen = 0;
    }
    return ret;
}



