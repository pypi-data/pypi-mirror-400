#include "Python.h"
#include <assert.h>
#include <string>

#include "cmacaddr.h"
#include "cipaddr.h"
#include "tlvpacket.h"

using namespace std;

#define PyDict_SetItemString_wrap(x,y,z) \
{ \
	PyObject *tmp=z; \
	if (NULL != tmp) { \
		PyDict_SetItemString(x,y,tmp); \
		Py_DECREF(tmp); \
	} \
}


const char* mulog_type2str(unsigned mu_log_type)
{
  static const char *s_muLogTypeStrArr[] = {
    "Registration",             /*MULOG_TYPE_REG*/
    "De-registration",          /*MULOG_TYPE_DEREG*/
    "State Change",             /*MULOG_TYPE_STATE_CHANGE*/
    "Registration Failure",     /*MULOG_TYPE_REG_FAILED*/
    "Roam",                     /*MULOG_TYPE_ROAM*/
    "MBA Timeout",              /*MULOG_TYPE_MAC_AUTH_TIMEOUT*/
    "MBA Accepted",             /*MULOG_TYPE_MAC_AUTH_ACCEPTED*/
    "MBA Rejected",             /*MULOG_TYPE_MAC_AUTH_REJECTED*/
    "Authorization Change",     /*MULOG_TYPE_EXT_CP_POLICY*/
    "Authentication",           /*MULOG_TYPE_AUTH*/
    "Authentication Failure",   /*MULOG_TYPE_AUTH_FAILED*/
    "Location Update",          /*MULOG_TYPE_LOCATION*/
    "Area Change"               /*MULOG_TYPE_AREA_CHANGE*/
  };
  return (mu_log_type < (sizeof(s_muLogTypeStrArr) / sizeof(s_muLogTypeStrArr[0]))) ? s_muLogTypeStrArr[mu_log_type] : "";
}

