#ifndef _ADDRCHK_H
#define _ADDRCHK_H

#define IPADDR_IPV6_SZ 16

/* mask defines which type of address is allowed. bit0 is hostname, bit1 is IPv4, bit2 is IPv6 */
/* addrchk() returns 0 if address has correct format, or position of first error otherwise */
#define ADDRCHK_HOSTNAME 1
#define ADDRCHK_IPV4     2
#define ADDRCHK_IPV6     4
#define ADDRCHK_IFACE    8

#define IPADDR_SCOPE_UNKNOWN               0
#define IPADDR_SCOPE_UNSPECIFIED           1
#define IPADDR_SCOPE_V4_PUBLIC             2
#define IPADDR_SCOPE_V4_LOOPBACK           3
#define IPADDR_SCOPE_V4_MULTICAST          4
#define IPADDR_SCOPE_V4_PRIVATE            5
#define IPADDR_SCOPE_V4_AUTO_CONF          6
#define IPADDR_SCOPE_V4_BROADCAST          7
#define IPADDR_SCOPE_V6_LOOPBACK           8
#define IPADDR_SCOPE_V6_IPV4_MAPPED        9
#define IPADDR_SCOPE_V6_GLOBAL_UNICAST     10
#define IPADDR_SCOPE_V6_LOCAL_UNICAST      11
#define IPADDR_SCOPE_V6_LINK_LOCAL_UNICAST 12
#define IPADDR_SCOPE_V6_MULTICAST          13

#define IPADDR_V6_MCAST_SCOPE_UNKNOWN            0
#define IPADDR_V6_MCAST_SCOPE_INTERFACE_LOCAL    0x01
#define IPADDR_V6_MCAST_SCOPE_LINK_LOCAL         0x02
#define IPADDR_V6_MCAST_SCOPE_ADMIN_LOCAL        0x04
#define IPADDR_V6_MCAST_SCOPE_SITE_LOCAL         0x05
#define IPADDR_V6_MCAST_SCOPE_ORGANIZATION_LOCAL 0x08
#define IPADDR_V6_MCAST_SCOPE_GLOBAL             0x0E

#ifdef __cplusplus
extern "C" {
#endif

int addrchk(const char *addr, int mask);
int addrchk_hostname(const char *addr);
int addrchk_ipv4(const char *addr);
int addrchk_ipv6(const char *addr);
int addrchk_interfaceaddr_v4(const char *addr);
int addrchk_interfaceaddr_v6(const char *addr);
int addrchk_common_name(const char *cn);
unsigned int addrchk_ipv6_assign_from_str(const char *in_addr, unsigned char *out_addr, unsigned *pDispFlags);
unsigned int addrchk_ipv4_addr_scope(const unsigned int addr);
unsigned int addrchk_ipv4_addr_scope_str(const char *addr);
unsigned int addrchk_ipv6_addr_scope(const unsigned char *addr);
unsigned int addrchk_ipv6_addr_scope_str(const char *in_addr, unsigned char *out_addr);
unsigned int addrchk_ipv6_mcast_scope(const unsigned char *addr);
unsigned int addrchk_ipv6_mcast_scope_str(const char *addr);

#ifdef __cplusplus
}
#endif
#endif
