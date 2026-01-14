#  Python SDK for Extreme Campus Controller (IQC)

# Platforms
* E1120
* E2120
* E2122
* E3120
* E3125
* VE6120/H/K, VE6125/K (Virtual)
* CE1000
* CE2000
* CE3000

# Getting Started with python SDK

IQC Python SDK provides wrappers around the raw XCC REST API's. Install the pyiqcsdk package and import it inside your own script, ipython or jupyter notebook. 

> Supports the XCC REST API Managers (version 1.25.0):
https://documentation.extremenetworks.com/Extreme%20Campus%20Controller/v5.26/API/index_rest_gateway.html

## Install / Upgrade pyiqcsdk from Pip Test
To use SDK as a python package, install it from the PiPy https://pypi.org/ using the pip. In this case, you don't need access to the code in the git repo. 
```python
pip install pyiqcsdk
```

# How to run the tests
Run the whole test suite:
```python
pytest tests/test_examples.py --xcc <url> --user <user> --passw <passw>
```
To run only one test:
```python
pytest tests/test_examples.py::test_apcreate --xcc <url> --user <user> --passw <passw>
```
# How to use it
In the python interpreter or inside the script, create a XCC Client. The Client class wraps up the initial login, all subsequent REST API calls to the XCC reuse the token obtained during Client instantiation.
```python
import pyiqcsdk as xcc
from xcc.api import Client
c=Client("admin", "abcd1234", "https://10.49.31.123:5825/")
```	
Once XCC client is successfully created, you can get all clients currently associated, across all sites and print their IP addresses:
```python
mus = c.mus.get()
print([x.ipAddress for x in mus])	
```
Below are examples of the SDK in action - from simple but powerful code snippets to more complex orchestration spanning multiple controller pairs.

