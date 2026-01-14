//---------------------------------------------------------------------------------------
// TLV API Wrapper Class
// 
// - TLV tagID's are integers
// - endian issues are handled in this class
//
//---------------------------------------------------------------------------------------

#define USE_MULTIMAP_TLV

#if (defined(_WIN16) || defined(_WIN32) || defined(_WIN64)) && !defined(__WINDOWS__)
#	define __WINDOWS__
#endif

#if defined(__linux__) || defined(__CYGWIN__)
#	define __LINUX__
#endif

#if defined __LINUX__
#   include <netinet/in.h>
#endif
#include "tlvpacket.h"
#include "cexcept.h"
#include "cipaddr.h"
#include "cmacaddr.h"
#include "cpointer.h"

static unsigned int block_size = 0x400; // 1024

//-------------------------------------------------------------------------------
// Constructors and destructor
//-------------------------------------------------------------------------------

// constructor for handling received TLV payloads
cTLVPacket::cTLVPacket(unsigned char* const p, unsigned int length) :
    _packet(p), _length(length), _alloc_size(0)
{
    if(_packet == 0)
        throw cExcept(__FILE__,__LINE__,"Packet is NULL");
    if(_length == 0)
        throw cExcept(__FILE__,__LINE__,"Length is 0");

    // build the tlv index map
    buildTlvMap();
}

// destructor
cTLVPacket::~cTLVPacket()
{
    // do not free if the packet was not allocated by this instance
    if(_alloc_size > 0 && _packet != 0)
        delete[] _packet;
}

// assignment operator - will make a copy of the packet argument
cTLVPacket& cTLVPacket::operator=(const cTLVPacket& rhs)
{
    if(this != &rhs)
    {
        if(_alloc_size > 0 && _packet != 0)
            delete[] _packet;

        _alloc_size = rhs._length + block_size;
        _length = rhs._length;
        _packet = new unsigned char[_alloc_size];
        std::memcpy(_packet, rhs._packet, rhs._length); // copy the data
        _tlv_index = rhs._tlv_index; // copy the index
    }
    return *this;
}

// assignment from a binary string
void cTLVPacket::assign(const unsigned char* const bytes, const unsigned int length)
{
    if(_alloc_size > 0 && _packet != 0)
    {
        // delete the previous contents
        delete[] _packet;
        _packet = 0;
        _alloc_size = 0;
    }

    // allocate the packet buffer
    expandPacket(length);
    std::memcpy(_packet, bytes, length);
    _length = length;

    // build the tlv index map
    buildTlvMap();
}

//-------------------------------------------------------------------------------
// Methods for adding values to the payload
//-------------------------------------------------------------------------------

// add an integer value to the payload, use as few bytes as possible
// Unsigned packing is used to avoid value change if different methods are used on different sides
void cTLVPacket::addCompressed(const int tlvID, const unsigned int value)
{
    if (value <= 0xFF) {
        unsigned char bin_value = (unsigned char)value;
        appendBinary(tlvID, sizeof(bin_value), &bin_value);
        return;
    }
    if (value <= 0xFFFF) {
        unsigned short bin_value = htons((uint16_t)value);
        appendBinary(tlvID, sizeof(bin_value), &bin_value);
        return;
    }
    unsigned int bin_value = htonl(value);
    appendBinary(tlvID, sizeof(bin_value), &bin_value);
}

// add an integer array to the payload
void cTLVPacket::add(const int tlvID, const int *value, const unsigned int count)
{
    int local_buf[64];
    int *p = local_buf, *pAlloc = NULL;

    if(count > (sizeof(local_buf) / sizeof(local_buf[0])))
        pAlloc = p = new int[count];
    // append the integer addresses in the buffer
    for(unsigned int i=0; i<count; ++i)
    {
        p[i] = htonl(value[i]); // handle endian issues
    }
    appendBinary(tlvID, sizeof(int) * count, p);
    delete[] pAlloc;
}

// add an IPAddr value to the payload
// only handles IPV4 for now
void cTLVPacket::add(const int tlvID, const IPAddr& value)
{
    int ip_netorder = htonl(value.get());
    appendBinary(tlvID, sizeof(ip_netorder), &ip_netorder);
}

