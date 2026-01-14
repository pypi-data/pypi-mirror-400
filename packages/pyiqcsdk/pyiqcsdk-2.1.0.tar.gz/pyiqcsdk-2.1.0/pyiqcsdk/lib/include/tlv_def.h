#ifndef __TLV_DEF_H
#define __TLV_DEF_H

/*****************************************************
* This file defines the TLV constants to be used
* for communication between HQC components and AP.
*

* Constant names have been merged to include both,
* the AP and HWC names.
****************************************************/

#define PW_TYPE_STRING              0
#define PW_TYPE_INTEGER             1
#define PW_TYPE_IPADDR              2
#define PW_TYPE_DATE                3
#define PW_TYPE_ABINARY             4
#define PW_TYPE_OCTETS              5
#define PW_TYPE_MACADD              6
#define PW_TYPE_BLOCK_TLV           7


// #define's should be in order of the numbers starting 0
// and unsused types must be declared EID_UNUSED_<number> <number>
// The format then is used to convert the file

/*****************************************************
* Main TLVs
****************************************************/
#define EID_UNUSED_0                0
#define EID_STATUS                  1
#define EID_RU_SW_VERSION           2
#define EID_RU_SERIAL_NUMBER        3
#define EID_RU_REG_CHALLENGE        4
#define EID_RU_REG_RESPONSE         5
#define EID_AC_IPADDR               6
#define EID_RU_VNSID                7
#define EID_TFTP_SERVER             8
#define EID_IMAGE_PATH              9
#define EID_CONFIG                  10 // config block for TLV/SNMP packet (until V4)
#define EID_RU_STATE                11
#define EID_SESSION_KEY             12
#define EID_RU_PROTOCOL             13
#define EID_RANDOM_NUMBER           14
#define EID_STANDBY_TIMEOUT         15
#define EID_RU_CHALLENGE_ID         16
#define EID_RU_MODEL                17
#define EID_RU_SCAN_MODE            18
#define EID_RU_SCAN_TYPE            19
#define EID_RU_SCAN_INTERVAL        20
#define EID_RU_RADIO_TYPE           21
#define EID_RU_CHANNEL_DWELL_TIME   22
#define EID_RU_CHANNEL_LIST         23
#define EID_RU_TRAP                 24
#define EID_RU_SCAN_TIMES           25
#define EID_RU_SCAN_DELAY           26
#define EID_RU_SCAN_REQ_ID          27
#define EID_STATIC_CONFIG           28
#define EID_LOCAL_BRIDGING          29
#define EID_STATIC_BP_IPADDR        30
#define EID_STATIC_BP_NETMASK       31
#define EID_STATIC_BP_GATEWAY       32
#define EID_STATIC_BM_IPADDR        33
#define EID_BP_BPSSID               34
#define EID_BP_WIRED_MACADDR        35
#define EID_RU_CAPABILITY           36    /*passed in ac registration msg indicating capabilities*/
#define EID_RU_SSID_NAME            37    /*this is the ssid string passes in ac registration msg */
#define EID_ALARM                   38
#define EID_RU_PREAUTH              39
#define EID_RU_PMK                  40
#define EID_AC_REG_CHALLENGE        41
#define EID_AC_REG_RESPONSE         42
#define EID_STATS                   43
#define EID_CERTIFICATE             44
#define EID_RADIO_ID                45
#define EID_REQ_ID                  46
#define EID_NETWORK_ID              47
#define EID_MU_MAC                  48
#define EID_TIME                    49
#define EID_NUM_RADIOS              50
#define EID_RADIO_INFO              51
#define EID_NETWORK_INFO            52
#define EID_VENDOR_ID               53
#define EID_PRODUCT_ID              54
#define EID_RADIO_INFO_ACK          55
#define EID_SECURE_TUNNEL           56
#define EID_MU_TOPOLOGY_ID          57
#define EID_SSID                    58 // WIDS / WIPS
#define EID_EVENT_BLOCK             59
#define EID_SNMP_ERROR_STATUS       60
#define EID_SNMP_ERROR_INDEX        61
#define EID_RU_REAUTH_TIMER         62
#define EID_AP_IMG_TO_RAM           63
#define EID_AP_IMG_ROLE             64
#define EID_AP_STATS_BLOCK          65
#define EID_MU_RF_STATS_BLOCK       66
#define EID_STATS_REQUEST_TYPE      67 //0 = All stats, other values TBD
#define EID_STATS_LAST              68
#define EID_TLV_CONFIG              69 // config block for TLV packet (new in V5)
#define EID_CONFIG_ERROR_BLOCK      70
#define EID_CONFIG_MODIFIED_BLOCK   71
#define EID_MU_PMKID_LIST           72 //type: PW_TYPE_STRING
#define EID_MU_PMK_BP               73 //type: PW_TYPE_STRING
#define EID_MU_PMKID_BP             74 //type: PW_TYPE_STRING
#define EID_COUNTDOWN_TIME          75 //type: PW_TYPE_INTEGER
#define EID_WASSP_VLAN_TAG          76 //type: INTEGER
#define EID_SSID_ID                 77 // V5R3 SA
#define EID_BULK_MU_BLOCK           78 // V5R3 SA: former EID_MU_BULK_REQ_BLOCK
#define EID_MU_BLOCK                79 // V5R3 SA
#define EID_PORT_OPEN_FLAG          80 // V5R3 SA
#define EID_WASSP_TUNNEL_TYPE       81 // V5R3 SA: WASSP-TUNNEL-DATA-ACTIVE = 1 | WASSP-TUNNEL-DATA-BACKUP=2
#define EID_LOG_TYPE                82 // V5R1 NGAP: INTEGER: 1=alarm log, 2=config log, 3=debug log, 4=crash report
#define EID_LOG_FILE                83 // V5R1 NGAP: STRING
#define EID_ALARM_SEVERITY          84 // V5R1 NGAP: INTEGER
#define EID_ALARM_DESCRIPTION       85 // V5R1 NGAP: STRING
#define EID_BULK_VNS_BLOCK          86 // V5R3 SA
#define EID_VNS_BLOCK               87 // V5R3 SA
#define EID_AP_DHCP_MODE            88 // DHCP=1, Static=2 (to be alligned with config TLV EID_DHCP_ASSIGNMENT)
#define EID_AP_IPADDR               89 // IP address of AP, for both DHCP and Static
#define EID_AP_NETMASK              90 // Netmask of AP, for both DHCP and Static
#define EID_AP_GATEWAY              91 // Gateway of AP, for both DHCP and Static
#define EID_BSSID2IP_BLOCK          92 // V6R0 VoWIFI: Block for BSSID to IP mapping
#define EID_RU_BACKUP_VERSION       93 // V6R0 Proactive AP Upgrade: Software version of the backup image
// #define EID_ACTION                  1  // V6R0 Proactive AP Upgrade: same ID as STATUS
#define EID_AC_SW_VERSION           94 // V6R0 Proactive AP Upgrade: Software version of the controller, if not included; pre-v6.0 controller is assumed
#define EID_MCAST_LAMG_LIST         95 // V7R0: WASSP_RU_LAMG_Update_Req - Multicast Optimization
#define EID_FILTER_NAME             96 // V7R0: WASPP_MU_Associate_Rsp (Filter group name, string up to 32 characters)
#define EID_FILTER_RULES            97 // V7R0: WASPP_MU_Associate_Rsp (Array of rule configuration structure bundled into a string)
#define EID_AUTH_STATE              98 // V7R0: WASPP_MU_Associate_Rsp (int: MU_NON_AUTHENTICATED=0, MU_AUTHENTICATED=1)
#define EID_MU_DISC_AFTER_AUTH      99 // V7R0: WASSP_MU_Update_Req (int: Not disconnect=0, Disconnect=1)
#define EID_MU_MAC_LIST            100 // V7R0: WASSP_MU_Bulk_Update_Req (Array of MAC 6 bytes each)
#define EID_TRANS_ID               101 // V6R1: transaction ID of the message determined at the home HWC.
#define EID_TIMEZONE_OFFSET        102 // V6R1: timezone offset
#define EID_SENSOR_FORCE_DOWNLOAD  103 // V6R1: HWM V2R3: Force download of sensor image
#define EID_SENSOR_IMG_VERSION     104 // V6R1: HWM V2R3: Sensor image version
#define EID_BRIDGE_MODE            105 // V7R0: WASSP_MU: uint: 0, 1, 2
#define EID_MU_VLAN_TAG            106 // V7R0: WASSP_MU: signed int: -2 to 4094 (For tunneled SSID, this parameter represents SSID ID)
#define EID_RATECTRL_CIR_UL        107 // V7R0: WASPP_MU: uint
#define EID_RATECTRL_CIR_DL        108 // V7R0: WASPP_MU: uint
#define EID_RATECTRL_CBS_UL        109 // V7R0: WASPP_MU: uint
#define EID_RATECTRL_CBS_DL        110 // V7R0: WASPP_MU: uint
#define EID_RATECTRL_NAME_UL       111 // V7R0: WASPP_MU: char(255)
#define EID_RATECTRL_NAME_DL       112 // V7R0: WASPP_MU: char(255)
#define EID_POLICY_NAME            113 // V7R0: WASSP_MU: char(255)

#define EID_SIAPP_PMK_BLOCK                         114
#define EID_SIAPP_PMKID                             115
#define EID_SIAPP_PMK_REAUTH                        116
#define EID_SIAPP_PMK_LIFETIME                      117
#define EID_SIAPP_PMKID_FLAG                        118
#define EID_SIAPP_MU_PMK                            119
#define EID_SIAPP_AP_NAME                           120
#define EID_SIAPP_RADIO_CONFIG_BLOCK                121
#define EID_SIAPP_CLUSTER_ACS_REQ                   122
#define EID_SIAPP_SIAPP_MU_STATS_BLOCK              123
#define EID_SIAPP_PACKET_RETRIES                    124
#define EID_SIAPP_ASSOC_IN_WLAN                     125
#define EID_SIAPP_ASSOC_IN_CLUSTER                  126
#define EID_SIAPP_REASSOC_IN_CLUSTER                127
#define EID_SIAPP_THIN_BLOCK                        128
#define EID_SIAPP_NEWAP_BSSID                       129
#define EID_SIAPP_OLDAP_BSSID                       130
#define EID_SIAPP_RAD_CACS_REQ                      131
#define EID_SIAPP_RADIOBLOCK                        132
#define EID_SIAPP_CLIENT_COUNT                      133
#define EID_SIAPP_BLOCK                             134
#define EID_SIAPP_MU_TransmittedFrameCount          135
#define EID_SIAPP_MU_ReceivedFrameCount             136
#define EID_SIAPP_MU_TransmittedBytes               137
#define EID_SIAPP_MU_ReceivedBytes                  138
#define EID_SIAPP_MU_UL_DroppedRateControlPackets   139
#define EID_SIAPP_MU_DL_DroppedRateControlPackets   140
#define EID_SIAPP_MU_DL_DroppedBufferFullPackets    141
#define EID_SIAPP_MU_DL_LostRetriesPackets          142
#define EID_SIAPP_MU_UL_DroppedRateControlBytes     143
#define EID_SIAPP_MU_DL_DroppedRateControlBytes     144
#define EID_SIAPP_MU_DL_DroppedBufferFullBytes      145
#define EID_SIAPP_MU_DL_LostRetriesBytes            146
#define EID_SIAPP_BP_BSSID                          147
#define EID_SIAPP_RADIO_ID                          148
#define EID_SIAPP_MACADDR                           149
#define EID_SIAPP_PREAUTH_REQ                       150
#define EID_SIAPP_USER_IDENTITY                     151
#define EID_SIAPP_LOADBAL_BLOCK                     152
#define EID_SIAPP_LOADBAL_PKT_TYPE                  153
#define EID_SIAPP_LOADBAL_LOADGROUP_ID              154
#define EID_SIAPP_LOADBAL_LOAD_VALUE                155
#define EID_SIAPP_AC_MGMT_MAC                       156
#define EID_SIAPP_FILTER_COS                        157

#define EID_COS                                     158 //V8.01: WASSP_MU: ap_cos_entry
#define EID_RATE_LIMIT_RESOURCE_TBL                 159 //V8.01: WASSP_MU: 9*(2 byte inCIR + 2 byte outCIR)
#define EID_UCAST_FILTER_DISABLE                    160 //V8.01: WASSP_MU: 1=disable, 0=enable

//V8.11 RAD@AP MU Session Attributes AP->AC and AC->AP
#define EID_MU_INFORM_REASON                       161 // MBA_SUCC 0; MBA_FAIL 1
                                                       // DOT1X_SUCC 2; DOT1X_FAIL 3
                                                       // CP_SUCC 4; CP_FAIL 5; MU_INFO_REPORT 6
#define EID_MU_FILTER_POLICY_NAME                  162 // char(64)
#define EID_MU_TOPOLOGY_POLICY_NAME                163 // char(64)
#define EID_MU_COS_POLICY_NAME                     164 // char(64)
#define EID_MU_FILTER_KEY                          165
#define EID_MU_TOPOLOGY_KEY                        166
#define EID_MU_COS_KEY                             167
#define EID_MU_SESSION_TIMEOUT                     168
#define EID_MU_ACCOUNTING_CLASS                    169
#define EID_MU_LOGIN_LAT_PORT                      170 // 0 = Non-auth, 1 = Auth
#define EID_MU_IDLE_TIMEOUT                        171
#define EID_MU_ACCT_INTERIM_INTERVAL               172
#define EID_MU_IP_ADDR                             173
#define EID_MU_TERMINATE_ACTION                    174 // 0 = Terminate; 1 = Reauth
//END V8.11 RAD@AP MU Session
#define EID_SITE_NAME                              175 // V8.11:RAD@AP, indicates that Assco req from that site name
#define EID_PEER_SITE_IP                           176 // V8.11 in MU assoc req indicating availability peer's IP, in AC tunnel only
// V8.11 Mitigator Enhancements
#define EID_INTERFERENCE_EVENTS_ENABLE             177
#define EID_EVENT_TYPE                             178
#define EID_EVENT_CHANNEL                          179
#define EID_EVENT_VALUE                            180

#define EID_SSS_MU_BLOCK                           181
#define EID_SSS_MU_ASSOC_TIME                      182
#define EID_SSS_TS64_MU_UPDATE                     183
#define EID_SSS_TS64_AP_CURRENT                    184
#define EID_SSS_MU_AUTH_STATE                      185
#define EID_SSS_AP_HOMEHASH                        186

#define EID_TIME_FIRST_DETECTED                    187
#define EID_TIME_LAST_REPORTED                     188
#define EID_EVENT_ARRAY                            189

#define EID_SSS_DEFAULT_SESSION_TIMEOUT            190
#define EID_SSS_SSID                               191
#define EID_SSS_PRIVACY_TYPE                       192
#define EID_POLICY_ZONE_NAME                       193
#define EID_RU_AC_EVENT_COMPONENT_ID               194
#define EID_MU_AUTH_STATE                          195
#define EID_MU_USER_NAME                           196
#define EID_BULK_TYPE                              197 //V8.11 RADAP: site=1; non-site=0(optional)
#define EID_SENT_TIME                              198 //V8.11 RADAP:the time that packet is sent
#define EID_INFORM_MU_PMK                          199 // PMK informed from AP
#define EID_COLLECTOR_IP_ADDR                      200
#define EID_ARP_PROXY                              201
#define EID_MCAST_FILTER_RULES                     202
/* Radar */
#define EID_AP_PARAMS                              203
#define EID_ASSOC_SSID_ARRAY                       204
#define EID_ASSOC_SSID_BLOCK                       205
#define EID_AP_LIST_BLOCK                          206
#define EID_AP_LIST_ARRAY                          207
#define EID_MAC_ADDR                               208
#define EID_SCAN_PROFILE_ID                        209
#define EID_ACTION_REQ                             210
#define EID_CHANNEL_LIST                           211
#define EID_COUNTERMEASURES_MAX_CH                 212
#define EID_COUNTERMEASURES_SET                    213
#define EID_SCAN_PROFILE_BLOCK                     214
#define EID_SEQ_NUM                                215
#define EID_THREAT_DEF_ARRAY                       216
#define EID_THREAT_DEF_BLOCK                       217
#define EID_THREAT_TYPE                            218
#define EID_THREAT_ID                              219
#define EID_THREAT_STATS_F                         220
#define EID_THREAT_FR_SFR                          221
#define EID_THREAT_PATTERN_ARRAY                   222
#define EID_THREAT_PATTERN_BLOCK                   223
#define EID_THREAT_PATTERN                         224
#define EID_THREAT_ALERT_TH_DUR                    225
#define EID_THREAT_CLEAR_TH_DUR                    226
#define EID_THREAT_PRIORITY                        227
#define EID_THREAT_MITIGATION_LIST                 228
#define EID_SSS_MU_IS_PORT_CLOSED                  229

#define EID_FULL_UPDATE                            230
#define EID_REASON                                 231
#define EID_SURVEILLANCE_DATA_ARRAY                232
#define EID_SURVEILLANCE_DATA_BLOCK                233
#define EID_SCAN_BSSID                             234
#define EID_PARAMS                                 235
#define EID_SCAN_RSS_RSSI                          236
#define EID_SCAN_SSID                              237
#define EID_SCAN_CAP                               238
#define EID_THREAT_CLASSIFICATION                  239
#define EID_THREAT_DATA_ARRAY                      240
#define EID_THREAT_DATA_BLOCK                      241
#define EID_STATE                                  242
#define EID_DROP_FR_CNT                            243
#define EID_STOP_ROAM_CNT                          244
#define EID_SPOOF_CNT                              245
#define EID_THREAT_CLASSIFY_ARRAY                  246
#define EID_THREAT_CLASSIFY_BLOCK                  247
#define EID_THREAT_NAME                            248
#define EID_LOCATION                               249
#define EID_ENCRYPTION_TYPE                        250

