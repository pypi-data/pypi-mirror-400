#################
## python 3.5.2 #
#################
import uuid
import ssl
import socket
import hashlib
import logging
import sys 
import binascii
from multiprocessing import Process, Pipe, Queue
import select
import time
import platform
import xml.dom.minidom
import base64
import errno
import tlv as tlvlib
from xcc import cianames
from enum import Enum

logging.basicConfig(
    format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(funcName)10s] %(message)s",
    handlers=[
        logging.FileHandler("{0}/{1}.log".format(".", "fix.log")),
        logging.StreamHandler(sys.stdout)
    ],
    level=logging.INFO)

XCAMessage = Enum('XCAMessage', cianames.messageNameToID)
XCAMessageName = cianames.GetMessageIDToName()

xcaEventNameToID = {
    'MU_EVENT':0,
    'AP_EVENT':1,
    'TOPOLOGY_CHANGE_NOTIFY':2,
    'PROFILE_CHANGE_NOTIFY':3,
    'RFS_CHANGE_NOTIFY':4,
    'POLICY_CHANGE_NOTIFY':5,
    'AP_CONFIG_CHANGE_NOTIFY':6,
    'LOC_EVENT':7
}

xcaEventIDToName = {
    0:'MU_EVENT',
    1:'AP_EVENT',
    2:'TOPOLOGY_CHANGE_NOTIFY',
    3:'PROFILE_CHANGE_NOTIFY',
    4:'RFS_CHANGE_NOTIFY',
    5:'POLICY_CHANGE_NOTIFY',
    6:'AP_CONFIG_CHANGE_NOTIFY',
    7:'LOC_EVENT'
}

def XCAGetEventNameToID():
    return xcaEventNameToID


def XCAGetEventIDToName():
    """Hello"""
    return xcaEventIDToName

XCAEvent = Enum('XCAEvent', xcaEventNameToID)
XCAEventName = XCAGetEventIDToName()

apEventNameToID = {
    'Connect':0,
    'Disconnect':1,
    'Create':2,
    'Delete':3,
    'Update':4
}

apEventIDToName = {
    0:'Connect',
    1:'Disconnect',
    2:'Create',
    3:'Delete',
    4:'Update'
}

def GetAPEventNameToID():
    return apEventNameToID

def GetAPEventIDToName():
    return apEventIDToName

XCAAPEvent = Enum('XCAEvent', apEventNameToID)
XCAAPEventName = GetAPEventIDToName()

class Timer(object):
    def __init__(self, reactor, callback = None):
        self._callback = callback
        self._uuid = uuid.uuid4()
        self._reactor = reactor
        
    def start(self, timeout):
        self._timeout = timeout
        self._reactor.addTimer(self)
        
    def expire(self, tick: int):
        self._timeout = self._timeout - tick
        return self._timeout < 0
            
    def stop(self):
        self._reactor.cancelTimer(self)
        
class Reactor(object):
    def __init__(self):
        self._handlers = {}
        self._timers = {}
        self.TIMEOUT = 1
        self._name = "None"
        self._server = Nonecond
        if platform.system().lower() == "windows":
            # dummy socket to get around the select on windows
            dummy = socket.socket(socket.AF_INET)
            self._handlers[dummy]= None 
    
    def addTimer(self, t):
        self._timers[t._uuid] = t
    
    def cancelTimer(self, t):
        self._timers.pop(t._uuid)
    
    def handleTimeout(self):
        timers = self._timers.copy()
        for t in timers.values():
            if t.expire(tick = self.TIMEOUT):
                self.cancelTimer(t)
                t._callback()
                
    def registerFd(self, fd, func):
        self._handlers[fd]=func
    
    def unregisterFd(self, fd):
        self._handlers.pop(fd)
    
    def svc(self):
        while self._handlers.keys() | self._timers.keys():
            try:
                inputready,outputready,exceptready = select.select(self._handlers.keys(),[], self._handlers.keys(), 
                                                                   self.TIMEOUT) 
               
                for s in inputready: 
                    if s is self._server: 
                        # handle the server socket 
                        # TO DO: not used for now
                        client, address = self._server.accept() 
                        client.setblocking(0)
                        self.registerFd(client, self.handle) 
                    elif s in list(self._handlers.keys()):
                        #print (f"asdfsdfsdfasdf {s}", flush=True)
                        self._handlers[s](s)
                           
                for s in outputready:
                    #nothing for now
                    print ("blank")

                for s in exceptready:
                    logging.error( "{name} got socket error {s}".format(name=self._name, s=s.getpeername()) )
                    #self.unregisterFd(s)
                    #s.close()

                    #TO DO: need to reconnect to the server 

                if not (inputready or outputready or exceptready):
                    raise socket.timeout #to run the timer on top level
                    #continue
            except socket.timeout:
                #check for modified time
                logging.debug("{name} Hit timeout at {hms} wait {wait}".format(name=self._name,
                                                                               hms=time.strftime("%H:%M:%S"),
                                                                               wait=self.TIMEOUT))
                try:
                    self.handleTimeout()
                except Exception as e:
                    logging.error( "{name}: handleTimeout got except due to {e}".format(name=self._name, e=e))
            except socket.error as e:
                for i in range(len(self._conn)):
                    self._conn[i] = -1
                logging.error( "{name} reset connection, got except due to {e}".format(name=self._name, e=e))
            except Exception as e:
                logging.error( "{name} got except due to {e}".format(name=self._name, e=e))

