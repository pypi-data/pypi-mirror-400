//---------------------------------------------------------------------------------------
// IP Address Wrapper Class
// 
//---------------------------------------------------------------------------------------

#ifndef _CIPADDR_H
#define _CIPADDR_H

#include <stdint.h>
#include <cstring>
#include <string>
#include "addrchk.h"

#define CIPADDR_IPV4 0x80000000

#define IPADDR_CONSTR_MODE_NTWKORDER   0
#define IPADDR_CONSTR_MODE_UNSERIALIZE 1

class IPAddr {
    public:
        IPAddr() {
            memset(&_view, 0, sizeof(_view));
            _view.displayFlags = CIPADDR_IPV4; // V4 by default
        }

        // copy constructor
        IPAddr(const IPAddr& rhs) { operator=(rhs); }

        // construct from the string representation (0.0.0.0)
        IPAddr(const char* const ipAddress)  { assignFromString(ipAddress); }
        IPAddr(const std::string& ipAddress) { assignFromString(ipAddress); }

        // construct from the binary representation
        IPAddr(const int ipAddress) { *this = ipAddress; }
        IPAddr(const unsigned char* const bytes, int mode) { if(mode == IPADDR_CONSTR_MODE_UNSERIALIZE) unserialize(bytes); else assignV6NtwkOrder(bytes); }

        // address version
        bool isV4() const { return (_view.displayFlags == CIPADDR_IPV4); }
        bool isV6() const { return !isV4(); }

        // assignment from another instance
        IPAddr& operator=(const IPAddr& rhs);

        // assignment from a string
        IPAddr& operator=(const char* const ipAddress)
        {
            assignFromString(ipAddress);
            return *this;
        }

        // assignment from a string
        IPAddr& operator=(const std::string& ipAddress)
        {
            assignFromString(ipAddress);
            return *this;
        }

        // assignment from a binary value
        IPAddr& operator=(const int ipAddress)
        {
            _view._address.v4 = ipAddress;
            _view.displayFlags = CIPADDR_IPV4;
            return *this;
        }

        // assignment from a binary string
        void unserialize(const unsigned char* const bytes);

        // comparison
        bool operator==(const IPAddr& rhs) const;
        bool operator!=(const IPAddr& rhs) const { return !(*this == rhs); }
        bool operator<(const IPAddr& rhs) const;
        IPAddr operator~() const;
        const IPAddr& operator++();
        IPAddr operator+(int offset) const;

        // fetch the address value
        int get() const { return (isV4()) ? _view._address.v4 : 0; }
        const unsigned char* getV6NtwkOrder() const { return (isV6()) ? _view._address.v6 : ipv6_addr_unspec; }

        // size of the binary representation
        int sizeV4() const { return sizeof(_view._address.v4); }
        int sizeV6() const { return sizeof(_view._address.v6); }

        void assignV4(const unsigned char* const bytes);
        void assignV6NtwkOrder(const unsigned char *const bytes);

        const unsigned char* serialize() const { return (unsigned char*)&_view; }
        int serializedSize() const { return sizeof(_view); }

        IPAddr operator & (const IPAddr& p) const;
        IPAddr operator | (const IPAddr& p) const;
        IPAddr mask(unsigned int prefixLen) const;

        // is '0.0.0.0'
        bool isZero() const;

        // Set IPv6 format to show all sections and pad them with zeroes
        void expandV6() { if (isV6()) _view.displayFlags = ~CIPADDR_IPV4; }

        // generate human readable debug string
        std::string toString() const;

        static int addrChk(const char *addr, int mask) { return addrchk(addr, mask); }
        static int addrChkHostname(const char *addr)   { return addrchk_hostname(addr); }
        static int addrChkIpV4(const char *addr)       { return addrchk_ipv4(addr); }
        static int addrChkIpV6(const char *addr)       { return addrchk_ipv6(addr); }
        static int addrChkCommonName(const char *cn)   { return addrchk_common_name(cn); }
        static unsigned int addrChkIPv4AddrScope(const unsigned int addr)     { return addrchk_ipv4_addr_scope(addr); }
        static unsigned int addrChkIPv6AddrScope(const unsigned char *addr)  { return addrchk_ipv6_addr_scope(addr); }
        static unsigned int addrChkIPv6McastScope(const unsigned char *addr) { return addrchk_ipv6_mcast_scope(addr); }
        static int hostname2ip(int family, const char* const hostname, IPAddr& ip);

    protected:
        struct {
            union {
                uint32_t v4;
                uint8_t v6[IPADDR_IPV6_SZ];
                uint64_t v6_64[2]; //for internal use only
            } _address;
            // displayFlags: 
            // Lower 24 bits: 3 bits per address: number of digits to display (0-4)
            // displayFlags == 0x80000000 (CIPADDR_IPV4) means address is V4
            uint32_t displayFlags;
        } _view;

        void assignFromString(const char* const ipAddress);
        void assignFromString(const std::string& ipAddress) { assignFromString(ipAddress.c_str()); }

        static const uint8_t ipv6_addr_unspec[IPADDR_IPV6_SZ];
};
#endif // _CIPADDR_H