#define EID_MU_EVENT_ARRAY                         251
#define EID_MU_EVENT_BLOCK                         252
#define EID_COMPONENT_ID                           253
#define EID_MU_EVENT_STRING                        254
#define EID_BYPASS_BMCAST                          255
#define EID_GETTIMEOFDAY                           256
/* Dedicated scanner / Guardian */
#define EID_COUNTRY_ID                             257
#define EID_COUNTRY_ARRAY                          258
#define EID_COUNTRY_BLOCK                          259

#define EID_MU_EVENT_TYPE                          260

#define EID_LOCATOR_FLOOR_ID                       261
#define EID_LOCATOR_LOC_TYPE                       262
#define EID_LOCATOR_LOC_BLOCK                      263
#define EID_LOCATOR_LOC_ARRAY                      264
#define EID_LOCATOR_LOC_POINT                      265
#define EID_MU_EVENT_DETAILS                       266
#define EID_MU_EVENT_FROM_AP                       267
#define EID_MU_EVENT_LOC_BLOB                      268
#define EID_LOCATOR_LOC_AP_DISTANCE                269
#define EID_LOCATOR_LOC_PRECISION                  270
#define EID_RSS_DATA_ARRAY                         271
#define EID_RSS_DATA_BLOCK                         272
#define EID_LOCATOR_MU_ACTION                      273
#define EID_EFFECTIVE_EGRESS_VLAN                  274
#define EID_REBOOT_ACK                             275
#define EID_MU_BSSID                               276
#define EID_AUTH_FLAG                              277
#define EID_ROAMED_FLAG                            278
#define EID_MU_RSS                                 279
#define EID_FILTER_RULES_VER                       280  //v8.31 Bonjour
#define EID_FILTER_TYPE                            281  //v8.31 Bonjour
#define EID_MCAST_FILTER_BLOCK                     282  //v8.31 Bonjour
#define EID_MCAST_FILTER_BLOCK_ENTRY               283  //v8.31 Bonjour
#define EID_DEFAULT_ACTION_TYPE                    284  //v8.31 Bonjour
#define EID_DEFAULT_CONTAIN_TO_VLAN                285  //v8.31 Bonjour
#define EID_DEFAULT_BRIDGE_MODE                    286  //v8.31 Bonjour
#define EID_INVALID_POLICY                         287  //v8.31 Bonjour
#define EID_LOCATOR_FLOOR_NAME                     288
#define EID_AP_FLAGS                               289
#define EID_AP_PVID                                290
#define EID_AP_REDIRECT                            291 //v8.31 Bonjour, boolean
#define EID_MU_CVLAN_BAP                           292 //v8.31 Bonjour, informing AP contain-to-vlan has BAP topology

#define EID_MU_SESSION_ARRAY                       293
#define EID_MU_SESSION_BLOCK                       294
#define EID_MU_SESSION_ID                          295
#define EID_MU_RFS_NAME                            296
#define EID_MU_FLAGS                               297
#define EID_MU_ASSOC_TIME                          298
#define EID_MU_ACTIVE_TIME                         299
#define EID_REPORT_REQ                             300
#define EID_MU_URL                                 301
#define EID_MU_SESSION_LIFETIME                    302
#define EID_MU_REAUTH_TIMER                        303
#define EID_MU_ACCT_SESSION_ID_STRING              304
#define EID_MU_ACCT_POLICY_NAME                    305
#define EID_MU_ACCT_START_TIME                     306
#define EID_MU_ACCT_CLASS                          307
#define EID_MU_LOGIN_LAT_GROUP                     308
#define EID_MU_TUNNEL_PRIVATE_GROUP_ID_STRING      309
#define EID_MU_USER_ID_STRING                      310
#define EID_MU_DEFENDED_STATE                      311
#define EID_MU_MOD_MASK                            312
#define EID_LOCATOR_TRACKED                        313
#define EID_PORT                                   314
#define EID_RETRIES_COUNT                          315
#define EID_MODULATION_TYPE                        316
#define EID_DETECTED_ROGUE_ARRAY                   317
#define EID_DETECTED_ROGUE_BLOCK                   318
#define EID_ROGUE_DETECTION                        319
#define EID_MAC_ADDR_TX                            320
#define EID_MAC_ADDR_RX                            321
#define EID_IP_ADDR_TX                             322
#define EID_IP_ADDR_RX                             323
#define EID_TTL                                    324
#define EID_GW_IP_ADDR                             325
#define EID_LOCATOR_STATE_DATA                     326
#define EID_LOCATOR_POINT_SET                      327
#define EID_FILTER_RULE_FIXED_APP_ID               328 //v9.12 Bonjour
#define EID_FILTER_RULES_EXT_BLOCK                 329 //v9.12 Bonjour
#define EID_MU_AREA_BLOCK                          330
#define EID_MU_LOCATION                            331
#define EID_MU_LOCATION_TS                         332
#define EID_DNS_IP_ADDR                            333
#define EID_IN_SERVICE_AP_LIST                     334 //v9.15 HA Radar
#define EID_OUT_SERVICE_AP_LIST                    335 //v9.15 HA Radar
#define EID_LAST_RD_AP                             336 //v9.15 HA Radar
#define EID_ROGUE_INFO                             337 //v9.15 HA Radar
#define EID_MU_IS_FT                               338 //v9.21 802.11r
#define EID_MU_PMK_R1                              339 //v9.21 802.11r
#define EID_SIAPP_R0KHID                           340 //v9.21
#define EID_SIAPP_R1KHID                           341 //v9.21
#define EID_SIAPP_FT_NONCE                         342
#define EID_SIAPP_FT_PMKR0NAME                     343
#define EID_SIAPP_FT_R1KHID                        344
#define EID_SIAPP_FT_S1KHID                        345
#define EID_SIAPP_FT_PMKR1                         346
#define EID_SIAPP_FT_PMKR1NAME                     347
#define EID_SIAPP_FT_PAIRWISE                      348
#define EID_SIAPP_FT_LIFETIME                      349
#define EID_MU_POWER_CAP                           350 //V9.21 802.11k
#define EID_AREA_NAME                              351
#define EID_PERIODIC_NEIGHBOUR_REPORT              352
#define EID_TIMESTAMP                              353
#define EID_NEIGHBOUR_ENTRY                        354
#define EID_MU_REQ                                 355
#define EID_RU_REQ                                 356
#define EID_NEIGHBOUR_REQ                          357
#define EID_SSS_FT_ASSOC                           358
#define EID_DEFAULT_MIRRORN                        359
#define EID_FILTER_RULE_EXT_ACT_FLAGS              360
#define EID_TOPO_GROUP_MAPPING                     361 //v9.21 Topology Pooling
#define EID_MU_PMK_R0NAME                          362 //v9.21 802.11r
#define EID_CUI                                    363 //v9.21
#define EID_SSS_CAPINFO                            364 //v9.21
#define EID_SSS_CAPPOWER                           365 //v9.21
#define EID_WFA_VSA                                366
#define EID_WFA_HS20_REMED_METHOD                  367
#define EID_WFA_HS20_URL                           368
#define EID_WFA_HS20_DEAUTH_CODE                   369
#define EID_WFA_HS20_REAUTH_DELAY                  370
#define EID_WFA_HS20_SWT                           371
#define EID_POWER_STATUS                           372 //V10 sent by AP in the WASSP_P_RU_CONFIG request
#define EID_IPV6_ADDR                              373
#define EID_FILTER_RULES_APP_SIG_GROUP_ID          374
#define EID_FILTER_RULES_APP_SIG_DISP_ID           375
#define EID_MU_DEV_IDENTITY                        376
#define EID_APPL_STATS_REQ                         377
#define EID_MU_APPL_STATS_BLOCK                    378
#define EID_TOPOLOGY_ARRAY                         379
#define EID_TOPOLOGY_STRUCT                        380
#define EID_FILTER_CONFIG_STRUCT                   381
#define EID_DHCP_HOST_NAME                         382
#define EID_NEIGHBOUR_ENTRY_2                      383
#define EID_CHANNEL_ENTRY                          384
#define EID_MU_ECP_PW                              385
#define EID_MU_ECP_TOKEN                           386
#define EID_STATIC_VSA_IPADDR                      387
#define EID_STATIC_VSA_NETMASK                     388
#define EID_PKT_CAPTURE_STATUS                     389
#define EID_PKT_CAPTURE_FILTERS                    390
#define EID_PKT_F_WIRELESS                         391
#define EID_PKT_F_WIREDCLIENT                      392
#define EID_PKT_F_DIRECTION                        393
#define EID_PKT_F_RADIO                            394
#define EID_PKT_F_FLAGS                            395
#define EID_PKT_F_IP_ARRAY                         396
#define EID_PKT_F_MAC                              397
#define EID_PKT_F_PROTOCOL                         398
#define EID_PKT_F_PORT                             399
#define EID_VSA_SSID_ID                            400
#define EID_MU_AUTH_TYPE                           401
#define EID_PKT_F_MAX_PKT_COUNT                    402
#define EID_PKT_F_FLAG_2                           403
#define EID_IMAGE_PORT                             404
#define EID_FILTER_ROLE_ID                         405
#define EID_FILTER_ROLE_TIMESTAMP                  406
#define EID_PKT_CAPTURE_ID                         407
#define EID_PKT_TRUNCATED_SIZE                     408

// Do not move this line - Used for auto generation
#define EID_MAX                                    EID_PKT_TRUNCATED_SIZE  // Make sure this is the MAX!!!
#define END_OF_TLV_ID_ARR EID_MAX // For RU Session Manager

// #define's should be in order of the numbers starting 0
// and unsused types must be declared EID_CONFIG_UNUSED_<number> <number>
// The format then is used to convert the file

/*****************************************************
* Configuration Main TLVs (New in V5R0)
* Contact: Roger Urscheler
****************************************************/
#define EID_CONFIG_UNUSED_0              0
#define EID_RADIO_CONFIG_BLOCK           1
#define EID_VNS_CONFIG_BLOCK             2
#define EID_AP_ROLE                      3
#define EID_LOC_ACTION_REQ               4
#define EID_TRACE_STATUS_DEBUG           5  //1.3.6.1.2.1.92.1.1.3.1.4.8.66.80.45.68.69.66.85.71
#define EID_TRACE_STATUS_CONFIG          6  //1.3.6.1.2.1.92.1.1.3.1.4.9.66.80.45.67.79.78.70.73.71
#define EID_MIC_ERR                      7
#define EID_USE_BCAST_FOR_DISASSC        8  //1.3.6.1.4.1.13906.3.1.2.3.0
#define EID_BANDWIDTH_VOICE_ASSC         9  //1.3.6.1.4.1.13906.3.1.3.1.0
#define EID_BANDWIDTH_VOICE_REASSC      10  //1.3.6.1.4.1.13906.3.1.3.2.0
#define EID_BANDWIDTH_VIDEO_ASSC        11  //1.3.6.1.4.1.13906.3.1.3.3.0
#define EID_BANDWIDTH_VIDEO_REASSC      12  //1.3.6.1.4.1.13906.3.1.3.4.0
#define EID_BANDWIDTH_VIDEO_RESERVE     13  //1.3.6.1.4.1.13906.3.1.3.5.0
#define EID_BANDWIDTH_ADM_CTRL_RESERVE  14  //1.3.6.1.4.1.13906.3.1.3.6.0
#define EID_VLAN_TAG                    15  //1.3.6.1.4.1.13906.3.11.1.8.0
#define EID_COUNTRY_CODE                16  //1.3.6.1.4.1.13906.3.11.2.1.0
#define EID_POLL_DURATION               17  //1.3.6.1.4.1.13906.3.11.4.1.0
#define EID_POLL_INTERVAL               18  //1.3.6.1.4.1.13906.3.11.4.2.0
#define EID_LOC_AUTO_COLLECT_ENABLE     19
#define EID_POLL_MAINTAIN_CLIENT_SESSION 20 //1.3.6.1.4.1.13906.3.11.4.4.0
#define EID_TELNET_ENABLE               21  //1.3.6.1.4.1.13906.3.11.8.1.1.0
#define EID_TELNET_PASSWORD             22  //1.3.6.1.4.1.13906.3.11.8.1.2.0
#define EID_TELNET_PASSWORD_ENTRY_MODE  23  //1.3.6.1.4.1.13906.3.11.8.1.3.0
#define EID_OUTDOOR_ENABLE              24  //1.3.6.1.4.1.13906.3.11.9.1.0
#define EID_ON_DEMAND_ARRAY             25
#define EID_LAG_ENABLED                 26
#define EID_APP_POLICY_FIXED_BLOCK      27  // V9R12
#define EID_SLP_RETRY_COUNT             28  //1.3.6.1.4.1.13906.3.15.1.1.0
#define EID_SLP_RETRY_DELAY             29  //1.3.6.1.4.1.13906.3.15.1.2.0
#define EID_DNS_RETRY_COUNT             30  //1.3.6.1.4.1.13906.3.15.1.3.0
#define EID_DNS_RETRY_DELAY             31  //1.3.6.1.4.1.13906.3.15.1.4.0
#define EID_MCAST_SLP_RETRY_COUNT       32 //1.3.6.1.4.1.13906.3.15.1.5.0
#define EID_MCAST_SLP_RETRY_DELAY       33 //1.3.6.1.4.1.13906.3.15.1.6.0
#define EID_DISC_RETRY_COUNT            34 //1.3.6.1.4.1.13906.3.15.1.7.0
#define EID_DISC_RETRY_DELAY            35 //1.3.6.1.4.1.13906.3.15.1.8.0
#define EID_LOGGING_ALARM_SEV           36 //1.3.6.1.4.1.13906.3.18.1.1.1.1.4.13906.1.2.2.1.2.0.0
#define EID_BLACKLIST_ADD               37 //1.3.6.1.4.1.13906.3.16.1.2.1.2.%d
#define EID_FAILOVER_AC_IP_ADDR         38 //1.3.6.1.4.1.13906.3.11.1.7.1.2.%d
#define EID_STATIC_AC_IP_ADDR           39 //1.3.6.1.4.1.13906.3.11.1.6.1.2.%d
#define EID_DHCP_ASSIGNMENT             40 //1.3.6.1.4.1.13906.3.11.1.2.0
#define EID_STATIC_AP_IP_ADDR           41 //1.3.6.1.4.1.13906.3.11.1.3.0
#define EID_STATIC_AP_IP_NETMASK        42 //1.3.6.1.4.1.13906.3.11.1.4.0
#define EID_STATIC_AP_DEFAULT_GW        43 //1.3.6.1.4.1.13906.3.11.1.5.0
#define EID_BLACKLIST_DEL               44 //1.3.6.1.4.1.13906.3.16.1.2.1.2.%d
#define EID_MACADDR_REQ                 45 // request wired and wireless mac addresses in ACK
#define EID_AVAILABILITY_MODE           46 // currently only used internally in AC
#define EID_AP_PERSISTENCE              47
#define EID_FOREIGN_AP                  48 // 0=home AP, 1=foreign AP
#define EID_SUPP1X_CREDENTIAL_REMOVE    49 // Remove credential from AP,type: bitmask (1 - EAP-TLS, 2 - PEAP)
#define EID_SUPP1X_CERT_TFTP_IP         50 // TFTP server IP address for EAP-TLS credential, type: 4 bytes IP
#define EID_SUPP1X_CERT_TFTP_PATH       51 // TFTP path for EAP-TLS credential, type:string
#define EID_SUPP1X_PRIVATE              52 // EAP-TLS private key, blowfish encrypted, type:octets
#define EID_SUPP1X_DOMAIN               53 // Community domain, type: string
#define EID_SUPP1X_USERID               54 // PEAP user id, type: string
#define EID_SUPP1X_PASSWORD             55 // PEAP password, blowfish encrypted, type: octets
#define EID_SUPP1X_CREDENT              56 // credential configuration of AP, tpye: bitmask (1 - EAP-TLS, 2 - PEAP)
#define EID_SUPP1X_SERIAL               57 // certificate serial, type: octets
#define EID_SUPP1X_START_DATE           58 // certificate start date, type: int (Number of seconds since midnight of January 1, 1970)
#define EID_SUPP1X_END_DATE             59 // certificate expiry date, type: int (Number of seconds since midnight of January 1, 1970)
#define EID_SUPP1X_ISSUED_BY            60 // certificate issuer name, type: string, format: distinguished name
#define EID_SUPP1X_ISSUED_TO            61 // certificate issued to name, type: string, format: distinguished name
#define EID_SUPP1X_SUBJALTNAME          62 // certificate subject alternative name (required fro microsoft)
#define EID_NOT_USED_CONFIG_TLV_63      63
#define EID_FAILOVER_AC_HOME_IP_ADDR    64 // similar to EID_FAILOVER_AC_IP_ADDR
#define EID_FAILOVER_AC_FOREIGN_IP_ADDR 65 // similar to EID_FAILOVER_AC_IP_ADDR
#define EID_AP_HOSTNAME                 66 // ap hostname
#define EID_LLDP_ENABLED                67 // LLDP enable
#define EID_LLDP_TTL                    68 // LLDP Time To Live
#define EID_LLDP_ANNOUNCEMENT_INT       69 // LLDP announcement interval
#define EID_LLDP_ANNOUNCEMENT_DELAY     70 // LLDP announcement delay
#define EID_VOWIFI_EXPIRATION_TIME      71 // V7R0 VoWIFI: 1-720 hours, default value: 720
#define EID_MOBILITY_SHARED_KEY         72 // V7R0 VoWIFI: Octet string, Encrypted with blowfish using AP serial as seed
#define EID_CHANNEL_REPORT_2_4G         73 // V7R0 VoWIFI: Octet string, New channel report that is not based on VNS, but instead a union of all ACS channel frequencies use in the system.
#define EID_CHANNEL_REPORT_5G           74 // V7R0 VoWIFI: Octet string, New channel report that is not based on VNS, but instead a union of all ACS channel frequencies use in the system.
#define EID_RATE_CONTROL_BLOCK          75 // V8R11 Site
#define EID_AP_DNS                      76
#define EID_STATIC_MTU                  77 // V7R41 AP static MTU
#define EID_MACFILTER_MODE              78
#define EID_SITE_CONFIG_BLOCK           79
#define EID_TOPOLOGY_BLOCK              80 // V8R11 Site
#define EID_AP_NAME                     81 // V6R1 HWM V2R3
#define EID_ANTENNA_MODELS              82 // V6R1 Antenna Models V2
#define EID_AIRTIME_FAIRNESS_LEVEL      83 // V7R0 Airtime Fairness: uint, 0-4
#define EID_VLAN_DEFAULT                84 // Thick AP default vlan  -1:untagged, 0~4094
#define EID_CLUSTER_PASSWORD            85 // Think/thin AP: Some password
#define EID_SIAPP_PRIVACY               86 // Think/thin AP: boolean
#define EID_LED_STATUS                  87 // AP LED status
#define EID_LBS_SRC_IP                  88
#define EID_LBS_SRC_PORT                89
#define EID_LBS_DST_IP                  90
#define EID_LBS_DST_PORT                91
#define EID_LBS_MCAST                   92
#define EID_LBS_TAG_MODE                93
#define EID_ETH_PORT_MODE               94
#define EID_INTER_AP_ROAM               95
#define EID_MGMT_MAC                    96
#define EID_REAL_CAPTURE_TIMEOUT        97
#define EID_POLICY_BLOCK                98
#define EID_FILTER_CONFIG_BLOCK         99
#define EID_COS_CONFIG_BLOCK            100 // CoS definitions
#define EID_LOCATION_BASED_LOOKUP_BLOCK 101 // Lookup table needed for location based policy
#define EID_RADIUS_SERVER_BLOCK         102
#define EID_BLACKLIST_WOUI_ADD          103
#define EID_BLACKLIST_WOUI_DEL          104
#define EID_SNIFFER_RADIO_BITMAP        105
#define EID_MCAST_ASSEMB                106 // V9R01 AP multicast assembly
#define EID_JUMBO_FRAME                 107 // V9R01 AP jumbo frame
#define EID_DYN_ON_DEMAND_ARRAY         108 // Location dynamic on-demand MAC list
#define EID_BANDWIDTH_BE_ASSC           109
#define EID_BANDWIDTH_BE_REASSC         110
#define EID_BANDWIDTH_BK_ASSC           111
#define EID_BANDWIDTH_BK_REASSC         112
#define EID_NETFLOW_EXPORT_INTERVAL     113
#define EID_MIRRORN_PACKETS             114
#define EID_ICON_NAME                   115 //v10 HotSpot 2.0
#define EID_ICON_FILE                   116 //v10 HotSpot 2.0
#define EID_ICON_BLOCK                  117 //v10 HotSpot 2.0
#define EID_BOARD_STATUS                118 //v10 Used locally by AP
#define EID_CP_MU_AUTO_LOGIN            119 // Int: Client auto login handling: 0 â€“ Hide auto login, 1 â€“ Redirect auto login, 2- Drop auto login
#define EID_EXTAPP_CONF_BLOCK           120 // v10.11 application control
#define EID_RB_REDIRECT                 121 // v10.11 role based redirection
#define EID_RB_REDIRECT_PORTS           122 // v10.11 role based redirection
#define EID_S_TOPOLOGY_ARRAY            123
#define EID_S_TOPOLOGY_STRUCT           124
#define EID_S_TOPOLOGY_KEY              125
#define EID_S_TOPOLOGY_VLAN_TAG         126
#define EID_S_TOPOLOGY_ARP_PROXY        127
#define EID_S_TOPO_MCAST_FILTER_CONFIG_BLOCK 128
#define EID_MCAST_PRIORITIZED_VOICE     129
#define EID_IOT_CONTROL                 130 // Will not be used in future
#define EID_IOT_APPLICATION_ID          131
#define EID_AP_LOCATION                 132
#define EID_IOT_ADMIN                   133
#define EID_IOT_IMAGE                   134
#define EID_IOT_BLE_ADVERTISE_INTERVAL  135
#define EID_IOT_BLE_ADVERTISE_POWER     136
#define EID_IOT_IBEACON_MAJOR           137
#define EID_IOT_IBEACON_MINOR           138
#define EID_IOT_IBEACON_UUID            139
#define EID_STATIC_ADSP_IP_ADDR         140
#define EID_OBSS_CHAN_ADJ_ACTIVE        141
#define EID_IOT_BLE_SCAN_SRC_IP         142
#define EID_IOT_BLE_SCAN_SRC_PORT       143
#define EID_IOT_BLE_SCAN_DST_IP         144
#define EID_IOT_BLE_SCAN_DST_PORT       145
#define EID_IOT_BLE_SCAN_INTERVAL       146
#define EID_IOT_BLE_SCAN_WINDOW         147
#define EID_IOT_BLE_SCAN_MIN_RSSI       148
#define EID_LSENSE_SERVER               149
#define EID_LSENSE_MIN_RSSI             150
#define EID_LSENSE_REP_FREQ             151
#define EID_DPI_SIG_HASH                152
#define EID_ANT_MODELS_IOT              153
#define EID_FABRICATTACH_ARRAY          154
#define EID_IOT_THREAD_CHANNEL          155
#define EID_IOT_THREAD_FACTORY_RESET    156
#define EID_IOT_THREAD_SHORT_PAN_ID     157
#define EID_IOT_THREAD_SHORT_EUI        158
#define EID_IOT_THREAD_PSKD             159
#define EID_IOT_THREAD_MASTER_KEY       160
#define EID_IOT_THREAD_NWK_NAME         161
#define EID_IOT_THREAD_COMM_CREDENTIAL  162
#define EID_IOT_THREAD_LONG_EUI         163
#define EID_IOT_THREAD_EXTENDED_PAN_ID  164
#define EID_AP_VSA_SSID_ID              165
#define EID_AP_STATIC_VSA_IPADDR        166
#define EID_AP_STATIC_VSA_NETMASK       167
#define EID_IOT_BLE_URL                 168
#define EID_AP_PERSONALITY              169  // wing7
#define EID_ADSP_RADIO_SHARE            170
#define EID_LOCATION_TENANT_ID          171
#define EID_IOT_BLE_BEACON_MEASURED_RSSI 172
#define EID_MU_NUM_RADAR_BACK           173
#define EID_IOT_BLE_SCAN_POST_INTERVAL  174
#define EID_IOT_BLE_SCAN_POST_URL       175
#define EID_MLRRM_ENABLE               176