class ReaderStatsUpdater(Timer):
    def __init__(self, reactor, queue):
        super(ReaderStatsUpdater, self).__init__(reactor)
        self._callback = self.updateStats
        self._q = queue
        self._stats = {}
        # the following are  variables used to store stats counters for the Queue size
        self._qSizeEMAPref = 0
        self._qSizeEMACur = 0
        self._qSizeEMAAlpha = 0.9
        self._qSizeEMATimeWindow = 1 * 60
        self._qSizeEMALastTimestamp = 0
        self._qSizeMax = 0
        self._qSizeLast = 0
        self._readerMessagesCounter = 0

    def incReaderMsgCounter(self):
        self._readerMessagesCounter = self._readerMessagesCounter + 1

    def updateStats(self):
        self.calculateQSizeEMA()
        self.start(1)

    def calculateQSizeEMA(self):
        currQSize = 0

        try:
            currQSize = self._q.qsize()
        except Exception as e:
            logging.error("calculateQSizeEMA call to qsize() got except due to {e}".format(e=repr(e)))

        curTime = time.time()

        if (self._qSizeEMALastTimestamp == 0):
            self._qSizeEMALastTimestamp = curTime

        elif (currQSize != self._qSizeLast):
            self._qSizeEMALastTimestamp = curTime
            self._qSizeLast = currQSize

        if (curTime - self._qSizeEMALastTimestamp > self._qSizeEMATimeWindow):
            self._qSizeEMACur = currQSize
            self._qSizeEMALastTimestamp = curTime
        else:
            if (self._qSizeEMAPref == 0):
                self._qSizeEMACur = currQSize
            else:
                self._qSizeEMACur = (currQSize * self._qSizeEMAAlpha) + ((1 - self._qSizeEMAAlpha) * self._qSizeEMAPref)

        if (currQSize > self._qSizeMax):
            self._qSizeMax = currQSize

        self._qSizeEMAPref = self._qSizeEMACur

        logging.debug("qSizeEMACur: {qSizeEMACur:.2f}, qSizeMax: {qSizeMax:.2f}, readerMessagesCounter: {readerMessagesCounter}".format(qSizeEMACur=self._qSizeEMACur, qSizeMax=self._qSizeMax, readerMessagesCounter=self._readerMessagesCounter))

        self._readerMessagesCounter = 0

    def getStats(self):
        stats = {}
        if (self._enableStats):
            stats['qSizeEMACur'] = self._qSizeEMACur
            stats['qSizeMax'] = self._qSizeMax
            stats['readerMessagesCounter'] = self._readerMessagesCounter
        return stats

