#ifndef __BITALGS_H__
#define __BITALGS_H__

#ifdef __cplusplus
extern "C" {
#endif

/*** Count Leading Zeros ***/

/* 8bit table lookup for counting leading zeros */
static const unsigned int clz_8b[256] = {
    8,7,6,6,5,5,5,5,
    4,4,4,4,4,4,4,4,
    3,3,3,3,3,3,3,3,
    3,3,3,3,3,3,3,3,
    2,2,2,2,2,2,2,2,
    2,2,2,2,2,2,2,2,
    2,2,2,2,2,2,2,2,
    2,2,2,2,2,2,2,2,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    1,1,1,1,1,1,1,1,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0,
    0,0,0,0,0,0,0,0
};

/* counting leading zeros in 32bit integer based on 8bit table lookup */
static inline unsigned clz4(unsigned int x)
{
    int n = 0;
    if ((x & 0xFFFF0000) == 0) { n  = 16; x <<= 16; }
    if ((x & 0xFF000000) == 0) { n +=  8; x <<=  8; }
    n += clz_8b[x >> (32 - 8)];
    return n;
}

/* counting leading zeros in a byte based on 8bit table lookup */
static inline unsigned clz_byte(unsigned char x)
{
    return clz_8b[x];
}

/* 4bit table lookup for counting leading zeros */
static const unsigned int clz_4b[16] = { 4, 3, 2, 2, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0 };

/* counting leading zeros in 32bit integer based on 4bit table lookup */
static inline unsigned clz4_s(unsigned int x)
{
    int n = 0;
    if ((x & 0xFFFF0000) == 0) {n  = 16; x <<= 16;}
    if ((x & 0xFF000000) == 0) {n +=  8; x <<=  8;}
    if ((x & 0xF0000000) == 0) {n +=  4; x <<=  4;}
    n += clz_4b[x >> (32 - 4)];
    return n;
}


/*** Count Trailing Zeros ***/

/* 4bit table lookup for counting trailing zeros */
static const unsigned int ctz_4b[16] = { 4, 0, 1, 0, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0 };

/* counting trailing zeros in 32bit integer based on 4bit table lookup */
static inline unsigned ctz4(unsigned int x)
{
    int n = 0;
    if ((x & 0x0000FFFF) == 0) { if (x == 0) return 32; n += 16; x >>= 16; }
    if ((x & 0x000000FF) == 0) { n += 8; x >>= 8; }
    if ((x & 0x0000000F) == 0) { n += 4; x >>= 4; }
    n += ctz_4b[x & 0x0F];
    return n;
}

#ifdef __cplusplus
}
#endif
#endif /*__BITALGS_H__*/