// Do not move this line - Used for auto generation
#define EID_CONFIG_MAX                  EID_MLRRM_ENABLE   // Make sure this is the MAX!!!

// #define's should be in order of the numbers starting 0
// and unsused types must be declared EID_SUB_UNUSED_<number> <number>
// The format then is used to convert the file

/*****************************************************
* Beast sub-TLVs
* Contact: Chong Wang
****************************************************/
#define EID_DOT11_NOT_USED                           0
#define EID_DOT11_ACKFailureCount                    1
#define EID_DOT11_FCSErrorCount                      2
#define EID_DOT11_FailedCount                        3
#define EID_DOT11_FrameDuplicateCount                4
#define EID_DOT11_MulticastReceivedFrameCount        5
#define EID_DOT11_MulticastTransmittedFrameCount     6
#define EID_DOT11_MultipleRetryCount                 7
#define EID_DOT11_RTSFailureCount                    8
#define EID_DOT11_RTSSuccessCount                    9
#define EID_DOT11_ReceivedFragementCount             10
#define EID_DOT11_RetryCount                         11
#define EID_DOT11_TransmittedFragmentCount           12
#define EID_DOT11_TransmittedFrameCount              13
#define EID_DOT11_WEBUndecryptableCount              14
#define EID_DOT11_WEPExcludedCount                   15
#define EID_DOT11_WEPICVErrorCount                   16
#define EID_DRM_AllocFailures                        17
#define EID_DRM_CurrentChannel                       18
#define EID_DRM_CurrentPower                         19
#define EID_DRM_DataTxFailures                       20
#define EID_DRM_DeviceType                           21 //Not Used
#define EID_DRM_InDataPackets                        22
#define EID_DRM_InMgmtPackets                        23
#define EID_DRM_LoadFactor                           24
#define EID_DRM_MgmtTxFailures                       25
#define EID_DRM_MsgQFailures                         26
#define EID_DRM_NoDRMCurrentChannel                  27
#define EID_DRM_OutDataPackets                       28
#define EID_DRM_OutMgmtPackets                       29
#define EID_IF_InBcastPackets                        30
#define EID_IF_InDiscards                            31
#define EID_IF_InErrors                              32
#define EID_IF_InMcastPackets                        33
#define EID_IF_InOctets                              34
#define EID_IF_InUcastPackets                        35
#define EID_IF_MTU                                   36
#define EID_IF_OutBcastPackets                       37
#define EID_IF_OutDiscards                           38
#define EID_IF_OutErrors                             39
#define EID_IF_OutOctets                             40
#define EID_IF_OutUcastPackets                       41
#define EID_IF_OutMCastPackets                       42
#define EID_MU_Address                               43
#define EID_MU_AssociationCount                      44
#define EID_MU_AuthenticationCount                   45
#define EID_MU_DeAssociationCount                    46
#define EID_MU_DeAuthenticationCount                 47
#define EID_MU_IfIndex                               48
#define EID_MU_ReAssociationCount                    49
#define EID_MU_ReceivedBytes                         50
#define EID_MU_ReceivedErrors                        51
#define EID_MU_ReceivedFrameCount                    52
#define EID_MU_ReceivedRSSI                          53
#define EID_MU_ReceivedRate                          54
#define EID_MU_TransmittedBytes                      55
#define EID_MU_TransmittedErrors                     56
#define EID_MU_TransmittedFrameCount                 57
#define EID_MU_TransmittedRSSI                       58
#define EID_MU_TransmittedRate                       59
#define EID_MU_RF_STATS_END                          60
#define EID_RFC_1213_SYSUPTIME                       61
#define EID_STATS_ETHER_BLOCK                        62
#define EID_STATS_RADIO_A_BLOCK                      63
#define EID_STATS_RADIO_B_G_BLOCK                    64
#define EID_MU_STATS_BLOCK                           65
#define EID_STATS_WDS_BLOCK                          66
#define EID_WDS_ROLE                                 67
#define EID_WDS_PARENTMAC                            68
#define EID_WDS_SSID                                 69
#define EID_STATS_SUPP1x_BLOCK                       70
#define EID_STATS_SUPP1X_CREDENT                     71
#define EID_STATS_SUPP1X_END_DATE                    72
#define EID_DOT11_ProtectionMode                     73 // new protection mode value
#define EID_MU_TSPEC_Stats_Block                     74 // TSPEC stats (see TSPEC FDB3/4)
#define EID_DOT11_ChannelBonding                     75 // new channel bonding value
#define EID_DCS_STAS_NF                              76 //
#define EID_DCS_STAS_CHANN_OCCUPANCY                 77 //
#define EID_DCS_STAS_TX_OCCUPANCY                    78 //
#define EID_DCS_STAS_RX_OCCUPANCY                    79 //
#define EID_CAC_DEAUTH                               80 //
#define EID_MU_IP                                    81 //
#define EID_STATS_CHECK                              82 //
#define EID_WDS_BONDING                              83 //
#define EID_MU_ReceivedRSS                           84 // RSS value
#define EID_MU_RadioIndex                            85 // Radio Index
#define EID_MU_FltPktAllowed                         86 // allowed MU packets
#define EID_MU_FltPktDenied                          87 // denied MU packets
#define EID_MU_FltName                               88 // MU filter group name
#define EID_MU_FltReset                              89 // Reset filter stats
#define EID_MU_DL_DroppedRateControlPackets          90
#define EID_MU_DL_DroppedRateControlBytes            91
#define EID_MU_DL_DroppedBufferFullPackets           92
#define EID_MU_DL_DroppedBufferFullBytes             93
#define EID_MU_DL_LostRetriesPackets                 94
#define EID_MU_DL_LostRetriesBytes                   95
#define EID_MU_UL_DroppedRateControlPackets          96
#define EID_MU_UL_DroppedRateControlBytes            97
#define EID_SiappClusterName                         98
#define EID_LB_LoadGroupID                           99
#define EID_LB_LoadValue                            100
#define EID_LB_MemberCount                          101
#define EID_LB_ClientCount                          102
#define EID_LB_LoadState                            103
#define EID_LB_ProbeReqsDeclined                    104
#define EID_LB_AuthReqsDeclined                     105
#define EID_LB_RebalanceEvents                      106
#define EID_MU_DOT11_CAPABILITY                     107
#define EID_BAND_PREFERENCE_STATS                   108
#define EID_R_LC_STATUS                             109
#define EID_WDS_ROAM_COUNT                          110
#define EID_WDS_TX_RETRIES                          111
#define EID_RealCaptureTimeout                      112
#define EID_MU_11N_ADVANCED                         113
#define EID_MU_Count                                114
#define EID_R_Clear_channel                         115
#define EID_R_RX_Occupancy                          116
#define EID_STATS_VNS_BLOCK                         117 // v8.11 For Radius@AP VNS stats
#define EID_STATS_VNS_ENTRY                         118 // v8.11 For Radius@AP VNS stats
#define EID_ETH_STATUS                              119 // v8r21 AP3725 dual eth
#define EID_LAG_ACT_AGGREGATE_STATUS                120 // v9r01 AP38xx LAG
#define EID_PERFORMANCE_STATS                       121
#define EID_APPL_STATS                              122
#define EID_APPL_COUNT                              123
#define EID_APPL_MAC                                124
#define EID_APPL_DISPLAY_ID                         125
#define EID_APPL_TX_BYTES                           126
#define EID_APPL_RX_BYTES                           127
#define EID_MU_TRANSMITTED_MCS                      128
#define EID_MU_TOTAL_LOST_FRAMES                    129
#define EID_MU_DL_AGGR_SIZE                         130
#define EID_RX_PHYS_ERRORS                          131
#define EID_RADIO_HARDWARE_RESET                    132
#define EID_TOTAL_PACKET_ERROR_RATE                 133
#define EID_STATS_PORT_BLOCK                        134
#define EID_PORT_ID                                 135
#define EID_MU_RADIO_ID                             136
#define EID_IF_LinkSpeed                            137
#define EID_MU_DL_RETRY_ATTEMPTS                    138
#define EID_FILTER_STATS_BLOCK                      139
#define EID_FILTER_STATS_RULES_BLOCK                140
#define EID_ROLE_ID                                 141
#define EID_ROLE_TIMESTAMP                          142
#define EID_DEFAULT_HIT_COUNT_IN                    143
#define EID_DEFAULT_HIT_COUNT_OUT                   144
#define EID_RULE_HIT_COUNT_IN                       145
#define EID_RULE_HIT_COUNT_OUT                      146
#define EID_STATS_RADIO_ID                          147
#define EID_STATS_RADIO_BLOCK                       148
#define EID_MU_RFQI                                 149
#define EID_RADIO_RFQI                              150
#define EID_IF_InBcastPackets_D                     151
#define EID_IF_InDiscards_D                         152
#define EID_IF_InErrors_D                           153
#define EID_IF_InMcastPackets_D                     154
#define EID_IF_InOctets_D                           155
#define EID_IF_InUcastPackets_D                     156
#define EID_IF_OutBcastPackets_D                    157
#define EID_IF_OutDiscards_D                        158
#define EID_IF_OutErrors_D                          159
#define EID_IF_OutOctets_D                          160
#define EID_IF_OutUcastPackets_D                    161
#define EID_IF_OutMCastPackets_D                    162
#define EID_MU_ReceivedFrameCount_D                 163
#define EID_MU_TransmittedFrameCount_D              164
#define EID_MU_ReceivedErrors_D                     165
#define EID_MU_TransmittedErrors_D                  166
#define EID_MU_ReceivedBytes_D                      167
#define EID_MU_TransmittedBytes_D                   168
#define EID_MU_rc_ul_dropped_pkts_D                 169
#define EID_MU_rc_ul_dropped_bytes_D                170
#define EID_MU_rc_dl_dropped_pkts_D                 171
#define EID_MU_rc_dl_dropped_bytes_D                172

// Do not move this line - Used for auto generation
#define EID_STATS_TLV_MAX                           EID_MU_rc_dl_dropped_bytes_D // Make sure this is the MAX

//EID_STATS_VNS_ENTRY
#define EID_V_STATS_VNSID                           1
#define EID_V_STATS_RADCL_REQS                      2
#define EID_V_STATS_RADCL_FAILED                    3
#define EID_V_STATS_RADCL_REJECTS                   4

enum eid_mu_login_lat_port_val {
    EID_MU_LOGIN_LAT_PORT_NON_AUTH = 0,
    EID_MU_LOGIN_LAT_PORT_AUTH
};

enum eid_mu_att_terminate_action_val {
    EID_MU_TERMINATE_ACTION_TERMINATE = 0,
    EID_MU_TERMINATE_ACTION_REAUTH
};


