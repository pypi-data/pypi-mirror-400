#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include "addrchk.h"
#include <stdlib.h>


int addrchk(const char *addr, int mask) {
    int errh = 0;
    int errv4 = 0;
    int errv6 = 0;
    int err = 0;

    if (mask & ADDRCHK_IPV4) {
        errv4 = addrchk_ipv4(addr);
        if (errv4 == 0 && (mask & ADDRCHK_IFACE)) return addrchk_interfaceaddr_v4(addr);
        if (errv4 == 0) return 0;
    }
    if (mask & ADDRCHK_HOSTNAME) {
        errh = addrchk_hostname(addr);
        if (errh == 0) return 0;
    }
    if (mask & ADDRCHK_IPV6) {
        if (mask & ADDRCHK_IFACE)
            return addrchk_interfaceaddr_v6(addr);
        if ((errv6 = addrchk_ipv6(addr)) == 0)
            return 0;
    }

    if (errh > err) err = errh;
    if (errv4 > err) err = errv4;
    if (errv6 > err) err = errv6;

    return err;
}

int addrchk_hostname(const char *addr) {
    int pos = 1;
    const char * p = addr;
    int state = 1; /* Last character was: 0 - alphanum, 1 - dot */
    int last_section = 1; /* last section content: 0 - alphanum, 1 - apha only */
    int last_dot = 1; /* position of last dot in the address */

    if (!*p) return pos;
    for (p = addr; *p; p++, pos++) {
        if (*p == '.') {
            if (state == 1) return pos;
            state = 1;
            last_section = 1;
            last_dot = pos;
            continue;
        }
        state = 0;
        if (!isgraph(*p)) return pos;
        if (!isalpha(*p)) last_section = 0;
    }
    if (state == 1) return pos - 1;
    if (last_section == 0) return last_dot;
    if (last_dot != 1 && pos - last_dot < 3) return last_dot; /* Single letter TLD */
    return 0;
}

int addrchk_ipv4(const char *addr) {
    int pos = 1;
    const char *p = addr;
    int state = 1; /* Last character was: 0 - num, 1 - dot */
    int last_dot = 1; /* position of last dot in the address */
    unsigned int octet = 0;
    int num_dots = 0;

    if (!p || !*p) return pos;
    for (; *p; p++, pos++) {
        if (*p == '.') {
            if (state != 0) return pos;
            state = 1;
            last_dot = pos;
            octet = 0;
            num_dots++;
            continue;
        }
        state = 0;
        if (!isdigit(*p)) return pos;
        if (pos - last_dot > 3) return pos;
        octet *= 10;
        octet += (*p - '0');
        if (octet > 255) return pos;
    }
    if (state != 0) return pos - 1;
    if (num_dots != 3) return pos - 1;
    return 0;
}

static int addrchk_ipv6_worker(const char *addr, int zeroAllowed) {
    int pos = 1;
    const char *p = addr;
    int state = 0; /* Last character was: 0 - num, 1 - colon */
    int last_colon = 0; /* position of last colon in the address */
    int gap_pos = 0;
    int num_colons = 0;
    int nonZero = 0;

    if (!p || !*p) return pos;
    for (; *p; p++, pos++) {
        if (*p == ':') {
            if (state != 0) {
                if (gap_pos) return pos;
                gap_pos = pos;
            }
            state = 1;
            last_colon = pos;
            num_colons++;
            if (num_colons > 7) return pos;
            continue;
        }
        state = 0;
        if (!isxdigit(*p)) return pos;
        if (pos - last_colon > 4) return pos;
        if (*p != '0') nonZero = 1;
    }
    if ((state != 0) && ((pos - gap_pos) != 1)) return pos - 1; /*double colon is fine at the end, but not a single one*/
    if (num_colons < 2) return pos - 1;
    if ((gap_pos == 0) && (num_colons < 7)) return pos - 1;
    if (!zeroAllowed && !nonZero) return 1;

    return 0;
}

int addrchk_ipv6(const char *addr) {
    return addrchk_ipv6_worker(addr, 1);
}