class langleyHandshake(Timer):
    def __init__(self, reactor):
        super(langleyHandshake, self).__init__(reactor)
        self._callback = self.handshake

    def subscribemsg(self, index):
        msgs = ''
        for i in self._reactor._events:
           msgs = msgs + '<item><message type="int">{type}</message></item>'.format(type=i.value)
        subsmsg = self._reactor._subscribe_msg.format(id=self._reactor._remote_id[index],itmstr=msgs)
        return subsmsg

    def intTobytes(self, integ: int) -> bytes:
        """Integer to bytes. 
        
           :param integ: integer 
        """
        ibytes = bytes.fromhex('0000')
        if integ <= 255:
            ibytes = ibytes + bytes.fromhex('00') + bytes([integ])
        elif integ <= 511:
            ibytes = ibytes + bytes.fromhex('01') + bytes([integ-256])
        elif len(subsmsg) <= 767:
            ibytes = ibytes + bytes.fromhex('01') + bytes([integ-512])
        elif len(subsmsg) <= 1023:
            ibytes = ibytes + bytes.fromhex('01') + bytes([integ-512])
        return ibytes

    def sendPadding(self, integ: int, index):
        cnt = 0
        while cnt < integ:
          self._reactor._conn[index].send(bytes.fromhex('00'))
          cnt+=1

    def handshake(self):
        for i, ip in enumerate(self._reactor._ip):
            if i in self._reactor._conn:
                if self._reactor._conn[i] != -1:
                    continue

            try:
                logging.info("Handshake starts with {u} ".format(u=ip)) 
                self._reactor._conn[i]=self._reactor._context.wrap_socket(socket.socket(socket.AF_INET))
                self._reactor._conn[i].setblocking(True)
                self._reactor._conn[i].connect((ip, self._reactor._port))
                data = self._reactor._conn[i].recv(32)
                logging.info("Recv Challenge: {n}".format(n=data))

                sz = len(self._reactor._apikey) + len(self._reactor._apikey_pw) + 2
                szb = self.intTobytes(sz)
                self.sendPadding(4, i)
                res=self._reactor._conn[i].send(szb)
                logging.info("Send credential size: [{n}]".format(n=sz))
                res=self._reactor._conn[i].send(bytes(self._reactor._apikey,'utf-8'))
                self.sendPadding(1, i)
                res=self._reactor._conn[i].send(bytes(self._reactor._apikey_pw,'utf-8'))
                self.sendPadding(1, i)
                if sz + 8 < 32: 
                   self.sendPadding(24-sz, i)
                logging.info("Send Response: user [{n}], bytes {b}".format(n=self._reactor._apikey, b = sz))

                res=self._reactor._conn[i].send(bytes.fromhex(self._reactor._session_id))
                logging.info("Send Id: {n}, bytes {b}".format(n=self._reactor._session_id, b=res))
            except ssl.SSLError as err:
                logging.info("SSL Exception: {c}".format(c= str(err)))
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)
            except socket.error as e:
                logging.error( "socket error {e}".format(e=e))
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)
            except Exception as e:
                logging.info("Exception: {c}".format(c= e)) 
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)

            try:
                if self._reactor._conn[i] != -1:
                    self._reactor._remote_id[i] = int(self._reactor._conn[i].recv(4).hex(),16)
            except Exception as e:
                logging.info("Authentication failure") 
                #self._reactor._conn[i].close()
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)

            try:
                if self._reactor._conn[i] != -1:
                    logging.info("Recv id: {n}".format(n=self._reactor._remote_id[i]))
                    # subscribe message
                    res=self._reactor._conn[i].send(bytes.fromhex(self._reactor._s_type))
                    subsmsg = self.subscribemsg(i)
                    res=self._reactor._conn[i].send(self.intTobytes(len(subsmsg)))
                    res=self._reactor._conn[i].send(bytes(subsmsg,'utf-8'))
                    logging.info("Send subscription size: {s}".format(s=res))

                    self._reactor.registerFd(self._reactor._conn[i], self._reactor.onMessage)
                    self._reactor._conn[i].setblocking(False)
                    #get the simulation going
                    #self._reactor._hello.start(2)

            except ssl.SSLError as err:
                logging.info("SSL Exception: {c}".format(c= str(err)))
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)
            except socket.error as e:
                logging.error( "Socket error {e}".format(e=e))
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)
            except Exception as e:
                logging.info("Exception: {c}".format(c= e)) 
                self._reactor._conn[i].close()
                self._reactor._conn[i] = -1
                self.start(5)