// #define's should be in order of the numbers starting 0
// and unsused types must be declared EID_R_UNUSED_<number> <number>
// The format then is used to convert the file

/*****************************************************
* CM sub-TLVs
* Contact: Roger Urscheler
****************************************************/
// Radio A and BG settings
#define EID_R_UNUSED_0                  0
#define EID_R_RADIO_ID                  1   //1.3.6.1.2.1.2.2.1.7.%d
#define EID_R_ENABLE_RADIO              2   //1.3.6.1.2.1.2.2.1.7.%d
#define EID_R_CHANNEL                   3   //1.3.6.1.4.1.13906.3.1.1.7.1.2.%d
#define EID_R_OP_RATE_SET               4   //1.2.840.10036.1.1.1.11.%d
#define EID_R_OP_RATE_MAX               5   //1.3.6.1.4.1.13906.3.1.1.7.1.5.%d
#define EID_R_BEACON_PERIOD             6   //1.2.840.10036.1.1.1.12.%d
#define EID_R_DTIM_PERIOD               7   //1.2.840.10036.1.1.1.13.%d
#define EID_R_RTS_THRESHOLD             8   //1.2.840.10036.2.1.1.2.%d
#define EID_R_ANTENNA_TYPE              9   // V6R0 only: AP4102 antenna model
#define EID_R_A_CHAN_PLAN_TYPE          10
#define EID_R_FRAGMENT_THRESHOLD        11  //1.2.840.10036.2.1.1.5.%d
#define EID_R_POWER_LEVEL               12  //1.2.840.10036.4.3.1.10.%d
#define EID_R_LC_ASSOC_TRY_MAX          13  // V8R11
#define EID_R_LC_STRICT_CLIENT_COUNT_LIMIT 14  // Strict limit for max number of clients per radio
#define EID_R_DIVERSITY_RX              15  //1.3.6.1.4.1.13906.3.1.1.10.1.1.%d
#define EID_R_DIVERSITY_TX              16  //1.3.6.1.4.1.13906.3.1.1.10.1.2.%d
#define EID_R_SHORT_PREAMBLE            17  //1.3.6.1.4.1.13906.3.1.1.7.1.1.%d
#define EID_R_BASIC_RATE_MAX            18  //1.3.6.1.4.1.13906.3.1.1.7.1.3.%d
#define EID_R_BASIC_RATE_MIN            19  //1.3.6.1.4.1.13906.3.1.1.7.1.4.%d
#define EID_R_HW_RETRIES                20  //1.3.6.1.4.1.13906.3.1.1.7.1.7.%d
#define EID_R_TX_POWER_MIN              21  // Format: integer
#define EID_R_TX_POWER_MAX              22  // Format: integer
#define EID_R_INTERFERENCE_EVENT_TYPE   23  // bitmask: Bluetooth 0x01,Microwave 0x02,Cordless Phone 0x04,Constant Wave 0x08,Video Bridge 0x10
#define EID_R_DOMAIN_ID                 24  // Format: 16 characters
#define EID_R_B_ENABLE                  25  //1.3.6.1.4.1.13906.3.1.1.4.1.1.%d
#define EID_R_B_BASIC_RATES             26  //1.3.6.1.4.1.13906.3.1.1.4.1.2.%d
#define EID_R_G_ENABLE                  27  //1.3.6.1.4.1.13906.3.1.1.5.1.1.%d
#define EID_R_G_PROTECT_MODE            28  //1.3.6.1.4.1.13906.3.1.1.5.1.3.%d
#define EID_R_G_PROTECT_TYPE            29  //1.3.6.1.4.1.13906.3.1.1.5.1.4.%d
#define EID_R_G_PROTECT_RATE            30  //1.3.6.1.4.1.13906.3.1.1.5.1.5.%d
#define EID_R_G_BASIC_RATE              31  //1.3.6.1.4.1.13906.3.1.1.5.1.6.%d
#define EID_R_A_SUPPORT_802_11_J        32  //1.3.6.1.4.1.13906.3.1.1.9.1.1.%d
#define EID_R_ATPC_EN_INTERVAL          33  // Format: integer   0 - disable,  range TBD
#define EID_R_ACS_CH_LIST               34  // Format: numChannel * 4 bytes, 4 bytes for each channel without delimiter
#define EID_R_TX_POWER_ADJ              35  // Format: integer <-- 5.0 ATPC
#define EID_R_WIRELESS_MODE             36  // Bitmask:0x0001=b,0x0002=g,0x0004=a,0x0008=j,0x0010=n
#define EID_R_N_CHANNEL_BONDING         37  // 802.11n Channel Bonding: 0=No Bonding, 1=Bond-Up, 2=Bond-Down
#define EID_R_N_CHANNEL_WIDTH           38  // 802.11n Channel Width: 1=20Mhz, 2=40Mhz, 3=both
#define EID_R_N_GUARD_INTERVAL          39  // 802.11n Guard Interval: 1=short, 2=long
#define EID_R_N_PROTECT_ENABLE          40  // 802.11n Channel Protection Mode: 0=disabled, 1=enabled
#define EID_R_N_PROTECT_TYPE            41  // 802.11n 40Mhz Channel Protection: 0=None, 1=CTS only, 2=RTS/CTS
#define EID_R_N_PROTECT_OFFSET          42  // 802.11n Channel Protection Offset: 1=20Mhz, 2=25MHz
#define EID_R_N_PROTECT_BUSY_THRESHOLD  43  // 802.11n 40Mhz Channel Busy Threshold: 0...100
#define EID_R_AGGREGATE_MSDU            44  // Aggregate MSDUs: 0=disabled, 1=enabled
#define EID_R_AGGREGATE_MSDU_MAX_LEN    45  // Aggregate MSDU Max Length: 2290...4096
#define EID_R_AGGREGATE_MPDU            46  // Aggregate MPDUs: 0=disabled, 1=enabled
#define EID_R_AGGREGATE_MPDU_MAX_LEN    47  // Aggregate MPDU Max Length: 1024...65535
#define EID_R_AGGREGATE_MPDU_SUBFRAMES  48  // Aggregate MPDU Max # of Sub-frames: 2...64
#define EID_R_ADDBA_SUPPORT             49  // ADDBA Support: 0=disabled, 1=enabled
#define EID_R_DCS_MODE                  50  // Dynamic channel selection mode (int): 0=off, 1=monitor, 2=active
#define EID_R_DCS_NOISE_THRESHOLD       51  // Dynamic channel selection noise threshold (int)
#define EID_R_DCS_CHL_OCCUPANCY_THRESHOLD 52  // Dynamic channel selection channel occupancy (int)
#define EID_R_DCS_UPDATE_PERIOD         53  // Dynamic channel selection update period (int)
#define EID_R_ANTENNA_SELECTION         54  // Antenna selection (int). LSB 0 - Left, bit 1 - Middle, bit 2 - Right
#define EID_R_BKGND_SCAN_ENABLE         55  // V7R0 VoWIFI: 0=off, 1=on
#define EID_R_BKGND_SCAN_INTERVAL       56  // V7R0 VoWIFI: 1-30, default value: 30
#define EID_R_BCMCRATECTRL_AIRTIME      57  // V7R0 Broadcast/Multicast rate control: The percentage of airtime allowed for Broadcast/Multicast traffic
#define EID_R_CACS                      58  // Thick/thin AP: Cluster ACS
#define EID_R_MAX_DISTANCE              59  // Configurable Max Distance (used for WDS)
#define EID_R_LOADGROUP_ID              60  // Load Group ID
#define EID_R_GROUP_BALANCING           61  // Load balance features enabled (bit0 = load balance, bit1 - Band Pref, bit2 - radio load
#define EID_R_LC_CLIENT_COUNT_LIMIT     62  // Max number of clients per radio
#define EID_R_ENABLE_LDPC               63  // Advanced 11n features
#define EID_R_ENABLE_TXSTBC             64  // Advanced 11n features
#define EID_R_ENABLE_RXSTBC             65  // Advanced 11n features
#define EID_R_ENABLE_TXBF               66  // Advanced 11n features
#define EID_R_TXBF_CLIENT_LIMIT         67  // Advanced 11n features
#define EID_R_INTERFERENCE_WAIT_TIME    68  // V8R11 (15 - 300 seconds)
#define EID_R_LC_ASSOC_TRY_TIMEOUT      69  // V8R11
#define EID_R_OPT_MCAST_PS              70  // V8R21
#define EID_R_MCAST_TO_UCAST_DELIVERY   71  // V8R21
#define EID_R_ADAPTABLE_RATE_FOR_MCAST  72  // V8R21
#define EID_R_ANTENNA_PORT_ATT          73  // V9R01
#define EID_R_PROBE_SUP_ENABLE          74  // V9R21
#define EID_R_PROBE_SUP_CAP             75  // V9R21
#define EID_R_PROBE_SUP_THRESH          76  // V9R21
#define EID_R_MU_NUM_RADAR_BACK         77 // wns0019810
#define EID_R_ADSP_RADIO_SHARE          78  //Wing7, radio-share per radio. AP internal used, in case back-porting
#define EID_R_OCS_CHANNEL_ENABLE        79  //Wing7, BOOLEAN; enable/disable OCS; AP internal used, in case back-porting
#define EID_R_OCS_CHANNEL_LIST          80  //Wing7, list of (freq:UINT16, channel_width:UINT16); AP internal used, in case back-porting
#define EID_R_OCS_SCAN_INTERVAL         81  //Wing7, UINT32, [2,100] in dtims; AP internal used, in case back-porting
#define EID_R_SENSOR_SCAN_MODE          82  //Wing7, enum (Default-Scan|Channel-Lock|Custom-Scan; AP internal used, in case back-porting
#define EID_R_SENSOR_SCAN_LIST          83  //Wing7, list of (freq:UINT16, channel_width:UINT16); AP internal used, in case back-porting
#define EID_R_11AX_OFDMA                84  //Wing7, V7.2.1 dl|ul|both|""
#define EID_R_11AX_TWT                  85  //Wing7, V7.2.1 boolean
#define EID_R_11AX_BSSCOLOR             86  //Wing7, V7.2.1 [1..63] | 0: disable

// Do not move this line - Used for auto generation
#define EID_R_MAX                       EID_R_11AX_BSSCOLOR  // Make sure this is the MAX

// #define's should be in order of the numbers starting 0
// and unsused types must be declared EID_V_UNUSED_<number> <number>
// The format then is used to convert the file

//VNS settings
#define EID_V_UNUSED_0                  0
#define EID_V_RADIO_ID                  1   //
#define EID_V_VNS_ID                    2   //
#define EID_V_TURBO_VOICE               3   //
#define EID_V_PROP_IE                   4   //
#define EID_V_ENABLE_802_11_H           5   //
#define EID_V_POWER_BACKOFF             6   //
#define EID_V_BRIDGE_MODE               7   // Per VLAN BP Bridging Mode: int: 0=tunneled, 1=bridged,  2=branch CP, 3=WDS
#define EID_V_VLAN_TAG                  8   // VLAN tag: int: -2=if bridge mode disabled, -1=untag ,1-4094
#define EID_V_PROCESS_IE_REQ            9   //
#define EID_V_ENABLE_U_APSD             10  //
#define EID_V_ADM_CTRL_VOICE            11  //
#define EID_V_ADM_CTRL_VIDEO            12  //
#define EID_V_QOS_UP_VALUE              13  //
#define EID_V_PRIORITY_OVERRIDE         14  //
#define EID_V_DSCP_OVERRIDE_VALUE       15  //
#define EID_V_ENABLE_802_11_E           16  //
#define EID_V_ENABLE_WMM                17  //
#define EID_V_LEGACY_CLIENT_PRIORITY    18  //
#define EID_V_SSID_ID                   19  //
#define EID_V_SSID_BCAST_STRING         20  //
#define EID_V_SSID_SUPPRESS             21  //
#define EID_V_802_1_X_ENABLE            22  //
#define EID_V_802_1_X_DYN_REKEY         23  //
#define EID_V_WPA_ENABLE                24  //
#define EID_V_WPA_V2_ENABLE             25  //
#define EID_V_WPA_PASSPHRASE            26  //
#define EID_V_WPA_CIPHER_TYPE           27  //
#define EID_V_WPA_V2_CIPHER_TYPE        28  //
#define EID_V_WEP_KEY_INDEX             29  //
#define EID_V_WEP_DEFAULT_KEY_VALUE     30  //
#define EID_V_CHANNEL_REPORT            31  //
#define EID_V_WDS_SERVICE               32  // type: TLV_INT
#define EID_V_WDS_BSSID_PARENT          33  // tpye: TLV_MACADDR
#define EID_V_WDS_BRIDGE                34  // type: TLV_INT
#define EID_V_OKC_ENABLED               35  // type: TLV_INT        ;okc/preauth enable/disable
#define EID_V_MU_ASSOC_RETRIES          36  // type: TLV_INT        ;assoc_req retry times
#define EID_V_MU_ASSOC_TIMEOUT          37  // type: TLV_INT        ;assoc_req timeout
#define EID_V_WDS_PARENT                38 // type TLV_STRING 32 char max
#define EID_V_WDS_BACK_PARENT           39  // type TLV_STRING 32 char max
#define EID_V_WDS_NAME                  40  // type TLV_STRING 32 char max (AP name)
#define EID_V_SESSION_AVAIL             41  // type: TLV_INT, 0=disabled, 1=enabled
#define EID_V_UL_POLICER_ACTION         42  // type: TLV_INT (see TSPEC FDB3/4)
#define EID_V_DL_POLICER_ACTION         43  // type: TLV_INT (see TSPEC FDB3/4)
#define EID_V_ENABLE_802_11_K           44 // V7R0 VoWIFI: Enable 802.1k
#define EID_V_ENABLE_802_11_H_BG        45 // V7R0 VoWIFI: Enable 802.1h for bg radio
#define EID_V_SITE_EGRESS_FILTER_MODE   46 // V8R11: Egress filtering enabled for site WLAN
#define EID_V_DEFAULT_IDLE_PRE_TIMEOUT  47
#define EID_V_DEFAULT_IDLE_POST_TIMEOUT 48
#define EID_V_IGNORE_COS                49 // V8R11 Ignore CoS in this VNS
#define EID_V_RADIUS_SERVER_INDEX2      50 // V8.11
#define EID_V_MCAST_OPTIMIZATION        51 // V7R0 Multicast: IGMP Snooping enable/disable per VNS (TRUE/FALSE, default value: FALSE)
#define EID_V_MCAST_IGMP_TIMEOUT        52 // V7R0 Multicast: IGMP Snooping LDMG entry expire timer in minutes (1~60, default value: 1)
#define EID_V_MCAST_FILTER_ENABLE       53 // V7R0 Multicast: Multicast filtering at AP enabled (TRUE/FALSE, default value: FALSE)
#define EID_V_FILTER_CONFIG_BLOCK       54 // V6R1 ACL@AP: Filter config block
#define EID_V_DATA_REASSEMBLY_ENABLE    55 // V7R0 Fragmentation: TRUE/FALSE, default value: FALSE
#define EID_V_UCAST_FILTER_ENABLE       56 // V6R1 ACL@AP: Enable filtering at the AP: TRUE/FALSE, default value: FALSE
#define EID_V_RATECTRL_CIR_UL           57 // V7R0 PolicyMgr: Uplink CIR
#define EID_V_RATECTRL_CIR_DL           58 // V7R0 PolicyMgr: Downlink CIR
#define EID_V_RATECTRL_CBS_UL           59 // V7R0 PolicyMgr: Uplink CBS
#define EID_V_RATECTRL_CBS_DL           60 // V7R0 PolicyMgr: Downlink CBS
#define EID_V_AIRTIME_FAIRNESS_ENABLE   61 // V7R0 Airtime Fairness: bool, 0-1
#define EID_V_POWERSAVE_ENABLE          62 // V7R2 Power save enable/disable
#define EID_V_GROUP_KP_SAVE_RETRY       63 // V7R2 Group Power Save retry
#define EID_V_BALANCE_GROUP             64 // V7R41 WLAN is a member of band preference group
#define EID_V_MESH_TYPE                 65 // V7R41 Mesh type (0 - static, 1 - dynamic)
#define EID_V_MESH_ROAMING_THRESHOLD    66 // V7R41 Mesh roaming  threshold (0 - low, 2 - medium, 3 - high)
#define EID_V_COS                       67 // V8.01: ap_cos_entry
#define EID_V_RATE_LIMIT_RESOURCE_TBL   68 // V8.01: 9*(2 byte inCIR + 2 byte outCIR)
#define EID_V_AP_AUTH_CLIENT_MODES      69 // V8.11 Bitwise OR of the following bits:bit_0 = MBA bit_1 = DOT1X bit_2 = Captive Portal
#define EID_V_DEFAULT_POLICY_INDEX      70 // V8.11 Policy to apply to new sessions before any other policy is applied. Index into row inside EID_POLICY_BLOCK. Cannot be -1
#define EID_V_AUTH_POLICY_INDEX         71 // V8.11
#define EID_V_NONAUTH_POLICY_INDEX      72 // V8.11
#define EID_V_RADIUS_SERVER_INDEX       73 // V8.11
#define EID_V_NAS_IP                    74 // V8.11
#define EID_V_NAS_ID                    75 // V8.11
#define EID_V_VSA_SELMASK               76 // V8.11
#define EID_V_MBA_OPTIONS_MASK          77 // V8.11
#define EID_V_MBA_TIMEOUT_POLICY_KEY    78 // V8.11
#define EID_V_WLAN_SERVICE_NAME         79 // V8.11
#define EID_V_DEFAULT_SESSION_TIMEOUT   80 // V8.11
#define EID_V_RADIUS_CALLED_STATION_ID  81 // V8.11
#define EID_V_CAPTIVE_PORTAL            82 // V8.11
#define EID_V_COS_CONFIG_BLOCK          83 // V8R11 CoS definitions
#define EID_V_TOPOLOGY_KEY              84 // V8R21
#define EID_V_MU_INIT_PERIOD_BEHAVIOUR  85 // V8R11
#define EID_V_DYNAMIC_EGRESS_VLANS      86 // V8R31
#define EID_V_STATIC_EGRESS_VLANS       87 // V8R31
#define EID_V_FLAGS                     88 // V8.31 policy flags: AP_POLICY_FLAG_*
#define EID_V_DEFAULT_ACTION            89 // V8.31 Bonjour
#define EID_V_CONTAIN_TO_VLAN           90 // V8.31 Bonjour
#define EID_V_PVID_TOPOLOGY_KEY         91 // V8.31 Bonjour
#define EID_V_AP_REDIRECT               92 //v9.01 Bonjour, boolean
#define EID_V_ADM_CTRL_BE               93
#define EID_V_ADM_CTRL_BK               94
#define EID_V_11K_ENABLE                95
#define EID_V_11K_RM_CAP                96
#define EID_V_11R_ENABLE                97
#define EID_V_11R_R0KH_ID               98
#define EID_V_11R_MD_ID                 99
#define EID_V_MGMT_FRAME_PROTECTION     100
#define EID_V_NETFLOW                   101
#define EID_V_WLAN_DEFAULT_MIRRORN      102
#define EID_V_DEFAULT_MIRRORN           103
#define EID_V_11U_ANQP_BLOCK            104 //v10 HotSpot 2.0
#define EID_V_HS2_BLOCK                 105 //v10 HotSpot 2.0
#define EID_V_APP_IDENTIFICATION_ENABLED 106 //v10 application identification
#define EID_V_PRIVACY                   107 //v10 HOtspot 2.0
#define EID_V_11U_OSEN                  108 //v10 HotSpot 2.0
#define EID_V_QOS_IN_USE                109 // 64 characters array: 0 - do not use DSCP value, 1 - use DSCP value
#define EID_V_CP_CONFIG_STRUCT          110 // v10.11 Captive portal at AP. Following are members of EID_V_CP_CONFIG_STRUCT block:
#define EID_V_CP_IDENTITY               111 // String:
#define EID_V_CP_PASSPHRASE             112 // String: Shared secret in encryption form
#define EID_V_CP_REDIRECT_URL           113 // External captive portal URL
#define EID_V_CP_USE_HTTPS              114 // Boolean
#define EID_V_CP_AUTH_URL               115 // String: Where to redirect MU after successful authentication: "original": Original destination, "session": Captive portal session page, <custom URL> User specified URL
#define EID_V_CP_FLAGS                  116 // Int: Bitmap for captive portal flags
#define EID_V_CP_AP_FQDN                117 // String: MU will connect to this URL after successful authentication with captive portal to provide authentication
#define EID_V_VNS_NAME                  118 // String: MU will connect to this URL after successful authentication with captive portal to provide authentication status. This TLV is optional but either this TLV or EID_V_CP_FLAGS TLV with bit 0 set to 1 must be present
#define EID_V_LDAP_SERVER_INDEX         119 // v10.31 for CP authentication with AD
#define EID_V_AIRTIME_RESERVATION       120 // v10.41 airtime reservation doe AP38xx/AP39xx
#define EID_V_MU_DISCON_REQ_ENABLE      121
#define EID_V_BEACON_IE_AP_NAME         122 // type: TLV_BOOL, v7.1.2 AP name in beacon vendor specific IE
#define EID_V_WPA_V3_TYPE               123 // V7.2 - Add WPA3 support
#define EID_V_MBO                       124 // V7.3 - Add MBO support

