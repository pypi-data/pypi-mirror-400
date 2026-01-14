//---------------------------------------------------------------------------------------
// TLV API Wrapper Class
// 
// - TLV tagID's are integers
// - endian issues are handled in this class
//
// ToDo:
// 1 - finish packet handling so that it may be used for send and receive operations.
// 2 - add packet compare operators
// 3 - add debug print
//
//---------------------------------------------------------------------------------------

#ifndef _TLVPACKET_H
#define _TLVPACKET_H

#if (defined(_WIN16) || defined(_WIN32) || defined(_WIN64)) && !defined(__WINDOWS__)
#	define __WINDOWS__
#endif

#if defined(__linux__) || defined(__CYGWIN__)
#	define __LINUX__
#endif

#include <cstring>
#include <map>
#include <vector>
#include <list>
#include <string>
#include <assert.h>
#include <exception>
#if defined(__WINDOWS__)
#   include <winsock2.h> //W
#else
#   include <arpa/inet.h>
#endif
#include "eendian.h"
#include "tlv_def.h"

#define TLV_64K_THRESHOLD (0xFFFF - 32)

class MACAddr;
class IPAddr;

class cTLVPacket
{
    public:
        enum cTLVOptions { cTLVLarge = 0x8000, cTLVIdMask = 0x0FFF };

        //-------------------------------------------------------------------------------
        // Constructors and destructor
        //-------------------------------------------------------------------------------

        // constructor for handling received TLV payloads
        cTLVPacket(unsigned char* const p, unsigned int length);

        // constructor for building a new TLV payload to send
        cTLVPacket() : _packet(0), _length(0), _alloc_size(0)
        {}

        // constructor for preallocating payload
        cTLVPacket(unsigned int sz) : _packet(0), _length(0), _alloc_size(0)
        {
            expandPacket(sz);
        }

        // copy constructor
        cTLVPacket(const cTLVPacket& rhs):_packet(0), _length(0), _alloc_size(0)
        { operator=(rhs); }

        // destructor
        virtual ~cTLVPacket();

        // assignment operator - will make a copy of the packet argument
        cTLVPacket& operator=(const cTLVPacket& rhs);

        // assignment from a binary string
        void assign(const unsigned char* const bytes, const unsigned int length);

        // check for TLV_64K_THRESHOLD limit payload
        bool tlv64kSizeCheck(unsigned sz)
        {
            return (getLength() + sz) < TLV_64K_THRESHOLD;
        }

        //-------------------------------------------------------------------------------
        // Methods for adding values to the payload
        //-------------------------------------------------------------------------------

        // add a boolean value to the payload
        void add(const int tlvID, const bool value)
        {
            unsigned char b = value != 0;
            appendBinary(tlvID, 1, &b);
        }

        // add an integer value to the payload
        void add(const int tlvID, const int value)
        {
            int bin_value = htonl(value); // handle endian issues
            appendBinary(tlvID, sizeof(bin_value), &bin_value);
        }

        // add an integer value to the payload
        void add(const int tlvID, const long long value)
        {
            long long bin_value = htobe64(value); // handle endian issues
            appendBinary(tlvID, sizeof(bin_value), &bin_value);
        }

    // add an integer value to the payload, use as few bytes as possible
        void addCompressed(const int tlvID, const int value)
        {
            addCompressed(tlvID, (unsigned)value);
        }

        // add an integer value to the payload, use as few bytes as possible
        void addCompressed(const int tlvID, const unsigned int value);

        // add an integer array to the payload
        void add(const int tlvID, const int *value, const unsigned int count);

        // add an IPAddr value to the payload
        void add(const int tlvID, const IPAddr& value);

        // add an IPAddr array to the payload
        void add(const int tlvID, const IPAddr *value, const unsigned int count);

        // add an MACAddr value to the payload
        void add(const int tlvID, const MACAddr& value);

        // add an MACAddr array to the payload
        void add(const int tlvID, const MACAddr *value, const unsigned int count);

        // add an octet stream value to the payload
        void add(const int tlvID, const unsigned char* const value, const unsigned int length)
        {
            appendBinary(tlvID, length, value);
        }

