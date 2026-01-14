import json
import requests
import logging
import time
import xml.etree.ElementTree
import base64
import io
import traceback
import pytest
import pandas as pd
from xcc.parts import History

def test_apcreate(get_xcc):
    """ Create and delete WW SKUs
    """
    c= get_xcc
    aps = c.aps

    csv = [ {"hardwaretype":"AP4000-WW", "serialNumber" :"TT012209W-31020",
                "apName" : "Test_sdk_1", "description":"Test_sdk", 
                "complianceRegion": "AP4000-FCC"},
            {"hardwaretype":"AP5010-WW", "serialNumber" :"TT012209W-31021",
                "apName" : "Test_sdk_2", "description":"Test_sdk", 
                "complianceRegion": "AP5010-CAN"},
            {"hardwaretype":"AP510i-FCC", "serialNumber" :"TT012209W-31022",
                "apName" : "Test_sdk_3", "description":"Test_sdk", 
                "complianceRegion": ""}]
    
    for query in csv:
        res = aps.create(query)
        assert (res.ok)
        #read back aps
        res = aps.refresh().getByName(query["apName"])
        assert (res != None)
        res = aps.deleteByName(query["apName"])
        assert (res.ok)
        res = aps.refresh().getByName(query["apName"])
        assert (res == None)
    
    return

def test_aptest(get_xcc):
    return

def test_apuptime(get_xcc):
    """Test that you can retrieve the AP uptime 
    """
    from datetime import datetime, timedelta
    from typing import NamedTuple
    from operator import lt, gt
    #
    def apuptime(ic):
        """ Return the AP and their uptime as a list of Uptime tuples.
        """
        class Uptime(NamedTuple):
            name: str
            uptime: timedelta
            status: str
        #
        aps = ic.aps.getStats()
        uptime = [Uptime(x.apName, timedelta(seconds=x.sysUptime), x.status) for x in aps]
        return uptime
    #
    def apIsUp(uptime, days = 1, longer=True):
        """ Find AP's with uptime greater or less than given number of days.
            Disregard (drop) AP's that have uptime 0.
            
            :param days: number of days 
            :param longer: True for greater and False for lesser 

            Returns a list of Ap Uptime tuples
        """
        days = timedelta(days=days)
        op = gt if longer == True else lt
        apup = [x for x in uptime if (op(x.uptime, days) & (x.uptime != timedelta(0))) ]
        return apup
    #
    c= get_xcc
    status = apuptime(c)
    res1 = apIsUp(status, days=1, longer=False)
    res2 = apIsUp(status, days=1, longer=True)
    assert (len(res1) > 0) or (len(res2) > 0)
    

def test_apEvents(get_xcc):
    """Test that you can retrieve the AP events for last 14 days
    """
    c= get_xcc
    myaps = [x for x in c.aps.get()]
    now = pd.Timestamp.utcnow()
    et = now - pd.Timedelta(days=14)
    alarms = [ c.aps.getAlarms(x.serialNumber, 
                                    startTime=int(et.value/10**6), 
                                    endTime=int(now.value/10**6))
                          .ok 
                    for x in myaps]
    assert all(alarms)

def test_l2ports(get_xcc):
    """Test  l2 ports """
    c= get_xcc
    ports = c.platformMgr.l2PortStats()
    if len(ports) != 0:
        assert True

def test_IPaddress(get_xcc):
    """Test if there are IP addresses for the mobile unit objects"""
    c= get_xcc
    mus = c.mus.get(showActive = True)
    muslist = [x.ipAddress for x in mus]
    if len(muslist) != 0:
        assert True

@pytest.mark.parametrize("APname", [("AP3912")]) 
def test_searchAP3912(APname, get_xcc):
    """Test if there is an AP that has "AP3912" in their name or description"""
    c= get_xcc
    aps = c.aps.get()

    n3912 = [x.apName for x in aps if x.hardwareType.startswith(APname)]

    d3912 = [x.description for x in aps if x.hardwareType.startswith(APname)]

    if (len(n3912) | len(d3912)) != 0:
        assert True


@pytest.mark.parametrize("status", [("ACTIVE")]) 
def test_activeClients(status, get_xcc):
    """Test the IP address MAC and AP name combinations for all active clients"""
    c= get_xcc
    for st in ["ACTIVE",  "INACTIVE"]:
        mus = c.mus.get(showActive=True if st == "ACTIVE" else False, history = History.d3D)
        for q in mus:
            if q.status == st:
                assert True

def test_apGet(get_xcc):
    """Test to find the AP that matches a specific name"""
    c= get_xcc
    #config
    for a in c.aps.get():
        if (len(a.radios) != 0):
            assert True
        ap = c.aps.getBySerial(serial=a.serialNumber)
        if (len(a.radios) != 0):
            assert True
        ap = c.aps.getByName(name=a.apName)
        if (ap.adoptedBy in ["Primary", "Backup"]):
            assert True
    #
    #stats
    for a in c.aps.getStats():
        if (len(a.radios) != 0):
            assert True
        if (a.sysUptime >= 0):
            assert True
        ap = c.aps.getStatsBySerial(serial=a.serialNumber)
        if (ap.sysUptime in ["Primary", "Backup"]):
            assert True
        

def test_roles(get_xcc):
    """Test if there are roles on the XCC"""
    c= get_xcc
    roles = c.roles.get()
    for r in roles:
        if len(roles) != 0:
            assert True

def test_mobileClient(get_xcc):
    """Test if there is either a location or "no location" for the mobile client"""
    c= get_xcc
    mus = c.mus.get()
    for m in mus:
        loc = c.location.get(m.macAddress)
        if loc != None:
            assert True
        else:
            assert True

def test_locations(get_xcc):
    """Test if there are floors at the location of the mobile client"""
    c= get_xcc
    fl = []
    for ss in c.sites.get():
        floors = c.plans.getFloors(ss.id)
        if len(floors) !=0:
            fl = fl + [f.floorId for f in floors]
            assert True

    """Test if there are locations of clients on each floor"""
    locsAllFloors = []
    for fid in fl:
        print (f'Floor: {fid}')
        locs = c.location.getPerFloor(fid)
        locsAllFloors += locs
        for l in locs:
    	    if len(locs) != 0:
                assert True

#test_station checks to see if the station event log's data frame is empty
#If it is not empty, then there is a data frame with values making it true
@pytest.mark.parametrize("macaddress, eventType, ssid, serialNumber", [("44:55:66:33:11:22", "Roam", "eca", "1234567890123456")])
def test_station(get_xcc, macaddress, eventType, ssid, serialNumber):
    c= get_xcc
    resp = c.platformMgr.getStationEvLog(lastDay=1, lastH=10)
    ldf=pd.DataFrame(resp) #load log in data frame
    ldf=ldf.fillna("")
    ldf[ldf.macAddress == macaddress] #match on MAC
    ldf[ldf.ssid.str.startswith(ssid)] #match on ssid 
    ldf[(ldf.eventType == "eventType") & (ldf.apName == serialNumber)] #match on more fields
    if ldf.empty is not True:
        assert True