class Reader(Reactor):
    def __init__(self, ip, user, passwd, events, q, enableStats = False):
        super(Reader, self).__init__()
        #Process.__init__(self)
        #Reactor.__init__(self)
        self._ip = ip
        self._conn = {}
        self._apikey = user 
        self._apikey_pw = passwd 
        self._port = 20506
        self._session_id = '0000004d28000000c0a80456000000650000007f' 
        self._q = q
        self._remote_id = {}
        for i in range(len(ip)):
            self._remote_id[i] = 0

        self._s_type = '000002f2'
        self._subscribe_msg = '''<?xml version="1.0"?><payload><header><msg_type>754</msg_type>
<from>101</from><from_session>{id}</from_session></header><subscriptions type="array">{itmstr}</subscriptions></payload>'''
        self._name = "reader"
        self._events = events
        self._msgtbl = cianames.GetMessageIDToName()
        self._msgids = cianames.GetMessageNameToID()
        self._tlvtbl = cianames.GetTlvIDToName()
        self._enableStats = enableStats
        self._readerStatsUpdater = None

    def makeResponse(self, challenge):
        return hashlib.md5(self._secret + challenge)

    def processReceivedMsg(self, messageId, payload):
        logging.info("processReceivedMsg messageId {s}".format(s=self._msgtbl[messageId]))

        if (messageId == XCAMessage.ES_MU_EVENT_NOTIFY.value) or (messageId == XCAMessage.ES_LOCATION_EVENT_NOTIFY.value):

            """ES_MU_EVENT_NOTIFY or ES_LOCATION_EVENT_NOTIFY message processing."""

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            docelems = "" + doc.getElementsByTagName('events')[0].firstChild.data
            elemdec = base64.b64decode(docelems)
            #logging.info("raw MU Station Events TLVs: {n}".format(n=elemdec))
            #type, length = struct.unpack('!HH', elemdec[:4])
            event_list = tlvlib.ReadEventTlv(elemdec)

        elif messageId == XCAMessage.IXP_RU_DISCONNECT_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))

            sn = doc.getElementsByTagName("sn")[0]
            ru_ip = doc.getElementsByTagName("ru_ip")[0]

            name = None
            if (doc.getElementsByTagName("name")):
                name = doc.getElementsByTagName("name")[0]

            mac = None
            if (doc.getElementsByTagName("mac")):
                mac = doc.getElementsByTagName("mac")[0]

            event_dict = {}
            event_dict["eventType"] = XCAAPEvent.Disconnect.value
            event_dict["eventTypeString"] = XCAAPEventName[XCAAPEvent.Disconnect.value]
            event_dict["serial"] = sn.firstChild.data
            if (name != None):
                event_dict["name"] = name.firstChild.data
            if (mac != None):
                event_dict["mac"] = mac.firstChild.data
            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.IXP_RU_REGISTER_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))

            sn = doc.getElementsByTagName("sn")[0]

            ru_ip = doc.getElementsByTagName("ru_ip")[0]

            name = None
            if (doc.getElementsByTagName("name")):
                name = doc.getElementsByTagName("name")[0]

            mac = None
            if (doc.getElementsByTagName("mac")):
                mac = doc.getElementsByTagName("mac")[0]

            event_dict = {}
            event_dict["eventType"] = XCAAPEvent.Connect.value
            event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Connect.value]
            event_dict["serial"] = sn.firstChild.data
            if (name != None):
                event_dict["name"] = name.firstChild.data
            if (mac != None):
                event_dict["mac"] = mac.firstChild.data
            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_AP_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))

            sn = doc.getElementsByTagName("serial")[0]

            action = doc.getElementsByTagName("action")[0]

            event_dict = {}

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_dict["serial"] = sn.firstChild.data
            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_TOPOLOGY_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            event_dict = {}

            if (doc.getElementsByTagName("topology_id")):
                topology_id = doc.getElementsByTagName("topology_id")[0]
                event_dict["topology_id"] = topology_id.firstChild.data

            if (doc.getElementsByTagName("topology_name")):
                topology_name = doc.getElementsByTagName("topology_name")[0]
                event_dict["topology_name"] = topology_name.firstChild.data

            if (doc.getElementsByTagName("uuid")):
                uuid = doc.getElementsByTagName("uuid")[0]
                event_dict["uuid"] = uuid.firstChild.data

            if (doc.getElementsByTagName("stamp")):
                stamp = doc.getElementsByTagName("stamp")[0]
                event_dict["stamp"] = stamp.firstChild.data

            if (doc.getElementsByTagName("vlan_id")):
                vlan_id = doc.getElementsByTagName("vlan_id")[0]
                event_dict["vlan_id"] = vlan_id.firstChild.data

            if (doc.getElementsByTagName("group")):
                group = doc.getElementsByTagName("group")[0]
                event_dict["group"] = group.firstChild.data

            action = doc.getElementsByTagName("action")[0]

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_AP_CONFIG_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            event_dict = {}

            if (doc.getElementsByTagName("id")):
                id = doc.getElementsByTagName("id")[0]
                event_dict["id"] = id.firstChild.data

            if (doc.getElementsByTagName("sn")):
                sn = doc.getElementsByTagName("sn")[0]
                event_dict["sn"] = sn.firstChild.data

            action = doc.getElementsByTagName("action")[0]

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_PROFILE_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            event_dict = {}

            if (doc.getElementsByTagName("id")):
                id = doc.getElementsByTagName("id")[0]
                event_dict["id"] = id.firstChild.data

            if (doc.getElementsByTagName("name")):
                name = doc.getElementsByTagName("name")[0]
                event_dict["name"] = name.firstChild.data

            if (doc.getElementsByTagName("uuid")):
                uuid = doc.getElementsByTagName("uuid")[0]
                event_dict["uuid"] = uuid.firstChild.data

            if (doc.getElementsByTagName("stamp")):
                stamp = doc.getElementsByTagName("stamp")[0]
                event_dict["stamp"] = stamp.firstChild.data

            action = doc.getElementsByTagName("action")[0]

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_RFS_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            event_dict = {}

            if (doc.getElementsByTagName("rfs_id")):
                rfs_id = doc.getElementsByTagName("rfs_id")[0]
                event_dict["rfs_id"] = rfs_id.firstChild.data

            if (doc.getElementsByTagName("rfs_name")):
                rfs_name = doc.getElementsByTagName("rfs_name")[0]
                event_dict["rfs_name"] = rfs_name.firstChild.data

            if (doc.getElementsByTagName("uuid")):
                uuid = doc.getElementsByTagName("uuid")[0]
                event_dict["uuid"] = uuid.firstChild.data

            if (doc.getElementsByTagName("stamp")):
                stamp = doc.getElementsByTagName("stamp")[0]
                event_dict["stamp"] = stamp.firstChild.data

            action = doc.getElementsByTagName("action")[0]

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_list = []
            event_list.append(event_dict)

        elif messageId == XCAMessage.OAM_POLICY_CHANGE_NOTIFY.value:

            doc = xml.dom.minidom.parseString(payload.decode('utf-8'))
            event_dict = {}

            if (doc.getElementsByTagName("policy_id")):
                policy_id = doc.getElementsByTagName("policy_id")[0]
                event_dict["policy_id"] = policy_id.firstChild.data

            if (doc.getElementsByTagName("policy_name")):
                policy_name = doc.getElementsByTagName("policy_name")[0]
                event_dict["policy_name"] = policy_name.firstChild.data

            if (doc.getElementsByTagName("uuid")):
                uuid = doc.getElementsByTagName("uuid")[0]
                event_dict["uuid"] = uuid.firstChild.data

            if (doc.getElementsByTagName("stamp")):
                stamp = doc.getElementsByTagName("stamp")[0]
                event_dict["stamp"] = stamp.firstChild.data

            action = doc.getElementsByTagName("action")[0]

            if(action.firstChild.data == "0"):
                event_dict["eventType"] = XCAAPEvent.Update.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Update.value]

            elif(action.firstChild.data == "1"):
                event_dict["eventType"] = XCAAPEvent.Create.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Create.value]

            elif(action.firstChild.data == "2"):
                event_dict["eventType"] = XCAAPEvent.Delete.value
                event_dict["eventTypeString"] =  XCAAPEventName[XCAAPEvent.Delete.value]

            event_list = []
            event_list.append(event_dict)

        else:
            logging.info("processReceivedMsg messageId {s} - adding payload to event list".format(s=self._msgtbl[messageId]))
            event_list = []
            event_list.append(payload)

        eventId = self.msgTypesMapping(messageId)
        curTime = time.time()

        msg = {'eventId': eventId, 'eventObj': event_list, 'eventTimeIn': curTime}

        try:
            self._q.put(msg, block=False, timeout=None)
        except Exception as e:
            logging.error("processReceivedMsg call to put() got except due to {e}".format(e=repr(e)))
        return

    def handleZeroReceive(self, fd):
        logging.info("remote end closed the connection {s}".format(s = fd))

        for i in range(len(self._conn)):
            if(fd == self._conn[i]):
                self._conn[i] = -1
                break

        self.unregisterFd(fd)
        fd.close()
        self._handshake.start(5) #restart
        return

    def readMessage(self, fd, size):
        msg = b''
        count = 0
        while len(msg) < size:
          pmsg = b''
          try:
            pmsg = fd.recv(size - len(msg))
          except socket.error as e:
            if e.args[0] != errno.EAGAIN and e.args[0] != errno.ENOENT and e.args[0] != errno.EWOULDBLOCK:
               logging.error("socket error: [{n}]".format(n=errno.errorcode[e.args[0]]))
               return b''
            else:
               logging.info("socket retry: [{n}] {s}".format(n=count,s=errno.errorcode[e.args[0]]))
               time.sleep(0.005)
          msg += pmsg
          count = count + 1
          if count > 100:
            logging.error("socket read retry max")
            return b''
        return msg

    def onMessage(self, fd):
        ## message header
        msg = self.readMessage(fd,12)
        if len(msg) == 0:
                    self.handleZeroReceive(fd)
                    return
        ## message id
        msg = self.readMessage(fd,4)
        if len(msg) == 0:
                    self.handleZeroReceive(fd)
                    return
        msgid = int(msg.hex(),16)
        if msgid >= self._msgids['CIA_MAX_NUM_MESSAGES']:
                    #logging.error( "wrong message id {e}".format(e=msgid))
                    return
        ## message size
        msg = self.readMessage(fd,4)
        if len(msg) == 0:
                    self.handleZeroReceive(fd)
                    return
        size = int(msg.hex(),16)
        if size >= 8388608:
                    logging.error( "wrong message size {e}".format(e=size))
                    return
        logging.info("Recv msg id: {n} msg size: {sz}".format(n=self._msgtbl[msgid],sz=size))
 
        ## message payload
        payload = self.readMessage(fd,size)
        if len(payload) == 0:
                    handleZeroReceive(fd)
                    return
        logging.info("Recv msg payload: {s}".format(s=len(payload)))

        logging.info("Recv msg printing XML doc start:")
        dom1 = xml.dom.minidom.parseString(payload.decode('utf-8'))
        dom_string = dom1.toprettyxml(encoding='UTF-8')
        logging.info(dom_string)
        logging.info("Recv msg printing XML doc end")

        ## decode 
        self.processReceivedMsg(msgid, payload)

        if (self._enableStats):
            self._readerStatsUpdater.incReaderMsgCounter()

        return

    def onClose(self, fd):
        print ('fd closed')
        self._handshake.start(3)
        return
    
    def open(self):
        self._context=ssl.create_default_context()
        self._context.check_hostname=False
        self._context.verify_mode = ssl.CERT_NONE
        #init timers
        self._handshake = langleyHandshake(self)
        self._hello = Hello(self) #will be started by the handshake when done
        
        # start the Handshake timer
        self._handshake.start(3)

        if(self._enableStats):
            self._readerStatsUpdater = ReaderStatsUpdater(self, self._q)
            self._readerStatsUpdater.start(1)
     
        return self
    
    def run(self):
        self.open()
        super().svc()

    def getStats(self):
        stats = {}
        if ((self._enableStats) and (self._readerStatsUpdater != None)):
            return self._readerStatsUpdater.getStats()
        return stats

    def msgTypesMapping(self, messageType: str) -> str:
        """Maps message type to event type.
           
          :param messageType: type of message
          :return: eventType

        """

        eventType = None
        if(messageType == XCAMessage.ES_MU_EVENT_NOTIFY.value):
            eventType = XCAEvent.MU_EVENT
        elif(messageType == XCAMessage.ES_LOCATION_EVENT_NOTIFY.value):
            eventType = XCAEvent.LOC_EVENT
        elif(messageType == XCAMessage.OAM_AP_CHANGE_NOTIFY.value or messageType == XCAMessage.IXP_RU_DISCONNECT_NOTIFY.value or messageType == XCAMessage.IXP_RU_REGISTER_NOTIFY.value):
            eventType = XCAEvent.AP_EVENT
        elif(messageType == XCAMessage.OAM_TOPOLOGY_CHANGE_NOTIFY.value):
            eventType = XCAEvent.TOPOLOGY_CHANGE_NOTIFY
        elif(messageType == XCAMessage.OAM_PROFILE_CHANGE_NOTIFY.value):
            eventType = XCAEvent.PROFILE_CHANGE_NOTIFY
        elif(messageType == XCAMessage.OAM_RFS_CHANGE_NOTIFY.value):
            eventType = XCAEvent.RFS_CHANGE_NOTIFY
        elif(messageType == XCAMessage.OAM_POLICY_CHANGE_NOTIFY.value):
            eventType = XCAEvent.POLICY_CHANGE_NOTIFY
        elif(messageType == XCAMessage.OAM_AP_CONFIG_CHANGE_NOTIFY.value):
            eventType = XCAEvent.AP_CONFIG_CHANGE_NOTIFY

        return eventType