// Do not move this line - Used for auto generation
#define EID_V_MAX                       EID_V_MBO // Make sure this is the MAX

//Members of EID_11U_ANQP_BLOCK block
#define EID_11U_3GPP_CELL_NETWORK_ARRAY        1 //v10 HotSpot 2.0
#define EID_11U_3GPP_CELL_NETWORK_STRUCT       2 //v10 HotSpot 2.0
#define EID_11U_3GPP_CELL_NETWORK_MCC          3 //v10 HotSpot 2.0
#define EID_11U_3GPP_CELL_NETWORK_MNC          4 //v10 HotSpot 2.0
#define EID_11U_ACCESS_NETWORK_TYPE            5 //v10 HotSpot 2.0
#define EID_11U_ASRA                           6 //v10 HotSpot 2.0
#define EID_11U_DOMAIN_NAME                    7 //v10 HotSpot 2.0
#define EID_11U_EAP_AUTH_PARAM                 8 //v10 HotSpot 2.0
#define EID_11U_EAP_AUTH_PARAM_ARRAY           9 //v10 HotSpot 2.0
#define EID_11U_EAP_AUTH_PARAM_STRUCT         10 //v10 HotSpot 2.0
#define EID_11U_EAP_AUTH_TYPE                 11 //v10 HotSpot 2.0
#define EID_11U_EAP_METHOD                    12 //v10 HotSpot 2.0
#define EID_11U_EAP_METHODS_ARRAY             13 //v10 HotSpot 2.0
#define EID_11U_EAP_METHODS_STRUCT            14 //v10 HotSpot 2.0
#define EID_11U_HESSID                        15 //v10 HotSpot 2.0
#define EID_11U_INTERNET_AVAILABLE            16 //v10 HotSpot 2.0
#define EID_11U_IPV4_ADDR_TYPE_AVAIL          17 //v10 HotSpot 2.0
#define EID_11U_IPV6_ADDR_TYPE_AVAIL          18 //v10 HotSpot 2.0
#define EID_11U_NAI_REALM                     19 //v10 HotSpot 2.0
#define EID_11U_NAI_REALM_ARRAY               20 //v10 HotSpot 2.0
#define EID_11U_NAI_REALM_STRUCT              21 //v10 HotSpot 2.0
#define EID_11U_NETWORK_AUTH_TYPE             22 //v10 HotSpot 2.0
#define EID_11U_ROAMING_CONSORTIUM            23 //v10 HotSpot 2.0
#define EID_11U_ROAMING_CONSORTIUM_ARRAY      24 //v10 HotSpot 2.0
#define EID_11U_VENUE_INFO_GROUP_CODE         25 //v10 HotSpot 2.0
#define EID_11U_VENUE_INFO_TYPE_ASSIGNMENTS   26 //v10 HotSpot 2.0
#define EID_11U_VENUE_NAME_ARRAY              27 //v10 HotSpot 2.0
#define EID_11U_VENUE_NAME                    28 //v10 HotSpot 2.0
#define EID_11U_NETWORK_AUTH_TYPE_URL         29 //v10 HotSpot 2.0

//Members of EID_HS2_BLOCK block
#define EID_HS2_ANQP_DOMAIN_ID                 1 //v10 HotSpot 2.0
#define EID_HS2_CONNECTION_CAP                 2 //v10 HotSpot 2.0
#define EID_HS2_CONNECTION_CAP_ARRAY           3 //v10 HotSpot 2.0
#define EID_HS2_DGAF                           4 //v10 HotSpot 2.0
#define EID_HS2_ICON_NAME                      5 //v10 HotSpot 2.0
#define EID_HS2_OPERATING_CLASS                6 //v10 HotSpot 2.0
#define EID_HS2_OP_FRIENDLY_NAME_ARRAY         7 //v10 HotSpot 2.0
#define EID_HS2_OP_FRIENDLY_NAME               8 //v10 HotSpot 2.0
#define EID_HS2_OSU_STRUCT                     9 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_ARRAY                  10 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_STRUCT                 11 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_DESC_ARRAY             12 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_DESC                   13 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_FRIENDLY_NAME_ARRAY    14 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_FRIENDLY_NAME          15 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_ICON_ARRAY             16 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_ICON_STRUCT            17 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_METHOD_LIST            18 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_NAI                    19 //v10 HotSpot 2.0
#define EID_HS2_OSU_SP_SERVER_URI             20 //v10 HotSpot 2.0
#define EID_HS2_OSU_SSID                      21 //v10 HotSpot 2.0
#define EID_HS2_RELEASE                       22 //v10 HotSpot 2.0
#define EID_HS2_WAN_METRICS_STRUCT            23 //v10 HotSpot 2.0
#define EID_HS2_UPLINK_LOAD                   24 //v10 HotSpot 2.0
#define EID_HS2_UPLINK_SPEED                  25 //v10 HotSpot 2.0
#define EID_HS2_WIDTH                         26 //v10 HotSpot 2.0
#define EID_HS2_DOWLINK_LOAD                  27 //v10 HotSpot 2.0
#define EID_HS2_DOWLINK_SPEED                 28 //v10 HotSpot 2.0
#define EID_HS2_HIGHT                         29 //v10 HotSpot 2.0

enum eid_v_cp_flags_val {
    EID_V_CP_FLAGS_IP_PORT      =0x00000001,
    EID_V_CP_FLAGS_AP_NAME_SER  =0x00000002,
    EID_V_CP_FLAGS_BSSID        =0x00000004,
    EID_V_CP_FLAGS_VNS_NAME     =0x00000008,
    EID_V_CP_FLAGS_SSID         =0x00000010,
    EID_V_CP_FLAGS_MU_MAC       =0x00000020,
    EID_V_CP_FLAGS_MU_ROLE      =0x00000040,
    EID_V_CP_FLAGS_VLAN         =0x00000080,
    EID_V_CP_FLAGS_TIMESTAMP    =0x00000100,
    EID_V_CP_FLAGS_SIGNATURE    =0x00000200,
    EID_V_CP_FLAGS_AP_ETH_MAC   =0x00000400,
    EID_V_CP_FLAGS_AP_LOCATION  =0x00000800
};

// V8.11 Bitwise OR of the following bits:bit_0 = MBA bit_1 = DOT1X bit_2 = Captive Portal
enum eid_v_ap_auth_client_modes_val {
    EID_V_AP_AUTH_CLIENT_MODES_MBA     =1,
    EID_V_AP_AUTH_CLIENT_MODES_DOT1X   =2,
    EID_V_AP_AUTH_CLIENT_MODES_CP      =4
};

// V8.11 For Site use. Must match VSA bit selection as defined in radclient/future/radius/inc/chantryradlib.h
enum eid_v_vsa_selmask_val {
    EID_V_VSA_SELMASK_AP =                ( 1 << 0 ),
    EID_V_VSA_SELMASK_VNS =               ( 1 << 1 ),
    EID_V_VSA_SELMASK_SSID =              ( 1 << 2 ),
    EID_V_VSA_SELMASK_POLICY =            ( 1 << 4 ),
    EID_V_VSA_SELMASK_TOPOLOGY =          ( 1 << 5 ),
    EID_V_VSA_SELMASK_INGRESS_RATE_CTRL = ( 1 << 6 ),
    EID_V_VSA_SELMASK_EGRESS_RATE_CTRL =  ( 1 << 7 ),
    EID_V_VSA_SELMASK_AP_WIRED_MAC =      ( 1 << 8 ),
    EID_V_VSA_SELMASK_ALL =               ((1 << 9) - 1 )
};

//RADIUS: Global Radius Config Block (V8R11: Site)
#define EID_RADIUS_ID                   0 // V8R11 Site: identifier of the RADIUS server
#define EID_RADIUS_IP_NAME              1 // V8R11 Site: IP address or DNS name of a RADIUS server
#define EID_RADIUS_SHAREDSECRET         2 // V8R11 Site: Shared secret of a RADIUS server corresponding to the IP above. This is encrypted using Blowfish and the AP serial #
#define EID_RADIUS_PROTOCOL             4 // V8.11 enum eid_radius_protocol_val
#define EID_RADIUS_PORT                 5 // V8.11 default EID_RADIUS_PORT_1812
#define EID_RADIUS_TIMEOUT              6 // V8.11 seconds
#define EID_RADIUS_RETRY                7 // V8.11 default 3
#define EID_RADIUS_MBA_MAC_FORMAT       8 // V8.11 enum eid_radius_mba_mac_format
#define EID_RADIUS_MBA_PASSWORD         9 // V8.11 MAC password
#define EID_RAIDUS_MBA_MAX   EID_RADIUS_MBA_PASSWORD

#define EID_RADIUS_PORT_1812            1812 // V8.11 default radius port

enum eid_radius_protocol_val {
    EID_RADIUS_PROTOCOL_PAP = 0,
    EID_RADIUS_PROTOCOL_CHAP,
    EID_RADIUS_PROTOCOL_MS_CHAP,
    EID_RADIUS_PROTOCOL_MS_CHAP2
};

enum eid_radius_mba_mac_format_val {
    EID_RADIUS_MBA_MAC_FORMAT_0 = 0,    // XXXXXXXXXXXX
    EID_RADIUS_MBA_MAC_FORMAT_1,        // XX:XX:XX:XX:XX:XX
    EID_RADIUS_MBA_MAC_FORMAT_2,        // XX-XX-XX-XX-XX-XX
    EID_RADIUS_MBA_MAC_FORMAT_3,        // XXXX.XXXX.XXXX
    EID_RADIUS_MBA_MAC_FORMAT_4,        // XXXXXX-XXXXXX
    EID_RADIUS_MBA_MAC_FORMAT_5,        // XX XX XX XX XX XX
    EID_RADIUS_MBA_MAC_FORMAT_6,        // xxxxxxxxxxxx
    EID_RADIUS_MBA_MAC_FORMAT_7,        // xx:xx:xx:xx:xx:xx
    EID_RADIUS_MBA_MAC_FORMAT_8,        // xx-xx-xx-xx-xx-xx
    EID_RADIUS_MBA_MAC_FORMAT_9,        // xxxx.xxxx.xxxx
    EID_RADIUS_MBA_MAC_FORMAT_10,       // xxxxxx-xxxxxx
    EID_RADIUS_MBA_MAC_FORMAT_11        // xx xx xx xx xx xx
};

enum eid_v_mba_options_mask_val {
    EID_V_MBA_OPTIONS_MASK_ENABLE_ON_ROAM =     ( 1 << 0 ),
    EID_V_MBA_OPTIONS_MASK_AUTO_AUTHENTICATE =  ( 1 << 1 ),
    EID_V_MBA_OPTIONS_MASK_ALLOW_UNAUTHORIZED = ( 1 << 2 ),
    EID_V_MBA_OPTIONS_MASK_ALL =                ( 0x7 )
};

//RADSRV:Radius Server Config Block for a specific VNS (for V6R0: Branch 802.1x)
#define EID_V_RADSRV_SRV_ID             1 // V8R11 Site: The ID of a RADIUS server corresponding to one already listed in the RADIUS block
#define EID_V_RADSRV_SRV_TYPE           2 // V8R11 Site: The type of radius server this is, corresponding to the IP above.
#define EID_V_RADSRV_SRV_PORT           3 // V8R11 Site: The port number of the server to use corresponding to the IP above.
#define EID_V_RADSRV_SRV_RETRY          4 // V8R11 Site: The number of retries for the server corresponding to the IP above.
#define EID_V_RADSRV_SRV_TIMEOUT        5 // V8R11 Site: The number of seconds to wait before a retry of the server corresponding to the IP above.
#define EID_V_RADSRV_AUTH_TYPE          6 // V8R11 Site: The authorization type for MBA (in the event that MBA servers are configured).
#define EID_V_RADSRV_PASSWORD           7 // V8R11 Site: This is the password corresponding to the MBA authorization type above. The password is encrypted using Blowfish and the AP serial #.
#define EID_V_RADSRV_NAS_IP             8 // V8R11 Site: This is the NAS-IP address that is used for RADIUS requests. If the HWC sends this parameter as 0.0.0.0, the AP will instead use its IP address.
#define EID_V_RADSRV_NAS_ID             9 // V8R11 Site: This is the NAS-ID that is used for RADIUS requests. If the HWC sends this parameter as an empty TLV, the AP will instead use its name.

//FILTER: Filter Config Block (for V6R0: ACL@AP)
//         same values used in EID_V_FILTER_CONFIG_BLOCK and EID_G_FILTER_CONFIG_BLOCK
#define EID_V_FILTER_NAME               1 // V6R1 ACL@AP: Filter group name
#define EID_V_FILTER_RULES              2 // V6R1 ACL@AP: Array of rule configuration structure ap_flt_rule_wassp_entry2
#define EID_V_FILTER_TYPE               3 // V6R1 ACL@AP: the filter type. MCAST=1,DEFAULT=3,GLOBAL=4,CUSTOM=6
#define EID_V_FILTER_KEY                4 // V8.11 same value used is policy block
#define EID_V_SITE_FILTER_RULES         5 // V8R11 Filter rules in site format ap_site_flt_rule_wassp_entry
#define EID_V_FILTER_BYPASS_BMCAST      6 // V8.21 wns0007783 Allow all bcast and multicast
#define EID_V_FILTER_RULES_EXT_BLOCK    7 // V9.12 The block for one of each following tlv together (only one for now) EID_V_FILTER_RULE_FIXED_APP_ID Can add future new TLV in the block
#define EID_V_SITE_FILTER_RULES_EXT_BLOCK 8 // V9.12 The block for one of each following tlv together (only one for now) EID_V_SITE_FILTER_RULE_FIXED_APP_ID Can add future new TLV in the block
#define EID_V_FILTER_ROLE_ID           9
#define EID_V_FILTER_ROLE_TIMESTAMP   10
#define EID_V_FILTER_MAX  EID_V_FILTER_ROLE_TIMESTAMP