extern "C" {

#define ATR_MU_EVENT_TYPE 0 /*EID_MU_EVENT_TYPE*/
#define ATR_MU_MAC 1 /*Station MAC address, EID_MU_MAC*/
#define ATR_MU_IP_ADDR 2 /*Station IP address, EID_MU_IP_ADDR*/
#define ATR_IPV6_ADDR 3 /*Station IPv6 address, EID_IPV6_ADDR*/
#define ATR_RU_SERIAL_NUMBER 4 /*Access Point Serial Number connected Station, EID_RU_SERIAL_NUMBER*/
#define ATR_MU_USER_NAME 5 /*Station logged in User name, EID_MU_USER_NAME*/
#define ATR_SSID 6 /*SSID connected Station, EID_SSID*/
#define ATR_MU_EVENT_DETAILS 7 /*Details of the Station Event, EID_MU_EVENT_DETAILS*/
#define ATR_MU_EVENT_FROM_AP 8 /*Source Roaming Acccess Point Station, EID_MU_EVENT_FROM_AP*/
#define ATR_MU_BSSID 9 /*Station BSSID, EID_MU_BSSID*/
#define ATR_GETTIMEOFDAY 10 /*timestamp of the event, EID_GETTIMEOFDAY*/
#define ATR_MU_EVENT_LOC_BLOB 11 /*Location data X-Y-P, EID_MU_EVENT_LOC_BLOB*/

static int attributeSupportArray[13][12] = {  
  /*
	0                 1          2              3             4
	EID_MU_EVENT_TYPE,EID_MU_MAC,EID_MU_IP_ADDR,EID_IPV6_ADDR,EID_RU_SERIAL_NUMBER,
	5                6        7                    8
	EID_MU_USER_NAME,EID_SSID,EID_MU_EVENT_DETAILS,EID_MU_EVENT_FROM_AP,
	9            10               11
	EID_MU_BSSID,EID_GETTIMEOFDAY,EID_MU_EVENT_LOC_BLOB
  */

  /* 0  1  2  3  4  5  6  7  8  9  10 11 */
    {1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0} ,   /* 0 "Registration" */
    {1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0} ,   /* 1 "De-registration" */
    {1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0} ,   /* 2 "State Change" */
    {1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0} ,   /* 3 "Registration Failure" */
    {1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0} ,   /* 4 "Roam" */
    {1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0} ,   /* 5 "MBA Timeout" */
    {1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0} ,   /* 6 "MBA Accepted" */
    {1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0} ,   /* 7 "MBA Rejected" */
    {1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0} ,   /* 8 "Authorization Change" */
    {1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0} ,   /* 9 "Authentication" */
    {1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0} ,   /* 10 "Authentication Failure" */
    {1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1} ,   /* 11 "Location Update" */
    {1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0}     /* 12 "Area Change" */
};

static int isAttributedSupportedForEventType(unsigned eventType, unsigned attributeType)
{
    return attributeSupportArray[eventType][attributeType];
}

static PyObject* ReadEventTlv(PyObject *self, PyObject *args)
{
	//const char *pStr;
	unsigned char *tlv_payload = NULL;
	int tlv_payload_len = 0;

	if (!PyArg_ParseTuple(args, "s#", &tlv_payload, &tlv_payload_len)) {
		PyErr_SetString(PyExc_TypeError, "Error parsing argument!");
		return NULL;
	}

	PyObject *obj = NULL;
	string tmp_str;
	string name_str;

	cTLVPacket eventArr, tlvPkt(tlv_payload, tlv_payload_len);

	if (tlvPkt.findValue(EID_MU_EVENT_ARRAY, eventArr, true))
	{
		std::vector<cTLVPacket> eventBlk;
		
		if (eventArr.findValue(EID_MU_EVENT_BLOCK, eventBlk, true))
		{
			unsigned long long stationEventTimeStamp = 0;
			unsigned eventType = 0;
			MACAddr mac;
			IPAddr ip;
			int *ts;
			unsigned int num = 0;
			//unsigned int i;
			PyObject *eList = PyList_New(eventBlk.size());
			
			for (unsigned ui = 0; ui < eventBlk.size(); ui++)
			{
				PyObject *pDict = PyDict_New(); 
				if (eventBlk[ui].findValue(EID_MU_EVENT_TYPE, eventType, true)) {
					obj = Py_BuildValue("I", eventType);
					PyDict_SetItemString_wrap(pDict, "eventType", obj);

					//get eventString
					tmp_str = mulog_type2str(eventType);
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "eventTypeString", obj);
				}
				else 
					continue;

				if (eventBlk[ui].findValue(EID_MU_MAC, mac, true) && isAttributedSupportedForEventType(eventType,ATR_MU_MAC)) {
					tmp_str = mac.toString();
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "macAddress", obj);
				}
				else if (isAttributedSupportedForEventType(eventType,ATR_MU_MAC)){
					tmp_str.clear();
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "macAddress", obj);
				}

				if (eventBlk[ui].findValue(EID_MU_IP_ADDR, ip, true) && isAttributedSupportedForEventType(eventType,ATR_MU_IP_ADDR)) {
					tmp_str = ip.toString();
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "ipAddress", obj);
				}
				else if (isAttributedSupportedForEventType(eventType,ATR_MU_IP_ADDR)){
					tmp_str.clear();
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "ipAddress", obj);
				}

				if (eventBlk[ui].findValue(EID_RU_SERIAL_NUMBER, tmp_str, true) && isAttributedSupportedForEventType(eventType,ATR_RU_SERIAL_NUMBER)) {
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "stationAPSerial", obj);
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "stationAPName", obj);
				}
				
				if (eventBlk[ui].findValue(EID_MU_USER_NAME, tmp_str, true) && isAttributedSupportedForEventType(eventType,ATR_MU_USER_NAME)) {
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "username", obj);
				}
				
				if (eventBlk[ui].findValue(EID_SSID, tmp_str, true) && isAttributedSupportedForEventType(eventType,ATR_SSID)) {
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "ssid", obj);
				}

				if (eventBlk[ui].findValue(EID_MU_EVENT_DETAILS, tmp_str, true) && isAttributedSupportedForEventType(eventType,ATR_MU_EVENT_DETAILS)) {
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "details", obj);
				}
				
				if (eventBlk[ui].findValue(EID_MU_EVENT_FROM_AP, tmp_str, true) && isAttributedSupportedForEventType(eventType,ATR_MU_EVENT_FROM_AP)) {
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "stationRoamedAPSerial", obj);

					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "stationRoamedAPName", obj);
				}
				
				if (eventBlk[ui].findValue(EID_MU_BSSID, mac, true) && isAttributedSupportedForEventType(eventType,ATR_MU_BSSID)) {
					tmp_str = mac.toString();
					obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
					PyDict_SetItemString_wrap(pDict, "bssid", obj);
				}

				if (eventBlk[ui].findValue(EID_GETTIMEOFDAY, ts, num, true) && isAttributedSupportedForEventType(eventType,ATR_GETTIMEOFDAY)) {
					//ts[1] is seconds ts[0] is useconds
					stationEventTimeStamp = ((unsigned long long)ts[0] * 1000u + (unsigned long long)ts[1] / 1000u);

					obj = Py_BuildValue("K", stationEventTimeStamp);
					PyDict_SetItemString_wrap(pDict, "timestamp", obj);
					delete[] ts;
				}

				cTLVPacket locBlob;
				if (eventBlk[ui].findValue(EID_MU_EVENT_LOC_BLOB, locBlob, true) && isAttributedSupportedForEventType(eventType,ATR_MU_EVENT_LOC_BLOB)) {
					if (locBlob.findValue(EID_LOCATOR_FLOOR_ID, tmp_str, true)) {
						obj = Py_BuildValue("s#", tmp_str.c_str(), tmp_str.size());
						PyDict_SetItemString_wrap(pDict, "floorID", obj);
					}
					int *pointSet = NULL;
					unsigned int cnt = 0;
					if (locBlob.findValue(EID_LOCATOR_POINT_SET, pointSet, cnt, true) && (cnt == 3)) {
						obj = Py_BuildValue("I", pointSet[0]);
						PyDict_SetItemString_wrap(pDict, "X", obj);
						obj = Py_BuildValue("I", pointSet[1]);
						PyDict_SetItemString_wrap(pDict, "Y", obj);
						obj = Py_BuildValue("I", pointSet[2]);
						PyDict_SetItemString_wrap(pDict, "P", obj);
					}
					delete[] pointSet;
				}

				PyList_SetItem(eList, ui, pDict);
			}
			return eList;
		}
	}

	return NULL;
}

static PyMethodDef tlvmethods[] = {
	{"ReadEventTlv", ReadEventTlv, METH_VARARGS, "Read event TLV data"},
	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef tlvmodule = {
	PyModuleDef_HEAD_INIT,
	"tlvmodule",
	NULL,
	-1,
	tlvmethods,
	NULL,
	NULL,
	NULL,
	NULL
};

PyMODINIT_FUNC PyInit_tlv(void)
{
	return PyModule_Create(&tlvmodule);
}

}//extern "C"