- [Code Snippets](#code-snippets)
- [AP uptime](#ap-uptime)
  - [Working with Uptime](#functions)
  - [Print Uptime Histogram](#print-uptime-histogram)
  - [Multi Controller Avalability Pairs](#multi-controller-avalability-pairs)


## Code Snippets
These are basic code examples, you can copy the code and run it in your notebook or script. 

Get AP's adopted by the IQC and find the one that have "AP3912" in their name or description:
```python
#get all aps
aps = c.aps.get()

#find names for the AP's of type AP3912
n3912 = [x.apName for x in aps if x.hardwareType.startswith("AP3912")]

#find description for the ap of type AP3912
d3912 = [x.description for x in aps if x.hardwareType.startswith("AP3912")]
```

Find all active (currently connected) clients and print the client IP address, MAC address and associated AP name:
```python
for q in mus:
    if q.status=="ACTIVE":
        print(f' {q.ipAddress} ({q.macAddress}) is active on {q.accessPointName}')
```

Get all adopted AP's, find one that have "Dionis" in the name and set their radio0 power to 7dBm:
```python
for a in c.aps.get():
    if (len(a.radios) != 0):
        print (  "Name: {n}, serial: {s}, power: {p}".format(n=a.apName, s=a.serialNumber, p=a.radios[0]['txMaxPower']))
    # 
    ap = c.aps.get(key=a.serialNumber)[0]
    if (ap.apName.find("Dionis") > -1):
        ap.radios[0]['txMaxPower']=7
	print (c.aps.set(ap).content)
	print ( "Name: {n}, changed to : {p}".format(n=a.apName, p=a.radios[0]['txMaxPower']))
```

Get all configured Roles and print the number of L2, L3 and L7 rules for each of the Role:
```python
#get number of rules in each role
roles = c.roles.get()
for r in roles:
    print ("name: {n}, l2: {l2}, l3: {l3}, l7: {l7}".format(n=r.name, 
							   l2=len(r.l2Filters), 
							   l3=len(r.l3Filters), 
							   l7=len(r.l7Filters)))
```

Get all active clients and print their location (require to positioning being enabled): 
```python
mus = c.mus.get(query={"showActive":True})
for m in mus:
    loc = c.location.get(m.macAddress)
    if loc != None:
        print (m.macAddress, len(loc.locations), loc.locations[0])
    else:
        print (m.macAddress, "no location")
```

Make the list of all floors (iterate over Sites to find the floors assigned to the Site) and for each floor print the clients location:
```python
fl = []
#collect floors per Site
for ss in c.sites.get():
    floors = c.plans.getFloors(ss.id)
    
    if len(floors) != 0:
        fl = fl + [{"site":ss.siteName, "floor":f} for f in floors]
        print (f'Site: {ss.siteName}, {ss.treeNode["campus"]} has {len(floors)} floor plan')
#
#get the locations of all clients on each floor
for floor in fl:
    clientsWithLocs = c.location.getPerFloor(floor["floor"].floorId)
    print (f'Site: {floor["site"]}, floor: {floor["floor"].name} has {len(clientsWithLocs)} client with location')
    for l in clientsWithLocs:
        print (l)
```

Get the client event log (all clients), for the last 1 day and 10 hours. Convert the log into pandas data frame and execute few pandas queries on the data: 
```python
import pandas as pd
resp = c.platformMgr.getStationEvLog(lastDay=1, lastH=10)
ldf=pd.DataFrame(resp) #load log in data frame
ldf=ldf.fillna("")
ldf[ldf.macAddress == "D8:84:66:8B:67:77"] #filter on MAC
ldf[ldf.ssid.str.startswith("eca")] #filter on ssid 
ldf[(ldf.eventType == "Roam") & (ldf.apName == "1710Y-1601000000")] #filter on more fields
#print out each event
for i, row in ldf.iterrows():
    print (f'Event: {row.eventType}, mac: {row.macAddress}, ts (epoch sec): {row.timestamp}, details: {row.details}')
```
Get the dataset for clients in the last 3 hours (returned as base64 encoded string): 
```python
resp = c.reports.dataset()
```

## AP Uptime
In this example, we want to find APs with uptime (seconds from last reboot) bigger or smaller than given number of days. For example, find APs that are up for longer than 5 days. The AP uptime is obtained by the SDK method aps.getStats. SDK method aps.getStats returns, beside the AP uptime ("sysUptime" field) other AP statistics. 

> Note: To see exactly which statistics aps.getStats returns, print the content of one of the objects returned by the call
> ```python
> print (ic.aps.getStats()[0].__dict__)
>
> {
> 'features': {'RELEASE-TO-CLOUD': 1},
> 'profileName': 'My-AP302W-Profile',
> 'status': 'critical',
> 'tunnel': 'N/A',
> 'wiredClients': 0,
> 'apName': 'My-AP3202W',
> 'environment': 'INDOOR',
> .....
> }
>    
> ```

### Functions
Implementation of the AP uptime example is split between two functions. The first one, "apuptime" calls the SDK to get the ap's stats and returns the uptime as a list of Uptime objects. The second one, "apIsUp" filters the output of the "apuptime" to finds the aps with uptime less or greater than the given number of days. 

```python
from datetime import datetime, timedelta
from typing import NamedTuple
from operator import lt, gt

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
```
### Print Uptime Histogram 
One application of the uptime functions, is to print the histogram of the ap counts with uptime greater than 1d, 7d, 30d. 

Note that to find the aps with greater uptime than given days, you need to set "longer=True". To find one with lesser uptime  "longer=False".

```python
from xcc.api import Client
from getpass import getpass
import requests
requests.packages.urllib3.disable_warnings() 

passw=getpass("input passw: ")
ip = "my.iqc.com"
ic=Client("admin", passw, f'https://{ip}:5825/')

status = apuptime(ic)
for days in [1,7,30,60]:
    res = apIsUp(status, days=days, longer=True)
    print('{0:2d} days: {1} ({2}) {3}'.format(days, '+' * len(res), 
                                                  len(res), str([x.name for x in res[:3]])))

 1 days: +++++++++++++++++++++ (21) ['AP505-x', 'Paulo-305C-DB', 'Paulo-AP410C']
 7 days: +++++++++++++++ (15) ['AP505-x', 'Paulo-305C-DB', 'Paulo-AP410C']
30 days: + (1) ['Hao-AP3912']
60 days: + (1) ['Hao-AP3912']
```
Similar print the histogram of ap count with uptime lesser than 1d, 7d, 30d. 

```python
for days in [1,7,30,60]:
    res = apIsUp(status, days=days, longer=False)
    print('{0:2d} days: {1} ({2}) {3} ...'.format(days, '+' * len(res), 
                                                  len(res), [x.name for x in res[:3]]))

 1 days:  (0) [] ...
 7 days: ++++++ (6) ['hg-ap5k_30256', 'David_AP505i-FCC', 'AP5KU-Dionis-MR'] ...
30 days: ++++++++++++++++++++ (20) ['AP505-x', 'Paulo-305C-DB', 'Paulo-AP410C'] ...
60 days: ++++++++++++++++++++ (20) ['AP505-x', 'Paulo-305C-DB', 'Paulo-AP410C'] ...
```
### Multi Controller Avalability Pairs

In many real life deployments, there are multiple controller pairs and results of the AP uptime query need be consolidated across all of them. It just takes few lines of code to combine the uptime from any number of pairs - practically turning this script into a kind of manager of managers. First create a list of controller SDK clients (you need credentials only for one of the controllers in the pair), collect the AP uptime for each of the pair in a single uptime list and create historgram across all pairs. 


```python
uptime = []
cc = [Client(x[0], x[1], f'https://{x[2]}:5825/') for x in [("admin",passw1, "myxcc1.ca"),
                                                            ("admin",passw2, "myxcc2.ca")]]
#
for ic in cc:
    uptime += apuptime(ic)
#
for days in [1,7,30,60]:
    res = apIsUp(uptime, days=days, longer=False)
    print('{0:2d} days: {1} ({2}) {3} ...'.format(days, '+' * len(res), 
                                                  len(res), [x.name for x in res[:3]]))
```
# Support
The software is provided as is and Extreme Networks has no obligation to provide maintenance, support, updates, enhancements or modifications. Any support provided by Extreme Networks is at its sole discretion.

Issues and/or bugs can be submitted as issues to this repo. 
