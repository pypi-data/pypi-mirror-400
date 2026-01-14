//---------------------------------------------------------------------------------------
// MAC Address Wrapper Class
// 
// File: cmacaddr.h
//
//---------------------------------------------------------------------------------------

#ifndef _CMACADDR_H
#define _CMACADDR_H

#include <stdlib.h>
#include <cstring>
#include <string>

#define MAC_FMT_DEFAULT     MAC_FMT_COLON
#define MAC_FMT_NOSPACE     1 /*XXXXXXXXXXXX*/
#define MAC_FMT_COLON       2 /*XX:XX:XX:XX:XX:XX*/
#define MAC_FMT_HYPHEN      3 /*XX-XX-XX-XX-XX-XX*/
#define MAC_FMT_WORD        4 /*XXXX.XXXX.XXXX*/
#define MAC_FMT_HALFNHALF   5 /*XXXXXX-XXXXXX*/
#define MAC_FMT_SPACE       6 /*XX XX XX XX XX XX*/
#define MAC_FMT_ATTR_LOWER  100

#include "eendian.h" //W

class MACAddr
{
    public:
        MACAddr() { _mac.val64 = 0; }
        MACAddr(const MACAddr& rhs) { operator=(rhs); }
        // from the string representation (00:00:00:00:00:00)
        MACAddr(const char* const mac)  { _mac.val64 = 0; assignFromString(mac); }
        MACAddr(const std::string& mac) { _mac.val64 = 0; assignFromString(mac); }
        // from the binary representation (6 bytes)
        MACAddr(const unsigned char* const mac) {
            _mac.val64 = 0;
            memcpy(_mac.bytes, mac, sizeof(_mac.bytes));
        }
        // from a binary hi16/lo32 pair
        MACAddr(unsigned mac_hi16, unsigned mac_lo32) { _mac.val64 = 0; assign(mac_hi16, mac_lo32); }
        // assignment from another instance
        MACAddr& operator=(const MACAddr& rhs) {
            if(this != &rhs)
                _mac.val64 = rhs._mac.val64;
            return *this;
        }
        // assignment from a char* string
        MACAddr& operator=(const char* const mac) {
            assignFromString(mac);
            return *this;
        }
        // assignment from a std::string
        MACAddr& operator=(const std::string& mac) {
            assignFromString(mac);
            return *this;
        }
        // assignment from a binary value
        MACAddr& operator=(const unsigned char* const mac) {
            memcpy(_mac.bytes, mac, sizeof(_mac.bytes));
            return *this;
        }
        MACAddr& operator+=(int v) {
            _mac.bytes[5] = (unsigned char)(_mac.bytes[5] + v);
            return *this;
        }
        MACAddr operator+(int v) const {
            MACAddr n(*this);
            n._mac.bytes[5] = (unsigned char)(n._mac.bytes[5] + v);
            return n;
        }
        // assignment from a binary string
        void assign(const unsigned char* const bytes, const unsigned int length) {
            memcpy(_mac.bytes, bytes, (length > sizeof(_mac.bytes)) ? sizeof(_mac.bytes) : length);
        }
        // assignment from a binary hi16/lo32 pair
        void assign(unsigned mac_hi16, unsigned mac_lo32) {
            unsigned short tmp_mac_hi16 = (unsigned short)mac_hi16;
            memcpy(&_mac.bytes[0], &tmp_mac_hi16, 2);
            memcpy(&_mac.bytes[2], &mac_lo32, 4);
        }
        // comparison
        bool operator==(const MACAddr& rhs) const { return _mac.val64 == rhs._mac.val64; }
        bool operator!=(const MACAddr& rhs) const { return _mac.val64 != rhs._mac.val64; }
        bool operator<(const MACAddr& rhs) const { return htobe64(_mac.val64) < htobe64(rhs._mac.val64); }
        bool operator>(const MACAddr& rhs) const { return htobe64(_mac.val64) > htobe64(rhs._mac.val64); }
        // conversion
        operator const unsigned char* const () const { return _mac.bytes; }
        MACAddr operator&(unsigned int prefixLen) const;
        MACAddr& operator&=(unsigned int prefixLen);
        MACAddr operator|(unsigned int prefixLen) const; /* Sets last 48-maskLen bits to 1 */
        MACAddr& operator|=(unsigned int prefixLen); /* Sets last 48-maskLen bits to 1 */

        // fetch the mac value
        const unsigned char* get() const { return _mac.bytes; }
        void getHi16Lo32(unsigned *mac_hi16, unsigned *mac_lo32) const {
            unsigned short tmp_mac_hi16 = 0;
            memcpy(mac_lo32, &_mac.bytes[2], 4);
            memcpy(&tmp_mac_hi16, &_mac.bytes[0], 2);
            *mac_hi16 = tmp_mac_hi16;
        }
        // pointer to the binary representation
        const unsigned char* bytes() const { return _mac.bytes; }
        // size of the binary representation
        int size() const { return sizeof(_mac.bytes); }

        // generate human readable debug string
        const char* toString(char *out) const;
        void toString(std::string *out) const;
        std::string toString() const;
        std::string toString(int fmt) const;
        void toStringFmt(std::string *out, int fmt) const;
        // Returns true when MAC is 00:00:00:00:00:00
        bool isZero() const { return (_mac.val64 == 0); }

        static bool isValid(const char *pmac);
        static bool isValid(const std::string &mac) { return isValid(mac.c_str()); }

    protected:
        // MAC binary representation
        union {
            unsigned char bytes[6];
            unsigned long long val64;
        } _mac;

        void assignFromString(const char* macstr);
        void assignFromString(const std::string& macstr) { assignFromString(macstr.c_str()); }
};
#endif // _CMACADDR_H