class ListenerStatsUpdater(Timer):
    def __init__(self, reactor):
        super(ListenerStatsUpdater, self).__init__(reactor)
        self._callback = self.updateStats
        self._listenerMessagesCounter = 0
        self._muEventsCounter = 0

    def incListenerMsgCounter(self):
        self._listenerMessagesCounter = self._listenerMessagesCounter + 1

    def getListenerMsgCounter(self):
        return self._listenerMessagesCounter

    def incListenerMuEventsCounter(self, cnt):
        self._muEventsCounter = self._muEventsCounter + cnt

    def getListenerMuEventsCounter(self):
        return self._muEventsCounter

    def updateStats(self):
        logging.debug("listener updateStats - listenerMessagesCounter: {listenerMessagesCounter}, muEventsCounter: {muEventsCounter}".format(listenerMessagesCounter=self._listenerMessagesCounter, muEventsCounter=self._muEventsCounter))
        self._listenerMessagesCounter = 0
        self._muEventsCounter = 0
        self.start(1)

class Listener(Reactor):
    def __init__(self, cb, queue, enableStats = False):
        super(Listener, self).__init__()
        self._name = "listener"
        self._q = queue
        self._cb = cb
        self._enableStats = enableStats
        self._listenerStatsUpdater = None
        # the following are variables used to store stats counters for the Message latency
        self._eventLatencyEMAPref = 0
        self._eventLatencyEMACur = 0
        self._eventLatencyEMAAlpha = 0.9
        self._eventLatencyMax = 0

    def open(self):
        if(self._enableStats):
            self._listenerStatsUpdater = ListenerStatsUpdater(self)
            self._listenerStatsUpdater.start(1)

        if platform.system().lower() != "windows":
            self.registerFd(self._q._reader, self.onMessage) #windows does not work with Queue in select.select
        return self

    def onMessage(self, fd):
        msg = self._q.get()
        eventId = msg['eventId']
        eventObj = msg['eventObj']

        if (self._enableStats):
            eventTimeIn = msg['eventTimeIn']
            self.calculateEventLatencyEMA(eventTimeIn)

            cnt = 0
            for ev in eventObj:
                cnt = cnt + 1
            self._listenerStatsUpdater.incListenerMuEventsCounter(cnt)
            self._listenerStatsUpdater.incListenerMsgCounter()

        self._cb(eventId, eventObj)
        return

    def run(self):
        if platform.system().lower() == "windows":
            #Reactor not supported on windows because Queue can't be added to the select()
            #windows will block, busy waiting on the message from the queue
            while 1:
                self.onMessage(-1)
        else:
            #run reactor svc() loop
            self.open()
            super().svc()

    #the following function calculates the stats for the Message latency
    #it implements the exponentially weighted moving average algorithm
    def calculateEventLatencyEMA(self, eventInQueueTime):
        curTime = time.time()
        eventLatency = curTime - eventInQueueTime

        if (self._eventLatencyEMAPref == 0):
            self._eventLatencyEMACur = eventLatency
        else:
            self._eventLatencyEMACur = (eventLatency * self._eventLatencyEMAAlpha) + ((1 - self._eventLatencyEMAAlpha) * self._eventLatencyEMAPref)

        if( eventLatency > self._eventLatencyMax):
            self._eventLatencyMax = eventLatency

        self._eventLatencyEMAPref = self._eventLatencyEMACur

        logging.debug("eventLatencyEMACur: {eventLatencyEMACur:.6f} seconds, eventLatencyMax: {eventLatencyMax:.6f} seconds".format(eventLatencyEMACur=self._eventLatencyEMACur,eventLatencyMax=self._eventLatencyMax))

    def getStats(self) -> dict:
        """Retrieves the stats."""
        stats = {}
        if (self._enableStats):
            stats['eventLatencyEMACur'] = self._eventLatencyEMACur
            stats['eventLatencyMax'] = self._eventLatencyMax
            stats['muEventsCounter'] = self._listenerStatsUpdater.getListenerMsgCounter()
            stats['listenerMessagesCounter'] = self._listenerStatsUpdater.getListenerMuEventsCounter()
        return stats