int addrchk_interfaceaddr_v4(const char *addr) {
    int a1, a2, a3, a4;
    if (sscanf(addr, "%d.%d.%d.%d", &a1, &a2, &a3, &a4) != 4) return 1;
    if (a1 == 0 || a1 == 127 || a1 == 224) return 1;
    if ((a2 | a3 | a4) == 0) return 1;
    if (a1 == 255 && a2 == 255 && a3 == 255 && a4 == 255) return 1;
    return 0;
}

int addrchk_interfaceaddr_v6(const char *addr) {
    unsigned char out_addr[IPADDR_IPV6_SZ];
    int ret = addrchk_ipv6_worker(addr, 0);
    if (ret)
        return ret;
    if ((ret = addrchk_ipv6_assign_from_str(addr, out_addr, NULL)) != 0)
        return ret;
    switch (addrchk_ipv6_addr_scope(out_addr)) {
        case IPADDR_SCOPE_UNSPECIFIED:
        case IPADDR_SCOPE_V6_GLOBAL_UNICAST:
        case IPADDR_SCOPE_V6_LOCAL_UNICAST:
        case IPADDR_SCOPE_V6_LINK_LOCAL_UNICAST:
            break;
        default:
            ret = 10;
    }
    return ret;
}

int addrchk_common_name(const char *cn) {
    if (addrchk(cn, ADDRCHK_HOSTNAME | ADDRCHK_IPV4 | ADDRCHK_IFACE) == 0) return 0;
    if (addrchk(cn, ADDRCHK_IPV6 | ADDRCHK_IFACE) == 0) return 1;
    if (cn[0] != '[') return 1;
    int len = strlen(cn);
    if (len < 3) return 2;
    if (cn[len - 1] != ']') return len;
    char *cnin = (char *)malloc(len - 1);
    if (cnin == NULL) return 1;
    strncpy(cnin, cn + 1, len - 2);
    cnin[len - 2] = '\0';
    int ipv6err = addrchk(cnin, ADDRCHK_IPV6 | ADDRCHK_IFACE);
    free(cnin);
    return ipv6err;
}

unsigned int addrchk_ipv4_addr_scope(const unsigned int addr) {
#define IPADDR_IPV4_UINT(b1, b2, b3, b4)    (((unsigned)(b1) << 24u) | ((unsigned)(b2) << 16u) | ((unsigned)(b3) << 8u) | (unsigned)(b4))
    unsigned int scope = IPADDR_SCOPE_V4_PUBLIC;

    if (addr == IPADDR_IPV4_UINT(0, 0, 0, 0))
        scope = IPADDR_SCOPE_UNSPECIFIED;
    else if (addr == IPADDR_IPV4_UINT(127, 0, 0, 1))
        scope = IPADDR_SCOPE_V4_LOOPBACK;
    else if (addr == IPADDR_IPV4_UINT(255, 255, 255, 255))
        scope = IPADDR_SCOPE_V4_BROADCAST;
    else if ((addr >= IPADDR_IPV4_UINT(224, 0, 0, 0)) && (addr <= IPADDR_IPV4_UINT(239, 255, 255, 255)))
        scope = IPADDR_SCOPE_V4_MULTICAST;
    else if (((addr >= IPADDR_IPV4_UINT(10, 0, 0, 0)) && (addr <= IPADDR_IPV4_UINT(10, 255, 255, 255))) ||
             ((addr >= IPADDR_IPV4_UINT(172, 16, 0, 0)) && (addr <= IPADDR_IPV4_UINT(172, 31, 255, 255))) ||
             ((addr >= IPADDR_IPV4_UINT(192, 168, 0, 0)) && (addr <= IPADDR_IPV4_UINT(192, 168, 255, 255))))
        scope = IPADDR_SCOPE_V4_PRIVATE;
    else if ((addr >= IPADDR_IPV4_UINT(169, 254, 0, 0)) && (addr <= IPADDR_IPV4_UINT(169, 254, 255, 255)))
        scope = IPADDR_SCOPE_V4_AUTO_CONF;

    return scope;
#undef IPADDR_IPV4_UINT
}