        // add a short integer value to the payload
        void add(const int tlvID, const short value)
        {
            short bin_value = htons(value); // handle endian issues
            appendBinary(tlvID, sizeof(bin_value), &bin_value);
        }

        // add a string value to the payload
        void add(const int tlvID, const std::string& value)
        {
            appendBinary(tlvID, value.length(), value.c_str());
        }

        void add(const int tlvID, const char* const value);

        // add an unsigned integer value to the payload
        void add(const int tlvID, const unsigned int value)
        {
            unsigned int bin_value = htonl(value); // handle endian issues
            appendBinary(tlvID, sizeof(bin_value), &bin_value);
        }

        // add an unsigned short integer value to the payload
        void add(const int tlvID, const unsigned short value)
        {
            unsigned short bin_value = htons(value); // handle endian issues
            appendBinary(tlvID, sizeof(bin_value), &bin_value);
        }

        // add an embedded TLV payload value to the outgoing payload by tag ID
        void add(const int tlvID, const cTLVPacket& value);

        //-------------------------------------------------------------------------------
        // Methods for locating values in the payload
        //-------------------------------------------------------------------------------

        // find and return a boolean value
        bool findValue(const int tlvID,
                       bool& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            unsigned char b;
            bool ok = locateValue(tlvID, 1, &b, optional, throwError);
            if(ok)
                valueStorage = b != 0;
            return ok;
        }

        // find and return an integer value
        bool findValue(const int tlvID,
                       int& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return findValue(tlvID, (unsigned&)valueStorage, optional, throwError);
        }