#define EID_V_FILTER_RULE_FIXED_APP_ID             1 // V9.12 Binary for array of short.  The TLV length is 4 + 2 bytes * Ã¢â‚¬Å“number of valid filter rules
#define EID_V_FILTER_RULE_EXT_ACT_FLAGS            2 // V9.21 Binary for array of short.  The TLV length is 4 + 2 bytes * Ã¢â‚¬Å“number of valid filter rules
#define EID_V_FILTER_RULES_APP_SIG_GROUP_ID        3 // V10.11 Application visibility
#define EID_V_FILTER_RULES_APP_SIG_DISP_ID         4 // V10.11 Application visibility
#define EID_V_FILTER_RULES_IPV6_ADDR               5 // V10.11 IPv6

#define EID_V_SITE_FILTER_RULE_FIXED_APP_ID        1 // V9.12 Binary for array of short.  The TLV length is 4 + 2 bytes * Ã¢â‚¬Å“number of valid filter rules
#define EID_V_SITE_FILTER_RULE_EXT_ACT_FLAGS       2 // V9.21 Binary for array of short.  The TLV length is 4 + 2 bytes * Ã¢â‚¬Å“number of valid filter rules
#define EID_V_SITE_FILTER_RULES_APP_SIG_GROUP_ID   3 // V10.11 Application visibility
#define EID_V_SITE_FILTER_RULES_APP_SIG_DISP_ID    4 // V10.11 Application visibility
#define EID_V_SITE_FILTER_RULES_IPV6_ADDR          5 // V10.11 IPv6

/*Members of EID_S_TOPO_MCAST_FILTER_CONFIG_BLOCK: */
#define EID_S_TOPO_MCAST_FILTER_NAME               1
#define EID_S_TOPO_MCAST_FILTER_RULES              2
#define EID_S_TOPO_MCAST_FILTER_RULES_EXT_BLOCK    3
/* Members of EID_S_TOPO_MCAST_FILTER_RULES_EXT_BLOCK: */
#define EID_S_TOPO_MCAST_FILTER_RULE_EXT_ACT_FLAGS 1
#define EID_S_TOPO_MCAST_FILTER_RULES_IPV6         2

//BSSID2IP: BSSID to IP mapping block (for V6R0: VoWIFI)
#define EID_BSSID2IP_BSSID                          1 // V7R0 VoWIFI: Base MAC Address (6 bytes)
#define EID_BSSID2IP_IP                             2 // V7R0 VoWIFI: IP address (4 bytes)

//EID_SITE_CONFIG_BLOCK: Site Config Block (V8.11: Rad@AP)
#define EID_G_SITE_ENABLE                           4 // Enable or Disable Site
#define EID_G_SITE_NAME                             5 // Max 32 chars.  Sent to AC in WASSP_MU_ASSOC_REQ
#define EID_G_RADIUS_CLIENT_AT_AP                   6 // Enables Radius Client @ AP. Requires EID_G_SITE_ENABLE == TRUE
#define EID_G_HYBRID_POLICY_MODE                    7 // 1 = POLICY_ONLY (Pre-8.11 behaviour)2 = VLAN_TUN_ID_ONLY 3 = COMBINATION
#define EID_G_LOCATION                              8 // Up to 32 characters used when EID_V_RADIUS_CALLED_STATION_ID == 1 (USE_LOCATION)
#define EID_G_INVALID_POLICY                        9  //v8.31 Bonjour

//EID_SITE_CONFIG_BLOCK: Site Config Block (V10.31: NAC@AP)
#define EID_NAC_MBA_LOCAL_AUTH                      10
#define EID_NAC_RULE_ARRAY                          11
#define EID_NAC_RULE_BLOCK                          12
#define EID_NAC_RULE_FLAGS                          13
#define EID_NAC_RULE_AUTH_TYPE                      14
#define EID_NAC_RULE_USER_USERNAME_GROUP_KEY        15
#define EID_NAC_RULE_USER_LDAPUSER_GROUP_KEY        16
#define EID_NAC_RULE_ENDSYS_HOSTNAME_GROUP_KEY      17
#define EID_NAC_RULE_ENDSYS_LDAPHOST_GROUP_KEY      18
#define EID_NAC_RULE_ENDSYS_IPv4_GROUP_KEY          19
#define EID_NAC_RULE_ENDSYS_MAC_GROUP_KEY           20
#define EID_NAC_RULE_DEV_TYPE_GROUP_KEY             21
#define EID_NAC_RULE_LOCATION_GROUP_KEY             22
#define EID_NAC_RULE_TIME_GROUP_KEY                 23
#define EID_NAC_RULE_POLICY_KEY                     24
#define EID_NAC_LDAP_USER_GROUP_ARRAY               25
#define EID_NAC_LDAP_USER_GROUP_BLOCK               26
#define EID_NAC_LDAP_USER_GROUP_KEY                 27
#define EID_NAC_LDAP_USER_GROUP_MATCH_MODE          28
#define EID_NAC_LDAP_USER_ATTR_ARRAY                29
#define EID_NAC_LDAP_USER_ATTR_BLOCK                30
#define EID_NAC_LDAP_USER_ATTR_KEY                  31
#define EID_NAC_LDAP_USER_ATTR_VAL                  32
#define EID_NAC_USERNAME_GROUP_ARRAY                33
#define EID_NAC_USERNAME_GROUP_BLOCK                34
#define EID_NAC_USERNAME_GROUP_KEY                  35
#define EID_NAC_USERNAME_ARRAY                      36
#define EID_NAC_USERNAME                            37
#define EID_NAC_HOSTNAME_GROUP_ARRAY                38
#define EID_NAC_HOSTNAME_GROUP_BLOCK                39
#define EID_NAC_HOSTNAME_GROUP_KEY                  40
#define EID_NAC_HOSTNAME_ARRAY                      41
#define EID_NAC_HOSTNAME                            42
#define EID_NAC_HOST_IPv4_GROUP_ARRAY               43
#define EID_NAC_HOST_IPv4_GROUP_BLOCK               44
#define EID_NAC_HOST_IPv4_GROUP_KEY                 45
#define EID_NAC_HOST_IPv4_ARRAY                     46
#define EID_NAC_HOST_IPv4_ADDRESS                   47
#define EID_NAC_LDAP_HOST_GROUP_ARRAY               48
#define EID_NAC_LDAP_HOST_GROUP_BLOCK               49
#define EID_NAC_LDAP_HOST_GROUP_KEY                 50
#define EID_NAC_LDAP_HOST_GROUP_MATCH_MODE          51
#define EID_NAC_LDAP_HOST_ATTR_ARRAY                52
#define EID_NAC_LDAP_HOST_ATTR_BLOCK                53
#define EID_NAC_LDAP_HOST_ATTR_KEY                  54
#define EID_NAC_LDAP_HOST_ATTR_VAL                  55
#define EID_NAC_HOST_MAC_GROUP_ARRAY                56
#define EID_NAC_HOST_MAC_GROUP_BLOCK                57
#define EID_NAC_HOST_MAC_GROUP_KEY                  58
#define EID_NAC_HOST_MAC_ARRAY                      59
#define EID_NAC_HOST_MAC                            60
#define EID_NAC_DEV_TYPE_GROUP_ARRAY                61
#define EID_NAC_DEV_TYPE_GROUP_BLOCK                62
#define EID_NAC_DEV_TYPE_GROUP_KEY                  63
#define EID_NAC_DEV_TYPE_ARRAY                      64
#define EID_NAC_DEV_TYPE_ATTRIBUTE                  65
#define EID_NAC_TIME_GROUP_ARRAY                    66
#define EID_NAC_TIME_GROUP_BLOCK                    67
#define EID_NAC_TIME_RANGE_GROUP_KEY                68
#define EID_NAC_TIME_RANGE_ARRAY                    69
#define EID_NAC_TIME_RANGE                          70
#define EID_NAC_LOC_GROUP_ARRAY                     71
#define EID_NAC_LOC_GROUP_BLOCK                     72
#define EID_NAC_LOC_GROUP_KEY                       73
#define EID_NAC_LOC_ATTR_ARRAY                      74
#define EID_RESERVED_75                             75  // Reserved for EID_RATE_CONTROL_BLOCK in site
#define EID_NAC_LOC_ATTR_BLOCK                      76
#define EID_NAC_LOC_SSID                            77
#define EID_NAC_LOC_APID                            78
#define EID_NAC_LDAP_SRV_ARRAY                      79
#define EID_RESERVED_80                             80  // Reserved for EID_TOPOLOGY_BLOCK in site
#define EID_NAC_LDAP_SRV_BLOCK                      81
#define EID_NAC_LDAP_SRV_KEY                        82
#define EID_NAC_LDAP_SRV_URL                        83
#define EID_NAC_LDAP_SRV_TIMEOUT                    84
#define EID_NAC_LDAP_USER_SRCH_ROOT                 85
#define EID_NAC_LDAP_HOST_SRCH_ROOT                 86
#define EID_NAC_LDAP_OU_SRCH_ROOT                   87
#define EID_NAC_LDAP_USER_OBJ_CLASS                 88
#define EID_NAC_LDAP_USER_SRCH_ATTR                 89
#define EID_NAC_LDAP_HOST_OBJ_CLASS                 90
#define EID_NAC_LDAP_HOST_SRCH_ATTR                 91
#define EID_NAC_LDAP_FLAGS                          92
#define EID_NAC_LDAP_USER_AUTH_TYPE                 93
#define EID_NAC_LDAP_OU_OBJ_CLASS_ARRAY             94
#define EID_NAC_LDAP_OU_OBJ_CLASS                   95
#define EID_NAC_KRB_REALM_ARRAY                     96
#define EID_NAC_KRB_REALM_BLOCK                     97
#define EID_RESERVED_98                             98  // Reserved for EID_POLICY_BLOCK in site
#define EID_RESERVED_99                             99  // Reserved for EID_FILTER_CONFIG_BLOCK in site
#define EID_RESERVED_100                           100  // Reserved for EID_COS_CONFIG_BLOCK in site
#define EID_RESERVED_101                           101  // Reserved for EID_LOCATION_BASED_LOOKUP_BLOCK in site
#define EID_RESERVED_102                           102  // Reserved for EID_RADIUS_SERVER_BLOCK in site
#define EID_NAC_KRB_KDCS                           103
#define EID_NAC_LDAP_SERVER_INDEX                  104  // v10.31 for LDAP search (MU authorization)
#define EID_NAC_SERVER_CONFIG_ARRAY                105
#define EID_NAC_SERVER_CONFIG_BLOCK                106
#define EID_NAC_SERVER_FQDN                        107
#define EID_NAC_SERVER_IPV4_ADDR                   108
#define EID_NAC_SERVER_DOMAIN                      109
#define EID_NAC_SERVER_ADMIN_ID                    110
#define EID_NAC_SERVER_ADMIN_PWD                   111
#define EID_NAC_SERVER_WORKGROUP                   112
#define EID_NAC_RULE_ENDSYS_WEB_AUTH_USER_GROUP_KEY 113 // v10.41
#define EID_NAC_WEB_AUTH_USER_GROUP_ARRAY          114  // v10.41
#define EID_NAC_WEB_AUTH_USER_GROUP_BLOCK          115  // v10.41
#define EID_NAC_WEB_AUTH_USER_GROUP_KEY            116  // v10.41
#define EID_NAC_WEB_AUTH_USER_ARRAY                117  // v10.41
 
//#define EID_RESERVED_120                           120  // Reserved for EID_EXTAPP_CONF_BLOCK in site
//#define EID_RESERVED_121                           121  // Reserved for EID_POLICY_REDIRECT in site
//#define EID_RESERVED_122                           122  // Reserved for EID_POLICY_REDIRECT_PORTS in site
//#define EID_RESERVED_123                           123  // Reserved for EID_S_TOPOLOGY_ARRAY in site
//#define EID_RESERVED_124                           124  // Reserved for EID_S_TOPOLOGY_STRUCT in site
//#define EID_RESERVED_125                           125  // Reserved for EID_S_TOPOLOGY_KEY in site
//#define EID_RESERVED_126                           126  // Reserved for EID_S_TOPOLOGY_VLAN_TAG in site
//#define EID_RESERVED_127                           127  // Reserved for EID_S_TOPOLOGY_ARP_PROXY in site
//#define EID_RESERVED_128                           128  // Reserved for EID_S_TOPO_MCAST_FILTER_CONFIG_BLOCK in site
//#define EID_RESERVED_129                           129  // Reserved for EID_MCAST_PRIORITIZED_VOICE in site


#define EID_G_SITE_MAX                              EID_NAC_WEB_AUTH_USER_ARRAY // This should be the max value

enum eid_g_hybrid_policy_mode_val {
    EID_G_HYBRID_POLICY_MODE_LEGACY = 1,
    EID_G_HYBRID_POLICY_MODE_VLAN_TUN_ID = 2,
    EID_G_HYBRID_POLICY_MODE_BOTH = 3    //   EID_G_HYBRID_POLICY_MODE_LEGACY|EID_G_HYBRID_POLICY_MODE_VLAN_TUN_ID
};

//EID_POLICY_BLOCK: Policy Table
#define EID_POLICY_ENTRY_NAME           1 // V8.11 policy Name (up to 256 bytes).  Used as search key for policy name found in Radius response.  Also serves as a separator for rows in the table
#define EID_POLICY_ENTRY_KEY            2 // V8.11 A unique ID Key to lookup associated Policy entry
#define EID_POLICY_TOPOLOGY_KEY         3 // V8.11 A unique ID Key to allow controller to lookup associated topology.  -1 for unchanged
#define EID_POLICY_TOPOLOGY_VLAN_ID     4 // V8.11 VLAN ID applicable only when EID_POLICY_TOPOLOGY_KEY != -1.  -1 for untagged
#define EID_POLICY_TOPOLOGY_TYPE        5 // V8.11 Topology type applicable only when EID_POLICY_TOPOLOGY_KEY != -1
#define EID_POLICY_FILTER_KEY           6 // V8.11 Lookup key into entry in table defined by EID_G_FILTER_CONFIG_BLOCK. -1 for unchanged
#define EID_POLICY_COS_KEY              7 // V8.11 Lookup key into entry in table defined by EID_COS_CONFIG_BLOCK. -1 for unchanged.
#define EID_POLICY_IGNORE_COS           8 // V8.11 indicate if CoS should be ignored on a policy. The values for TLV will be: 0 - do not ignore CoS. 1 - ignore CoS
#define EID_POLICY_DYNAMIC_EGRESS_VLANS 9 // V8.31 list of dynamic egress VLAN IDs: array of 16 bit integers, lower 12 bits is VLAN ID
#define EID_POLICY_STATIC_EGRESS_VLANS 10 // V8.31 list of static egress VLAN IDs: array of 16 bit integers, lower 12 bits is VLAN ID
#define EID_POLICY_DEFAULT_ACTION      11 // V8.31 default action for policy:
                                          // DefaultActionNoChange =0,
                                          // DefaultActionNone = 1,
                                          // DefaultActionAllow = 2,
                                          // DefaultActionDeny = 3,
                                          // DefaultActionContainToVlan = 4
#define EID_POLICY_FLAGS               12 // V8.31 policy flags: AP_POLICY_FLAG_*
#define EID_POLICY_DEFAULT_MIRRORN     13
#define EID_POLICY_RB_REDIRECT_URL     14
#define EID_POLICY_MAX  EID_POLICY_RB_REDIRECT_URL

#define AP_POLICY_FLAG_HAVE_ALLOW_PVID 0x01 // Deprecated in V9R01
#define AP_POLICY_FLAG_HAVE_ALLOW      0x01
#define AP_POLICY_FLAG_HAVE_ROUTED     0x02
#define AP_POLICY_FLAG_AP_FILTERING    0x04

//EID_COS_CONFIG_BLOCK
#define EID_COS_KEY                     1 // V8.11 A unique ID Key to allow controller to lookup the associated CoS entry
#define EID_COS_DEFINITION              2 // V8.11 Binary encoded CoS definition following existing format for EID_V_COS
#define EID_COS_IN_RATE_LIMIT           3 // V8.11 Intput Rate Limit in Kbps
#define EID_COS_OUT_RATE_LIMIT          4 // V8.11 Output Rate Limit in Kbps

//EID_LOCATION_BASED_LOOKUP_BLOCK
#define EID_LOC_VLAN_ID_KEY             1 // V8.11 VLAN ID Key value, Also serves as a separator for rows in the table.
#define EID_LOC_POLICY_TOPOLOGY_KEY     2 // V8.11 Corresponding Policy ID Key (EID_POLICY_ENTRY_KEY) associated with the policy where topology will be obtained
#define EID_LOC_MAX  EID_LOC_POLICY_TOPOLOGY_KEY

//EID_APP_POLICY_FIXED_BLOCK
#define EID_APP_POLICY_ENTRY_BLOCK      1 // V9.12 The block contains exactly 1 instance of each following TLVs
#define EID_APP_POLICY_FIXED_BLOCK_MAX  EID_APP_POLICY_ENTRY_BLOCK

// EID_APP_POLICY_ENTRY_BLOCK
#define EID_APP_POLICY_APP_ID           1 // V9.12 Application ID, unsigned short int Value up to APP_POLICY_FIXED_MAX_ID
#define EID_APP_POLICY_OFFSET_LW        2 // V9.12 Binary for array of 16 bits short. The TLV length is 4 + 2 bytes * valid_entry_number
#define EID_APP_POLICY_MASK             3 // V9.12 Binary for array of 32 bits word. The TLV length is 4 + 4 bytes * valid_entry_number
#define EID_APP_POLICY_VALUE            4 // V9.12 Binary for array of 32 bits word. The TLV length is 4 + 4 bytes * valid_entry_number
#define EID_APP_POLICY_ENTRY_BLOCK_MAX EID_APP_POLICY_VALUE