unsigned int addrchk_ipv6_addr_scope(const unsigned char *addr) {
    //| 3 | 45 bits             | 16 bits   | 64 bits      |
    //+---+---------------------+-----------+--------------+
    //|001|global routing prefix| subnet ID | interface ID |
    //+---+---------------------+-----------+--------------+
    const unsigned char ipv6_addr_global_unicast_byte = 0x20;
    //| 7 bits  |1|  40 bits  |  16 bits  |     64 bits      |
    //+---------+-+-----------+-----------+------------------+
    //| 1111110 |L| Global ID | Subnet ID |   Interface ID   |
    //+---------+-+-----------+-----------+------------------+
    const unsigned char ipv6_addr_local_unicast_byte = 0xFC;
    //| 8      | 4   | 4   | 112 bits |
    //+------ -+-----+-----+----------+
    //|11111111|flags|scope| group ID |
    //+--------+-----+-----+----------+
    const unsigned char ipv6_addr_multicast_byte = 0xFF;
    //| 10 bits  | 54 bits   | 64 bits      |
    //+----------+-----------+--------------+
    //|1111111010| 0         | interface ID |
    //+----------+-----------+--------------+
    static const unsigned char ipv6_addr_link_local_unicast[IPADDR_IPV6_SZ] = {0xFE, 0x80, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    //| 80 bits                 | 16 | 32 bits      |
    //+-------------------------+----+--------------+
    //|0000.................0000|FFFF| IPv4 address |
    //+-------------------------+----+--------------+
    static const unsigned char ipv6_addr_ipv4_mapped[IPADDR_IPV6_SZ] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0xFF, 0xFF, 0, 0, 0, 0};
    static const unsigned char ipv6_addr_unspec[IPADDR_IPV6_SZ]      = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00, 0x00, 0, 0, 0, 0};
    static const unsigned char ipv6_addr_loopback[IPADDR_IPV6_SZ]    = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x00, 0x00, 0, 0, 0, 1};
    unsigned int scope = IPADDR_SCOPE_UNKNOWN;

    if (addr[0] != 0) {
        if ((addr[0] & 0xE0) == ipv6_addr_global_unicast_byte)
            scope = IPADDR_SCOPE_V6_GLOBAL_UNICAST;
        else if ((addr[0] & 0xFE) == ipv6_addr_local_unicast_byte)
            scope = IPADDR_SCOPE_V6_LOCAL_UNICAST;
        else if ((addr[0] & 0xFF) == ipv6_addr_multicast_byte)
            scope = IPADDR_SCOPE_V6_MULTICAST;
        else if (memcmp(addr, ipv6_addr_link_local_unicast, 8) == 0)
            scope = IPADDR_SCOPE_V6_LINK_LOCAL_UNICAST;
    } else if (memcmp(addr, ipv6_addr_unspec, sizeof(ipv6_addr_unspec)) == 0)
        scope = IPADDR_SCOPE_UNSPECIFIED;
    else if (memcmp(addr, ipv6_addr_loopback, sizeof(ipv6_addr_loopback)) == 0)
        scope = IPADDR_SCOPE_V6_LOOPBACK;
    else if (memcmp(addr, ipv6_addr_ipv4_mapped, sizeof(ipv6_addr_ipv4_mapped) - 4) == 0)
        scope = IPADDR_SCOPE_V6_IPV4_MAPPED;

    return scope;
}

unsigned int addrchk_ipv6_mcast_scope(const unsigned char *addr) {
    unsigned int scope = addr[1] & 0x0F;

    switch (scope) {
        case IPADDR_V6_MCAST_SCOPE_INTERFACE_LOCAL:
        case IPADDR_V6_MCAST_SCOPE_LINK_LOCAL:
        case IPADDR_V6_MCAST_SCOPE_ADMIN_LOCAL:
        case IPADDR_V6_MCAST_SCOPE_SITE_LOCAL:
        case IPADDR_V6_MCAST_SCOPE_ORGANIZATION_LOCAL:
        case IPADDR_V6_MCAST_SCOPE_GLOBAL:
            break;
        default:
            scope = IPADDR_V6_MCAST_SCOPE_UNKNOWN;
    }
    return scope;
}