// add an IPAddr array to the payload
// only handles IPV4 for now
void cTLVPacket::add(const int tlvID, const IPAddr *value, const unsigned int count)
{
    unsigned char *p = new unsigned char[value[0].sizeV4() * count];

    // append the IP addresses in the buffer
    for(unsigned int i=0; i<count; ++i)
    {
        int ip_netorder = htonl(value[i].get());
        std::memcpy(&p[i*(value[0].sizeV4())], &ip_netorder, sizeof(ip_netorder));
    }
    appendBinary(tlvID, value[0].sizeV4() * count, p);
    delete[] p;
}

// add an MACAddr value to the payload
void cTLVPacket::add(const int tlvID, const MACAddr& value)
{
    appendBinary(tlvID, value.size(), value.bytes());
}

// add an MACAddr array to the payload
void cTLVPacket::add(const int tlvID, const MACAddr *value, const unsigned int count)
{
    unsigned char *p = new unsigned char[value[0].size() * count];

    // append the MAC addresses in the buffer
    for(unsigned int i=0; i<count; ++i)
    {
        std::memcpy(&p[i*value[i].size()], value[i].bytes(), value[i].size());
    }
    appendBinary(tlvID, value[0].size() * count, p);
    delete[] p;
}

void cTLVPacket::add(const int tlvID, const char* const value)
{
    if(value == 0)
        throw cExcept(__FILE__,__LINE__,"Value is NULL");
    appendBinary(tlvID, static_cast<unsigned int>(std::strlen(value)), value);
}

// add an embedded TLV payload value to the outgoing payload by tag ID
void cTLVPacket::add(const int tlvID, const cTLVPacket& value)
{
    if(this == &value)
        throw cExcept(__FILE__,__LINE__,"Self reference for TLV:",tlvID);

    appendBinary(tlvID, value._length, value._packet);
}

//-------------------------------------------------------------------------------
// Methods for locating values in the payload
//-------------------------------------------------------------------------------

// find and return an integer value
// Unsigned packing is used to avoid value change if different methods are used on different sides
bool cTLVPacket::findValue(const int tlvID, unsigned &valueStorage, const bool optional, const bool throwError) const
{
    unsigned int value_size = 0;
    int v = 0;
    if (!locateValue(tlvID, sizeof(v), (unsigned char* const)&v, value_size, optional, throwError)) return false;
    if (value_size == sizeof(uint32_t)) {
        valueStorage = htonl(v);
        return true;
    }
    if (value_size == sizeof(short)) {
        valueStorage = htons(v);
        return true;
    }
    valueStorage = (unsigned)v;
    return true;
}

// find and return an octet stream value
bool cTLVPacket::findValue(const int tlvID,
                           unsigned char*& valueOut,
                           unsigned int& valueLengthOut,
                           const bool optional,
                           const bool throwError) const
{
    bool ok = fetchValueLength(tlvID, valueLengthOut, optional, throwError);
    if(!ok)
        return ok;

    cPtr<unsigned char> storage(new unsigned char[valueLengthOut]);

    ok = locateValue(tlvID, valueLengthOut, storage.get(),
    valueLengthOut, optional, throwError);
    valueOut = storage.release();
    return ok;
}


//-------------------------------------------------------------------------------
// Methods for comparing payloads
//-------------------------------------------------------------------------------

bool cTLVPacket::operator==(const cTLVPacket& rhs) const
{
    if(this == &rhs)
        return true; // rhs is an alias
    if(_length != rhs._length)
        return false;
    if(_packet != 0 && rhs._packet != 0)
        return std::memcmp(_packet, rhs._packet, _length) == 0;
    else
        return false;
}

//-------------------------------------------------------------------------------
// Methods for concatenating payloads
//-------------------------------------------------------------------------------
cTLVPacket cTLVPacket::operator +(const cTLVPacket& rhs) const
{
    cTLVPacket p(*this);
    p += rhs;
    return p;
}

cTLVPacket& cTLVPacket::operator +=(const cTLVPacket& rhs)
{
    // expand the packet buffer if necessary
    expandPacket(rhs.getLength());

    // append the bytes
    appendTlvValue(rhs.getPayload(), rhs.getLength());

    return *this;
}