// Filter rule, used for EID_V_FILTER_RULES

// Filter Entry Flags are higher 2 bytes
#define AP_FILTER_ENTRY_FLAG_ETHER_TYPE            0x0001
#define AP_FILTER_ENTRY_TEST_FLAGS_SOURCE_IP_OUT   0x0002
#define AP_FILTER_ENTRY_TEST_FLAGS_DEST_IP_IN      0x0004
#define AP_FILTER_ENTRY_FLAG_PROT_TYPE             0x0008
#define AP_FILTER_ENTRY_TEST_FLAGS_SOURCE_PORT_OUT 0x0010
#define AP_FILTER_ENTRY_TEST_FLAGS_DEST_PORT_IN    0x0020
#define AP_FILTER_ENTRY_FLAG_TCP_FLAGS             0x0040 // can be removed
#define AP_FILTER_ENTRY_FLAGS_OUT_DIR              0x0080
#define AP_FILTER_ENTRY_FLAGS_IN_DIR               0x0100
#define AP_FILTER_ENTRY_TEST_FLAGS_SOURCE_IP_IN    0x0200
#define AP_FILTER_ENTRY_TEST_FLAGS_SOURCE_PORT_IN  0x0400
#define AP_FILTER_ENTRY_TEST_FLAGS_DEST_IP_OUT     0x0800
#define AP_FILTER_ENTRY_TEST_FLAGS_DEST_PORT_OUT   0x1000
#define AP_FILTER_ENTRY_FLAGS_UP                   0x2000
#define AP_FILTER_ENTRY_FLAGS_TOS                  0x4000
#define AP_FILTER_ENTRY_FLAGS_DEFAULT_RULE         0x8000 // deprecated in V8R31

#define AP_FILTER_ENTRY_FLAGS_SHADOW_FRAG          0x0040
#define AP_FILTER_ENTRY_FLAGS_SHADOW_ARP           0x8000

// Filter Action Flags are lower 2 bytes
#define AP_FILTER_ENTRY_ACTION_DENY                 0x0001
#define AP_FILTER_ENTRY_ACTION_REPLICATE            0x0002
#define AP_FILTER_ENTRY_ACTION_PRIORITY             0x0004
#define AP_FILTER_ENTRY_ACTION_ACCESS_CTRL          0x0008 // Set if Access Control is other than N/A
#define AP_FILTER_ENTRY_ACTION_COS_DEFINED          0x0010 // Set if COS is other than N/A
#define AP_FILTER_ENTRY_ACTION_COS_USE_WLAN_MARKING 0x0020
#define AP_FILTER_ENTRY_ACTION_COS_UP               0x0040
#define AP_FILTER_ENTRY_ACTION_COS_TOS              0x0080
#define AP_FILTER_ENTRY_ACTION_COS_TXQ              0x0100
#define AP_FILTER_ENTRY_ACTION_COS_IRL              0x0200
#define AP_FILTER_ENTRY_ACTION_COS_ORL              0x0400
#define AP_FILTER_ENTRY_ACTION_VLAN                 0x0800
#define AP_FILTER_ENTRY_ACTION_ALLOW_PVID           0x1000 // Deprecated in V9R01

// The following flags apply to EID_FILTER_RULE_EXT_ACT_FLAGS, EID_V_FILTER_RULE_EXT_ACT_FLAGS, EID_V_SITE_FILTER_RULE_EXT_ACT_FLAGS
#define FILTER_RULE_EXT_ACT_FLAGS_MIRRORN_DEFINED   0x8000
#define FILTER_RULE_EXT_ACT_FLAGS_MIRRORN           0x4000
#define FILTER_RULE_EXT_ACT_FLAGS_REDIRECTION       0x2000

// CoS Action Flags (1 byte), used for ap_cos_entry
#define AP_COS_ACTION_IGNORE_COS        0x01    // if set dont enforce CoS and dont even use standard DSCP/UP mapping
#define AP_COS_ACTION_UP                0x02
#define AP_COS_ACTION_TOS               0x04
#define AP_COS_ACTION_TXQ               0x08
#define AP_COS_ACTION_IRL               0x10
#define AP_COS_ACTION_ORL               0x20
#define AP_COS_ACTION_USE_WLAN_MARKING  0x40

// AP multicast flags (1 byte), used in ap_mcast_flt_rule_wassp_entry
#define AP_MCAST_FILTER_ENTRY_FLAGS_WIRELESS_REPLICATION 0x01
#define AP_MCAST_FILTER_ENTRY_FLAGS_DENY                 0x02

// AppVisibility Enforce config block EID_EXTAPP_CONF_BLOCK
#define EID_EXTAPP_BLOCK     1
#define EID_EXTAPP_BLOCK_MAX EID_EXTAPP_BLOCK

#define EID_EXTAPP_DISP_NAME 1
#define EID_EXTAPP_DISP_ID   2
#define EID_EXTAPP_MATCH_STR 3
#define EID_EXTAPP_APP_ID    4
#define EID_EXTAPP_GROUP_ID  5
#define EID_EXTAPP_CONF_BLOCK_MAX EID_EXTAPP_GROUP_ID

typedef struct {
    unsigned long  r_flt_flags;    /* Filter flags, ingress (uplink) egress (downlink) accept deny, mobility enhancement enable/disable */
    unsigned long  r_ipaddr;       /* IP address, for uplink it is destination address and for downlink it is source address */
    unsigned long  r_port;         /* TCP/UDP port range */
    unsigned char   r_protocol;     /* IP protocol */
    unsigned char   r_ipmasklen;    /* Netmask length bit */
    unsigned short  r_rsv;          /* Reserve for 4 bytes alignment, could be use for EtherType filter in the future */
} ap_flt_rule_wassp_entry;

typedef struct {
    unsigned        r_flt_flags;    /* Filter flags, ingress (uplink) egress (downlink) accept deny, mobility enhancement enable/disable */
    unsigned        r_ipaddr;       /* IP address, for uplink it is destination address and for downlink it is source address */
    unsigned        r_port;         /* TCP/UDP port range */
    unsigned char   r_protocol;     /* IP protocol */
    unsigned char   r_ipmasklen;    /* Netmask length bit */
    unsigned short  r_rsv;          /* Reserve for 4 bytes alignment, could be use for EtherType filter in the future */
} ap_flt_rule_wassp_entry_fixcompat;

typedef struct {
    unsigned long  r_flt_flags;    /* Filter flags */
    unsigned long  r_ipaddr;       /* IP address  */
    unsigned long  r_port;         /* TCP/UDP port range */
    unsigned char  r_protocol;     /* IP protocol */
    unsigned char  r_ipmasklen;    /* Netmask length bit */
    unsigned char  r_tos;          /* 8 bits ToS */
    unsigned char  r_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    unsigned char  r_cos_tos;      /* COS: 8 bits ToS */
    unsigned char  r_cos_tosmask;  /* COS: 8 bits ToS mask */
    unsigned char  r_cos_prio_txq; /* COS: 4 bits Priority, 4 bits TXQ */
    unsigned char  r_cos_rates;    /* COS: 4 bits IRL, 4 bits ORL */
} ap_flt_rule_wassp_entry2;

typedef struct {
    unsigned       r_flt_flags;    /* Filter flags */
    unsigned       r_ipaddr;       /* IP address  */
    unsigned       r_port;         /* TCP/UDP port range */
    unsigned char  r_protocol;     /* IP protocol */
    unsigned char  r_ipmasklen;    /* Netmask length bit */
    unsigned char  r_tos;          /* 8 bits ToS */
    unsigned char  r_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    unsigned char  r_cos_tos;      /* COS: 8 bits ToS */
    unsigned char  r_cos_tosmask;  /* COS: 8 bits ToS mask */
    unsigned char  r_cos_prio_txq; /* COS: 4 bits Priority, 4 bits TXQ */
    unsigned char  r_cos_rates;    /* COS: 4 bits IRL, 4 bits ORL */
} ap_flt_rule_wassp_entry2_fixcompat;

typedef struct {
    unsigned long  r_flt_flags;    /* Filter flags */
    unsigned long  r_ipaddr;       /* IP address  */
    unsigned long  r_port;         /* TCP/UDP port range */
    unsigned char  r_protocol;     /* IP protocol */
    unsigned char  r_ipmasklen;    /* Netmask length bit */
    unsigned char  r_tos;          /* 8 bits ToS */
    unsigned char  r_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    unsigned char  r_cos_tos;      /* COS: 8 bits ToS */
    unsigned char  r_cos_tosmask;  /* COS: 8 bits ToS mask */
    unsigned char  r_cos_prio_txq; /* COS: 4 bits Priority, 4 bits TXQ */
    unsigned char  r_cos_rates;    /* COS: 4 bits IRL, 4 bits ORL */
    unsigned char  r_mac[6];       /* MAC address to match */
    unsigned char  r_macmask[6];   /* MAC address mask */
    unsigned short r_vlan_id;      /* Contain to VLAN, upper bit is set if tunnelled topology */
    unsigned short r_eth_type;     /* ethernet type. 0 if Any */
} ap_flt_rule_wassp_entry3;

typedef struct {
    unsigned       r_flt_flags;    /* Filter flags */
    unsigned       r_ipaddr;       /* IP address  */
    unsigned       r_port;         /* TCP/UDP port range */
    unsigned char  r_protocol;     /* IP protocol */
    unsigned char  r_ipmasklen;    /* Netmask length bit */
    unsigned char  r_tos;          /* 8 bits ToS */
    unsigned char  r_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    unsigned char  r_cos_tos;      /* COS: 8 bits ToS */
    unsigned char  r_cos_tosmask;  /* COS: 8 bits ToS mask */
    unsigned char  r_cos_prio_txq; /* COS: 4 bits Priority, 4 bits TXQ */
    unsigned char  r_cos_rates;    /* COS: 4 bits IRL, 4 bits ORL */
    unsigned char  r_mac[6];       /* MAC address to match */
    unsigned char  r_macmask[6];   /* MAC address mask */
    unsigned short r_vlan_id;      /* Contain to VLAN, upper bit is set if tunnelled topology */
    unsigned short r_eth_type;     /* ethernet type. 0 if Any */
} ap_flt_rule_wassp_entry3_fixcompat;


typedef struct {
    unsigned long  s_flt_flags;    /* Filter flags */
    unsigned long  s_ipaddr;       /* IP address  */
    unsigned long  s_port;         /* TCP/UDP port range */
    unsigned char  s_protocol;     /* IP protocol */
    unsigned char  s_ipmasklen;    /* Netmask length bit */
    unsigned char  s_tos;          /* 8 bits ToS */
    unsigned char  s_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    int            s_coskey;       /* index to site global COS table */
} ap_site_flt_rule_wassp_entry;

typedef struct {
    unsigned       s_flt_flags;    /* Filter flags */
    unsigned       s_ipaddr;       /* IP address  */
    unsigned       s_port;         /* TCP/UDP port range */
    unsigned char  s_protocol;     /* IP protocol */
    unsigned char  s_ipmasklen;    /* Netmask length bit */
    unsigned char  s_tos;          /* 8 bits ToS */
    unsigned char  s_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    int            s_coskey;       /* index to site global COS table */
} ap_site_flt_rule_wassp_entry_fixcompat;

typedef struct {
    unsigned long  s_flt_flags;    /* Filter flags */
    unsigned long  s_ipaddr;       /* IP address  */
    unsigned long  s_port;         /* TCP/UDP port range */
    unsigned char  s_protocol;     /* IP protocol */
    unsigned char  s_ipmasklen;    /* Netmask length bit */
    unsigned char  s_tos;          /* 8 bits ToS */
    unsigned char  s_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    int            s_coskey;       /* index to site global COS table */
    unsigned char  s_mac[6];       /* MAC address to match */
    unsigned char  s_macmask[6];   /* MAC address mask */
    unsigned short s_vlan_id;      /* Contain to VLAN, upper bit is set if tunnelled topology */
    unsigned short s_eth_type;     /* ethernet type. 0 if Any */
} ap_site_flt_rule_wassp_entry2;

typedef struct {
    unsigned       s_flt_flags;    /* Filter flags */
    unsigned       s_ipaddr;       /* IP address  */
    unsigned       s_port;         /* TCP/UDP port range */
    unsigned char  s_protocol;     /* IP protocol */
    unsigned char  s_ipmasklen;    /* Netmask length bit */
    unsigned char  s_tos;          /* 8 bits ToS */
    unsigned char  s_tosmask_prio; /* 4 bits ToS mask, 4 bits Priority */
    int            s_coskey;       /* index to site global COS table */
    unsigned char  s_mac[6];       /* MAC address to match */
    unsigned char  s_macmask[6];   /* MAC address mask */
    unsigned short s_vlan_id;      /* Contain to VLAN, upper bit is set if tunnelled topology */
    unsigned short s_eth_type;     /* ethernet type. 0 if Any */
} ap_site_flt_rule_wassp_entry2_fixcompat;

// Class of Service, used for in EID_V_COS and also in ap_flt_rule_wassp_entry2
typedef struct {
    unsigned char  r_flags;        /* 8 bits flags */
    unsigned char  r_tos;          /* 8 bits ToS */
    unsigned char  r_tosmask;      /* 8 bits ToS mask */
    unsigned char  r_prio_txq;     /* 4 bits Priority, 4 bits TXQ */
    unsigned char  r_rates;        /* 4 bits IRL, 4 bits ORL */
} ap_cos_entry;

// Class of Service, used for in EID_COS
typedef struct {
    unsigned char  s_flags;        /* 8 bits flags */
    unsigned char  s_tos;          /* 8 bits ToS */
    unsigned char  s_tosmask;      /* 8 bits ToS mask */
    unsigned char  s_prio_txq;     /* 4 bits Priority, 4 bits TXQ */
    unsigned char  s_rates_in;     /* 8 bits IRL */
    unsigned char  s_rates_out;    /* 8 bits ORL */
} ap_site_cos_entry;

typedef struct {
    unsigned long  r_ipaddr;
    unsigned char  r_ipmasklen;
    unsigned char  r_flt_flags;
    /* bit 0 wireless replication; 1 - enable, 0 - disable */
} ap_mcast_flt_rule_wassp_entry;

typedef struct {
    unsigned       r_ipaddr;
    unsigned char  r_ipmasklen;
    unsigned char  r_flt_flags;
    /* bit 0 wireless replication; 1 - enable, 0 - disable */
} ap_mcast_flt_rule_wassp_entry_fixcompat;

enum eid_spectrum_analysis_events {
    SPECTRUM_ANALYSIS_Radar = 1,
    SPECTRUM_ANALYSIS_Microwave,
    SPECTRUM_ANALYSIS_Phone,
    SPECTRUM_ANALYSIS_Video_Bridge,
    SPECTRUM_ANALYSIS_Bluetooth_Stereo,
    SPECTRUM_ANALYSIS_Bluetooth_Headset,
    SPECTRUM_ANALYSIS_CWA
};

enum eid_action_config_req_val {
    EID_ACTION_CONFIG_REQ_STOP = 0,
    EID_ACTION_CONFIG_REQ_START = 1,
    EID_ACTION_CONFIG_REQ_ABORT = 2,
    EID_ACTION_CONFIG_REQ_START_BASIC = 3
};

enum eid_ap_role {
    EID_AP_ROLE_TRAFFIC_FORWARDER = 0,
    EID_AP_ROLE_DEDICATED_SCANNER = 1,
    EID_AP_ROLE_ADSP_SCANNER = 2
};

//defined values for EID_AUTH_FLAG
#define AUTH_FLAG_NON_AUTH  0
#define AUTH_FLAG_AUTH      1
#define AUTH_FLAG_UNKNOWN   2

//defined values for locator
#define LOCATOR_MU_ACTION_ADD                     1
#define LOCATOR_MU_ACTION_DELETE                  2
#define LOCATOR_MU_ACTION_MODIFY                  3
#define LOCATOR_MU_ACTION_RESET                   4
#define LOCATOR_LOCATION_TYPE_UNKNOWN             0
#define LOCATOR_LOCATION_TYPE_RSS_TRIANGULATION   1
#define LOCATOR_LOCATION_TYPE_RSS_CELL_OF_ORIGIN  2
#define LOCATOR_LOCATION_ACCURACY_UNKNOWN         0
#define LOCATOR_LOCATION_ACCURACY_EXCELLENT       1
#define LOCATOR_LOCATION_ACCURACY_GOOD            2
#define LOCATOR_LOCATION_ACCURACY_FAIR            3
#define LOCATOR_LOCATION_ACCURACY_POOR            4

#define LOCATOR_STATE_DATA_ON_DEMAND                0x0001
#define LOCATOR_STATE_DATA_TRACKED                  0x0002

enum eid_locator_mu_action {
    LOCATOR_MU_ADD    = LOCATOR_MU_ACTION_ADD,
    LOCATOR_MU_DELETE = LOCATOR_MU_ACTION_DELETE,
    LOCATOR_MU_MODIFY = LOCATOR_MU_ACTION_MODIFY,
    LOCATOR_MU_RESET  = LOCATOR_MU_ACTION_RESET
};

enum eid_location_type {
    LOCATOR_LOCATION_UNKNOWN   = LOCATOR_LOCATION_TYPE_UNKNOWN,
    LOCATOR_RSS_TRIANGULATION  = LOCATOR_LOCATION_TYPE_RSS_TRIANGULATION,
    LOCATOR_RSS_CELL_OF_ORIGIN = LOCATOR_LOCATION_TYPE_RSS_CELL_OF_ORIGIN
};