/* The format needs to be verified before calling this function */
unsigned int addrchk_ipv6_assign_from_str(const char *in_addr, unsigned char *out_addr, unsigned *pDispFlags) {
    const char *pcol, *p;
    unsigned v6parts[8];
    const char *colons[sizeof(v6parts) / sizeof(v6parts[0]) + 1];
    unsigned int numParts = 0;
    int hasGap = 0;
    unsigned int i, displayFlags = 0;
    unsigned int ippos = 0;

    if ((in_addr == NULL) || (*in_addr == '\0'))
        return 1;

    if (*(p = in_addr) == ':')
        p++;
    for (;;) {
        pcol = strchr(p, ':');
        if (pcol != p) {
            if (sscanf(p, "%x", &v6parts[numParts]) != 1)
                return 3;
        } else {
            if (hasGap != 0)
                return 2;
            v6parts[numParts] = 0;
            hasGap = 1;
        }
        colons[numParts++] = p;
        if (pcol == NULL) {
            colons[numParts] = in_addr + strlen(in_addr) + 1;
            break;
        }
        p = pcol + 1;
        if (*p == '\0') {
            colons[numParts] = p;
            break;
        }
        if (numParts >= (sizeof(v6parts) / sizeof(v6parts[0])))
            return 4;
    }

    for (i = 0; (i < numParts) && (ippos < IPADDR_IPV6_SZ); i++) {
        unsigned int g, partLen = colons[i + 1] - colons[i];
        if (partLen == 1) {
            // Gap in the address
            for (g = 0; g < (sizeof(v6parts) / sizeof(v6parts[0]) - numParts) && (ippos < IPADDR_IPV6_SZ); g++) {
                out_addr[ippos++] = 0;
                out_addr[ippos++] = 0;
                displayFlags >>= 3;
            }
        }
        if (ippos < IPADDR_IPV6_SZ) {
            out_addr[ippos + 0] = (unsigned char)((v6parts[i] >> 8) & 0xFF);
            out_addr[ippos + 1] = (unsigned char)(v6parts[i] & 0xFF);
            ippos += 2;
            displayFlags >>= 3;
            displayFlags |= ((partLen - 1) << 21) & 0xE00000;
        }
    }
    if (pDispFlags != NULL)
        *pDispFlags = displayFlags;
    return 0;
}

unsigned int addrchk_ipv4_addr_scope_str(const char *addr) {
    unsigned scope = IPADDR_SCOPE_UNKNOWN;
    unsigned int v41, v42, v43, v44;

    if ((addrchk_ipv4(addr) == 0) && (sscanf(addr, "%3u.%3u.%3u.%3u", &v41, &v42, &v43, &v44) == 4))
        scope = addrchk_ipv4_addr_scope((v41 << 24) | (v42 << 16) | (v43 << 8) | v44);
    return scope;
}

unsigned int addrchk_ipv6_addr_scope_str(const char *in_addr, unsigned char *out_addr) {
    unsigned scope = IPADDR_SCOPE_UNKNOWN;

    if (addrchk_ipv6(in_addr) == 0) {
        if (addrchk_ipv6_assign_from_str(in_addr, out_addr, NULL) == 0)
            scope = addrchk_ipv6_addr_scope(out_addr);
    }
    return scope;
}

unsigned int addrchk_ipv6_mcast_scope_str(const char *addr) {
    unsigned scope = IPADDR_V6_MCAST_SCOPE_UNKNOWN;
    unsigned char ipv6_addr[IPADDR_IPV6_SZ];

    if (addrchk_ipv6_addr_scope_str(addr, ipv6_addr) == IPADDR_SCOPE_V6_MULTICAST)
        scope = addrchk_ipv6_mcast_scope(ipv6_addr);
    return scope;
}