//-------------------------------------------------------------------------------
// Miscellaneous (protected in class)
//-------------------------------------------------------------------------------
void cTLVPacket::printMap() const
{
    mmapTLV::const_iterator iter = _tlv_index.begin();
    while(iter != _tlv_index.end())
    {
        printf("iter->first=%d, iter->second=%d\n",iter->first, iter->second);
        iter++;
    }
}

// add the specified tlv and offset to map
void cTLVPacket::addTlvToMap(const int tlvID, const unsigned int offset)
{
#ifdef USE_MULTIMAP_TLV
    _tlv_index.insert(std::pair<short,unsigned int>(tlvID,offset));
#else
    mapTLV::const_iterator iter = _tlv_index.find(static_cast<short>(tlvID));
    if(iter != _tlv_index.end())
    {
        throw cExcept(__FILE__,__LINE__,"Duplicate TLV:",tlvID);
    }
    _tlv_index[tlvID] = offset;
#endif
}

// add the value to the packet
void cTLVPacket::appendBinary(const int tlvID, const unsigned int length, const void *value)
{
    unsigned tlvlength = length + sizeof(short) + ((length > 0xFFFB) ? sizeof(uint32_t) : sizeof(short)); // include the ID and length values

    // expand the packet buffer if necessary
    expandPacket(tlvlength);

    // append the tlv ID
    appendTlvID(tlvID | ((tlvlength > 0xFFFF) ? cTLVLarge : 0));

    // append the length
    appendTlvLength(tlvlength);

    // append the bytes
    appendTlvValue(value, length);
}

// append the tlvID to the end of the packet
void cTLVPacket::appendTlvID(const int tlvID)
{
    short bin_tlvID = htons((short)tlvID);
    std::memcpy(&_packet[_length], &bin_tlvID, sizeof(bin_tlvID));
    _length += sizeof(bin_tlvID);
}

// append the tlv length
void cTLVPacket::appendTlvLength(const unsigned int length)
{
    if (length > 0xFFFF) {
        uint32_t bin_length = htonl((uint32_t)length);
        std::memcpy(&_packet[_length], &bin_length, sizeof(bin_length));
        _length += sizeof(bin_length);
    }
    else {
        unsigned short bin_length = htons((unsigned short)length);
        std::memcpy(&_packet[_length], &bin_length, sizeof(bin_length));
        _length += sizeof(bin_length);
    }
}

// append the tlv value
void cTLVPacket::appendTlvValue(const void *value, const unsigned int length)
{
    if (value) std::memcpy(&_packet[_length], value, length);
    else std::memset(&_packet[_length], 0, length);
    _length += length;
}

// build the tlv index map from a complete packet
void cTLVPacket::buildTlvMap()
{
    if(_packet == 0 || _length == 0)
        return;

    _tlv_index.clear(); // make sure the map is empty

    for(unsigned int offset = 0; offset<_length; )
    {
        if (sizeof(short) > _length - offset) {
            throw cExcept(__FILE__,__LINE__,"Invalid TLV length 1");
        }
        unsigned int tlv_id = getTlvID(offset);
        unsigned int header_len = (tlv_id & cTLVLarge) ? (sizeof(short) + sizeof(uint32_t)) : (sizeof(short) * 2);
        tlv_id &= cTLVIdMask;

        if (header_len > _length - offset) {
            throw cExcept(__FILE__,__LINE__,"Invalid TLV length 2");
        }

        unsigned int tlv_length = getTlvLength(offset);
        if (tlv_length < header_len || tlv_length > _length - offset) {
            throw cExcept(__FILE__,__LINE__,"Invalid TLV length 3");
        }

        // add to the map
        addTlvToMap(tlv_id, offset);

        offset += tlv_length;
    }
}

// expand the packet buffer by the specified amount
void cTLVPacket::expandPacket(const unsigned int length)
{
    // is there enough room right now?
    if(_alloc_size > 0 && ((_alloc_size - _length) > length))
        return; // we have enough room

    // round up to the next 1K size
    _alloc_size = _length + length + block_size;

    // allocate the new buffer
    unsigned char * temp = new unsigned char[_alloc_size];

    if(_packet != 0)
    {
        // copy the old packet to the new buffer
        std::memcpy(temp, _packet, _length);
        delete[] _packet;
    }

    // keep the new packet buffer
    _packet = temp;
}