        // find and return an IPAddr value
        bool findValue(const int tlvID,
                       IPAddr& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, optional, throwError);
        }

        // find and return an IPAddr array
        // free the returned array with delete [] ipaddr
        bool findValue(const int tlvID,
                       IPAddr*& valueStorage,
                       unsigned int& itemCountOut,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, itemCountOut, optional, throwError);
        }

        // find and return a MACAddr value
        bool findValue(const int tlvID,
                       MACAddr& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, optional, throwError);
        }

        // find and return a MACAddr array
        // free the returned array with delete [] macaddr
        bool findValue(const int tlvID,
                       MACAddr*& valueStorage,
                       unsigned int& itemCountOut,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, itemCountOut, optional, throwError);
        }

        // find and return an octet stream value
        bool findValue(const int tlvID,
                       unsigned char*& valueOut,
                       unsigned int& valueLengthOut,
                       const bool optional=false,
                       const bool throwError=true) const;

        // find and return a short integer value
        bool findValue(const int tlvID,
                       short& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            short v;
            bool ok = locateValue(tlvID, sizeof(short), (unsigned char* const)&v, optional, throwError);
            if(ok)
                valueStorage = htons(v); // handle endian issues
            return ok;
        }

        // find and return a string value
        bool findValue(const int tlvID,
                       std::string& storage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, storage, optional, throwError);
        }

        // find and return an unsigned short integer value
        bool findValue(const int tlvID,
                       unsigned short& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            unsigned short v;
            bool ok = locateValue(tlvID, sizeof(unsigned short), (unsigned char*)&v, optional, throwError);
            if(ok)
                valueStorage = htons(v); // handle endian issues
            return ok;
        }

        // find and return an unsigned integer value
        bool findValue(const int tlvID,
                       unsigned int& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const;

        // find and return a TLV payload value
        bool findValue(const int tlvID,
                       cTLVPacket& storage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, storage, optional, throwError);
        }

        // find and return multiple TLVs
        bool findValue(const int tlvID,
                       std::vector<cTLVPacket>& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, optional, throwError);
        }

        // find and return multiple IPAddr
        bool findValue(const int tlvID,
                       std::vector<IPAddr>& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, optional, throwError);
        }

        // find and return multiple int
        bool findValue(const int tlvID,
                       std::vector<int>& valueStorage,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, valueStorage, optional, throwError);
        }

        // find and return an int array
        // free the returned array with delete []
        // It would be nice that we implement this with template
        // instead of array of IPAddr, MACAddr, int and so on.
        // but that will change APIs.
        bool findValue(const int tlvID,
                       int*& intArr,
                       unsigned int& itemCountOut,
                       const bool optional=false,
                       const bool throwError=true) const
        {
            return locateValue(tlvID, intArr, itemCountOut, optional, throwError);
        }

        //-------------------------------------------------------------------------------
        // Methods for comparing payloads
        //-------------------------------------------------------------------------------

        bool operator==(const cTLVPacket& rhs) const;
        bool operator!=(const cTLVPacket& rhs) const { return operator==(rhs)==0; }

        cTLVPacket operator +(const cTLVPacket& rhs) const;
        cTLVPacket& operator +=(const cTLVPacket& rhs);

        //-------------------------------------------------------------------------------
        // Miscellaneous
        //-------------------------------------------------------------------------------

        // return the payload pointer
        const unsigned char* getPayload() const { return _packet; }

        // return the payload length
        unsigned int getLength() const { return _length; }

        // reset packet length to reuse the same object (packet buffer) within the loop
        // to avoid/minimize reallocations, as well as constructions/destructions
        void reset() { _length = 0; }

        // is the payload null?
        bool isNull() const { return _packet==0; }

        // generate hex debug string
        std::string toOctetString() const;

    protected:
        unsigned char* _packet;
        unsigned int   _length;
        unsigned int   _alloc_size;

        // the map which indexes tlv's to offsets into the packet buffer
        typedef std::multimap<short, unsigned int> mmapTLV;
        mmapTLV _tlv_index;

        // add the specified tlv and offset to map
        void addTlvToMap(const int tlvID, const unsigned int offset);

        // add the value to the packet
        void appendBinary(const int tlvID, const unsigned int length, const void *value);

        // append the tlvID to the end of the packet
        void appendTlvID(const int tlvID);

        // append the tlv length
        void appendTlvLength(const unsigned int length);

        // append the tlv value
        void appendTlvValue(const void *value, const unsigned int length);

        // build the tlv index map from a complete packet
        void buildTlvMap();

        // return a tlv ID
        unsigned int getTlvID(const unsigned int offset) const
        {
            return htons(*(short*)(_packet + offset));
        }

        // return a tlv's length value
        unsigned int getTlvLength(const unsigned int offset) const
        {
            if (getTlvID(offset) & cTLVLarge) {
                uint32_t *len = (uint32_t*)(_packet + sizeof(short) + offset);
                return htonl(*len);
            }
            else {
                unsigned short *len = (unsigned short*)(_packet + sizeof(short) + offset);
                return htons(*len);
            }
        }

        // return a pointer to the next item in a variable item length tlv array
        const unsigned char* getTlvNextVarItem(const unsigned char* const item) const
        {
            return &item[getTlvVarItemLength(item) + sizeof(unsigned short)];
        }

        // return the tlv's value length
        unsigned int getTlvValueLength(const unsigned int offset) const
        {
            unsigned int tlvlength, header_len;
            if (getTlvID(offset) & cTLVLarge) {
                header_len = sizeof(short) + sizeof(uint32_t);
                uint32_t* p = (uint32_t*)&_packet[offset + sizeof(short)];
                tlvlength = htonl(*p);
            }
            else {
                header_len = sizeof(short) * 2;
                unsigned short* p = (unsigned short*)&_packet[offset + sizeof(short)];
                tlvlength = htons(*p);
            }
            return (tlvlength - header_len);
        }

        // return a pointer to the tlv's value
        const unsigned char* getTlvValuePtr(const unsigned int offset) const
        {
            unsigned int header_len = sizeof(short) + ((getTlvID(offset) & cTLVLarge) ? sizeof(uint32_t) : sizeof(short));
            return &_packet[offset + header_len];
        }

        // return the tlv's value and a pointer to the tlv's value
        const unsigned char* getTlvValuePtrLength(const unsigned int offset, unsigned *pLen) const
        {
            unsigned int tlvlength, header_len;
            if (getTlvID(offset) & cTLVLarge) {
                header_len = sizeof(short) + sizeof(uint32_t);
                uint32_t* p = (uint32_t*)&_packet[offset + sizeof(short)];
                tlvlength = htonl(*p);
            }
            else {
                header_len = sizeof(short) * 2;
                unsigned short* p = (unsigned short*)&_packet[offset + sizeof(short)];
                tlvlength = htons(*p);
            }
            *pLen = tlvlength - header_len;
            return &_packet[offset + header_len];
        }

        // return the tlv's value and a pointer to the tlv's value
        const unsigned char* getTlvLenAndValuePtrLength(const unsigned int offset, unsigned *pValLen, unsigned *pTlvLen) const
        {
            unsigned int tlvlength, header_len;
            if (getTlvID(offset) & cTLVLarge) {
                header_len = sizeof(short) + sizeof(uint32_t);
                uint32_t* p = (uint32_t*)&_packet[offset + sizeof(short)];
                tlvlength = htonl(*p);
            }
            else {
                header_len = sizeof(short) * 2;
                unsigned short* p = (unsigned short*)&_packet[offset + sizeof(short)];
                tlvlength = htons(*p);
            }
            *pTlvLen = tlvlength;
            *pValLen = tlvlength - header_len;
            return &_packet[offset + header_len];
        }

        // return the length of an item in a variable item length tlv array
        unsigned int getTlvVarItemLength(const unsigned char* const item) const
        {
            unsigned short itemlength = htons(*((unsigned short*)item));
            return static_cast<unsigned int>(itemlength);
        }

        // return a pointer to an item in a variable item length tlv array
        const unsigned char* getTlvVarItemValuePtr(const unsigned char* const item) const
        {
            return &item[sizeof(unsigned short)];
        }

        // expand the packet buffer by the specified amount
        void expandPacket(const unsigned int length);

        // fetch the length value for the specified tlvID
        bool fetchValueLength(const int tlvID,
                              unsigned int& valueLengthOut,
                              const bool optional,
                              const bool throwError) const;

        // locate fixed size values
        bool locateValue(const int tlvID,
                         const unsigned int storageSize,
                         unsigned char* const storageLocation,
                         const bool optional,
                         const bool throwError) const
        {
            unsigned int value_size;
            return locateValue(tlvID, storageSize, storageLocation, value_size, optional, throwError);
        }

        // locate an IPAddr
        bool locateValue(const int tlvID,
                         IPAddr& ipaddr,
                         const bool optional,
                         const bool throwError) const;

        // locate an IPAddr array
        // free the returned array with delete [] ipaddr
        bool locateValue(const int tlvID,
                         IPAddr*& ipaddr,
                         unsigned int& itemCountOut,
                         const bool optional,
                         const bool throwError) const;

        // locate a MACAddr
        bool locateValue(const int tlvID,
                         MACAddr& macaddr,
                         const bool optional,
                         const bool throwError) const;

        // locate a MACAddr array
        // free the returned array with delete [] macaddr
        bool locateValue(const int tlvID,
                         MACAddr*& macaddr,
                         unsigned int& itemCountOut,
                         const bool optional,
                         const bool throwError) const;

        // locate a std::string
        bool locateValue(const int tlvID,
                         std::string& str,
                         const bool optional,
                         const bool throwError) const;

        // locate a cTLVPacket
        bool locateValue(const int tlvID,
                         cTLVPacket& tlvpkt,
                         const bool optional,
                         const bool throwError) const;

        // locate multiple cTLVPackets
        bool locateValue(const int tlvID,
                         std::vector<cTLVPacket>& tlvpkt,
                         const bool optional,
                         const bool throwError) const;

        // locate multiple IPAddr
        bool locateValue(const int tlvID,
                         std::vector<IPAddr>& tlvpkt,
                         const bool optional,
                         const bool throwError) const;

        // locate multiple int
        bool locateValue(const int tlvID,
                         std::vector<int>& tlvpkt,
                         const bool optional,
                         const bool throwError) const;

        // locate variable size values
        bool locateValue(const int tlvID,
                         const unsigned int storageSize,
                         unsigned char* const storageLocation,
                         unsigned int& valueLengthOut,
                         const bool optional,
                         const bool throwError) const;

        // find and return an int array
        // free the returned array with delete []
        bool locateValue(const int tlvID,
                       int*& intArr,
                       unsigned int& itemCountOut,
                       const bool optional=false,
                       const bool throwError=true) const;


        // lookup the offset of the specified tlv
        bool lookup(const int tlvID, unsigned int& offset) const;

        // print map
        void printMap() const;
};
#endif // _TLVPACKET_H