enum eid_location_accuracy {
    LOCATOR_ACCURACY_UNKNOWN   = LOCATOR_LOCATION_ACCURACY_UNKNOWN,
    LOCATOR_ACCURACY_EXCELLENT = LOCATOR_LOCATION_ACCURACY_EXCELLENT,
    LOCATOR_ACCURACY_GOOD      = LOCATOR_LOCATION_ACCURACY_GOOD,
    LOCATOR_ACCURACY_FAIR      = LOCATOR_LOCATION_ACCURACY_FAIR,
    LOCATOR_ACCURACY_POOR      = LOCATOR_LOCATION_ACCURACY_POOR
};

typedef struct {
    int version;
    char mac[6];
    short channel;
    char rss;
    char flags;
    short rssQuality;
    int readTime;
} rssBlockInfo;

// Area Notification Defines
#define MAX_AREAS                   1600
#define MAX_AREAS_FLOOR             16
#define MAX_AREA_ID                 256
#define AREA_ID_UNKNOWN             2
#define AREA_ID_REST                1
#define MAX_FLOOR_NAME_LENGTH       256
#define MAX_AREA_NAME_LENGTH        32
#define MAX_AP_LOCATION_NAME_LENGTH 256
#define MAX_AREA_FULL_NAME_LENGTH   256

// May be obsolete or Replace in the code
#define EID_BP_SW_VERSION           EID_RU_SW_VERSION // Not used in controller
#define EID_BP_SERIAL_NUMBER        EID_RU_SERIAL_NUMBER
#define EID_BP_REG_CHALLENGE        EID_RU_REG_CHALLENGE
#define EID_BP_REG_RESPONSE         EID_RU_REG_RESPONSE
#define EID_BM_IPADDR               EID_AC_IPADDR
#define EID_BP_VNSID                EID_RU_VNSID
#define EID_BP_STATE                EID_RU_STATE
#define EID_MESSAGE_TYPE            EID_RU_PROTOCOL
#define EID_RU_SCAN_REQID           EID_RU_SCAN_REQ_ID
#define EID_BP_BSSID                EID_BP_BPSSID
#define EID_BP_SNMP_ALARM           EID_ALARM
#define EID_PREAUTH_RESP            EID_RU_PREAUTH
#define EID_BP_PMK                  EID_RU_PMK
#define EID_REQUEST_ID              EID_REQ_ID
#define EID_ALTERNATE_AC_IPADDR     EID_RU_REAUTH_TIMER //not used !!!
#define EID_PMK_FLAG                EID_PORT_OPEN_FLAG // V5R3 SA

#define EID_ENVIRONMENT             EID_OUTDOOR_ENABLE  //1.3.6.1.4.1.13906.3.11.9.1.0 (old name)
#define EID_BLACKLIST               EID_BLACKLIST_ADD //1.3.6.1.4.1.13906.3.16.1.2.1.2.%d

#define EID_V_BSSID_SLOT            EID_V_VNS_ID

/****************************************************
 *Code points for TLvs'
 ****************************************************/
/*EID_STATUS values*/
#define EID_STATUS_SUCCESS 1
#define EID_STATUS_FAILURE 2
#define EID_STATUS_CONFIG_OUT_OF_SYNC 3
#define EID_STATUS_FRAG_NOT_SUPPORTED 4

// TLVs that were never used
#define EID_RADIUS_CONFIG_BLOCK   0 // V7R0 Branch 802.1x: Contains the list of all RADIUS servers
#define EID_V_RADSRV_CONFIG_BLOCK 0 // V7R0 Branch 802.1x: list of RADIUS servers of a specific type
#define EID_V_BASE_VNS_NAME       0 // V7R0 Branch 802.1x: The name of the base VNS from which the derived VNS is created
#define EID_V_RADIUS_VSA_BITMASK  0 // V7R0 Branch 802.1x: bit mask for all of the Siemens-AP VSAs, bit mask:AP = 0x00000001, VNS = 0x00000002, SSID = 0x00000004
#define EID_V_RADIUS_ACCT_INTV    0 // V7R0 Branch 802.1x: The # of minutes for the Interim Accounting report (in the event that accounting servers are configured)
#define EID_V_RADIUS_MBA_ROAM     0 // V7R0 Branch 802.1x: If TRUE, then MBA is always performed on every roam
#define EID_40MHZ_COUNTERMEASURES_MAX_CH EID_COUNTERMEASURES_MAX_CH

/* Radar defines - START */
/* AP flags */
#define AP_PARAMS_ACTIVE_CONNECTED   0x00000001 // Deprecated in V9R15
#define AP_PARAMS_SCAN_ALLOWED       0x00000002
#define AP_PARAMS_SPEC_AN            0x00000004
#define AP_PARAMS_IN_SERVICE_SCAN    0x00000008
#define AP_PARAMS_MULTI_CHANNEL_SCAN 0x00000010
#define AP_PARAMS_FOREIGN            0x00000020
#define AP_PARAMS_DEDICATED_SCANNER  0x00000040
#define AP_PARAMS_SERVICE_ASSIGNED   0x00000080
#define AP_PARAMS_SITE_ASSIGNED      0x00000100
#define AP_PARAMS_BASIC_MODE         0x00000200
#define AP_PARAMS_ROGUE_DETECTION    0x00000400
#define AP_PARAMS_CONNECTED          0x00000800
#define AP_PARAMS_ACTIVE             0x00001000
/* QoS parameters */
#define RADIO_PARAMS_QOS_NONE       0x00000000
#define RADIO_PARAMS_QOS_WMM        0x00000001
#define RADIO_PARAMS_QOS_80211E     0x00000002
#define RADIO_PARAMS_QOS_NA         0x00000004
#define RADIO_PARAMS_SUPPRESS       0x00000008
#define RADIO_PARAMS_BSSID_ACTIVE   0x00000010
/* Countermeasure flags */
#define COUNTERM_E_HONEYPOT_AP      0x00000001
#define COUNTERM_I_HONEYPOT_AP      0x00000002
#define COUNTERM_FRIENDLY_AP        0x00000004
#define COUNTERM_SPOOFED_AP         0x00000008
#define COUNTERM_DROP_FLOOD         0x00000010
/* The next 2 items are not sent to the AP, but used by INS, for automatic client blacklisting */
#define COUNTERM_BLACKLISTING       0x00000020
#define COUNTERM_DOS_ATTACK         0x00000040
#define COUNTERM_ROGUE_AP           0x00000080

/* EID_ACTION bitmask for EID_SCAN_PROFILE_BLOCK */
#define SECURITY_SCAN               0x00000001
#define INTERFERENCE_CLASSIFICATION 0x00000002
/* Threat states */
#define THREAT_STATE_NA             0
#define THREAT_STATE_ACTIVE         1
#define THREAT_STATE_INACTIVE       2
#define THREAT_STATE_AGED           3
/* Countermeasure actions */
#define MITIGATION_NONE             0x0000
#define MITIGATION_DROP_MATCHES     0x0001
#define MITIGATION_BROADCAST_DEAUTH 0x0002
#define MITIGATION_TARGET_DEAUTH    0x0004
#define MITIGATION_BLACKLISTING     0x0008
#define MITIGATION_UNKNOWN          0x0010
/* Reason values */
#define REASON_CH_CHANGE            0x00000001
#define REASON_RADIO_STOP           0x00000002
/* Threat types */
#define TYPE_NONE                   0xFFFF
#define TYPE_AUTHORIZED             0xFFFE
#define TYPE_PREAUTHORIZED          0xFFFD
#define TYPE_FRIENDLY               0xFFFC
#define TYPE_INTERNAL_HONEYPOT      0xFFFB
#define TYPE_EXTERNAL_HONEYPOT      0xFFFA
#define TYPE_PROHIBITED             0xFFF9
#define TYPE_ROGUE_CANDIDATE        0xFFF8
#define TYPE_ROGUE_DETECTED         0XFFF7
#define TYPE_ROGUE_NOT_FOUND        0XFFF6
#define TYPE_ROGUE_FAILED_TEST      0XFFF5
#define TYPE_SPOOF_CANDIDATE        0XFFF4

/* Spoof action */
#define SPOOF_ACTION_NONE           0
#define SPOOF_ACTION_DETECT         1
#define SPOOF_DETECTED              2
/* pre 8.21 threat categories */
#define LEGACY_UNKNOWN_AP_INVALID_SSID                  0x00000001
#define LEGACY_UNKNOWN_AP_VALID_SSID                    0x00000002
#define LEGACY_KNOWN_AP_INVALID_SSID_MAPPING            0x00000004  // cannot determine this state at this time
#define LEGACY_KNOWN_AP_INVALID_SSID                    0x00000008
#define LEGACY_KNOWN_AP_VALID_SSID_SUPPRESS_CONFLICT    0x00000010
#define LEGACY_INACTIVE_AP_VALID_SSID                   0x00000020
#define LEGACY_INACTIVE_AP_INVALID_SSID                 0x00000040
#define LEGACY_DEVICE_IN_AD_HOC_MODE                    0x00000080
/* 8.21 threat categories */
#define THREAT_CATEGORY_INTERFERENCE                    0x00000100
#define THREAT_CATEGORY_CRACKING                        0x00000200
#define THREAT_CATEGORY_SURVEILLANCE                    0x00000400
#define THREAT_CATEGORY_DOS                             0x00000800
#define THREAT_CATEGORY_AP_SPOOF                        0x00001000
#define THREAT_CATEGORY_CLIENT_SPOOF                    0x00002000
#define THREAT_CATEGORY_INT_HONEYPOT                    0x00004000
#define THREAT_CATEGORY_EXT_HONEYPOT                    0x00008000
#define THREAT_CATEGORY_CHAFF                           0x00010000
#define THREAT_CATEGORY_ADHOC                           0x00020000
#define THREAT_CATEGORY_UNAUTH_BR                       0x00040000
#define THREAT_CATEGORY_INJECTION                       0x00080000
#define THREAT_CATEGORY_PERFORMANCE                     0x00100000
#define THREAT_CATEGORY_PROHIBITED                      0x00200000
#define THREAT_CATEGORY_UNCATEGORIZED                   LEGACY_UNKNOWN_AP_INVALID_SSID
/* Category boundaries */
#define SAIR_LAST_THREAT_TYPE                           THREAT_CATEGORY_PROHIBITED
#define SAIR_ALL_THREAT_TYPES                           0x003FFFFF

#define THREAT_PRIORITY_NONE            0
#define THREAT_PRIORITY_ROGUE           1
#define THREAT_PRIORITY_PROHIBITED      2
#define THREAT_PRIORITY_INT_HONEYPOT    3
#define THREAT_PRIORITY_SPOOFED_AP      4
#define THREAT_PRIORITY_ADHOC           5
#define THREAT_PRIORITY_EXT_HONEYPOT    6
/* Radar defines - END */

/* Area Change Methods (EID_MU_AREA_BLOCK:EID_EVENT_TYPE) */
#define AREA_CHANGE_METHOD_ROAMING              0
#define AREA_CHANGE_METHOD_TRIANGULATION        1
#define AREA_CHANGE_METHOD_RESET                2

/* Station event types (redefined for WM) */
#define STATION_EVENT_TYPE_REG                  0  /*MULOG_TYPE_REG*/
#define STATION_EVENT_TYPE_DEREG                1  /*MULOG_TYPE_DEREG*/
#define STATION_EVENT_TYPE_STATE_CHANGE         2  /*MULOG_TYPE_STATE_CHANGE*/
#define STATION_EVENT_TYPE_REG_FAILED           3  /*MULOG_TYPE_REG_FAILED*/
#define STATION_EVENT_TYPE_ROAM                 4  /*MULOG_TYPE_ROAM*/
#define STATION_EVENT_TYPE_MAC_AUTH_TIMEOUT     5  /*MULOG_TYPE_MAC_AUTH_TIMEOUT*/
#define STATION_EVENT_TYPE_MAC_AUTH_ACCEPTED    6  /*MULOG_TYPE_MAC_AUTH_ACCEPTED*/
#define STATION_EVENT_TYPE_MAC_AUTH_REJECTED    7  /*MULOG_TYPE_MAC_AUTH_REJECTED*/
#define STATION_EVENT_TYPE_EXT_CP_POLICY        8  /*MULOG_TYPE_EXT_CP_POLICY*/
#define STATION_EVENT_TYPE_AUTH                 9  /*MULOG_TYPE_AUTH*/
#define STATION_EVENT_TYPE_AUTH_FAILED          10 /*MULOG_TYPE_AUTH_FAILED*/
#define STATION_EVENT_TYPE_LOCATION             11 /*MULOG_TYPE_LOCATION*/
#define STATION_EVENT_TYPE_AREA_CHANGE          12 /*MULOG_TYPE_AREA_CHANGE*/

/* NAC rule authentication type */
#define NAC_AUTH_TYPE_MBA               0x00000001
#define NAC_AUTH_TYPE_MBA_PAP           0x00000002
#define NAC_AUTH_TYPE_MBA_CHAP          0x00000004
#define NAC_AUTH_TYPE_MBA_MSCHAP        0x00000008
#define NAC_AUTH_TYPE_MBA_MSCHAPv2      0x00000010
#define NAC_AUTH_TYPE_PAP               0x00000020
#define NAC_AUTH_TYPE_CHAP              0x00000040
#define NAC_AUTH_TYPE_MSCHAP            0x00000080
#define NAC_AUTH_TYPE_MSCHAPv2          0x00000100
#define NAC_AUTH_TYPE_1X                0x00000200
#define NAC_AUTH_TYPE_1X_EAP_TLS        0x00000400
#define NAC_AUTH_TYPE_1X_TTLS           0x00000800
#define NAC_AUTH_TYPE_1X_TTLS_IT        0x00001000
#define NAC_AUTH_TYPE_1X_EAP_MD5        0x00002000
#define NAC_AUTH_TYPE_1X_PEAP           0x00004000
#define NAC_AUTH_TYPE_1X_PEAP_IT        0x00008000
#define NAC_AUTH_TYPE_1X_EAP_FAST       0x00010000
#define NAC_AUTH_TYPE_1X_EAP_LEAP       0x00020000
#define NAC_AUTH_TYPE_1X_EAP_RSA        0x00040000
#define NAC_AUTH_TYPE_1X_EAP_SIM        0x00080000
#define NAC_AUTH_TYPE_1X_EAP_AKA        0x00100000

/* NAC rule flags */
#define NAC_RULE_FLAG_NEGATE_USER_GROUP         0x01
#define NAC_RULE_FLAG_NEGATE_END_SYS_GROUP      0x02
#define NAC_RULE_FLAG_NEGATE_DEV_TYPE_GROUP     0x04
#define NAC_RULE_FLAG_NEGATE_LOCATION_GROUP     0x08
#define NAC_RULE_FLAG_NEGATE_TIME_GROUP         0x10
#define NAC_RULE_FLAG_NEGATE_AUTH_TYPE          0x20

/* NAC LDAP server flags */
#define NAC_LDAP_SRV_FLAG_KEEP_DOMAIN_NAME      0x0001
#define NAC_LDAP_SRV_FLAG_USE_FQDN              0x0002

/* NAC LDAP/AD authentication types */
typedef enum nac_auth_type {
     NAC_AUTH_TYPE_LDAP_BIND_SIMPLE
    ,NAC_AUTH_TYPE_NTLM_AUTH
    ,NAC_AUTH_TYPE_LDAP_BIND_GSSAPI
    ,NAC_AUTH_TYPE_MAX
} NAC_AUTH_TYPE;

enum nac_ldap_match_mode {
     NAC_LDAP_USER_MATCH_ANY
    ,NAC_LDAP_USER_MATCH_ALL
    ,NAC_LDAP_USER_MATCH_EXISTS
};

enum eid_default_mirrorn {
    EID_DEF_MIRRORN_NONE = 0,
    EID_DEF_MIRRORN_PROHIBITED = 1,
    EID_DEF_MIRRORN_ENABLE,
    EID_DEF_MIRRORN_ENABLE_BOTH_TCPUDP,
    EID_DEF_MIRRORN_ENABLE_INONLY_TCPUDP
};

/********************************************************************************
 *v10.11 extended EID_AP_REDIRECT from boolean to enum.
 *AP_REDIRECT_BAC:
 *  if default action's contain-to-vlan is tunneled topology
 *  if default action type is Allow or None, PVID is tunneled topology
 *AP_REDIRECT_BAP_CP:
 *  if default action's contain-to-vlan is B@AP topology  && FFECP
 *  if default action type is Allow or None, PVID is B@AP topology  && FFECP
 *AP_REDIRECT_DEFAULT:
 *  otherwise
********************************************************************************/
typedef enum e_ap_redirect {
    AP_REDIRECT_INVALID = -1,
    AP_REDIRECT_DISABLE,
    AP_REDIRECT_ATAC,
    AP_REDIRECT_ATAP
} t_ap_redirect;

/* Device identity: osClassId << 32 | osId << 16 | weight*/
#define DEV_IDENT_LENGTH                      6
typedef unsigned char t_dev_ident[DEV_IDENT_LENGTH];

/* Bitmask for EID_STATS_REQUEST_TYPE */
#define STATS_MU_REQ        0x00000001
#define STATS_RU_REQ        0x00000002
#define STATS_NEIGHBOUR_REQ 0x00000004
#define STATS_APPL_REQ      0x00000008
#define STATS_FILTER_REQ    0x00000010

typedef enum e_mu_stats_radio_id {
    radio1 = 1,
    radio2 = 2,
    radio3 = 3,
    wcl1 = 20,
    wcl2 = 21,
    wcl3 = 22
} t_mu_stats_radio_id;

#endif /*__TLV_DEF_H*/