// fetch the length value for the specified tlvID
bool cTLVPacket::fetchValueLength(const int tlvID,
                                  unsigned int& valueLengthOut,
                                  const bool optional,
                                  const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        valueLengthOut = getTlvValueLength(offset);
        return true;
    }
    if(optional)
    {
        valueLengthOut = 0;
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate an IPAddr
bool cTLVPacket::locateValue(const int tlvID,
                             IPAddr& ipaddr,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        ipaddr = ntohl(*(int*)getTlvValuePtr(offset));
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate an IPAddr array
// free the returned array with delete [] ipaddr
bool cTLVPacket::locateValue(const int tlvID,
                             IPAddr*& ipaddr,
                             unsigned int& itemCountOut,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        // alocate array storage
        unsigned int length;
        unsigned char* item = const_cast<unsigned char*>(getTlvValuePtrLength(offset, &length)); // start
        unsigned int arraylength = length / ipaddr->sizeV4();
        IPAddr* array = new IPAddr[arraylength];

        for(unsigned int i=0; i < arraylength; ++i)
        {
            array[i] = ntohl(*(int*)item);
            item += ipaddr->sizeV4();
        }
        ipaddr = array;
        itemCountOut = arraylength;
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate a MACAddr
bool cTLVPacket::locateValue(const int tlvID,
                             MACAddr& storage,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset, len;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        const unsigned char *ptr = getTlvValuePtrLength(offset, &len);
        storage.assign(ptr, len);
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate a MACAddr array
// free the returned array with delete [] macaddr
bool cTLVPacket::locateValue(const int tlvID,
                             MACAddr*& macaddr,
                             unsigned int& itemCountOut,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        // alocate array storage
        unsigned int length;
        unsigned char* item = const_cast<unsigned char*>(getTlvValuePtrLength(offset, &length)); // start
        unsigned int arraylength = length / sizeof(MACAddr);
        MACAddr* array = new MACAddr[arraylength];

        for(unsigned int i=0; i < arraylength; ++i)
        {
            array[i].assign(item, sizeof(MACAddr));
            item += sizeof(MACAddr);
        }
        macaddr = array;
        itemCountOut = arraylength;
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate a std::string
bool cTLVPacket::locateValue(const int tlvID,
                             std::string& str,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset, len;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        const unsigned char *ptr = getTlvValuePtrLength(offset, &len);
        str.assign((char*)ptr, len);
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate a cTLVPacket
bool cTLVPacket::locateValue(const int tlvID,
                             cTLVPacket& storage,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset, len;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        const unsigned char *ptr = getTlvValuePtrLength(offset, &len);
        storage.assign(ptr, len);
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate multiple cTLVPackets
bool cTLVPacket::locateValue(const int tlvID,
                 std::vector<cTLVPacket>& tlvpkt,
                 const bool optional,
                 const bool throwError) const
{
    tlvpkt.clear();
    std::pair<mmapTLV::const_iterator, mmapTLV::const_iterator> TLVs = _tlv_index.equal_range(static_cast<short>(tlvID));
    mmapTLV::const_iterator iter;
    if(TLVs.first != TLVs.second)
    {
        for (iter = TLVs.first; iter != TLVs.second; iter++)
        {
            unsigned int len, offset = iter->second; // return the offset
            cTLVPacket p;
            const unsigned char *ptr = getTlvValuePtrLength(offset, &len);
            p.assign(ptr, len);
            tlvpkt.push_back(p);
        }
        return true;
    }

    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate multiple IPAddr
bool cTLVPacket::locateValue(const int tlvID,
                 std::vector<IPAddr>& tlvpkt,
                 const bool optional,
                 const bool throwError) const
{
    tlvpkt.clear();
    std::pair<mmapTLV::const_iterator, mmapTLV::const_iterator> TLVs = _tlv_index.equal_range(static_cast<short>(tlvID));
    mmapTLV::const_iterator iter;
    if(TLVs.first != TLVs.second)
    {
        for (iter = TLVs.first; iter != TLVs.second; iter++)
        {
            unsigned int offset = iter->second; // return the offset
            IPAddr p(ntohl(*(int*)getTlvValuePtr(offset)));
            tlvpkt.push_back(p);
        }
        return true;
    }

    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate multiple int(s)
bool cTLVPacket::locateValue(const int tlvID,
                 std::vector<int>& tlvpkt,
                 const bool optional,
                 const bool throwError) const
{
    tlvpkt.clear();
    std::pair<mmapTLV::const_iterator, mmapTLV::const_iterator> TLVs = _tlv_index.equal_range(static_cast<short>(tlvID));
    mmapTLV::const_iterator iter;
    if(TLVs.first != TLVs.second)
    {
        for (iter = TLVs.first; iter != TLVs.second; iter++)
        {
            unsigned int offset = iter->second; // return the offset
            int p = ntohl(*(int*)getTlvValuePtr(offset));
            tlvpkt.push_back(p);
        }
        return true;
    }

    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate variable size values
bool cTLVPacket::locateValue(const int tlvID,
                             const unsigned int storageSize,
                             unsigned char* const storageLocation,
                             unsigned int& valueLengthOut,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        const unsigned char *ptr = getTlvValuePtrLength(offset, &valueLengthOut);
        if(valueLengthOut > storageSize)
        {
            if(throwError)
                throw cExcept(__FILE__,__LINE__,"Storage is too small");
            else
                return false; // value size is larger than the storage size
        }
        std::memcpy(storageLocation, ptr, valueLengthOut);
        return true;
    }
    if(optional)
    {
        valueLengthOut = 0;
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}

// locate an int array
// free the returned array with delete [] ipaddr
bool cTLVPacket::locateValue(const int tlvID,
                             int*& intArr,
                             unsigned int& itemCountOut,
                             const bool optional,
                             const bool throwError) const
{
    unsigned int offset;
    bool found = lookup(tlvID, offset);
    if(found)
    {
        // allocate array storage
        unsigned int length;
        unsigned char* item = const_cast<unsigned char*>(getTlvValuePtrLength(offset, &length)); // start
        unsigned int arraylength = length / sizeof(int);
        int* arr = new int[arraylength];

        for(unsigned int i=0; i < arraylength; ++i)
        {
            arr[i] = ntohl(*(int*)item);
            item += sizeof(int);
        }
        intArr = arr;
        itemCountOut = arraylength;
        return true;
    }
    if(optional)
    {
        return false;
    }
    if(throwError)
    {
        throw cExcept(__FILE__,__LINE__,"TLV not found: ", tlvID);
    }
    return false;
}


// lookup the offset of the specified tlv
bool cTLVPacket::lookup(const int tlvID, unsigned int& offset) const
{
#ifdef USE_MULTIMAP_TLV
    int count = _tlv_index.count(tlvID);

    //printf("cTLVPacket::lookup - tlv count for TLV [%d] is [%d]\n", tlvID, count);
    if(count == 0)
        return false;

    if(count > 1)
        throw cExcept(__FILE__,__LINE__,"Multiple TLV's found: ", tlvID);
    mmapTLV::const_iterator iter = _tlv_index.find(static_cast<short>(tlvID));
    if(iter != _tlv_index.end())
    {
        offset = iter->second; // return the offset
        return true;
    }
    return false; // not found
#else
    mapTLV::const_iterator iter = _tlv_index.find(static_cast<short>(tlvID));
    if(iter != _tlv_index.end())
    {
        offset = iter->second; // return the offset
        return true;
    }
    return false; // not found
#endif
}

std::string cTLVPacket::toOctetString() const
{
    static const char HexTbl[16] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
    std::string out(2 * _length, '\0'); /* preallocate the space and set the final length */
    unsigned i, val;

    if(_packet != 0) {
        for(i = 0; i < _length; i++) {
            val = _packet[i];
            out[2 * i] = HexTbl[val >> 4];
            out[2 * i + 1] = HexTbl[val & 0xF];
        }
    }
    return out;
}