def worker(ip, key, passwd, events, pipe, enableStats):
    Reader(ip, key, passwd, events, pipe, enableStats).run()

def worker2(cb, queue, enableStats):
    Listener(cb, queue, enableStats).run()

class Subscriber(Reactor):
    def __init__(self, ip: list, key: str, passwd, events, cb, enableStats: bool = False):
        """Instantiates the Subscriber class.
        
          :param ip: is a list containing the IP addresses of the XCC systems to subscribe messages from
          :param key: the shared secret
          :param cb: the callback function to invoke when a message is received (handle to function)
          :param enableStats: boolean to indicate if the stats collection should be enabled (False) or disabled (True)
          :return: None

          The key and password are either the username and password or API key and password.

          | *It is recommended to use the API key and password.*

          Usage::
            
            >> def cb3(eventId, eventObj):
            >>      logging.info("Callback#3 eventId {s}".format(s=eventId))
            >>
            >> api_key = input("API Key: [default]") or defaultKey   #
            >> api_password = input("API Password: [default]") or defaultPassword 
            >>
            >> s = Subscriber(ipList = ["ese.extremewireless.ca"], api_key, 
            >>                          api_password, events = [XCAEvent.MU_EVENT, 
            >>                          XCAEvent.AP_EVENT], cb=cb3)
            >> s.open()
        """

        super(Subscriber, self).__init__()
        self._name = "subscriber"
        self._ip = ip
        self._key = key
        self._passwd = passwd
        self._q = Queue(1024)
        self._cb = cb
        self._events = self.eventTypesMapping(events)
        self._enableStats = enableStats

    def eventTypesMapping(self, events: str) -> str:
        """Maps event types to message types.
            
           :param events: name of the event
           :return: messages
        """

        messages = []

        for ev in events:
            if ev == XCAEvent.MU_EVENT:
                messages.append(XCAMessage.ES_MU_EVENT_NOTIFY)
                logging.debug("eventTypesMapping event is MU_EVENT, appending XCAMessage.ES_MU_EVENT_NOTIFY")

            elif ev == XCAEvent.LOC_EVENT:
                messages.append(XCAMessage.ES_LOCATION_EVENT_NOTIFY)
                logging.debug("eventTypesMapping event is LOC_EVENT, appending XCAMessage.ES_LOCATION_EVENT_NOTIFY")

            elif ev == XCAEvent.AP_EVENT:
                messages.append(XCAMessage.OAM_AP_CHANGE_NOTIFY)
                messages.append(XCAMessage.IXP_RU_DISCONNECT_NOTIFY)
                messages.append(XCAMessage.IXP_RU_REGISTER_NOTIFY)
                logging.debug("eventTypesMapping event is AP_EVENT, appending XCAMessage.OAM_AP_CHANGE_NOTIFY,IXP_RU_DISCONNECT_NOTIFY,IXP_RU_REGISTER_NOTIFY")

            elif ev == XCAEvent.TOPOLOGY_CHANGE_NOTIFY:
                messages.append(XCAMessage.OAM_TOPOLOGY_CHANGE_NOTIFY)
                logging.debug("eventTypesMapping event is TOPOLOGY_CHANGE_NOTIFY, appending XCAMessage.OAM_TOPOLOGY_CHANGE_NOTIFY")

            elif ev == XCAEvent.PROFILE_CHANGE_NOTIFY:
                messages.append(XCAMessage.OAM_PROFILE_CHANGE_NOTIFY)
                logging.debug("eventTypesMapping event is PROFILE_CHANGE_NOTIFY, appending XCAMessage.OAM_PROFILE_CHANGE_NOTIFY")

            elif ev == XCAEvent.RFS_CHANGE_NOTIFY:
                messages.append(XCAMessage.OAM_RFS_CHANGE_NOTIFY)
                logging.debug("eventTypesMapping event is RFS_CHANGE_NOTIFY, appending XCAMessage.OAM_RFS_CHANGE_NOTIFY")

            elif ev == XCAEvent.POLICY_CHANGE_NOTIFY:
                messages.append(XCAMessage.OAM_POLICY_CHANGE_NOTIFY)
                logging.debug("eventTypesMapping event is POLICY_CHANGE_NOTIFY, appending XCAMessage.OAM_POLICY_CHANGE_NOTIFY")

            elif ev == XCAEvent.AP_CONFIG_CHANGE_NOTIFY:
                messages.append(XCAMessage.OAM_AP_CONFIG_CHANGE_NOTIFY)
                logging.debug("eventTypesMapping event is AP_CONFIG_CHANGE_NOTIFY, appending XCAMessage.OAM_AP_CONFIG_CHANGE_NOTIFY")

        return messages

    def open(self):
        """Inform the subscriber to initiate the connection to the XCC."""

        self._reader = Process(target = worker, args = (self._ip, self._key, self._passwd, self._events,  self._q, self._enableStats, ))
        self._reader.start()

        #self._listener = Process(target = worker2, args = (self._cb, self._q, self._enableStats, ))
        #self._listener.start()
        self._listener = Listener(self._cb, self._q, self._enableStats)
        self._listener.open().run()
        
        return self

    def getStats(self) -> dict:
        """Collects event statistics.
           
           :return: Subscribser stats containing the reader (readerStats) and listener (listenerStats) processes stats
        """
        stats = {}
        if (self._enableStats):
            stats['readerStats'] = self._reader.getStats()
            stats['listenerStats'] = self._listener.getStats()
        return stats


def cb1(eventId, eventObj):

    logging.info("Callback#1 eventId {s}".format(s=eventId))

    cnt = 1
    for ev in eventObj:
       logging.info("Callback#1 ---eventId[{i}], event[{c}]----".format(i=eventId, c=cnt))
       cnt = cnt + 1
       event_dict_keys = ev.keys()
       for ky in event_dict_keys:
          logging.info("Callback#1 prop:[{k}]=[{v}]".format(k=ky,v=ev[ky]))

def cb2(eventId, eventObj):

    logging.info("Callback#2 eventId {s}".format(s=eventId))

    cnt = 1
    for ev in eventObj:
        logging.info("Callback#2 ---eventId[{i}], event[{c}]----".format(i=eventId, c=cnt))
        cnt = cnt + 1
        event_dict_keys = ev.keys()
        for ky in event_dict_keys:
            logging.info("Callback#2 prop:[{k}]=[{v}]".format(k=ky, v=ev[ky]))

def cb3(eventId, eventObj):

    logging.info("Callback#3 eventId {s}".format(s=eventId))

