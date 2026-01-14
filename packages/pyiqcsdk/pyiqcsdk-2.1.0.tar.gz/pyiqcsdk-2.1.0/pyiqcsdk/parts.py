# This module is the ExCloud Appliance Data Model elements.
import json
import requests
import logging
import time
import xml.etree.ElementTree
import base64
import zlib
import io
import os
from datetime import datetime, timedelta
from urllib.parse import quote
from enum import Enum
from typing import BinaryIO, NamedTuple, List, Union


LOGGER = logging.getLogger(__name__)


class History(str, Enum):
    """
    Enumeration for different history durations.

    Attributes:
        d3H (str): Represents a duration of 3 hours.
        d3D (str): Represents a duration of 3 days.
        d14D (str): Represents a duration of 14 days.
    """
    d3H = "3H",
    d3D = "3D",
    d14D = "14D"


class actionParams(Enum):
    """
    Enumeration for different HTTP action parameters.

    Attributes:
        GET (int): Represents the HTTP GET method.
        POST (int): Represents the HTTP POST method.
        PUT (int): Represents the HTTP PUT method.
        DELETE (int): Represents the HTTP DELETE method.
    """
    GET = 0
    POST = 1
    PUT = 2
    DELETE = 3


class one(object):
    """
    Single Object class.

    Methods:
        fromDict(data: dict) -> one:
            Create an object from a JSON representation.

    """

    def fromDict(self, data: dict) -> 'one':
        """
        Create an object from a JSON representation.

        Args:
            data (dict): JSON representation of the object.

        Returns:
            one: The created object.
        """
        for key, value in data.items():
            setattr(self, key, value)
        return self


class Base(object):
    """
    Base class for managing various operations on the Appliance.

    Methods:
        __init__(nseClient, fresh=True):
            Initialize the Base class with a client and optional fresh flag.

        clone(fromName: str, toName: str):
            Clone an entry from one name to another.

        create(name: str, path=None) -> requests.Response:
            Create a new entry with the given name and optional path.

        createCustom(object: object, path=None):
            Create a custom entry with the given object and optional path.

        delete(key: str, path=None) -> requests.Response:
            Delete an entry by key and optional path.

        deleteByKeyword(prefix: str, path=None):
            Delete entries by keyword and optional path.

        deleteByName(name: str, path=None):
            Delete an entry by name and optional path.

        deleteByPrefix(prefix: str, path=None):
            Delete entries by prefix and optional path.

        get(key='all', path=None, query=None, encode=True) -> List[one]:
            Retrieve data based on the provided key, path, and query.

        getAll(path=None, query=None, encode=True) -> List[one]:
            Retrieve all data based on the provided path and query.

        getByName(name: str) -> Union[one, None]:
            Retrieve data by name.

        getWithPathParam(pathParam: str = "", query=None):
            Retrieve data using a path parameter and optional query.

        nameToId(name: str, map=None):
            Convert a name to its corresponding ID.

        refresh():
            Refresh the data.

        set(object: object, uuid=None, path=None) -> requests.Response:
            Set data for the given object and optional UUID and path.

        toList(asObject=False):
            Convert data to a list.
    """

    def __init__(self, nseClient) -> None:
        """
        Initialize the Base class.

        Args:
            nseClient: The client to use for operations.
        """
        self.client = nseClient
        self._hash = {}
        self._id = None
        self._name = None
        self._path = None
        self._map = dict()

    def clone(self, fromName: str, toName: str) -> requests.Response:
        """
        Clone an entry from one name to another.

        Args:
            fromName (str): The name of the entry to clone from.
            toName (str): The name of the entry to clone to.

        Returns:
            requests.Response: The response from the createCustom operation.
        """
        if self._map is None:
            self.refresh()
        uuid = self.nameToId(fromName)
        o = self.get(uuid)[0]
        o.name = toName
        resp = self.createCustom(o)
        return resp

    def create(self, name: str, path=None) -> requests.Response:
        """
        Create a new entry with the given name and optional path.

        Args:
            name (str): The name of the new entry.
            path: Optional path to use for creation.

        Returns:
            requests.Response: The response from the create operation.
        """
        path = path if path is not None else self._path
        default = self.get('default', path=path)[0]
        default.name = name
        self.createCustom(default, path)
        return default

    def createCustom(self, object: object, path=None) -> requests.Response:
        """
        Create a custom entry with the given object and optional path.

        Args:
            object (object): The object to create.
            path: Optional path to use for creation.

        Returns:
            None
        """
        path = path if path is not None else self._path
        cleandict = object.__dict__.copy()
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest[path], json=cleandict)
        return resp

    def delete(self, key: str, path=None) -> requests.Response:
        """
        Delete an entry by key and optional path.

        Args:
            key (str): The key of the entry to delete.
            path: Optional path to use for deletion.

        Returns:
            requests.Response: The response from the delete operation.
        """
        path = path if path is not None else self._path
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + self.client.rest[path] + "/" + key)
        return resp

    def deleteByKeyword(self, prefix: str) -> None:
        """
        Delete entries by keyword and optional path.

        Args:
            prefix (str): The keyword to use for deletion.

        Returns:
            None
        """
        self.refresh()
        nn = [x for x in self.get() if prefix in getattr(x, self._name)]
        resp = None
        for n in nn:
            resp = self.delete(getattr(n, self._id))
        return resp

    def deleteByName(self, name: str, path=None) -> None:
        """
        Delete an entry by name and optional path.

        Args:
            name (str): The name of the entry to delete.
            path: Optional path to use for deletion.

        Returns:
            None
        """
        key = self.nameToId(name)
        return self.delete(key, path) if key is not None else None

    def deleteByPrefix(self, prefix: str) -> None:
        """
        Delete entries by prefix and optional path.

        Args:
            prefix (str): The prefix to use for deletion.

        Returns:
            None
        """
        self.refresh()
        nn = [x for x in self.get() if getattr(x, self._name).startswith(prefix)]
        resp = None
        for n in nn:
            resp = self.delete(getattr(n, self._id))
        return resp

    def get(self, key='all', path=None, query=None, encode=True) -> List[one]:
        """
        Retrieve data based on the provided key, path, and query.

        Args:
            key (str): The key to use for retrieval.
            path: Optional path to use for retrieval.
            query: Optional query to use for retrieval.
            encode (bool): Optional flag to indicate if encoding should be used.

        Returns:
            List[one]: The retrieved data.
        """
        path = path if path is not None else self._path
        self._hash = {}
        try:
            if key == 'all':
                resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[path],
                                                   params=query)
                for m in json.loads(resp.content.decode('utf-8')):
                    element = one().fromDict(m)
                    self._hash[m[self._id]] = element
            else:
                resp = self.client.requestsWrapper(actionParams.GET,
                                                   self.client.url + self.client.rest[path] + "/" + str(key),
                                                   params=query)
                if not resp.ok:
                    print(resp.content)
                    return []

                m = resp.json()
                element = one().fromDict(m)
                self._hash[m.get(self._id, "fake")] = element
            return self.toList(asObject=encode)
        except json.JSONDecodeError as e:
            print(e)
            return []

    def getAll(self, path=None, query=None, encode=True) -> List[one]:
        """
        Retrieve all data based on the provided path and query.

        Args:
            path: Optional path to use for retrieval.
            query: Optional query to use for retrieval.
            encode (bool): Optional flag to indicate if encoding should be used.

        Returns:
            List[one]: The retrieved data.
        """
        basePath = self.client.rest[self._path]
        path = f'{basePath}/{path}' if path is not None else basePath
        self._hash = {}
        try:
            resp = self.client.requestsWrapper(actionParams.GET, f'{self.client.url}{path}', params=query)
            for m in json.loads(resp.content.decode('utf-8')):
                element = one().fromDict(m)
                self._hash[m[self._id]] = element
            return self.toList(asObject=encode)
        except json.JSONDecodeError as e:
            print(e)
            return []

    def getByName(self, name: str) -> Union[one, None]:
        """
        Retrieve data by name.

        Args:
            name (str): The name to use for retrieval.

        Returns:
            Union[one, None]: The retrieved data or None if not found.
        """
        uuid = self.nameToId(name)
        return self.get(uuid)[0] if uuid is not None else None

    def getWithPathParam(self, pathParam: str = "", query=None) -> List[one]:
        """
        Retrieve data using a path parameter and optional query.

        Args:
            pathParam (str): The path parameter to use for retrieval.
            query: Optional query to use for retrieval.

        Returns:
            The retrieved data.
        """
        try:
            resp = self.client.requestsWrapper(actionParams.GET,
                                               self.client.url + self.client.rest[self._path] + "/" + pathParam,
                                               params=query)
            m = resp.json()
            if isinstance(m, list):
                return [one().fromDict(oo) for oo in m]
            else:
                return one().fromDict(m)
        except json.JSONDecodeError as e:
            print(e)
            return []

    def nameToId(self, name: str, map=None) -> Union[str, None]:
        """
        Convert a name to its corresponding ID.

        Args:
            name (str): The name to convert.
            map: Optional mapping to use for conversion.

        Returns:
            The corresponding ID.
        """
        map = map if map is not None else self._map
        res = [v for k, v in map.items() if k == name]
        return None if len(res) == 0 else res[0]

    def refresh(self) -> 'Base':
        """
        Refresh the data.

        Returns:
            self
        """
        idpath = self.client.rest[self._path + "idmap"]
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + idpath)
        self._map = resp.json()
        return self

    def set(self, object: object, uuid=None, path=None) -> requests.Response:
        """
        Set data for the given object and optional UUID and path.

        Args:
            object (object): The object to set.
            uuid: Optional UUID to use for setting.
            path: Optional path to use for setting.

        Returns:
            requests.Response: The response from the set operation.
        """
        path = path if path is not None else self._path
        uuid = uuid if uuid is not None else object.__dict__[self._id]
        cleandict = object.__dict__.copy()
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest[path] + "/" + uuid, json=cleandict)
        return resp

    def toList(self, asObject=False) -> List[one]:
        """
        Convert data to a list.

        Args:
            asObject (bool): Optional flag to indicate if the data should be returned as objects.

        Returns:
            The data as a list.
        """
        l = []
        for k, v in self._hash.items():
            l.append(v if asObject else v.__dict__)
        return l


class AAAPolicy(Base):
    """
    AAAPolicy class for managing AAA policies on the Appliance.

    Methods:
        __init__(client):
            Initialize the AAAPolicy class.

        create(name: str, ipAddress: str = None, sharedSecret = None, auth_protocol = AuthenticationProtocol.CHAP.value, called_station_id = CalledStationID.WIRED_MAC_COLON_SSID.value):
            Create a new AAA policy with default values.

    """

    def __init__(self, client) -> None:
        """
        Initialize the AAAPolicy class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(AAAPolicy, self).__init__(client)
        self._id = 'id'
        self._path = 'aaapolicy'
        self._name = 'name'

    class AuthenticationProtocol(Enum) :
        """
        Enumeration for different authentication protocols.

        Attributes:
            PAP: Password Authentication Protocol.
            CHAP: Challenge Handshake Authentication Protocol.
            MSCHAP: Microsoft Challenge Handshake Authentication Protocol.
            MSCHAP2: Microsoft Challenge Handshake Authentication Protocol v2.
        """
        PAP = "PAP"
        CHAP = "CHAP"
        MSCHAP = "MSCHAP"
        MSCHAP2 = "MSCHAP2"

    class CalledStationID(Enum):
        """
        Enumeration for different Called Station ID formats.

        Attributes:
            WIRED_MAC_COLON_SSID: Wired MAC address followed by SSID.
            BSSID: Basic Service Set Identifier.
            SITE_NAME: Site name.
            SITE_NAME_COLON_DEVICE_GROUP_NAME: Site name followed by device group name.
            SERIAL: Serial number.
            SITE_CAMPUS: Site campus.
            SITE_REGION: Site region.
            SITE_CITY: Site city.
        """
        WIRED_MAC_COLON_SSID = "WiredMacColonSsid"
        BSSID = "Bssid"
        SITE_NAME = "SiteName"
        SITE_NAME_COLON_DEVICE_GROUP_NAME = "SiteNameColonDeviceGroupName"
        SERIAL = "Serial"
        SITE_CAMPUS = "SiteCampus"
        SITE_REGION = "SiteRegion"
        SITE_CITY = "SiteCity"

    def create(self, name: str, ipAddress: str = None, sharedSecret=None,
               auth_protocol=AuthenticationProtocol.CHAP.value,
               called_station_id=CalledStationID.WIRED_MAC_COLON_SSID.value) -> requests.Response:
        """
        Create a new AAA policy with default values.

        Args:
            name (str): The name of the AAA policy.
            ipAddress (str, optional): The IP address for the AAA policy. Defaults to None.
            sharedSecret (str, optional): The shared secret for the AAA policy. Defaults to None.
            auth_protocol (str, optional): The authentication protocol. Defaults to AuthenticationProtocol.CHAP.value.
            called_station_id (str, optional): The Called Station ID format. Defaults to CalledStationID.WIRED_MAC_COLON_SSID.value.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(AAAPolicy, self).get('default', path=self._path)[0]
        default.name = name
        default.authenticationType = auth_protocol

        if ipAddress and sharedSecret:
            default.authenticationRadiusServers = [{
                "ipAddress": ipAddress,
                "sharedSecret": sharedSecret,
                "port": 1812,
                "timeout": 5,
                "totalRetries": 3,
                "pollInterval": 60}]
            default.accountingRadiusServers = [{
                "ipAddress": ipAddress,
                "sharedSecret": sharedSecret,
                "port": 1813,
                "timeout": 5,
                "totalRetries": 3,
                "pollInterval": 60}]

        default.attributes = {
            "calledStationId": called_station_id,
            "nasId": "",
            "nasIpAddress": ""}

        # create new aaa policy
        resp = super(AAAPolicy, self).createCustom(default, path=self._path)
        return resp


class AccessRules(Base):
    """
    AccessRules class for managing access rules on the Appliance.

    Methods:
        __init__(client):
            Initialize the AccessRules class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the AccessRules class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(AccessRules, self).__init__(client)
        self._path = 'rules'


class Airdefense(Base):
    """
    Airdefense class for managing Airdefense profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the Airdefense class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Airdefense class.

        Args:
            client: The client instance to use for making requests.
        """
        super(Airdefense, self).__init__(client)
        self._id = 'id'
        self._path = 'airdefense'
        self._name = 'name'


class AnalyticsProfiles(Base):
    """
    AnalyticsProfiles class for managing analytics profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the AnalyticsProfiles class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the AnalyticsProfiles class.

        Args:
            client: The client instance to use for making requests.
        """
        super(AnalyticsProfiles, self).__init__(client)
        self._id = 'id'
        self._path = 'analytics'


class Appkeys():
    """
    Appkeys class for managing app keys on the Appliance.

    Methods:
        __init__(client):
            Initialize the Appkeys class.

        create_and_download(username: str, filename=None) -> (requests.Response, str):
            Create and download a new app key for the provided username.

        get(username: str) -> requests.Response:
            Get the app key for the provided username.

        delete(id) -> requests.Response:
            Delete the app key with the provided key ID.
    """
    def __init__(self, client) -> None:
        """
        Initialize the Appkeys class.

        Args:
            client: The client instance to use for making requests.
        """
        self.client = client
        self._path = 'appkeys'

    def create_and_download(self, username: str, filename=None) -> requests.Response:
        """
        Create and download a new app key for the provided username.
        Args:
            username (str): The username for which to create the app key.
            filename (str, optional): The name of the file to save the app key. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        params = {
            'user': username
        }
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest[self._path],
                                           json=params)
        if resp.ok:
            saved_file = f'{username}_api_key.json' if not filename else filename

            # Save the app key to a file
            with open(saved_file, "w") as f:
                f.write(resp.text)
            print(f"App key created and saved to '{saved_file}'")
        return resp

    def get(self, username: str) -> requests.Response:
        """
        Get the app key for the provided username.
        Args:
            username (str): The username for which to get the app key.

        Returns:
            requests.Response: The response from the server.
        """
        params = {
            'user': username
        }
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[self._path], params=params)
        return resp

    def delete(self, key_id) -> requests.Response:
        """
        Delete the app key with the provided key ID.
        Args:
            key_id: The key ID of the app key to delete.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + self.client.rest[self._path] + "/" + key_id)
        return resp


class Aps(Base):
    """
    Aps class for managing Access Points (APs) on the Appliance.

    Methods:
        __init__(client):
            Initialize the Aps class.

        adoptionPreference(serialNumberList: list, affinity: Affinity) -> requests.Response:
            Set the adoption preference for the specified AP.

        apInfo() -> requests.Response:
            Get information about all APs.

        apLogLevel(serialNumberList: list, logLevel: LogLevel) -> requests.Response:
            Set the log level for the specified APs.

        applyCertificate(serialNumber, certificateFile, password) -> requests.Response:
            Apply a certificate to the AP.

        assignAPsToFloor(floorId: str, serialNumbersList: list) -> requests.Response:
            Assign list of APs to a floor.

        clone(sourceSerialNumber: str, newSerialNumber: str, newApName: str) -> requests.Response:
            Clone an AP from one serial number to another.

        create(query: dict) -> requests.Response:
            Create a new AP.

        getAPReport(serialNumber) -> requests.Response:
            Get the AP report by serial number.

        getAFCInfo() -> requests.Response:
            Get AFC info for all APs in the controller.

        getAlarms(serialNumber, startTime, endTime, categories=None) -> requests.Response:
            Get AP alarm report.

        getAPPowerConsumption(serialNumber) -> requests.Response:
            Get the AP power consumption by serial number.

        getByName(name: str) -> Union[one, None]:
            Get the AP by name, returns the config object.

        getBySerial(serial: str) -> one:
            Get the AP by serial, returns the config object.

        getDevicesSshPassword() -> requests.Response
            Get the SSH password for all devices.

        getInfoBySerial(serial: str) -> one:
            Get the AP info by serial, returns the config object.

        getStats() -> Union[List[one], None]:
            Get list of APs, returns the stats object (extended).

        getStatsBySerial(serial: str) -> one:
            Get AP by serial and return the stats object (extended).

        imageDelete(fname: str, apModel: str) -> requests.Response:
            Delete the AP image.

        imageUpgrade(apSerialList: str, version: str, upgradeNoServiceInterruption) -> requests.Response:
            Upgrade the AP image.

        imageUpload(fname: str, apModel: str, fpath: str = "") -> requests.Response:
            Upload image from local computer to the XCC for the AP to install it later.

        images() -> requests.Response:
            Get the list of AP images.

        imagesApLocal(model: str, exact=False) -> dict:
            Return AP images currently local. Exact is used for differentiating between similar models.

        inventory(flat=False) -> dict:
            Utility function to return all APs inventory (BSSIDs) as dictionary.

        logsDownload(serial: str, downloadFile: str) -> requests.Response:
            Download AP trace.

        logsRetrieve(serial: str) -> requests.Response:
            Retrieve logs of the AP.

        reboot(apSerialList: str) -> requests.Response:
            Reboot the access points in the provided input list.

        refresh():
            Override the base refresh method.

        releaseToCloud(serialNumberList: list) -> requests.Response:
            Release the AP serial number list to the cloud.

        resetCertificate(serialNumber) -> requests.Response:
            Reset the certificate of the AP.

        setDevicesSshPassword() -> requests.Response
            Set the SSH password for all devices.

        setRadioState(serialNumber: str, radioIdx: int, state: str) -> requests.Response:
            Given the AP serial number and radio index, enable/disable the specified radio.

        smarttRF(serialNumber, widget_list, band="Band5", duration="D_3h") -> requests.Response:
            Get smart RF data for the AP.

        state() -> requests.Response:
            Get the state of the AP.

        swVersion(serial) -> list:
            Get the software version of the AP by serial.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Aps class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(Aps, self).__init__(client)
        self._id = 'serialNumber'
        self._path = 'aps'
        self._name = 'apName'

    class Affinity(Enum):
        """
        Enumeration for different AP adoption preferences.
        """
        PRIMARY = "Primary"
        BACKUP = "Backup"
        ANY = "Any"

    class LogLevel(Enum):
        """
        Enumeration for different log levels.

        Attributes:
            DEBUG: Debug log level.
            INFO: Info log level.
            WARNING: Warning log level.
            MAJOR: Error log level.
            CRITICAL: Critical log level.
        """
        INFO = "Informational"
        MINOR = "Warnings"
        MAJOR = "Errors"
        CRITICAL = "Critical"

    def adoptionPreference(self, serialNumberList: list, affinity: Affinity) -> requests.Response:
        """
        Set the adoption preference for the specified AP.

        Args:
            serialNumberList (list): The serial number list of the APs.
            affinity (str): The adoption preference to set.

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest['aps'] + "/affinity"
        params = {
            "affinityOvr": True,
            'affinity': affinity.value,
            "serialNumbers": serialNumberList
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, json=params)
        return resp

    def apInfo(self) -> requests.Response:
        """
        Get information about all APs.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[self._path],
                                           params={"brief": True})
        return resp

    def apLogLevel(self, serialNumberList: list, logLevel: LogLevel) -> requests.Response:
        """
        Set the log level for the specified APs.

        Args:
            serialNumberList (list): The list of AP serial numbers.
            logLevel (LogLevel): The log level to set.

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest['aps'] + "/aploglevel"
        params = {
            "apLogLevelOvr": True,
            "serialNumbers": serialNumberList,
            "apLogLevel": logLevel.value
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, json=params)
        return resp

    def applyCertificate(self, serialNumber, certificateFile, password) -> requests.Response:
        """
        Apply a certificate to the specified AP.

        Args:
            serialNumber (str): The serial number of the AP.
            certificateFile (str): The path to the certificate file.
            password (str): The password for the certificate file.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['cert']}/apply"
        with open(certificateFile, "rb") as cert_file:
            cert_content = cert_file.read()
        b64_data = base64.b64encode(cert_content).decode('utf-8')

        params = {
            'filename': certificateFile,
            'password': password,
            'serialNumbers': [serialNumber],
            'data': b64_data
        }

        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + path,
                                           json=params)
        return resp

    def assignAPsToFloor(self, floorId: str, serialNumbersList: list) -> requests.Response:
        """
        Assign APs to a specified floor.

        Args:
            floorId (str): The ID of the floor.
            serialNumbersList (list): The list of AP serial numbers to assign to the floor.

        Returns:
            requests.Response: The response from the server.
        """
        data = {
            "floorId": floorId,
            "serialNumbers": serialNumbersList
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest['assignfloor'],
                                           json=data)
        return resp

    def clone(self, sourceSerialNumber: str, newSerialNumber: str, newApName: str) -> requests.Response:
        """
        Clone an AP from one serial number to another.

        Args:
            sourceSerialNumber (str): The serial number of the AP to clone from.
            newSerialNumber (str): The serial number of the new AP.
            newApName (str): The name of the new AP.

        Returns:
            requests.Response: The response from the server.
        """
        json_params = {
            "sourceSerialNumber": sourceSerialNumber,
            "serialNumber": newSerialNumber,
            "apName": newApName,
            "hardwaretype": self.getBySerial(sourceSerialNumber).hardwareType,
        }

        query = {
            "sourceSerialNumber": sourceSerialNumber,
            "newSerialNumber": newSerialNumber,
            "newApName": newApName,
        }
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest[self._path] + "/clone",
                                           params=query, json=json_params)
        return resp


    def create(self, query: dict) -> requests.Response:
        """
        Create a new AP with the specified query parameters.

        Args:
            query (dict): The query parameters for creating the AP.

        Returns:
            requests.Response: The response from the server.
        """
        # create new ap. Pattern for ap creation is quite different than other objects
        requestBody = {'hardwaretype': query['hardwaretype'],
                       'serialNumber': query['serialNumber'],
                       'apName': query['apName'],
                       'complianceRegion': query['complianceRegion'],
                       'act': "create"}
        # description is required even empty
        query['description'] = ""

        resp = self.client.requestsWrapper(actionParams.POST,
                                           self.client.url + self.client.rest[self._path] + "/create",
                                           params=query,
                                           json=requestBody)
        return resp

    def getAPReport(self, serialNumber) -> requests.Response:
        """
        Get the report for the specified AP serial number.

        Args:
            serialNumber: The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['statistics']}/{serialNumber}"
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path,
                                           params={
                                               "widgetList": "pollApStats%2CpollApRttPacketLoss"})  # This adds AP smart poll results into the response

        return resp

    def getAFCInfo(self) -> requests.Response:
        """
        Get the AFC (Automated Frequency Coordination) information.

        Returns:
            requests.Response: The response from the server.
        """

        path = f"{self.client.rest['afc']}?noCache={str(int(time.time() * 1000))}"
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path)
        return resp

    def getAlarms(self, serialNumber, startTime, endTime, categories=None) -> requests.Response:
        """
        Get the alarms for the specified AP serial number within the given time range.

        Args:
            serialNumber: The serial number of the AP.
            startTime: The start time for the alarm query.
            endTime: The end time for the alarm query.
            categories (optional): The categories of alarms to query.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['aps']}/{serialNumber}/alarms"
        params = {
            "startTime": startTime,
            "endTime": endTime,
            "categories": categories
        }
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path, params=params)
        return resp

    def getAPPowerConsumption(self, serialNumber) -> requests.Response:
        """
        Get the power consumption for the specified AP serial number.

        Args:
            serialNumber: The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['statistics']}/{serialNumber}"
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path,
                                           params={
                                               "widgetList": "all%2CapPowerConsumptionTimeseries"})

        return resp

    def getByName(self, name: str) -> Union[one, None]:
        """
        Get the AP by name, returns the config object.

        Args:
            name (str): The name of the AP.

        Returns:
            Union[one, None]: The AP object or None if not found.
        """
        r = [x for x in self.get() if x.apName == name]
        return r[0] if len(r) != 0 else None

    def getBySerial(self, serial: str) -> one:
        """
        Get the AP by serial, returns the config object.

        Args:
            serial (str): The serial number of the AP.

        Returns:
            one: The AP object.
        """
        r = [x for x in self.get() if x.serialNumber == serial]
        return r[0] if len(r) != 0 else None

    def getDevicesSshPassword(self) -> requests.Response:
        """
        Get the SSH password for all APs .

        Args:
            None

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['aps']}/registration"
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path)
        return resp

    def getInfoBySerial(self, serial: str) -> one:
        """
        Get the AP info by serial, returns the config object.

        Args:
            serial (str): The serial number of the AP.

        Returns:
            one: The AP info object.
        """
        r = self.get(key=serial)
        return r[0] if len(r) != 0 else None

    def getStats(self) -> Union[List[one], None]:
        """
        Get list of APs, returns the stats object (extended).

        Returns:
            Union[List[one], None]: List of AP stats objects or None if not found.
        """
        r = self.getAll(path="query")
        return r

    def getStatsBySerial(self, serial: str) -> one:
        """
        Get AP by serial and return the stats object (extended).

        Args:
            serial (str): The serial number of the AP.

        Returns:
            one: The AP stats object.
        """
        r = [x for x in self.getAll(path="query") if x.serialNumber == serial]
        return r[0] if len(r) != 0 else None

    def imageDelete(self, fname: str, apModel: str) -> requests.Response:
        """
        Delete the image for the specified AP model.

        Args:
            fname (str): The name of the image file to be deleted.
            apModel (str): The model of the AP for which the image is to be deleted.

        Returns:
            requests.Response: The response from the server.
        """
        files = {'apPlatform': apModel, 'filename': fname}
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest["apimages"] + "/" + "delete",
                                           json=files)
        return resp

    def imageUpgrade(self, apSerialList: str, version: str, upgradeNoServiceInterruption) -> requests.Response:
        """
        Upgrade the image for the specified APs.

        Args:
            apSerialList (str): The list of AP serial numbers.
            version (str): The version of the image.
            upgradeNoServiceInterruption: Whether to upgrade without service interruption.

        Returns:
            requests.Response: The response from the server.
        """
        query = {'upgradeNoServiceInterruption': upgradeNoServiceInterruption, "swVersion": version}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["aps"] + "/swupgrade",
                                           json={'serialNumbers': apSerialList},
                                           params=query)
        return resp

    def imageUpload(self, fname: str, apModel: str, fpath: str = "") -> requests.Response:
        """
        Upload an image for the specified AP model.

        Args:
            fname (str): The name of the image file.
            apModel (str): The model of the AP.
            fpath (str, optional): The file path of the image. Defaults to "".

        Returns:
            requests.Response: The response from the server.
        """
        files = {'apPlatform': (None, apModel), 'file': (fname, open(os.path.join(fpath, fname), 'rb'))}
        resp = self.client.requestsWrapper(actionParams.POST,
                                           self.client.url + self.client.rest["apimages"] + "/" + "fileupload",
                                           files=files)
        return resp

    def images(self) -> requests.Response:
        """
        Get the list of AP images.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["apimages"] + "/" + "list",
                                           params=None)
        return resp

    def imagesApLocal(self, model: str, exact=False) -> dict:
        """
        Get the list of local images for the specified AP model.

        Args:
            model (str): The model of the AP.
            exact (bool, optional): Whether to match the model exactly. Defaults to False.

        Returns:
            dict: A dictionary containing the local images.
        """
        if exact:
            return [x['images'] for x in self.images().json() if x['displayName'] == model][0]
        else:
            return [x['images'] for x in self.images().json() if x['displayName'].startswith(model)][0]

    def inventory(self, flat=False) -> dict:
        """
        Get the inventory of all APs.

        Args:
            flat (bool, optional): Whether to return a flat inventory. Defaults to False.

        Returns:
            dict: A dictionary containing the inventory of all APs.
        """
        bssid = self.get(query={"brief": True, "inventory": True}, encode=False)
        if flat:
            fbssid = []
            for b in bssid:
                for i in range(len(b['radios'])):
                    for w in b['radios'][i]['wlan']:
                        t = w
                        t['ap'] = b['serialNumber']
                        t['radio'] = i
                        fbssid.append(t)
            bssid = fbssid
        return bssid

    def logsDownload(self, serial: str, downloadFile: str) -> requests.Response:
        """
        Download logs for the specified AP serial number.

        Args:
            serial (str): The serial number of the AP.
            downloadFile (str): The file path to save the downloaded logs. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        path = "management/v1/aps/{s}/traceurls".format(s=serial)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path,
                                           params=None)
        if resp.ok:
            tarName = resp.json()[0]
            path = "management/v1/aps/downloadtrace/{s}".format(s=tarName)
            resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path,
                                               params=None,
                                               stream=True)
            if resp.ok:
                with open(downloadFile, 'wb') as f:
                    for chunk in resp.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                            f.flush()

        return resp

    def logsRetrieve(self, serial: str) -> requests.Response:
        """
        Retrieve logs for the specified AP serial number.

        Args:
            serial (str): The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        path = "management/v1/aps/{s}/logs".format(s=serial)
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path,
                                           params=None,
                                           json={'serialNumber': serial})
        return resp

    def reboot(self, apSerialList: str) -> requests.Response:
        """
        Reboot the access points in the provided input list.

        Args:
            apSerialList (str): Serial number list of the APs.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["aps"] + "/reboot",
                                           json={'serialNumbers': apSerialList})
        return resp

    def refresh(self) -> None:
        """
        Refresh the AP data.

        Returns:
            None
        """
        aps = self.get()
        for a in aps:
            self._map[a.apName] = a.serialNumber
        return self

    def releaseToCloud(self, serialNumberList: list) -> requests.Response:
        """
        Release the specified APs to the cloud.

        Args:
            serialNumberList (list): The list of AP serial numbers to release.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['aps']}/releasetocloud"
        params = {
            'serialNumbers': serialNumberList,
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, json=params)
        return resp

    def resetCertificate(self, serialNumber) -> requests.Response:
        """
        Reset the certificate for the specified AP.

        Args:
            serialNumber (str): The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['cert']}/reset"

        params = {
            'serialNumbers': [serialNumber],
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path,
                                           json=params)
        return resp

    def setDevicesSshPassword(self, password: str) -> requests.Response:
        """
        Set the SSH password for all devices.
        Args:
            password (str): The SSH password to set for all devices.

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['aps']}/registration"
        payload = {
            "sshPassword": password
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, json=payload)
        return resp

    def setRadioState(self, serialNumber: str, radioIdx: int, state: str) -> requests.Response:
        """
        Set the radio state for the specified AP serial number and radio index.

        Args:
            serialNumber (str): The serial number of the AP.
            radioIdx (int): The radio index.
            state (str): The desired state of the radio.

        Returns:
            requests.Response: The response from the server.
        """
        # Get the current AP configuration, modify specific parameters, and then write back.
        # This is how modify is done on the XCA.
        path = "management/v1/aps/{s}".format(s=serialNumber)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path,
                                           params=None)
        if resp.ok:
            ap = json.loads(resp.text)

            if state == "disable":
                ap['radios'][radioIdx]['adminStateOvr'] = True
                ap['radios'][radioIdx]['adminState'] = False
            else:
                ap['radios'][radioIdx]['adminStateOvr'] = False

            resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, json=ap)
        return resp

    def smarttRF(self, serialNumber, widget_list, band="Band5", duration="D_3h") -> requests.Response:
        """
        Perform smart RF operations on the specified AP.

        Args:
            serialNumber (str): The serial number of the AP.
            widget_list (list): The list of widgets for the smart RF operation.
            band (str, optional): The band for the smart RF operation. Defaults to "Band5".
            duration (str, optional): The duration for the smart RF operation. Defaults to "D_3h".

        Returns:
            requests.Response: The response from the server.
        """
        path = f"{self.client.rest['smartrf']}/{serialNumber}/smartrf?"
        widgets = []
        for w in widget_list:
            widgets.append({"id": w})

        params = {
            'band': band,
            'duration': duration,
            'widgets': widgets
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path,
                                           json=params)
        return resp

    def state(self) -> requests.Response:
        """
        Get the state of all APs.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["state"] + "/aps")
        return resp

    def swVersion(self, serial) -> list:
        """
        Get the software version for the specified AP serial number.

        Args:
            serial: The serial number of the AP.

        Returns:
            list: A list containing the software version information.
        """
        return [x.softwareVersion for x in self.get() if x.serialNumber == serial]



class APTestRun(Base):
    """
    APTestRun class for managing AP Test Runs on the Appliance.

    Methods:
        __init__(client):
            Initialize the APTestRun class.

        create(name: str, testSuiteId: str, serviceId: str, devices: list, iperfBasePort: int, duration: int):
            Create a new AP Test Run with the specified parameters.

        deleteOldtestResult(id: str, minutes: str) -> requests.Response:
            Delete old test results older than the specified age in minutes.

        getTestResultByRunId(id: str) -> requests.Response:
            Get test results by test run UUID.

        runIsDone(id: str) -> bool:
            Check if the test run is done.

        startTestRun(params: str) -> requests.Response:
            Start a test run with the specified parameters.
    """

    def __init__(self, client) -> None:
        """
        Initialize the APTestRun class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(APTestRun, self).__init__(client)
        self._id = 'id'
        self._path = 'testrun'
        self._name = 'name'

    def create(self, name: str, testSuiteId: str, serviceId: str, devices: list, iperfBasePort: int, duration: int) -> requests.Response:
        """
        Create a new AP Test Run with the specified parameters.

        Args:
            name (str): The name of the AP Test Run.
            testSuiteId (str): The ID of the test suite.
            serviceId (str): The ID of the service.
            devices (list): The list of devices.
            iperfBasePort (int): The base port for iperf.
            duration (int): The duration of the test run.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(APTestRun, self).get('default', path=self._path)[0]
        default.name = name
        default.testSuiteId = testSuiteId
        default.serviceId = serviceId
        default.devices = devices
        default.iperfBasePort = iperfBasePort
        default.duration = duration
        resp = super(APTestRun, self).createCustom(default, path=self._path)
        return resp

    def deleteOldtestResult(self, id: str, minutes: str) -> requests.Response:
        """
        Delete old test results older than the specified age in minutes.

        Args:
            id (str): The UUID of the test run.
            minutes (str): The age in minutes for the test run results to delete.

        Returns:
            requests.Response: The response from the server.
        """
        path = self._path
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest[path] + "/" + id + '/age?age=' + minutes)
        return resp

    def getTestResultByRunId(self, id: str) -> requests.Response:
        """
        Get test results by test run UUID.

        Args:
            id (str): The UUID of the test run.

        Returns:
            requests.Response: The response from the server.
        """
        path = self._path
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest[path] + "/" + id + '/stats')
        return resp

    def runIsDone(self, id: str) -> bool:
        """
        Check if the test run is done.

        Args:
            id (str): The UUID of the test run.

        Returns:
            bool: True if the test run is done, otherwise False.
        """
        resp = self.getTestResultByRunId(id)
        status = all([x["status"].startswith("Done") for x in resp.json()])
        return status

    def startTestRun(self, params: str) -> requests.Response:
        """
        Start a test run with the specified parameters.

        Args:
            params (str): The parameters for the test run.

        Returns:
            requests.Response: The response from the server.
        """
        path = self._path
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest[path] + "/" + "start",
                                           json=params)
        return resp


class APTestSuite(Base):
    """
    APTestSuite class for managing AP Test Suites on the Appliance.

    Methods:
        __init__(client):
            Initialize the APTestSuite class.

        create(name: str, testCommands: List[cmd], useDhcp: bool = None, mac: clientMac = None, staticIp: clientIp = None):
            Create a new AP Test Suite with the specified parameters.
    """

    def __init__(self, client) -> None:
        """Instantiates the APTestSuite Manager.

           :param client: reference to Client
           :type client: class
        """
        super(APTestSuite, self).__init__(client)
        self._id = 'id'
        self._path = 'testsuites'
        self._name = 'name'

    class cmd(NamedTuple):
        """
        Named tuple representing a test command.

        Attributes:
            enabled (str): Indicates if the command is enabled.
            cmd (str): The command to be executed.
            dest (str): The destination for the command.
            cmdParams (str): The parameters for the command.
        """
        enabled: str
        cmd: str
        dest: str
        cmdParams: str

    class clientMac(NamedTuple):
        """
        Named tuple representing a client MAC address.

        Attributes:
            defaultMac (bool): Indicates if the default MAC address is used.
            custom (str): The custom MAC address.
        """
        defaultMac: bool
        custom: str

    class clientIp(NamedTuple):
        """
        Named tuple representing a client IP address.

        Attributes:
            ipAddress (str): The IP address.
            gateway (str): The gateway address.
            cidr (int): The CIDR notation for the subnet mask.
        """
        ipAddress: str
        gateway: str
        cidr: int

    def create(self, name: str, testCommands: List[cmd], useDhcp: bool = None, mac: clientMac = None,
               staticIp: clientIp = None) -> requests.Response:
        """
        Create a new AP Test Suite with the specified parameters.

        Args:
            name (str): The name of the AP Test Suite.
            testCommands (List[cmd]): The list of test commands.
            useDhcp (bool, optional): Indicates if DHCP is used. Defaults to None.
            mac (clientMac, optional): The client MAC address. Defaults to None.
            staticIp (clientIp, optional): The client IP address. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(APTestSuite, self).get('default', path=self._path)[0]
        default.name = name
        default.test = [{k: v for k, v in cmd._asdict().items()} for cmd in testCommands]
        default.useDhcp = useDhcp if useDhcp is not None else default.useDhcp
        default.mac = mac._asdict() if mac is not None else default.mac
        default.staticAddr = staticIp._asdict() if staticIp is not None else default.staticAddr
        #
        resp = super(APTestSuite, self).createCustom(default, path=self._path)
        return resp


class BestPracticesMgr:
    """
    Best Practices Manager class for managing best practices operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the BestPracticesMgr class with a client.

        accept(id) -> requests.Response:
            Accept a best practice by its ID.

        evaluate() -> requests.Response:
            Evaluate the best practices.


    """

    def __init__(self, client) -> None:
        """
        Initialize the BestPracticesMgr class.

        Args:
            client: The client to use for operations.
        """
        self.client = client

    def accept(self, id) -> requests.Response:
        """
        Accept a best practice by its ID.

        Args:
            id: The ID of the best practice to accept.

        Returns:
            requests.Response: The response from the accept operation.
        """
        resp = self.client.requestsWrapper(actionParams.PUT,
                                           self.client.url + self.client.rest["bestpractices"] + "/" + id + "/accept")
        return resp

    def evaluate(self) -> requests.Response:
        """
        Evaluate the best practices.

        Returns:
            requests.Response: The response from the evaluate operation.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["bestpractices"] + "/evaluate")
        return resp


class ChannelInspector(Base):
    """
    ChannelInspector class for managing channel inspection on the Appliance.

    Methods:
        __init__(client):
            Initialize the ChannelInspector class.

        getChannelInspectorReport(serial: str) -> requests.Response:
            Retrieve the channel inspector report for the given AP serial number.
    """

    def __init__(self, client) -> None:
        """
        Initialize the ChannelInspector class.

        Args:
            client: The client instance to use for making requests.
        """
        super(ChannelInspector, self).__init__(client)
        self._id = 'apSn'
        self._path = 'channelinspector'

    def getChannelInspectorReport(self, serial: str) -> requests.Response:
        """
        Retrieve the channel inspector report for the given AP serial number.

        Args:
            serial (str): The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        path = "management/v1/aps/{s}/channelinspector".format(s=serial)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path, params=None)
        return resp


class ConcentratorManager(Base):
    """
    ConcentratorManager class for managing concentrators on the Appliance.

    Methods:
        __init__(client):
            Initialize the ConcentratorManager class.

        create(name: str, description: str, secure: bool, ikev2Psk: str, terminationAddr: str, serialNumber: str = None, bridgePortID: str = None, termination: dict = None) -> requests.Response:
            Create a new Concentrator using default values.

        deleteConcentrator(name: str) -> requests.Response:
            Delete the concentrator object with the given name.

        getConcentratorList() -> list:
            Return the entire list of concentrator objects.

        setConcentrator(name: str, description: str, secure: bool, ikev2Psk: str, terminationAddr: str, serialNumber: str = None, bridgePortID: str = None, termination: dict = None) -> requests.Response:
            Update the concentrator object with the given name.
    """

    def __init__(self, client) -> None:
        """
        Initialize the ConcentratorManager class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(ConcentratorManager, self).__init__(client)
        self._id = 'id'
        self._path = 'concentrators'
        self._name = 'name'

    # Post
    def create(self, name: str, description: str, secure: bool, ikev2Psk: str, terminationAddr: str,
               serialNumber: str = None, bridgePortID: str = None, termination: dict = None) -> requests.Response:
        """
        Create a new Concentrator using default values.

        Args:
            name (str): The name of the concentrator.
            description (str): The description of the concentrator.
            secure (bool): Indicates if the concentrator is secure.
            ikev2Psk (str): The key for IKEV2 protocol.
            terminationAddr (str): The termination address of the concentrator.
            serialNumber (str, optional): The serial number of the concentrator. Defaults to None.
            bridgePortID (str, optional): The bridge port ID of the concentrator. Defaults to None.
            termination (dict, optional): The termination information. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(ConcentratorManager, self).get('default', path=self._path)[0]
        default.name = name
        default.description = description
        default.secure = secure
        default.ikev2Psk = ikev2Psk
        default.terminationAddr = terminationAddr

        if serialNumber:
            default.serialNumber = serialNumber
        if bridgePortID:
            default.bridge = {"portId": bridgePortID}
        if termination:
            default.termination = termination

        resp = super(ConcentratorManager, self).createCustom(default, path=self._path)
        return resp

    # Delete by ID
    def deleteConcentrator(self, name: str) -> requests.Response:
        """
        Delete the concentrator object with the given name.

        Args:
            name (str): The name of the concentrator.

        Returns:
            requests.Response: The response from the server.
        """
        rec = self.refresh().nameToId(name)
        if rec is not None:
            rest = self.client.rest["concentrators"] + "/" + str(rec)
            resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)
        else:
            resp = {'status_code': 404, 'error': "Not Found"}
        return resp

    # Get All
    def getConcentratorList(self) -> list:
        """
        Return the entire list of concentrator objects.

        Returns:
            list: A list of concentrator objects.
        """
        concentrators = [x.__dict__ for x in self.getAll()]
        return concentrators

    # Put by ID (name)
    def setConcentrator(self, name: str, description: str, secure: bool, ikev2Psk: str, terminationAddr: str,
                        serialNumber: str = None, bridgePortID: str = None,
                        termination: dict = None) -> requests.Response:
        """
        Update the concentrator object with the given name.

        Args:
            name (str): The name of the concentrator.
            description (str): The description of the concentrator.
            secure (bool): Indicates if the concentrator is secure.
            ikev2Psk (str): The key for IKEV2 protocol.
            terminationAddr (str): The termination address of the concentrator.
            serialNumber (str, optional): The serial number of the concentrator. Defaults to None.
            bridgePortID (str, optional): The bridge port ID of the concentrator. Defaults to None.
            termination (dict, optional): The termination information. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        rec = self.refresh().getByName(name)
        if rec:
            rec.description = description
            rec.secure = secure
            rec.ikev2Psk = ikev2Psk
            rec.terminationAddr = terminationAddr
            if serialNumber:
                rec.serialNumber = serialNumber
            if bridgePortID:
                rec.bridge = {"portId": bridgePortID}
            if termination:
                rec.termination = termination
            resp = self.set(rec)
        else:
            resp = {'status_code': 404, 'error': "Not Found"}
        return resp


class ContainerTemplates(Base):
    """
    ContainerTemplates class for managing application container templates on the Appliance.

    Methods:
        __init__(client):
            Initialize the ContainerTemplates class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the ContainerTemplates class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(ContainerTemplates, self).__init__(client)
        self._path = 'containerTemplates'
        self._id = 'AppName'


class Cos(Base):
    """
    Class of Service class on the Appliance.

    Methods:
        __init__(client):
            Initialize the Cos class.

        create(cos_name, priority: 'Cos.Priority | str' = Priority.ANY_PRIORITY, tos_dscp=None, mask=None, inbound_rate_limiter_id=None,
                outbound_rate_limiter_id=None) -> requests.Response:
                Create a new Class of Service (CoS) with the specified parameters.
    """

    class Priority(Enum):
        ANY_PRIORITY = "notApplicable"
        PRIORITY0 = "priority0"
        PRIORITY1 = "priority1"
        PRIORITY2 = "priority2"
        PRIORITY3 = "priority3"
        PRIORITY4 = "priority4"
        PRIORITY5 = "priority5"
        PRIORITY6 = "priority6"
        PRIORITY7 = "priority7"

        @classmethod
        def from_label(cls, label: str) -> "Cos.Priority":
            mapping = {
                "Any Priority": cls.ANY_PRIORITY,
                "Priority0": cls.PRIORITY0,
                "Priority1": cls.PRIORITY1,
                "Priority2": cls.PRIORITY2,
                "Priority3": cls.PRIORITY3,
                "Priority4": cls.PRIORITY4,
                "Priority5": cls.PRIORITY5,
                "Priority6": cls.PRIORITY6,
                "Priority7": cls.PRIORITY7,
            }
            return mapping[label]

    def __init__(self, client) -> None:
        """
        Initialize the Cos class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(Cos, self).__init__(client)
        self._id = 'id'
        self._path = 'cos'
        self._name = 'cosName'

    def create(self, cos_name, priority: 'Cos.Priority | str' = Priority.ANY_PRIORITY, tos_dscp=None, mask=None, inbound_rate_limiter_id=None,
               outbound_rate_limiter_id=None) -> requests.Response:
        """
        Create a new Class of Service (CoS) with the specified parameters.
        Args:
            cos_name (str): The name of the CoS.
            priority (Cos.Priority | str, optional): The priority level. Defaults to Priority.ANY_PRIORITY.
            tos_dscp (int, optional): The TOS/DSCP value. Defaults to None.
            mask (str, optional): The mask value. Defaults to None.
            inbound_rate_limiter_id (str, optional): The inbound rate limiter ID. Defaults to None.
            outbound_rate_limiter_id (str, optional): The outbound rate limiter ID. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        # Allow passing either Enum or raw string
        priority_value = priority.value if isinstance(priority, Cos.Priority) else priority
        payload = {
            'cosName': cos_name,
            'cosQos': {
                'priority': priority_value,
                'tosDscp': tos_dscp,
                'mask': mask
            },
            'inboundRateLimiterId': inbound_rate_limiter_id,
            'outboundRateLimiterId': outbound_rate_limiter_id,
        }
        resp = self.client.requestsWrapper(
            actionParams.POST,
            self.client.url + self.client.rest[self._path],
            json=payload
        )
        return resp


class GeoLocation(Base):
    """
    GeoLocation class for managing geolocation operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the GeoLocation class.

        apRanging(floorId: str) -> requests.Response:
            Perform AP-to-AP ranging for the specified floor ID.

        autolocate(floorId: str) -> requests.Response:
            Build the subgraphs and derive coordinates for the specified floor ID.

        getFloorOverview(floorId: str) -> requests.Response:
            Get an overview of the floor with the specified ID.

        getInfoBySiteName(siteName: str) -> requests.Response:
            Get summary of geolocation information for the specified site name.
    """

    def __init__(self, client) -> None:
        """
        Initialize the GeoLocation class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(GeoLocation, self).__init__(client)
        self._path = 'geolocation'

    def apRanging(self, floorId: str) -> requests.Response:
        """
        Perform AP-to-AP ranging for the specified floor ID.

        Args:
            floorId (str): The ID of the floor.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(
            actionParams.POST,
            self.client.url + self.client.rest[self._path] + "/" + floorId + "/range",
        )
        return resp

    def autolocate(self, floorId: str) -> requests.Response:
        """
        Build the subgraphs and derive coordinates for the specified floor ID.

        Args:
            floorId (str): The ID of the floor.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(
            actionParams.POST,
            self.client.url + self.client.rest[self._path] + "/" + floorId + "/autolocate",
        )
        return resp

    def getFloorOverview(self, floorId: str) -> requests.Response:
        """
        Get an overview of the floor with the specified ID.

        Args:
            floorId (str): The ID of the floor.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(
            actionParams.GET,
            self.client.url + self.client.rest[self._path] + "/" + floorId + "/overview"
        )
        return resp

    def getInfoBySiteName(self, siteName: str) -> requests.Response:
        """
        Get summary of geolocation information for the specified site name.

        Args:
            siteName (str): The name of the site.

        Returns:
            requests.Response: The response from the server.
        """
        siteId = self.client.sites.refresh().getByName(siteName).id
        resp = self.client.requestsWrapper(
            actionParams.GET,
            self.client.url + self.client.rest[self._path] + "/" + "floors/" + siteId
        )
        return resp


class iotProfiles(Base):
    """
    iotProfiles class for managing IoT profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the iotProfiles class.

        create(name: str):
            Create a new IoT profile with the provided name.

        create_v2(data: dict):
            Create a new IoT profile using the provided data.
    """

    def __init__(self, client) -> None:
        """
        Initialize the iotProfiles class.

        Args:
            client: The client instance to use for making requests.
        """
        super(iotProfiles, self).__init__(client)
        self._id = 'id'
        self._path = 'iotprofile'

    def create(self, name: str) -> requests.Response:
        """
        Create a new IoT profile with the provided name.

        Args:
            name (str): The name of the profile.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(iotProfiles, self).get('default', path=self._path)[0]
        default.name = name
        default.appId = 'eddystoneAdvertisement'
        default.eddystoneAdvertisement['interval'] = 100
        default.eddystoneAdvertisement['url'] = 'http://www.google.com'
        default.eddystoneScan = None
        default.iBeaconAdvertisement = None
        default.iBeaconScan = None
        default.threadGateway = None
        default.genericScan['destPort'] = 1
        default.genericScan['destAddr'] = '192.168.1.10'
        resp = super(iotProfiles, self).createCustom(default, path=self._path)
        return resp

    def create_v2(self, data) -> requests.Response:
        """
        Create a new IoT profile using the provided data.

        Args:
            data (dict): A dictionary containing the profile data.

        Returns:
            requests.Response: The response from the create operation.
        """
        resp = self.client.requestsWrapper(actionParams.POST, f'{self.client.url}/{self.client.rest[self._path]}',
                                           json=data)
        return resp


class LDAP:
    """
    LDAP class for managing LDAP configuration on the Appliance.
    Methods:
        __init__(client):
            Initialize the LDAP class.

        getConfigs() -> requests.Response:
            Get the LDAP configurations.

        getConfigByName(config_name) -> requests.Response:
            Get a specific LDAP configuration by name.

        createConfig(payload) -> requests.Response:
            Create a new LDAP configuration.

        deleteConfig(config_name) -> requests.Response:
            Delete an existing LDAP configuration.

        updateConfig(config_name, items_to_update) -> requests.Response:
            Update an existing LDAP configuration.
    """

    class UserAuthType(Enum):
        ntlm_auth = "NTLM Authentication"
        ldap_bind = "LDAP Bind"
        ptpl = "Plain Text Password Lookup"
        nhpl = "NTHash Password Lookup"

    def __init__(self, client):
        """
        Initialize the LDAP class.
        """
        self._path = 'ldap'
        self.client = client

    def getConfigs(self) -> requests.Response:
        """
        Get the LDAP configurations.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[self._path])
        return resp

    def getConfigByName(self, config_name) -> requests.Response:
        """
        Get a specific LDAP configuration by name.

        Args:
            config_name: The name of the LDAP configuration.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[self._path] +
                                           f"/{config_name}")
        return resp

    def createConfig(self, payload) -> requests.Response:
        """
        Create a new LDAP configuration.
        Args:
            payload: The configuration object to create.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest[self._path],
                                           json=payload)
        return resp

    def deleteConfig(self, config_name) -> requests.Response:
        """
        Delete an existing LDAP configuration.

        Args:
            config_name: Configuration name.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + self.client.rest[self._path] +
                                           f"/{config_name}")
        return resp

    def updateConfig(self, config_name, items_to_update) -> requests.Response:
        """
        Update an existing LDAP configuration.

        Args:
            config_name: Configuration name.
            items_to_update: The items to update in the configuration.

        Returns:
            requests.Response: The response from the server.
        """
        config_object = self.getConfigByName(config_name).json()

        # Update the config with values from modified_payload
        for key, value in items_to_update.items():
            config_object[key] = value

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest[self._path] +
                                           f"/{config_name}", json=config_object)
        return resp


class Licenses:
    """
    Licenses class for managing Controller Licensing.

    Methods:
        __init__(client):
            Initialize the Licenses class.

        airGapMode(enabled: bool) -> requests.Response:
            Enable or disable Air-Gap mode on the controller.

        LicensesReport() -> requests.Response:
            Retrieve all entitlements and activations.

        LicenseSync() -> requests.Response:
            Synchronize with the Gemalto Server.

        pilotOnlyMode(enabled: bool) -> requests.Response:
            Enable or disable Pilot only mode on the controller.

        SynchronizeNow(updatenow: str, updatetime: str) -> requests.Response:
            Synchronize the controller immediately.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Licenses class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        self.client = client

    def airGapMode(self, enabled: bool) -> requests.Response:
        """
        Enable or disable Air-Gap mode on the controller.

        Args:
            enabled (bool): True to enable Air-Gap mode, False to disable it.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {'enabled': not enabled}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["LicenseSync"], payload)
        return resp

    def LicensesReport(self) -> requests.Response:
        """
        Retrieve all entitlements and activations.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["LicenseDetailsReport"])
        return resp

    def LicenseSync(self) -> requests.Response:
        """
        Synchronize with the Gemalto Server.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["LicenseSync"])
        return resp

    def pilotOnlyMode(self, enabled: bool) -> requests.Response:
        """
        Enable or disable Pilot only mode on the controller.

        Args:
            enabled (bool): True to enable Pilot only mode, False to disable it.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {'pilotLicense': enabled}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["LicensePilot"],
                                           payload)
        return resp

    def SynchronizeNow(self, updatenow: str, updatetime: str) -> requests.Response:
        """
        Synchronize the controller immediately.

        Args:
            updatenow (str): "True" or "False" to indicate whether to update now.
            updatetime (str): The time of the update.

        Returns:
            requests.Response: The response from the server.
        """
        body = {"updatenow": updatenow, "updateTime": updatetime}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["LicenseSync"],
                                           json=body)
        return resp


class Location(object):
    """
    Location API class for managing location-related operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Location API.

        client(NamedTuple):
            Named tuple representing a client.

        get(mac: str, query: str = "") -> requests.Response:
            Get the locations of a client by MAC address in the last hour.

        getPerFloor(floorId: str, query: str = "") -> requests.Response:
            Get the locations of clients on a specific floor.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Location API.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        self._id = 'mac'
        self._path = 'location'
        self.client = client  # reference to client

    class client(NamedTuple):
        """
        Named tuple representing a client.

        Attributes:
            mac (str): The MAC address of the client.
            deviceFamily (str): The device family of the client.
            locations (List[pos]): A list of positions of the client.
        """

        class pos(NamedTuple):
            """
            Named tuple representing a position.

            Attributes:
                x (float): The x-coordinate of the position.
                y (float): The y-coordinate of the position.
                z (float): The z-coordinate of the position.
                timestamp (int): The timestamp of the position.
            """
            floor_uuid: str
            ap: str  # serial of the associated ap
            x: int  # distance in meters from the top left floor corner
            y: int
            time: int  # time in msec from epoch

        mac: str
        deviceFamily: str
        locations: List[pos]

    def get(self, mac: str, query: str = "") -> requests.Response:
        """
        Get the locations of a client by MAC address in the last hour.

        Args:
            mac (str): The MAC address of the client.
            query (str, optional): Additional query parameters. Defaults to "".

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest["muloc"].format(mac=mac)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path, params=query)
        return resp

    def getPerFloor(self, floorId: str, query: str = "") -> requests.Response:
        """
        Get the locations of clients on a specific floor.

        Args:
            floorId (str): The ID of the floor.
            query (str, optional): Additional query parameters. Defaults to "".

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest["floorloc"].format(fid=floorId)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path, params=query)
        return resp


class Mus(Base):
    """
    Mus class for managing Mobile Unit Objects on the Appliance.

    Methods:
        __init__(client):
            Initialize the Mus class.

        accessListAdd(mac: str) -> requests.Response:
            Add a MAC address to the global list.

        accessListGet() -> requests.Response:
            Get the allow/deny global list.

        accessListRemove(mac: str) -> requests.Response:
            Remove a MAC address from the global list.

        get(showActive=True, history=History.d3H) -> list:
            Retrieve Mobile Unit data.

        getByIpAddress(ipAddress: str) -> Union[one, None]:
            Retrieve a Mobile Unit object using its IP address.

        getByMacAddress(macAddress: str) -> Union[one, None]:
            Retrieve a Mobile Unit object using its MAC address.

        muDelete(muMacAddress: str, deleteUserRegistrations=True, deleteHistory=True) -> requests.Response:
            Delete a Mobile Unit.

        muDisassociate(muMacAddress: str, deleteHistory=False) -> requests.Response:
            Disassociate a Mobile Unit.

        muReauthenticate(muMacAddress: str) -> requests.Response:
            Re-authenticate a Mobile Unit.
    """
    def __init__(self, client) -> None:
        """
        Initialize the Mus class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(Mus, self).__init__(client)
        self._id = "macAddress"
        self._path = 'mus'

    def accessListAdd(self, mac: str) -> requests.Response:
        """
        Add a MAC address to the global list.

        Args:
            mac (str): The MAC address to add.

        Returns:
            requests.Response: The response from the server.
        """
        ll = self.accessListGet().json()
        ll["macList"].append(mac)
        resp = self.client.requestsWrapper(actionParams.PUT, f'{self.client.url}{self.client.rest["allowDenyList"]}',
                                           json=ll)
        return resp

    def accessListGet(self) -> requests.Response:
        """
        Get the allow/deny global list.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, f'{self.client.url}{self.client.rest["allowDenyList"]}',
                                           params=None)
        return resp

    def accessListRemove(self, mac: str) -> requests.Response:
        """
        Remove a MAC address from the global list.

        Args:
            mac (str): The MAC address to remove.

        Returns:
            requests.Response: The response from the server.
        """
        list = self.accessListGet().json()
        list["macList"].remove(mac)
        resp = self.client.requestsWrapper(actionParams.PUT, f'{self.client.url}{self.client.rest["allowDenyList"]}',
                                           json=list)
        return resp

    def get(self, showActive = True, history:History = History.d3H)-> list:
        """
        Retrieve Mobile Unit data.

        Args:
            showActive (bool): Flag to show active Mobile Units only.
            history (History): Duration of history to retrieve.

        Returns:
            list: List of Mobile Unit objects.
        """
        query = {'duration':history, "showActive": showActive}
        res = super(Mus, self).getAll(path=None, query=query)
        return res

    def getByIpAddress(self, ipAddress: str) -> Union[one, None]:
        """
        Retrieve a Mobile Unit object using its IP address.

        Args:
            ipAddress (str): The IP address of the Mobile Unit.

        Returns:
            Union[one, None]: The Mobile Unit object or None if not found.
        """
        r = [x for x in self.get() if x.ipAddress == ipAddress]
        return r[0] if len(r) != 0 else None

    def getByMacAddress(self, macAddress: str) -> Union[one, None]:
        """
        Retrieve a Mobile Unit object using its MAC address.

        Args:
            macAddress (str): The MAC address of the Mobile Unit.

        Returns:
            Union[one, None]: The Mobile Unit object or None if not found.
        """
        r = [x for x in self.get() if x.macAddress == macAddress]
        return r[0] if len(r) != 0 else None

    def muDelete(self, muMacAddress, deleteUserRegistrations=True, deleteHistory=True) -> requests.Response:
        """
        Delete a Mobile Unit.

        Args:
            muMacAddress (str): The MAC address of the Mobile Unit.
            deleteUserRegistrations (bool): Flag to delete user registrations.
            deleteHistory (bool): Flag to delete the history of the Mobile Unit.

        Returns:
            requests.Response: The response from the server.
        """
        params = {
            "delete_registered_devices": deleteUserRegistrations,
            "delete_values_in_named_lists": deleteUserRegistrations,
            "force": True
        }
        json_params = [muMacAddress]
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + self.client.rest["muactions"],
                                           json=json_params, params=params)
        if resp.ok:
            # Send disassociate
            resp = self.muDisassociate(muMacAddress, deleteHistory=deleteHistory)
        return resp

    def muDisassociate(self, muMacAddress, deleteHistory=False) -> requests.Response:
        """
        Disassociate a Mobile Unit.

        Args:
            muMacAddress (str): The MAC address of the Mobile Unit.
            deleteHistory (bool): Flag to delete the history of the Mobile Unit.

        Returns:
            requests.Response: The response from the server.
        """
        json_params = {"custId": None, "id": None, "canDelete": None, "macList": [f"{muMacAddress}"]}
        params = None
        if deleteHistory:
            params = {"deleteHistory": deleteHistory}
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["mudisassociate"],
                                           json=json_params, params=params)
        return resp

    def muReauthenticate(self, muMacAddress) -> requests.Response:
        """
        Re-authenticate a Mobile Unit.

        Args:
            muMacAddress (str): The MAC address of the Mobile Unit.

        Returns:
            requests.Response: The response from the server.
        """
        params = {"force_reauth": True}
        json_params = {muMacAddress: ""}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["muactions"],
                                           json=json_params, params=params)
        return resp


class Networks(Base):
    """
    Networks class for managing network-related operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Networks class.

        assignDefaultRoleByName(name: str, roleName: str, auth = False) -> requests.Response:
            Assign the default role to a network using the role name.

        assignDefaultTopoByName(name: str, topoName: str) -> requests.Response:
            Assign the default topology to a network using the topology name.

        create(name: str, ssid: str = None, privacy: PrivacyEnum = PrivacyEnum.open, passw: str = None, aaapolicyid = None) -> requests.Response:
            Create a new network with the specified parameters.

        createMeshPointNetwork(name: str, passw: str = None) -> requests.Response:
            Create a new mesh point network with the specified name and password.

        createPortal(network_name: str) -> requests.Response:
            Create a portal for the specified network.

        deleteMeshPointNetwork(name: str) -> requests.Response:
            Delete a mesh point network by its name.

        deleteMeshPointNetworkByID(id: str) -> requests.Response:
            Delete a mesh point network by its ID.

        deleteECPPortal(network_name: str) -> requests.Response:
            Delete the ECP portal for the specified network.

        getMeshPointNetworks():
            Retrieve all mesh point networks.

        getMeshPointsTreeById(id):
            Retrieve the mesh point tree by its ID.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Networks class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(Networks, self).__init__(client)
        self._id = 'id'
        self._path = 'networks'
        self._name = 'serviceName'

    class PrivacyEnum(str, Enum):
        """
        Enumeration for different network privacy settings.

        Attributes:
            open: Open network.
            wpa2_psk: WPA2-PSK security.
            wpa3_sae: WPA3-SAE security.
            wpa3_enterprise: WPA3-Enterprise security.
            wpa2_enterprise: WPA2-Enterprise security.
            OWE: Opportunistic Wireless Encryption.
            wpa3_enterprise_192: WPA3-Enterprise-192 security.
            wpa3_compatibility: WPA3-Compatibility mode.
        """
        open = "Open"
        wpa2_psk = "WPA2-PSK"
        wpa3_sae = "WPA3-SAE"
        wpa3_enterprise = "WPA3-Enterprise"
        wpa2_enterprise = "WPA2-Enterprise"
        OWE = "OWE"
        wpa3_enterprise_192 = "WPA3-Enterprise-192"
        wpa3_compatibility = "WPA3-Compatibility"

    def assignDefaultRoleByName(self, name: str, roleName: str, auth=False) -> requests.Response:
        """
        Assign the default role to a network using the role name.

        Args:
            name: The name of the network.
            roleName: The name of the role.
            auth: Boolean indicating if the role is for authenticated users (default is False).

        Returns:
            requests.Response: The response from the server.
        """
        netw = self.refresh().getByName(name)
        roleId = self.client.roles.refresh().getByName(roleName).id
        if auth:
            netw.authenticatedUserDefaultRoleID = roleId
        else:
            netw.unAuthenticatedUserDefaultRoleID = roleId
        resp = self.set(netw)
        return resp

    def assignDefaultTopoByName(self, name: str, topoName: str) -> requests.Response:
        """
        Assign the default topology to a network using the topology name.

        Args:
            name: The name of the network.
            topoName: The name of the topology.

        Returns:
            requests.Response: The response from the server.
        """
        netw = self.refresh().getByName(name)
        topoId = self.client.topologies.refresh().getByName(topoName).id
        netw.defaultTopology = topoId
        resp = self.set(netw)
        return resp

    def create(self, name: str, ssid: str = None, privacy: PrivacyEnum = PrivacyEnum.open,
               passw: str = None, aaapolicyid=None) -> requests.Response:
        """
        Create a new network with the specified parameters.

        Args:
            name: The name of the network.
            ssid: The SSID of the network (optional).
            privacy: The privacy setting of the network (default is open).
            passw: The password for the network (optional).
            aaapolicyid: The AAA policy ID (optional).

        Returns:
            requests.Response: The response from the server.
        """
        default = super(Networks, self).get('default', path=self._path)[0]
        default.serviceName = name
        default.ssid = name if ssid is None else ssid
        if privacy == self.PrivacyEnum.wpa3_enterprise:
            default.privacy = {'Wpa3EnterpriseElement': {'fastTransitionEnabled': False,
                                                         'fastTransitionMdId': 0}
                               }
        elif privacy == self.PrivacyEnum.wpa2_enterprise:
            default.privacy = {'WpaEnterpriseElement': {'mode': 'aesOnly', 'pmfMode': 'disabled',
                                                        'fastTransitionEnabled': True,
                                                        'fastTransitionMdId': 0}
                               }
        elif privacy == self.PrivacyEnum.wpa2_psk:
            passw = "abcd1234" if passw is None else passw
            default.privacy = {"WpaPskElement": {'mode': "aesOnly", 'pmfMode': "disabled",
                                                 'presharedKey': passw,
                                                 'keyHexEncoded': False}
                               }
        elif privacy == self.PrivacyEnum.wpa3_sae:
            passw = "abcd1234" if passw is None else passw
            default.privacy = {"WpaSaeElement": {'mode': "aesOnly", 'pmfMode': "required",
                                                 'presharedKey': passw,
                                                 'keyHexEncoded': False}
                               }
        elif privacy == self.PrivacyEnum.OWE:
            default.privacy = {"OweElement": {}
                               }
        elif privacy == self.PrivacyEnum.wpa3_enterprise_192:
            default.privacy = {
                'Wpa3Enterprise192bElement': {
                    'mode': "aesOnly",
                    'pmfMode': "required",
                    'fastTransitionEnabled': False,
                    'fastTransitionMdId': 0
                }
            }
            # When creating 192b encrypted network, the AAA policy ID must be specified at the time of creation.
            # 192b cannot take Local on-boarding as the default policy
            default.aaaPolicyId = aaapolicyid
        elif privacy == self.PrivacyEnum.wpa3_compatibility:
            passw = "abcd1234" if passw is None else passw
            default.privacy = {"WpaSaePskElement": {'pmfMode': "enabled",
                                                    'presharedKey': passw,
                                                    'keyHexEncoded': False}
                               }

        # set default nonauth and topology
        default.unAuthenticatedUserDefaultRoleID = self.client.EnterpriseUserId
        default.defaultTopology = self.client.bridgeAtAPId
        # create new Network
        resp = super(Networks, self).createCustom(default, path=self._path)
        return resp

    def createMeshPointNetwork(self, name: str, passw: str = None) -> requests.Response:
        """
        Create a new mesh point network with the specified name and password.

        Args:
            name: The name of the mesh point network.
            passw: The password for the mesh point network (optional).

        Returns:
            requests.Response: The response from the server.
        """
        default = super(Networks, self).get('default', path='meshpoints')[0]
        default.name = name
        default.meshId = name
        default.privacy['PskElement']['presharedKey'] = passw
        return super(Networks, self).createCustom(default, path='meshpoints')

    def createPortal(self, portal_name: str, network_name: str, ecp: bool = False) -> requests.Response:
        """
        Creates a portal for the specified network.

        Args:
            portal_name: The name of the portal.
            network_name: The name of the network.
            ecp: Is ECP URL provided. Defaults to False.

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest['portals'] if not ecp else self.client.rest['portals_ecp']
        params = {"name": portal_name} if not ecp else None
        resp = self.client.requestsWrapper(actionParams.PUT, f"{self.client.url}{path}/{network_name}", json=params)
        return resp

    def deleteMeshPointNetwork(self, name: str) -> requests.Response:
        """
        Delete a mesh point network by its name.

        Args:
            name: The name of the mesh point network.

        Returns:
            requests.Response: The response from the server.
        """
        meshpoint_networks = self.getMeshPointNetworks()
        networkId = [x for x in meshpoint_networks if x.name == name][0].id
        return super(Networks, self).delete(networkId, path='meshpoints')

    def deleteMeshPointNetworkByID(self, id: str) -> requests.Response:
        """
        Delete a mesh point network by its ID.

        Args:
            id: The ID of the mesh point network.

        Returns:
            requests.Response: The response from the server.
        """
        return super(Networks, self).delete(id, path='meshpoints')

    def deleteECPPortal(self, network_name: str) -> requests.Response:
        """
        Delete the ECP portal for the specified network.

        Args:
            network_name: The name of the network.

        Returns:
            requests.Response: The response from the server.
        """
        path = self.client.rest['portals_ecp']
        resp = self.client.requestsWrapper(actionParams.DELETE, f"{self.client.url}{path}/{network_name}")
        return resp

    def getMeshPointNetworks(self) -> List[one]:
        """
        Retrieve all mesh point networks.

        Returns:
            List[one]: A list of mesh point networks.
        """
        return super(Networks, self).get(path='meshpoints')

    def getMeshPointsTreeById(self, id) -> one:
        """
        Retrieve the mesh point tree by its ID.

        Args:
            id: The ID of the mesh point tree.

        Returns:
            one: The mesh point tree object.
        """
        return super(Networks, self).get(key=id, path='meshpointstree')


class Pcap(Base):
    """
    Pcap class for managing packet capture operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Pcap class.

        _start(capture: str, apSerial: str, wireless: bool = True, wired: bool = False, radio: str = 'All', direction: str = None, duration: int = None, macAddrListFilter: list = None, appliance: bool = False) -> one:
            Internal method to start the packet capture on the AP and pass all the filters.

        active() -> List[dict]:
            Show the packet captures in progress.

        packetCaptureFiles() -> requests.Response:
            Get the packet capture files.

        packetCaptureStatus() -> requests.Response:
            Get the packet capture status.

        startLocal(apSerial: str, wireless: bool = True, wired: bool = False, radio: str = 'All', direction: str = None, duration: int = None, macAddrListFilter: list = None, appliance: bool = False) -> one:
            Start a packet capture on the AP and store the pcap locally on the XCC.

        startScp(ip: str, user: str, passw: str, apSerial: str, wireless: bool = True, wired: bool = False, radio: str = 'All', appliance: bool = False) -> one:
            Start a packet capture on the AP and stream the pcap to the external SCP server.

        stop(id: str) -> requests.Response:
            Stop the ongoing packet capture by ID.

        stopByAp(apSerial: str) -> List[requests.Response]:
            Stop all ongoing packet captures for the specified AP serial number.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Pcap class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(Pcap, self).__init__(client)
        self._id = 'id'
        self._path = 'pcap'
        self._cache = {}

    def _start(self, capture: str, apSerial: str, wireless=True, wired=False, radio='All', direction=None,
               duration=None, macAddrListFilter=None, appliance=False) -> one:
        """
        Internal method to start the packet capture on the AP and pass all the filters.

        Args:
            capture (str): The capture dictionary.
            apSerial (str): The serial number of the AP.
            wireless (bool): Whether to capture on the wireless interface. Defaults to True.
            wired (bool): Whether to capture on the wired interface. Defaults to False.
            radio (str): The radio to capture on. Defaults to 'All'.
            direction (str, optional): The direction to capture (tx, rx, or both). Defaults to None.
            duration (int, optional): The duration of the capture in minutes. Defaults to None.
            macAddrListFilter (list, optional): A list of MAC addresses to filter the pcap. Defaults to None.
            appliance (bool): Whether to capture the interfaces on the XCC. Defaults to False.

        Returns:
            one: The capture object.
        """
        capture.apSerialNumber = apSerial
        capture.captureIf['wireless'] = wireless
        capture.captureIf['wired'] = wired
        capture.captureIf['appliance'] = appliance
        capture.captureIf['radio'] = radio  # 'All', 'Radio1', 'Radio2'

        if direction is not None:
            capture.captureIf['direction'] = direction

        if duration is not None:
            capture.duration = duration

        if macAddrListFilter is not None:
            capture.filter['macAddr'] = macAddrListFilter
        else:
            capture.filter['macAddr'] = []

        resp = self.createCustom(capture)
        m = resp.json()
        return one().fromDict(m), resp.status_code

    def active(self) -> List[dict]:
        """
        Show the packet captures in progress.

        Returns:
            List[dict]: A list of packet captures in progress.
        """
        return [c.__dict__ for c in self.get()]

    def packetCaptureFiles(self) -> requests.Response:
        """
        Get the packet capture files.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["packetcapturefiles"] + '?noCache=' + str(
                                               int(time.time() * 1000)))
        return resp

    def packetCaptureStatus(self) -> requests.Response:
        """
        Get the packet capture status.

        Returns:
            requests.Response: The response from the server.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[
            "packetcapturestatus"] + '?noCache=' + str(int(time.time() * 1000)))
        return resp

    def startLocal(self, apSerial: str, wireless=True, wired=False, radio='All', direction=None,
                   duration=None, macAddrListFilter=None, appliance=False) -> one:
        """
        Start a packet capture on the AP and store the pcap locally on the XCC.

        Args:
            apSerial (str): The serial number of the AP.
            wireless (bool): Whether to capture on the wireless interface. Defaults to True.
            wired (bool): Whether to capture on the wired interface. Defaults to False.
            radio (str): The radio to capture on. Defaults to 'All'.
            direction (str, optional): The direction to capture (tx, rx, or both). Defaults to None.
            duration (int, optional): The duration of the capture in minutes. Defaults to None.
            macAddrListFilter (list, optional): A list of MAC addresses to filter the pcap. Defaults to None.
            appliance (bool): Whether to capture the interfaces on the XCC. Defaults to False.

        Returns:
            one: The capture object.
        """
        capture = self.get("default")[0]
        delattr(capture, 'storage')  # work the bug in the API
        return self._start(capture, apSerial, wireless, wired, radio, direction, duration, macAddrListFilter, appliance)

    def startScp(self, ip: str, user: str, passw: str, apSerial: str) -> one:
        """
        Start a packet capture on the AP and stream the pcap to the external SCP server.

        Args:
            ip (str): The IP address of the SCP server.
            user (str): The username for the SCP server.
            passw (str): The password for the SCP server.
            apSerial (str): The serial number of the AP.

        Returns:
            one: The capture object.
        """
        capture = self.get("default")[0]
        capture.storage['ScpStorage']['ip'] = ip
        capture.storage['ScpStorage']['usernme'] = user
        capture.storage['ScpStorage']['password'] = passw
        return self._start(capture, apSerial, wireless=True, wired=False, radio='All')

    def stop(self, id) -> requests.Response:
        """
        Stop the ongoing packet capture by ID.

        Args:
            id (str): The ID of the packet capture to stop.

        Returns:
            requests.Response: The response from the server.
        """
        return self.delete(id)

    def stopByAp(self, apSerial) -> List[requests.Response]:
        """
        Stop all ongoing packet captures for the specified AP serial number.

        Args:
            apSerial (str): The serial number of the AP.

        Returns:
            List[requests.Response]: The responses from the server.
        """
        return [self.delete(c.id) for c in self.get() if c.apSerialNumber == apSerial]


class PcapFiles(Base):
    """
    PcapFiles class for managing packet capture files on the Appliance.

    Methods:
        __init__(client):
            Initialize the PcapFiles class.

        delAll() -> requests.Response:
            Delete all packet capture files.

        delBySerialNumber(apserial: str) -> requests.Response:
            Delete packet capture files by AP serial number.

        download(file: str) -> requests.Response:
            Download the specified packet capture file.

        get() -> List[dict]:
            Retrieve the list of packet capture files.
    """

    def __init__(self, client) -> None:
        """
        Initialize the PcapFiles class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(PcapFiles, self).__init__(client)
        self._id = 'filename'
        self._path = 'pcap_files'
        self._cache = {}

    def delAll(self) -> requests.Response:
        """
        Delete all packet capture files.

        Returns:
            requests.Response: The response from the server.
        """
        results = [self.delete(f.filename) for f in self.get()]
        return results

    def delBySerialNumber(self, apserial) -> requests.Response:
        """
        Delete packet capture files by AP serial number.

        Args:
            apserial (str): The serial number of the AP.

        Returns:
            requests.Response: The response from the server.
        """
        results = []
        for f in self.get():
            if apserial in f.filename:
                results.append(self.delete(f.filename))
        return results

    def download(self, file: str) -> requests.Response:
        """
        Download the specified packet capture file.

        Args:
            file (str): The name of the file to download.

        Returns:
            requests.Response: The response from the server.
        """
        file = quote(file)
        p = self.client.url + f"platformmanager/v3/packetcapture/files/{file}"

        resp = self.client.requestsWrapper(actionParams.GET, p, stream=True)
        if not resp.ok:
            print("failed")
            return resp.status_code

        with open(file, 'wb') as fd:
            for chunk in resp.iter_content(chunk_size=500):
                fd.write(chunk)

        return resp

    def get(self, key='all') -> List[dict]:
        """
        Retrieve the list of packet capture files.

        Returns:
            List[dict]: A list of packet capture files.
        """
        if key == 'all':
            return super(PcapFiles, self).get()
        else:
            return self.download(key).status_code


class PlatformMgr:
    """
    Platform Manager class for managing platform-related operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the PlatformMgr class with a client.

        addRadiusLogin(serverIp: str, nasIpAddress: str, nasIdentifier: str, authenticationType: str,
                       sharedSecret: str, priority: bool = False) -> requests.Response:
            Add radius server for login authentication.

        addRadiusLoginV2(self, aaaPolicyName: str, priority: bool = False) -> requests.Response:
            Add a RADIUS server for login authentication. From controller version 10.15 onward

        backupfileToLocal(id: str) -> requests.Response:
            Backup file to local storage.

        backupFtp(path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
            Backup using File Transfer Protocol.

        backupScp(path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
            Backup using Secure Copy Protocol.

        configureNtp(isNtpClient: str, ntpServer1: str, ntpServer2: str) -> requests.Response:
            Configure NTP settings.

        controllerRestart() -> requests.Response:
            Restart the operating system, platform software, and applications.

        controllerShutdown() -> requests.Response:
            Initiate a controlled shutdown.

        createAccount(userId, password, access=Access.READ_ONLY.value) -> requests.Response:
            Create an account in the controllers.

        createBackupFile(backupWhat: str, backupDestination: str) -> requests.Response:
            Create a backup file.

        createInterface(name: str, ipaddr: str, port: str, cidr: str, vlanId: str, tagged=False) -> requests.Response:
            Create a network interface.

        createRoute(gateWay: str, ipAddress, cidr: str) -> requests.Response:
            Create a network route.

        delete_tcpdumpfile(filename: str) -> requests.Response:
            Delete a TCP dump file.

        deleteAccount(username) -> requests.Response:
            Delete an account in the controllers.

        deleteBackupFile(filename: str) -> requests.Response:
            Delete a backup file.

        deleteImage(imageName) -> requests.Response:
            Delete an image.

        deleteInterface(name: str):
            Delete a network interface.

        deleteRadiusLogin() -> requests.Response:
            Delete radius login settings.

        deleteRoute(ipAddress: str) -> requests.Response:
            Delete a network route.

        download_tcpdumpfile(filename: str) -> requests.Response:
            Download a TCP dump file.

        get_tcpdumpfiles() -> requests.Response:
            Get a list of TCP dump files.

        getAccessEventsLog(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return Events Log.

        getAccounts() -> requests.Response:
            Get the current accounts in the controllers.

        getAdminPort() -> requests.Response:
            Get admin port settings.

        getAPEvLog(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return AP Event Log.

        getAuditLogs(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return Audit Logs.

        getAvailability() -> requests.Response:
            Get availability settings.

        getBackupFiles() -> requests.Response:
            Get a list of backup files.

        getControllerLimits() -> dict:
            Get platform manufacturing information.

        getDefaultGw() -> requests.Response:
            Get default gateway settings.

        getEvLog(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return Events Log.

        getHostAttributes() -> requests.Response:
            Get host attributes.

        getInterfaces() -> requests.Response:
            Get network interfaces.

        getL2Ports() -> requests.Response:
            Get L2 ports.

        getLicenseStatus() -> requests.Response:
            Get the system environment information.

        getNtp() -> requests.Response:
            Get NTP settings.

        getNtpStatus() -> requests.Response:
            Get NTP status.

        getRadiusLoginV2(self) -> requests.Response:
            Get RADIUS login settings. From controller version 10.15 onward

        getRoutes() -> requests.Response:
            Get a list of network routes.

        getSmartRfLog(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return Smart RF Log.

        getStationEvLog(lastDay=1, lastH=0, lastMin=0) -> requests.Response:
            Return Station Event Log.

        getSystemEnv() -> requests.Response:
            Get the system environment information.

        getSysLog() -> requests.Response:
            Get system log.

        getSysLogv2() -> requests.Response:
            Get system log v2.

        getSystemLogLevel() -> requests.Response:
            Get system log level.

        getSystemTime() -> requests.Response:
            Get the current system time.

        getTimeZone() -> requests.Response:
            Get the current time zone.

        getWebSessionTimeout() -> requests.Response:
            Get the current web session timeout.

        getWebViewCredentials() -> requests.Response:
            Get web view credentials.

        l2PortStats() -> requests.Response:
            Get statistics for all L2 ports.

        localUpgrade(imageName: str) -> requests.Response:
            Perform a local upgrade.

        networkhealth() -> requests.Response:
            Get network health status.

        ping(targetIPAddress: str, sourceInterface: str, specificInterface: bool = True) -> requests.Response:
            Ping a target IP address.

        radiusLoginTest(aaaPolicyName: str, username: str, password: str) -> requests.Response:
            Test RADIUS login settings.

        resetToDefaults() -> requests.Response:
            Reset to defaults.

        restorefile(id: str) -> requests.Response:
            Restore file from backup.

        restoreFtp(path: str, fileName: str, ip: str, user: str, passw: str, local_destination: str = "local") -> requests.Response:
            Restore using File Transfer Protocol.

        restoreScp(path: str, fileName: str, ip: str, user: str, passw: str, local_destination: str = "local") -> requests.Response:
            Restore using Secure Copy Protocol.

        setAvailability(onOff: bool, role: str, pairIP: str, balanceAP: bool, secureConnection: bool = False,
                        staticMtu: int = 1500) -> requests.Response:
            Set availability settings.

        setDefaultGateway(default_gateway):
            Set default gateway.

        setHostAttributes(hostname, domain_name, dns_server1, dns_server2="8.8.8.8"):
            Set host attributes.

        setL2Ports(L2PortsInfo):
            Set L2 ports.

        setMgmtInterface(self, name: str, setmgmt=True):
            Set the management interface.

        setSysLogConfigurationV2(server_list, auditFacility, stationEventFacility, msgFacility, eventFacility, varLog=True, auditLog=True, stationEvent=True):
            Set the syslog configuration with the provided details.

        setSystemLogLevel(loglevel, trap):
            Set system log level.

        setSystemTime(data) -> requests.Response:
            Set the system time.

        setTimeZone(timezone) -> requests.Response:
            Set the time zone.

        showImages() -> requests.Response:
            Show available images.

        showVersion() -> requests.Response:
            Show the version of the product.

        setWebSessionTimeout() -> requests.Response:
            Set web session timeout.

        setWebViewPassword() -> requests.Response:
            Set the password for web view credentials.

        tcpdump_start(size: int, filename: str, interface: str, destination="local") -> requests.Response:
            Start a TCP dump.

        tcpdump_stop() -> requests.Response:
            Stop a TCP dump.

        traceroute(targetIPAddress: str, sourceInterface: str, specificInterface: bool = True) -> requests.Response:
            Traceroute to a target IP address.

        updateAccount(self, userId, password=None, **access) -> requests.Response:
            Update an account in the controller.

        updateControllerIP(self, new_ip: str) -> requests.Response:
            Update the controller's IP address.

        updateInterface(interface_name: str, **kwargs) -> requests.Response:
            Update a network interface.

        upgradeFtp(path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
            Upgrade using FTP.

        upgradeScp(path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
            Upgrade the Secure Copy Protocol.
    """

    def __init__(self, client):
        """
        Initialize the PlatformMgr class.

        Args:
            client: The client to use for operations.
        """
        self.client = client

    class Access(Enum):
        """
        Enumeration for different access levels.

        Attributes:
            READ_ONLY (str): Represents read-only access.
            FULL (str): Represents full access.
        """
        READ_ONLY = "RO"
        FULL = "RW"

    class LogLevelEnum(Enum):
        """
        Enumeration for different log levels.

        Attributes:
            INFO (str): Represents the informational log level.
            MINOR (str): Represents the minor log level.
            MAJOR (str): Represents the major log level.
            CRITICAL (str): Represents the critical log level.
        """
        INFO = "info"
        MINOR = "minor"
        MAJOR = "major"
        CRITICAL = "critical"

    class TrapLevelEnum(Enum):
        """
        Enumeration for different trap levels.

        Attributes:
            ENABLE (bool): Represents the enabled trap level.
            DISABLE (bool): Represents the disabled trap level.
        """
        ENABLE = True
        DISABLE = False

    def addRadiusLogin(self, serverIp: str, nasIpAddress: str, nasIdentifier: str, authenticationType: str,
                       sharedSecret: str, priority: bool = False) -> requests.Response:
        """
        Add a RADIUS server for login authentication.

        Args:
            serverIp (str): The IP address of the RADIUS server.
            nasIpAddress (str): The NAS IP address.
            nasIdentifier (str): The NAS identifier.
            authenticationType (str): The authentication type. can be PAP, CHAP, MSCHAP, MSCHAP2
            sharedSecret (str): The shared secret.
            priority (bool): If True, RADIUS is given priority over local authentication.
                If False (default), local authentication is given priority over RADIUS authentication.

        Returns:
             requests.Response: The response from the RADIUS login add operation.
        """
        rad_list_params = {
            "authenticationRetryCount": 1,
            "authenticationTimeout": 2,
            "authenticationType": authenticationType,
            "authorizationClientPort": 1812,
            "nasIdentifier": nasIdentifier,
            "nasIpAddress": nasIpAddress,
            "serverIp": serverIp,
            "sharedSecret": sharedSecret
        }

        loginAuthPriorityList = ["local", "radius"] if not priority else ["radius", "local"]

        params = {
            "loginAuthMode": loginAuthPriorityList,
            "radiusList": [rad_list_params]
        }

        resp = self.client.requestsWrapper(actionParams.PUT,
                                           f"{self.client.url}{self.client.rest['radiusLogin']}",
                                           json=params)
        return resp

    def addRadiusLoginV2(self, aaaPolicyName: str, priority: bool = False) -> requests.Response:
        """
        Add a RADIUS server for login authentication. From controller version 10.15 onward

        Args:
            aaaPolicyName (str): The name of the AAA policy.
            priority (bool): If True, RADIUS is given priority over local authentication.
                If False (default), local authentication is given priority over RADIUS authentication.

        Returns:
             requests.Response: The response from the RADIUS login add operation.
        """
        loginAuthPriorityList = ["local", "radius"] if not priority else ["radius", "local"]

        aaaPolicyObj = self.client.aaapolicy.refresh().getByName(aaaPolicyName)
        if aaaPolicyObj:
            aaaPolicyId = aaaPolicyObj.id
        else:
            raise ValueError(f"AAA Policy with name '{aaaPolicyName}' not found.")

        params = {
            "loginAuthMode": loginAuthPriorityList,
            "aaaPolicyId": aaaPolicyId
        }

        resp = self.client.requestsWrapper(actionParams.PUT,
                                           f"{self.client.url}{self.client.rest['radiusLoginV2']}",
                                           json=params)
        return resp

    def backupfileToLocal(self, id: str) -> requests.Response:
        """
        Backup file to local storage.

        Args:
            id (str): The ID of the file to backup.

        Returns:
            requests.Response: The response from the backup operation.
        """
        params = {"id": id}
        resp = self.client.requestsWrapper(actionParams.PUT,
                                           f"{self.client.url}{self.client.rest['backupfileToLocal']}/{id}",
                                           json=params)
        return resp

    def backupFtp(self, path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
        """
        Backup using File Transfer Protocol.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.

        Returns:
            requests.Response: The response from the backup operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ftpBackupTo"],
                                           json=params)
        return resp

    def backupScp(self, path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
        """
        Backup using Secure Copy Protocol.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.

        Returns:
            requests.Response: The response from the backup operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["scpBackupTo"],
                                           json=params)
        return resp

    def configureNtp(self, isNtpClient: str, ntpServer1: str, ntpServer2: str) -> requests.Response:
        """
        Configure NTP settings.

        Args:
            isNtpClient (str): Flag to indicate if NTP client is enabled.
            ntpServer1 (str): The primary NTP server.
            ntpServer2 (str): The secondary NTP server.

        Returns:
            requests.Response: The response from the configure operation.
        """
        if ntpServer1 is not None and ntpServer2 is not None:
            params = {"isNtpClient": isNtpClient, "remoteTimeServers": [ntpServer1, ntpServer2]}
        elif ntpServer1 is not None:
            params = {"isNtpClient": isNtpClient, "remoteTimeServers": [ntpServer1]}
        elif ntpServer2 is not None:
            params = {"isNtpClient": isNtpClient, "remoteTimeServers": [ntpServer2]}
        else:
            params = {"isNtpClient": isNtpClient, "remoteTimeServers": []}

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ntp"], json=params)
        return resp

    def controllerRestart(self) -> requests.Response:
        """
        Restart the operating system, platform software, and applications.

        Returns:
            requests.Response: The response from the restart operation.
        """
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["restart"])
        return resp

    def controllerShutdown(self) -> requests.Response:
        """
        Initiate a controlled shutdown.

        Returns:
            requests.Response: The response from the shutdown operation.
        """
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["shutdown"])
        return resp

    def createAccount(self, userId, password, access=Access.READ_ONLY.value) -> requests.Response:
        """
        Create an account in the controllers.

        Args:
            userId (str): The user ID for the new account.
            password (str): The password for the new account.
            access (str, optional): The access level for the new account. Default is Access.READ_ONLY.value.

        Returns:
            requests.Response: The response from the create operation.
        """
        keys = ["account", "adoption", "application", "cliSupport", "deviceAp", "deviceSwitch", "eGuest", "license",
                "network", "onboardAaa", "onboardCp", "onboardGroupsAndRules", "onboardGuestCp", "platform", "site",
                "troubleshoot"]
        scopes = dict.fromkeys(keys, access)

        payload = {
            "accountState": "ENABLED",
            "adminRole": "READ_ONLY",  # this is different from `access`. `adminRole` is always `READ_ONLY`
            "userId": userId,
            "password": password,
            "scopes": scopes,
            "custId": None
        }

        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["administrators"],
                                           json=payload)
        return resp

    def createBackupFile(self, backupWhat: str, backupDestination: str) -> requests.Response:
        """
        Create a backup file.

        Args:
            backupWhat (str): The data to backup.
            backupDestination (str): The destination for the backup.

        Returns:
            requests.Response: The response from the create operation.
        """
        params = {"backupWhat": backupWhat, "backupDestination": backupDestination}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["createbackup"],
                                           json=params)
        return resp

    def createInterface(self, name: str, ipaddr: str, port: str, cidr: str, vlanId: str,
                        tagged=False) -> requests.Response:
        """
        Create a network interface.

        Args:
            name (str): The name of the interface.
            ipaddr (str): The IP address of the interface.
            port (str): The port of the interface.
            cidr (str): The CIDR of the interface.
            vlanId (str): The VLAN ID of the interface.
            tagged (bool): Flag to indicate if the interface is tagged.

        Returns:
            requests.Response: The response from the create operation.
        """
        params = {"custId": "", "id": "", "name": name, "vlanId": vlanId, "tagged": tagged, "mode": "Physical",
                  "mtu": 1500, "allowManagementTraffic": True, "layer3": True, "ipAddress": ipaddr, "cidr": cidr,
                  "dhcpMode": "DHCPNone", "cert": 0, "certCa": 0, "port": port,
                  "localDhcp": {"custId": None, "id": None, "domainName": None, "defaultLease": 36000,
                                "maxLease": 2592000, "dnsServers": None, "wins": None, "gateway": None,
                                "rangeFrom": None, "rangeTo": None}, "dhcpServers": "", "apRegistration": False}
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["interfaces"],
                                           json=params)
        return resp

    def createRoute(self, gateWay: str, ipAddress, cidr: str) -> requests.Response:
        """
        Create a network route.

        Args:
            gateWay (str): The gateway for the route.
            ipAddress: The IP address for the route.
            cidr (str): The CIDR for the route.

        Returns:
            requests.Response: The response from the create operation.
        """
        params = {"gateWay": gateWay, "ipAddress": ipAddress, "cidr": cidr}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["routes"] + "/route",
                                           json=params)
        return resp

    def delete_tcpdumpfile(self, filename: str) -> requests.Response:
        """
        Delete a TCP dump file.

        Args:
            filename (str): The name of the file to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest["tcpdump"] + "file" + f"/{filename}")
        return resp

    def deleteAccount(self, username) -> requests.Response:
        """
        Delete an account in the controllers.

        Args:
            username (str): The username of the account to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + self.client.rest["administrators"] +
                                           "/" + username)
        return resp

    def deleteBackupFile(self, filename: str) -> requests.Response:
        """
        Delete a backup file.

        Args:
            filename (str): The name of the file to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest["delbackupfile"] + "/" + filename)
        return resp

    def deleteImage(self, imageName) -> requests.Response:
        """
        Delete an image.

        Args:
            imageName: The name of the image to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest["delImage"] + "/" + imageName)
        return resp

    def deleteInterface(self, name: str) -> requests.Response:
        """
        Delete a network interface.

        Args:
            name (str): The name of the interface to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        if_list = json.loads(self.getInterfaces().content)
        resp = None
        for interface in if_list:
            if name == interface['name']:
                resp = self.client.requestsWrapper(actionParams.DELETE,
                                                   self.client.url + self.client.rest["interfaces"] + '/' + interface[
                                                       'id'])

                break
        return resp

    def deleteRadiusLogin(self) -> requests.Response:
        """
        Delete RADIUS login settings.

        Returns:
            requests.Response: The response from the delete operation.
        """
        params = {
            "loginAuthMode": ["local"],
        }

        resp = self.client.requestsWrapper(actionParams.PUT,
                                           f"{self.client.url}{self.client.rest['radiusLogin']}",
                                           json=params)
        return resp

    def deleteRoute(self, ipAddress: str) -> requests.Response:
        """
        Delete a network route.

        Args:
            ipAddress (str): The IP address of the route to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest["routes"] + "/route/" + ipAddress)
        return resp

    def download_tcpdumpfile(self, filename: str) -> requests.Response:
        """
        Download a TCP dump file.

        Args:
            filename (str): The name of the file to download.

        Returns:
            requests.Response: The response from the download operation.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["tcpdump"] + "file" + f"/{filename}")
        return resp

    def get_tcpdumpfiles(self) -> requests.Response:
        """
        Get a list of TCP dump files.

        Returns:
            requests.Response: The response containing the list of TCP dump files.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["tcpdump"] + "files")
        return resp

    def getAccessEventsLog(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return Events Log.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the access event log.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["accesseventslog"],
                                           params={"startTime": s, "endTime": e})
        return resp

    def getAccounts(self) -> requests.Response:
        """
        Get the current accounts in the controllers.

        Returns:
            requests.Response: The response containing the list of accounts.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["administrators"])
        return resp

    def getAdminPort(self) -> requests.Response:
        """
        Get admin port settings.

        Returns:
            requests.Response: The response containing the admin port settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["admin"])
        return resp

    def getAPEvLog(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return AP Event Log.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the AP event log.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["aplog"],
                                           params={"startTime": s, "endTime": e})
        return resp

    def getAuditLogs(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return Audit Logs.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the audit logs.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["auditlogs"] + "/query?",
                                           params={"startTime": s, "endTime": e})
        return resp


    def getAvailability(self) -> requests.Response:
        """
        Get availability settings.

        Returns:
            requests.Response: The response containing the availability settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["availability"])
        return resp

    def getBackupFiles(self) -> requests.Response:
        """
        Get a list of backup files.

        Returns:
            requests.Response: The response containing the list of backup files.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["getbackuplist"])
        return resp

    def getControllerLimits(self) -> dict:
        """
        Get platform manufacturing information.

        Returns:
            dict: A dictionary containing platform model, maximum number of supported APs and clients.
        """
        platform_dict = {
            # keyword = platform model, value = [SA max number of APs, SA max number of clients, HA max number of APs, HA max number of clients]
            'VE6120-Small': [50, 1000, 100, 2000],
            'VE6120-Medium': [250, 4000, 500, 8000],
            'VE6120-Large': [500, 8000, 1000, 16000],
            'VE6120H-Small': [50, 1000, 100, 2000],
            'VE6120H-Medium': [250, 4000, 500, 8000],
            'VE6120H-Large': [500, 8000, 1000, 16000],
            'VE6120K-Small': [50, 1000, 100, 2000],
            'VE6120K-Medium': [250, 4000, 500, 8000],
            'VE6120K-Large': [500, 8000, 1000, 16000],
            'VE6125': [2000, 16000, 4000, 32000],
            'VE6125K-XL': [2000, 16000, 4000, 32000],
            'E3125': [10000, 50000, 20000, 100000],
            'E3120': [10000, 50000, 20000, 100000],
            'E2120': [2000, 16000, 4000, 32000],
            'E2122': [2000, 16000, 4000, 32000],
            'E1120': [250, 2000, 500, 4000],
        }

        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["manufacturing_info"])

        result = resp.json()['result'].split("\n")
        model = "default"
        max_aps_sa = 0
        max_clients_sa = 0
        max_aps_ha = 0
        max_clients_ha = 0
        for r in result:
            if "Model" in r:
                model = r.split(": ")[1].replace(" ", "-")
                break

        if model != "default":
            if model in platform_dict:
                max_aps_sa = platform_dict[model][0]
                max_clients_sa = platform_dict[model][1]
                max_aps_ha = platform_dict[model][2]
                max_clients_ha = platform_dict[model][3]

        resp_json_orig = resp.json()
        resp_json_orig.update({
            'model': model,
            'max_aps_sa': max_aps_sa,
            'max_clients_sa': max_clients_sa,
            'max_aps_ha': max_aps_ha,
            'max_clients_ha': max_clients_ha,
        })

        return resp_json_orig if resp.ok else None

    def getDefaultGw(self) -> requests.Response:
        """
        Get default gateway settings.

        Returns:
          requests.Response: The response containing the default gateway settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["defaultgateway"])
        return resp

    def getEvLog(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return Events Log.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the event logs.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["eventslog"],
                                           params={"startTime": s, "endTime": e})
        return resp

    def getHostAttributes(self) -> requests.Response:
        """
        Get host attributes.

        Returns:
            requests.Response: The response containing the host attributes.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["hostattributes"])
        return resp

    def getInterfaces(self) -> requests.Response:
        """
        Get network interfaces.

        Returns:
            requests.Response: The response containing the network interfaces.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["getInterfaces"])
        return resp

    def getL2Ports(self) -> requests.Response:
        """
        Get L2 ports information.

        Returns:
            requests.Response: The response containing the L2 ports information.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["l2ports"])
        return resp

    def getLicenseStatus(self) -> requests.Response:
        """
        Get the system environment information.

        Returns:
            requests.Response: The response containing the license status.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["softwareActivationReport"])
        return resp

    def getNtp(self) -> requests.Response:
        """
        Get NTP settings.

        Returns:
            requests.Response: The response containing the NTP settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["ntp"])
        return resp

    def getNtpStatus(self) -> requests.Response:
        """
        Get NTP status.

        Returns:
            requests.Response: The response containing the NTP status.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["ntpStatus"])
        return resp

    def getRadiusLoginV2(self) -> requests.Response:
        """
        Get RADIUS server login settings. From the controller version 10.15 onward

        Returns:
             requests.Response: The response containing the RADIUS login settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           f"{self.client.url}{self.client.rest['radiusLoginV2']}")
        return resp

    def getRoutes(self) -> requests.Response:
        """
        Get a list of network routes.

        Returns:
            requests.Response: The response containing the list of network routes.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest["routes"] + "/allroutes")
        return resp

    def getSmartRfLog(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return Smart RF Log.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the Smart RF log.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["smartrflog"],
                                           params={"startTime": s, "endTime": e})
        return resp

    def getStationEvLog(self, lastDay=1, lastH=0, lastMin=0) -> requests.Response:
        """
        Return Station Event Log.

        Args:
            lastDay (int, optional): Number of days to look back. Default is 1.
            lastH (int, optional): Number of hours to look back. Default is 0.
            lastMin (int, optional): Number of minutes to look back. Default is 0.

        Returns:
            requests.Response: The response containing the station event log.
        """
        e = datetime.now()
        s = e - timedelta(days=lastDay, seconds=0, microseconds=0,
                          milliseconds=0, minutes=lastMin,
                          hours=lastH, weeks=0)
        e = int(e.timestamp() * 1000)
        s = int(s.timestamp() * 1000)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["stationlog"],
                                           params={"startTime": s, "endTime": e})
        return resp

    def getSystemEnv(self) -> requests.Response:
        """
        Retrieve the system environment information.

        Returns:
            requests.Response: The response containing the system environment information.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["productenv"])
        return resp

    def getSysLog(self) -> requests.Response:
        """
        Retrieve the syslog configuration from the syslog data.

        Returns:
            requests.Response: The syslog configuration if the request is successful, otherwise None.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["syslog"])
        return resp

    def getSysLogv2(self) -> requests.Response:
        """
        Retrieve the syslog configuration (version 2) from the syslog data.

        Returns:
            requests.Response: The syslog configuration if the request is successful, otherwise None.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["syslogv2"])
        return resp

    def getSystemLogLevel(self) -> requests.Response:
        """
        Get the system log level.

        Returns:
            requests.Response: The response containing the system log level.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["logLevel"])
        return resp

    def getSystemTime(self) -> requests.Response:
        """
        Get the current system time.

        Returns:
            requests.Response: The response containing the system time.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["systemtime"])
        return resp

    def getTimeZone(self) -> requests.Response:
        """
        Get the current time zone.

        Returns:
            requests.Response: The response containing the time zone.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["timezone"])
        return resp

    def getWebSessionTimeout(self) -> requests.Response:
        """
        Get the current web session timeout.

        Returns:
            requests.Response: The response containing the web session timeout values.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["websessiontimeout"])
        return resp

    def getWebViewCredentials(self) -> requests.Response:
        """
        Get web view credentials.

        Returns:
            requests.Response: The response containing the web view credentials.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["diagnosticcredentials"])
        return resp

    def l2PortStats(self) -> requests.Response:
        """
        Get statistics for all L2 ports.

        Returns:
            requests.Response: The response containing the L2 port statistics.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["l2stats"])
        return resp

    def localUpgrade(self, imageName: str) -> requests.Response:
        """
        Perform a local upgrade.

        Args:
            imageName (str): The name of the image to upgrade.

        Returns:
            requests.Response: The response from the upgrade operation.
        """
        params = {"id": "none", "id2": imageName}
        resp = self.client.requestsWrapper(actionParams.PUT,
                                           self.client.url + self.client.rest["localupgrade"] + "/" + imageName,
                                           json=params)
        return resp

    def networkhealth(self) -> requests.Response:
        """
        Get network health status.

        Returns:
            requests.Response: The response containing the network health status.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["network_health"])
        return resp

    def ping(self, targetIPAddress: str, sourceInterface: str, specificInterface: bool = True) -> requests.Response:
        """
        Ping a target IP address.

        Args:
            targetIPAddress (str): The target IP address to ping.
            sourceInterface (str): The source interface for the ping.
            specificInterface (bool, optional): Flag to indicate if a specific interface is used. Default is True.

        Returns:
            requests.Response: The response from the ping operation.
        """
        params = {"specificInterface": specificInterface, "targetIPAddress": targetIPAddress,
                  "sourceInterface": sourceInterface}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ping"], json=params)
        return resp

    def radiusLoginTest(self, aaaPolicyName: str, username: str, password: str) -> requests.Response:
        """
        Do RADIUS server login test. From the controller version 10.15 onward

        Args:
            aaaPolicyName (str): The name of the AAA policy to use for the test.
            username (str): The username for the RADIUS login test.
            password (str): The password for the RADIUS login test.

        Returns:
             requests.Response: The response from the RADIUS login test operation.
        """
        aaaPolicyId = self.client.aaapolicy.refresh().getByName(aaaPolicyName).id
        payload = {
            "aaaPolicyId": aaaPolicyId,
            "username": username,
            "password": password
        }
        resp = self.client.requestsWrapper(actionParams.POST,
                                           f"{self.client.url}{self.client.rest['radiusLoginV2']}/test",
                                           json=payload)
        return resp

    def resetToDefaults(self) -> requests.Response:
        """
        Reset to default settings.

        Returns:
            requests.Response: The response from the reset operation.
        """
        params = {"license": False, "mgmtport": False}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["resetToDefaults"],
                                           json=params)
        return resp

    def restorefile(self, id: str) -> requests.Response:
        """
        Restore file from backup.

        Args:
            id (str): The ID of the file to restore.

        Returns:
            requests.Response: The response from the restore operation.
        """
        params = {"id": id}
        resp = self.client.requestsWrapper(actionParams.PUT, f"{self.client.url}{self.client.rest['restorefile']}/{id}",
                                           json=params)
        return resp

    def restoreFtp(self, path: str, fileName: str, ip: str, user: str, passw: str, local_destination: str = "local") -> requests.Response:
        """
        Restore using File Transfer Protocol.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.
            local_destination (str): The local destination for the restored file. Default is "local". Options: "local", "flash".

        Returns:
            requests.Response: The response from the restore operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user,
                  "localDestination": local_destination}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ftpRestoreFrom"],
                                           json=params)
        return resp

    def restoreScp(self, path: str, fileName: str, ip: str, user: str, passw: str, local_destination: str = "local") -> requests.Response:
        """
        Restore using Secure Copy Protocol.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.
            local_destination (str): The local destination for the restored file. Default is "local". Options: "local", "flash".

        Returns:
            requests.Response: The response from the restore operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user,
                  "localDestination": local_destination}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["scpRestoreFrom"],
                                           json=params)
        return resp


    def setAvailability(self, onOff: bool, role: str, pairIP: str, balanceAP: bool, secureConnection: bool = False,
                        staticMtu: int = 1500) -> requests.Response:
        """
        Set availability settings.

        Args:
            onOff (bool): Flag to turn availability on or off.
            role (str): The role for availability.
            pairIP (str): The IP address of the pair.
            balanceAP (bool): Flag to balance AP.
            secureConnection (bool): Flag to enable secure connection. Default is False.
            staticMtu (int): The static MTU value. Default is 1500.
        Returns:
            requests.Response: The response from the set operation.
        """
        params = {
            "availabilityEnabled": onOff,
            "availabilityRole": role,
            "availabilityPairAddr": pairIP,
            "balanceAps": balanceAP,
            "secureConnection": secureConnection,
            "staticMtu": staticMtu
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["availability"],
                                           json=params)
        return resp

    def setDefaultGateway(self, default_gateway) -> requests.Response:
        """
        Set the default gateway.

        Args:
            default_gateway (str): The IP address of the default gateway.

        Returns:
            requests.Response: The response from the set operation.
        """
        params = {
            "ipv4Address": default_gateway
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["defaultgateway"],
                                           json=params)
        return resp

    def setHostAttributes(self, hostname, domain_name, dns_server1, dns_server2="8.8.8.8") -> requests.Response:
        """
        Set host attributes.

        Args:
            hostname: The host name.
            domain_name: The domain name.
            dns_server1: The primary DNS server.
            dns_server2: The secondary DNS server (default is "8.8.8.8").
         Returns:
            requests.Response: The response from the set operation.
        """
        params = {
            "dnsServers": [dns_server1, dns_server2],
            "domainName": domain_name,
            "hostName": hostname
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["hostattributes"],
                                           json=params)
        return resp

    def setL2Ports(self, L2PortsInfo) -> requests.Response:
        """
        Update L2 ports information.

        Args:
            L2PortsInfo (dict): A dictionary containing the L2 ports information to be updated.

        Returns:
            requests.Response: The response from the update operation.
        """
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["l2ports"],
                                           json=L2PortsInfo)
        return resp

    def setMgmtInterface(self, name: str, setmgmt=True) -> requests.Response:
        """
        Set management interface.

        Args:
            name (str): The name of the interface.
            setmgmt (bool): Flag to set management interface.

        Returns:
            requests.Response: The response from the set operation.
        """
        if_list = json.loads(self.getInterfaces().content)
        resp = None
        for interface in if_list:
            if name == interface['name']:
                interface["allowManagementTraffic"] = setmgmt
                resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["interfaces"],
                                                   json=interface)
                break
        return resp

    """ commenting out for now as this is for older version"""
    """ might need in feature so not modifying it"""
    """
    def setSysLogConfiguration(self, payload):
        "sets the syslog server ip"
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["syslog"],
                                           json=payload)
        return resp
   """

    def setSysLogConfigurationV2(self, server_list, auditFacility, stationEventFacility, msgFacility, eventFacility,
                                 varLog=True, auditLog=True, stationEvent=True) -> requests.Response:
        """
        Set the syslog configuration with the provided details.

        Args:
            server_list (list): List of syslog servers.
            auditFacility (str): Facility for audit logs.
            stationEventFacility (str): Facility for station event logs.
            msgFacility (str): Facility for message logs.
            eventFacility (str): Facility for event logs.
            varLog (bool, optional): Flag to enable/disable var log. Default is True.
            auditLog (bool, optional): Flag to enable/disable audit log. Default is True.
            stationEvent (bool, optional): Flag to enable/disable station event log. Default is True.

        Returns:
            requests.Response: The response from the set operation.
        """
        syslog_payload = {
            'syslogServers': server_list,
            'msgToSend': {
                'varLog': varLog,
                'auditLog': auditLog,
                'stationEvent': stationEvent
            },
            'facility': {
                'audit': auditFacility,
                'stationEvent': stationEventFacility,
                'msg': msgFacility,
                'event': eventFacility
            }
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["syslogv2"],
                                           json=syslog_payload)
        return resp

    def setSystemLogLevel(self, loglevel: LogLevelEnum = LogLevelEnum.INFO, trap: TrapLevelEnum = TrapLevelEnum.ENABLE) -> requests.Response:
        """
        Set the system log level.

        Args:
            loglevel (LogLevelEnum): The log level to set. Default is LogLevelEnum.INFO.
            trap (TrapLevelEnum): The trap level to set. Default is TrapLevelEnum.ENABLE.

        Returns:
            requests.Response: The response from the set operation.
        """
        payload = {
            "logLevel": loglevel.value,
            "sendStationEventTrap": trap.value
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["logLevel"],
                                           json=payload)
        return resp

    def setSystemTime(self, data) -> requests.Response:
        """
        Set the system time.

        Args:
            data (dict): The data to set the system time.

        Returns:
            requests.Response: The response from the set operation.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["ntp"])
        if resp.ok:
            remoteTimeServers = resp.json()['remoteTimeServers']
            payload = {
                "isNtpClient": False,
                "remoteTimeServers": remoteTimeServers
            }

            resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ntp"], json=payload)
            if resp.ok:
                resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["systemtime"],
                                               json=data)
        return resp

    def setTimeZone(self, timezone) -> requests.Response:
        """
        Set the time zone.

        Args:
            timezone (str): The time zone to set.

        Returns:
            requests.Response: The response from the set operation.
        """
        payload = {"timeZone": timezone}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["timezone"],
                                           json=payload)
        return resp

    def setWebSessionTimeout(self, hour: int, minute: int) -> requests.Response:
        """
        Set the web session timeout.

        Args:
            hour (int): The hour for the timeout.
            minute (int): The minute for the timeout.

        Returns:
            requests.Response: The response from the set operation.
        """
        payload = {
            "hour": hour,
            "minute": minute
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["websessiontimeout"],
                                           json=payload)
        return resp

    def setWebViewPassword(self, password: str) -> requests.Response:
        """
        Set the web view password.

        Args:
            password (str): The new password for web view.

        Returns:
            requests.Response: The response from the set operation.
        """
        payload = {
            "username": "admin",
            "password": password
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["diagnosticcredentials"],
                                           json=payload)
        return resp

    def showImages(self) -> requests.Response:
        """
        Show available images.

        Returns:
            requests.Response: The response containing the list of images.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["getImages"])
        return resp

    def showVersion(self) -> requests.Response:
        """
        Show the version of the product.

        Returns:
            requests.Response: The response containing the version information.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["version"])
        return resp

    def tcpdump_start(self, size: int, filename: str, interface: str, destination="local") -> requests.Response:
        """
        Start a TCP dump.

        Args:
            size (int): The size of the dump.
            filename (str): The name of the dump file.
            interface (str): The interface to capture.
            destination (str): The destination for the dump.

        Returns:
            requests.Response: The response from the start operation.
        """
        params = {
            "captureFileMaxMegabytes": size,
            "captureFileName": filename,
            "destination": destination,
            "sourceInterface": interface
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["tcpdump"], json=params)
        return resp

    def tcpdump_stop(self) -> requests.Response:
        """
        Stop a TCP dump.

        Returns:
            requests.Response: The response from the stop operation.
        """
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["tcpdump"] + "/stop")
        return resp

    def traceroute(self, targetIPAddress: str, sourceInterface: str, specificInterface: bool = True) -> requests.Response:
        """
        Traceroute to a target IP address.

        Args:
            targetIPAddress (str): The target IP address to traceroute.
            sourceInterface (str): The source interface for the traceroute.
            specificInterface (bool, optional): Flag to indicate if a specific interface is used. Default is True.

        Returns:
            requests.Response: The response from the traceroute operation.
        """
        params = {"specificInterface": specificInterface, "targetIPAddress": targetIPAddress,
                  "sourceInterface": sourceInterface}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["traceroute"],
                                           json=params)
        return resp

    def updateAccount(self, userId, password=None, **access) -> requests.Response:
        """
        Update an account's password and/or access.

        Args:
            userId (str): The user ID for the account.
            password (str, optional): The password for the account if it needs to be changed.
            access (str, optional): The access level for the new account. Default is Access.READ_ONLY.value.

        Returns:
            requests.Response: The response from the update operation.
        """
        keys = ["account", "adoption", "application", "cliSupport", "deviceAp", "deviceSwitch", "eGuest", "license",
                "network", "onboardAaa", "onboardCp", "onboardGroupsAndRules", "onboardGuestCp", "platform", "site",
                "troubleshoot"]

        resp = self.client.requestsWrapper(actionParams.GET,
                                                  self.client.url + self.client.rest["administrators"] + "/" + userId)
        if resp.ok:
            account = resp.json()

            admin_role = account.get("adminRole", "READ_ONLY")
            input_password = password or account.get("password", None)  # Use existing password if not provided
            scopes = {key: access.get(key, account['scopes'].get(key, False)) for key in keys}  # Use existing access if not provided

            payload = {
                "accountState": account.get("accountState", "ENABLED"),  # Default to ENABLED if not found
                "adminRole": admin_role,  # Default to READ_ONLY if not found
                "userId": userId,
                "password": input_password,
                "scopes": scopes,
                "custId": None
            }

            resp = self.client.requestsWrapper(actionParams.PUT,
                                               self.client.url + self.client.rest["administrators"] + "/" + userId,
                                               json=payload)
            if not resp.ok:
                return resp

            # Update account password if provided
            if password:
                payload = {
                    "userId": userId,
                    "password": password,
                }
                resp = self.client.requestsWrapper(actionParams.PUT,
                                                   self.client.url + self.client.rest["administrators"] + "/adminpassword",
                                                   json=payload)
            return resp

    def updateControllerIP(self, new_ip: str) -> requests.Response:
        """
        Update the controller IP address.
        Args:
            new_ip (str): The new IP address to set for the controller.

        Returns:
            requests.Response: The response containing the result of the IP update operation.
        """
        # fetch the current interface details
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["admin"])
        if not resp.ok:
            return resp
        current_details = resp.json()

        # Update current_details with new IP
        current_details['ipAddress'] = new_ip
        payload = current_details

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["admin"], json=payload)
        return resp

    def updateInterface(self, interface_name: str, **kwargs) -> requests.Response:
        """
        Update the specified network interface with the provided keyword arguments.

        Args:
            interface_name (str): The name of the interface to update.
            **kwargs: Key-value pairs to update in the interface configuration.

        Returns:
            requests.Response: The response from the update operation.
        """
        # Fetch the list of interfaces
        interfaces = self.getInterfaces().json()

        # Find the interface matching the given name
        interface = next((iface for iface in interfaces if iface.get("name") == interface_name), None)
        if not interface:
            raise ValueError(f"Interface '{interface_name}' not found.")

        # Update the interface with the provided keyword arguments
        for key, value in kwargs.items():
            if key in interface:
                interface[key] = value
            else:
                raise KeyError(f"Key '{key}' not found in the interface configuration.")

        # Send the updated interface configuration
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["interfaces"],
                                           json=interface)
        return resp

    def upgradeFtp(self, path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
        """
        Upgrade using FTP.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.

        Returns:
            requests.Response: The response from the upgrade operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user,
                  "localDestination": "local"}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["ftpImage"],
                                           json=params)
        return resp

    def upgradeScp(self, path: str, fileName: str, ip: str, user: str, passw: str) -> requests.Response:
        """
        Upgrade the Secure Copy Protocol.

        Args:
            path (str): The path to the file.
            fileName (str): The name of the file.
            ip (str): The IP address of the server.
            user (str): The username for the server.
            passw (str): The password for the server.

        Returns:
            requests.Response: The response from the upgrade operation.
        """
        params = {"directory": path, "fileName": fileName, "password": passw, "serverIP": ip, "userid": user}
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["scpImage"],
                                           json=params)
        return resp


class Plans(Base):
    """
    Floor Plan Manager class for managing floor plans on the Appliance.

    Methods:
        __init__(client):
            Initialize the Floor Plan Manager.

        _image(root: str) -> List[Union[BinaryIO, str]]:
            Extract binary image from the XML root.

        create():
            Create a new floor plan.

        floorExport(floorid: str) -> requests.Response:
            Export the floor from the Floor Plan Manager.

        get(siteid: str) -> List:
            Get the plan for the specified site.

        getFloors(siteid: str, floorName: str = 'all') -> List[floor]:
            Get the floors for the specified site.

        imageFromFile(xmlFile: str) -> BinaryIO:
            Get image from the XML file.

        imageFromString(xmlstring: str) -> BinaryIO:
            Get image from the XML string.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Floor Plan Manager.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(Plans, self).__init__(client)
        self._id = 'planId'
        self._path = 'mapservices-plan'

    class floor(NamedTuple):
        """
        Named tuple representing a floor.

        Attributes:
            name (str): The name of the floor.
            floorId (str): The ID of the floor.
            width (float): The width of the floor.
            height (float): The height of the floor.
            floorHeight (float): The height of the floor in meters.
            aps (List[ap]): A list of AP positions.
        """

        class ap(NamedTuple):
            """
            Named tuple representing an AP position.

            Attributes:
                model (str): The model of the AP.
                xloc (float): The x-coordinate of the AP.
                yloc (float): The y-coordinate of the AP.
                zloc (float): The z-coordinate of the AP.
            """
            model: str
            xloc: float
            yloc: float
            zloc: float
            name: str

        name: str
        floorId: str
        width: float
        height: float
        floorHeight: float
        aps: List[ap]  #: list ap positions

    # extract binary image from the xml root
    def _image(self, root: str) -> List[Union[BinaryIO, str]]:
        """
        Extract binary image from the XML root.

        Args:
            root (str): The root (or parent) of the XML file.

        Returns:
            List[Union[BinaryIO, str]]: The binary image and its format.
        """
        for neighbor in root.iter('background'):
            a = neighbor.text

        format = a.split(";")[0]
        image = a.split(";")[1].split(",")[1]
        png = io.BytesIO(base64.b64decode(image))
        return [png, format]

    def create(self) -> None:
        """
        Create a new floor plan.

        Returns:
            None
        """
        # TODO: implement floor plan creation
        return

    def floorExport(self, floorid: str) -> requests.Response:
        """
        Export the floor from the Floor Plan Manager.

        Args:
            floorid (str): The ID of the floor.

        Returns:
            requests.Response: The response from the export operation.

        >>>  #get the image
        >>>  xml = c.plans.floorExport(ff.floorId)
        >>>  image = c.plans.imageFromString(xml)
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest['mapservices-export-xml'] + "/" + floorid)
        return resp.content

    def get(self, siteid: str) -> List:
        """
        Get the plan for the specified site.

        Args:
            siteid (str): The ID of the site.

        Returns:
            List: A list of plans for the site.
        """
        resp = super(Plans, self).get(siteid)
        return list(resp)

    def getFloors(self, siteid: str, floorName: str = 'all') -> List[floor]:
        """
        Get the floors for the specified site.

        Args:
            siteid (str): The ID of the site.
            floorName (str, optional): The name of the floor. Defaults to 'all'.

        Returns:
            List[floor]: A list of floors for the site.

        >>>    #collect floors per Site
        >>>    floors = c.plans.getFloors(ss.id)
        >>>    print (floors)
        >>>    Out:
        >>>    [
        >>>      floor(name='Thornhill', floorId='3a145b8c-cf32-11e9-bb12-0050568f5941',
        >>>      width=55.166649, height=37.162037, floorHeight=3.0,
        >>>      aps=[
        >>>            ap(model='AP505i-FCC', xloc=48.364574, yloc=23.387268, zloc=3.0),
        >>>            ap(model='AP505i-FCC', xloc=1.673785, yloc=31.481018, zloc=3.0)
        >>>          ])
        >>>     ]
        """
        plans = self.get(siteid)
        if len(plans) == 0:
            return []
        # there is only one plan per site
        floors = plans[0].floors
        ff = []
        for f in floors:
            name = f['name'] if floorName == 'all' else floorName
            if f['name'] == name:
                _obj = one().fromDict(f)
                print(_obj.name, _obj.aps)
                aps = [Plans.floor.ap(x["model"], x["xloc"], x["yloc"], x["zloc"], x["name"]) for x in
                       _obj.aps] if _obj.aps is not None else []
                ff.append(Plans.floor(floorId=_obj.floorId, name=_obj.name, width=_obj.width, height=_obj.height,
                                      floorHeight=_obj.floorHeight,
                                      aps=aps)
                          )
        return ff

    # get image from the xml file
    def imageFromFile(self, xmlFile: str) -> BinaryIO:
        """
        Get image from the XML file.

        Args:
            xmlFile (str): The XML file name.

        Returns:
            BinaryIO: The image as a binary array.
        """
        root = xml.etree.ElementTree.parse(xmlFile).getroot()
        [png, _] = self._image(root)
        return png

    # get image from the xml string
    def imageFromString(self, xmlstring: str) -> BinaryIO:
        """
        Get image from the XML string.

        Args:
            xmlstring (str): The XML string.

        Returns:
            BinaryIO: The image as a binary array.
        """
        root = xml.etree.ElementTree.fromstring(xmlstring)
        [png, _] = self._image(root)
        return png


class Positioning(Base):
    """
    Positioning class for managing positioning profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the Positioning class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Positioning class.

        Args:
            client: The client instance to use for making requests.
        """
        super(Positioning, self).__init__(client)
        self._id = 'id'
        self._path = 'positioning'
        self._name = 'name'


class Profiles(Base):
    """
    Profiles class for managing client profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the Profiles class.

        assignNetworkByName(profileName: str, networkName: str, radio: int) -> requests.Response:
            Assign network by the provided profile name and network name.

        assignNetworkListByName(profileName: str, networkNameList: str, radio: int) -> requests.Response:
            Assign network list by the provided profile name and network names.

        configureMeshRoot(profileName: str, networkName: str, radioIndex: int) -> requests.Response:
            Configure the mesh root for the provided profile name, network name, and radio index.

        create(name: str, platf: str) -> requests.Response:
            Create a new client profile with the provided name and platform.

        getBssid0(profileName: str) -> requests.Response:
            Return the "bssid0" network for the provided profile name.

        removeNetwork(profileName: str, networkId: str, radio: int) -> requests.Response:
            Remove network by the provided profile name and network ID.

        removeNetworkByName(profileName: str, networkName: str, radio: int) -> requests.Response:
            Remove network by the provided profile name and network name.

        removeNetworkListByName(profileName: str, networkNameList: str, radio: int) -> requests.Response:
            Remove network list by the provided profile name and network names.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Profiles class.

        Args:
            client: The client instance to use for making requests.
        """
        super(Profiles, self).__init__(client)
        self._id = 'id'
        self._path = 'profiles'
        self._name = 'name'
        self._pathString = self.client.rest[self._path]

    def assignNetwork(self, profileName: str, networkId: str, radio: int) -> requests.Response:
        """
        Assign the client's network by the provided profile name and network ID.

        Args:
            profileName (str): The name of the profile.
            networkId (str): The ID of the network.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the assign operation.
        """
        p = self.get(self.refresh().nameToId(profileName))[0]
        netw = {'serviceId': networkId, 'index': radio}
        p.radioIfList.append(netw)
        resp = self.set(p)
        return resp

    def assignNetworkByName(self, profileName: str, networkName: str, radio: int) -> requests.Response:
        """
        Assign the client's network by the provided profile and network names.

        Args:
            profileName (str): The name of the profile.
            networkName (str): The name of the network.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the assign operation.
        """
        ntw = self.client.networks.refresh()
        return self.assignNetwork(profileName, ntw.getByName(networkName).id, radio)

    def assignNetworkListByName(self, profileName: str, networkNameList: str, radio: int) -> requests.Response:
        """
        Assign network list by the provided profile name and network names.

        Args:
            profileName (str): The name of the profile.
            networkNameList (str): The list of network names.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the assign operation.
        """
        ntw = self.client.networks.refresh()
        p = self.get(self.refresh().nameToId(profileName))[0]
        for networkName in networkNameList:
            networkId = ntw.getByName(networkName).id
            netw = {'serviceId': networkId, 'index': radio}
            p.radioIfList.append(netw)
        resp = self.set(p)
        return resp

    def configureMeshRoot(self, profileName: str, networkName: str, radioIndex) -> requests.Response:
        """
        Configure the mesh root for the provided profile name, network name, and radio index.

        Args:
            profileName (str): The name of the profile.
            networkName (str): The name of the network.
            radioIndex (int): The radio index.

        Returns:
            requests.Response: The response from the configure operation.
        """
        meshpoint_networks = self.client.networks.getMeshPointNetworks()
        networkId = [x for x in meshpoint_networks if x.name == networkName][0].id

        default = self.get(self.refresh().nameToId(profileName))[0]
        default.meshpointIfList = [
            {
                "index": radioIndex,
                "meshpointId": networkId
            }
        ]

        default.meshpoints = [
            {
                "meshpointId": networkId,
                "meshRoot": True
            }
        ]

        resp = self.set(default)
        return resp

    def create(self, name: str, platf: str) -> requests.Response:
        """
        Create a new client profile with the provided name and platform.

        Args:
            name (str): The name of the profile.
            platf (str): The platform of the profile.

        Returns:
            requests.Response: The response from the create operation.
        """
        default = one().fromDict({"name": name, "apPlatform": platf})
        resp = super(Profiles, self).createCustom(default, path=self._path)
        return resp

    def getBssid0(self, profileName: str) -> requests.Response:
        """
        Return the "bssid0" network for the provided profile name.

        Args:
            profileName (str): The name of the profile.

        Returns:
            requests.Response: The response from the get operation.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           f"{self.client.url}{self._pathString}/{self.refresh().nameToId(profileName)}/bssid0",
                                           params=None,
                                           stream=True)
        return resp

    def removeNetwork(self, profileName: str, networkId: str, radio: int) -> requests.Response:
        """
        Remove network by the provided profile name and network ID.

        Args:
            profileName (str): The name of the profile.
            networkId (str): The ID of the network.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the remove operation.
        """
        p = self.get(self.refresh().nameToId(profileName))[0]
        p.radioIfList = [x for x in p.radioIfList if (x['serviceId'] != networkId) | (x['index'] != radio)]
        resp = self.set(p)
        return resp

    def removeNetworkByName(self, profileName: str, networkName: str, radio: int) -> requests.Response:
        """
        Remove network by the provided profile name and network name.

        Args:
            profileName (str): The name of the profile.
            networkName (str): The name of the network.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the remove operation.
        """
        ntw = self.client.networks.refresh()
        return self.removeNetwork(profileName, ntw.getByName(networkName).id, radio)

    def removeNetworkListByName(self, profileName: str, networkNameList: str, radio: int) -> requests.Response:
        """
        Remove network list by the provided profile name and network names.

        Args:
            profileName (str): The name of the profile.
            networkNameList (str): The list of network names.
            radio (int): The radio index.

        Returns:
            requests.Response: The response from the remove operation.
        """
        ntw = self.client.networks.refresh()
        p = self.get(self.refresh().nameToId(profileName))[0]
        for networkName in networkNameList:
            networkId = ntw.getByName(networkName).id
            p.radioIfList = [x for x in p.radioIfList if (x['serviceId'] != networkId) | (x['index'] != radio)]
        resp = self.set(p)
        return resp


# radio manager
class Radios(Base):
    """
    Radios class for managing radio-related operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Radios class.

        channels(sn: str, rm: str, bw: int, cn: str, ridx: int, txBf: float) -> requests.Response:
            Retrieve the available radio channels.

        getChannels(sn: str, rm: str, bw: int, cn: str, ridx: int, txBf: float) -> requests.Response:
            Retrieve the available radio channels for the specified parameters.

        getModes(sn: str, bw: int, ridx: int) -> requests.Response:
            Retrieve the available radio modes for the specified parameters.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Radios class.

        Args:
            client: The client instance to use for API requests.
        """
        super(Radios, self).__init__(client)
        self._id = None  # no identity
        self._path = 'radios'

    def channels(self, sn: str, rm: str, bw: int, cn: str, ridx: int, txBf: float) -> requests.Response:
        """
        Retrieve the available radio channels.

        Args:
            sn (str): The serial number of the AP.
            rm (str): The radio mode.
            bw (int): The channel width.
            cn (str): The country code.
            ridx (int): The radio index.
            txBf (float): The transmit beamforming value.

        Returns:
            requests.Response: The response from the server containing the available radio channels.
        """
        query = {"sn": sn, "radioMode": rm, "channelWidth": bw,
                 "country": cn, "radioIndex": ridx, "txbf": txBf}
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + self.client.rest[self._path] + "/channels",
                                           params=query)
        return resp

    def getChannels(self, sn: str, rm: str, bw: int, cn: str, ridx: int, txBf: float) -> requests.Response:
        """
        Retrieve the available radio channels for the specified parameters.

        Args:
            sn (str): The serial number of the AP.
            rm (str): The radio mode.
            bw (int): The channel width.
            cn (str): The country code.
            ridx (int): The radio index.
            txBf (float): The transmit beamforming value.

        Returns:
            requests.Response: The response from the server containing the available radio channels.
        """
        query = {"sn": sn, "radioMode": rm, "channelWidth": bw, "country": cn, "radioIndex": ridx, "txBf": txBf}
        resp = self.get("channels", path=None, query=query)
        return resp[0].channelList

    def getModes(self, sn: str, bw: int, ridx: int) -> requests.Response:
        """
        Retrieve the available radio modes for the specified parameters.

        Args:
            sn (str): The serial number of the AP.
            bw (int): The channel width.
            ridx (int): The radio index.

        Returns:
            requests.Response: The response from the server containing the available radio modes.
        """
        query = {"sn": sn, "channelWidth": bw, "radioIndex": ridx}
        resp = self.get("modes", path=None, query=query)
        return resp[0].radioModeList


class Radius(object):
    """
    Radius class for managing RADIUS server configurations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Radius class.

        configDefaultAAARadius(primary_server_ip: str, backup_server_ip: str = None, local_mac_auth: bool = True):
            Configure the default AAA with RADIUS information.

        createLocalUser(username: str, password: str, params: dict = None):
            Create a new local user with the specified username and password.

        createNetworkAaa(auth_method: str, wlan_name: str, radius_server_ip: str):
            Create a new network AAA configuration.

        createRadiusServer(radius_server: dict):
            Create a new RADIUS server with the specified configuration.

        createRadiusServerParam(server_ip: str, shared_secret: str
            Create a new RADIUS server with the specified IP and shared secret.

        deleteLocalUser(username: str):
            Delete the specified local user.

        deleteNetworkAaa(wlan_name: str):
            Delete the specified network AAA configuration.

        deleteRadiusServer(server_ip: str):
            Delete the specified RADIUS server by IP address.

        getLocalUser(username: str = None, encode: bool = True):
            Retrieve local user information.

        getNetworkAaa():
            Retrieve all network AAA configurations.

        getRadiusServer(address: str = None, encode: bool = True):
            Retrieve RADIUS server information.

        setLocalUser(username: str, object: object):
            Update the local user information.

        setRadiusServer(object: object, address: str):
            Update the RADIUS server configuration.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Radius class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        self.client = client
        self.create_radius_payload = {
            "server_ip": "",  # this you set
            "response_window": 20,
            "authentication_timeout": 2,
            "authentication_retry_count": 1,
            "authorization_client_port": 1812,
            "proxy_radius_accounting_requests": False,
            "accounting_client_port": 1813,
            "shared_secret": "",  # this you set
            "username_format": "Keep Domain Name",
            "require_message_authenticator": True,
            "use_server_status_request": True,
            "use_access_request": True,
            "username": "fakeUser",
            "password": "fakePassword",
            "check_interval": 30,
            "number_of_answers_to_alive": 3,
            "revive_interval": 60
        }

    def configDefaultAAARadius(self, primary_server_ip, backup_server_ip=None, local_mac_auth=True) -> requests.Response:
        """
        Configure the default AAA with RADIUS information.

        Args:
            primary_server_ip (str): The IP address of the primary RADIUS server.
            backup_server_ip (str, optional): The IP address of the backup RADIUS server. Defaults to None.
            local_mac_auth (bool, optional): Whether to enable local MAC authentication. Defaults to True.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {
            "auth_method": "Proxy RADIUS",
            "primary_radius_server": {"server_ip": primary_server_ip},
            "backup_radius_server": {"server_ip": backup_server_ip} if backup_server_ip else None,
            "ldap_configuration": None,
            "local_password_repository": None,
            "local_mac_auth": local_mac_auth,
            "third_radius_server": None,
            "fourth_radius_server": None
        }
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest["radiusDefaultAAA"],
                                           json=payload)
        return resp

    def createLocalUser(self, username, password, params: dict = None) -> requests.Response:
        """
        Create a new local user with the specified username and password.

        Args:
            username (str): The username of the new local user.
            password (str): The password for the new local user.
            params (dict, optional): Additional parameters for the local user. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {"description": "", "display_name": "", "enabled": True, "first_name": "", "last_name": "",
                   "password": password, "password_hash_type": "PKCS5 Reversible Hash", "username": username}

        if params is not None and params != {}:
            for key in params:
                if key in payload.keys():
                    payload[key] = params[key]
                else:
                    print("The key {k} does not match any payload keys - it is ignored".format(k=key))

        # rest = "access-control/v1/local_password_repos/Default"
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["radiusLocal"],
                                           json=payload)
        # print(str(resp.json()))
        return resp

    def createNetworkAaa(self, auth_method, wlan_name, radius_server_ip) -> requests.Response:
        """
        Create a new network AAA configuration.

        Args:
            auth_method (str): The authentication method.
            wlan_name (str): The WLAN name.
            radius_server_ip (str): The IP address of the RADIUS server.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {
            "location_name": wlan_name,
            "auth_method": auth_method,
            "primary_radius_server": {"server_ip": radius_server_ip},
            "backup_radius_server": None,
            "third_radius_server": None,
            "fourth_radius_server": None,
            "ldap_configuration": None,
            "local_mac_auth": False
        }

        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["radiusNetworksAAA"],
                                           json=payload)
        return resp

    def createRadiusServer(self, radius_server: dict) -> requests.Response:
        """
        Create a new RADIUS server with the specified configuration.

        Args:
            radius_server (dict): The configuration for the new RADIUS server.

        Returns:
            requests.Response: The response from the server.
        """
        payload = self.create_radius_payload
        for key in radius_server:
            if key not in self.create_radius_payload.keys():
                LOGGER.error("Wrong Dictionary keys were found")
                return "Response 404"  ## To be Determined
            else:
                payload[key] = radius_server[key]
        # rest = "access-control/v1/radius_servers"
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["radiusServer"],
                                           json=payload)
        return resp

    def createRadiusServerParam(self, server_ip: str, shared_secret: str) -> requests.Response:
        """
        Create a new RADIUS server with the specified IP and shared secret.

        Args:
            server_ip (str): The IP address of the RADIUS server.
            shared_secret (str): The shared secret for the RADIUS server.

        Returns:
            requests.Response: The response from the server.
        """
        payload = self.create_radius_payload
        if server_ip is None or shared_secret is None:
            LOGGER.error("ERROR: Please specify server ip and shared secret values")
            return "Response 404"
        payload["server_ip"] = server_ip
        payload["shared_secret"] = shared_secret
        # rest = "access-control/v1/radius_servers"
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["radiusServer"],
                                           json=payload)
        return resp

    def deleteLocalUser(self, username) -> requests.Response:
        """
        Delete the specified local user.

        Args:
            username (str): The username of the local user to delete.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["radiusLocal"] + "/" + username
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)
        return resp

    def deleteNetworkAaa(self, wlan_name: str) -> requests.Response:
        """
        Delete the specified network AAA configuration.

        Args:
            wlan_name (str): The WLAN name of the network AAA configuration to delete.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["radiusNetworksAAA"] + wlan_name
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)

        return resp

    def deleteRadiusServer(self, server_ip: str) -> requests.Response:
        """
        Delete the specified RADIUS server by IP address.

        Args:
            server_ip (str): The IP address of the RADIUS server to delete.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["radiusServer"] + "/" + server_ip
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)
        return resp

    def getLocalUser(self, username=None) -> requests.Response:
        """
        Retrieve local user information.

        Args:
            username (str, optional): The username of the local user. Defaults to None.

        Returns:
            requests.Response: The response from the server containing local user information.
        """
        if username is None or username == "":
            resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["radiusLocal"])
        else:
            resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["radiusLocal"] +
                                               "/" + username)
        return resp

    def getNetworkAaa(self) -> requests.Response:
        """
        Retrieve all network AAA configurations.

        Returns:
            requests.Response: The response from the server containing the network AAA configurations.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["radiusNetworksAAA"])
        return resp

    def getRadiusServer(self, address=None) -> requests.Response:
        """
        Retrieve RADIUS server information.

        Args:
            address (str, optional): The IP address of the RADIUS server. Defaults to None.

        Returns:
            requests.Response: The response from the server containing RADIUS server information.
        """
        if address is None:
            resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["radiusServer"])
        else:
            rest = self.client.rest["radiusServer"] + "/" + address
            resp = self.client.requestsWrapper(actionParams.GET, self.client.url + rest)
        return resp

    def setLocalUser(self, username, object: object) -> requests.Response:
        """
        Update the local user information.

        Args:
            username (str): The username of the local user.
            object (object): The object containing updated user information.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["radiusLocal"] + "/" + username
        cleandict = object.__dict__.copy()

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + rest,
                                           json=cleandict)
        return resp

    def setRadiusServer(self, object: object, address: str) -> requests.Response:
        """
        Update the RADIUS server configuration.

        Args:
            object (object): The object containing updated RADIUS server information.
            address (str): The IP address of the RADIUS server to update.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["radiusServer"] + "/" + address
        dict = object.__dict__.copy()
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + rest,
                                           json=dict)
        return resp


class Ratelimiters(Base):
    """
    Ratelimiters class for managing rate limiters on the Appliance.

    Methods:
        __init__(client):
            Initialize the Ratelimiters class.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Ratelimiters class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(Ratelimiters, self).__init__(client)
        self._id = 'id'
        self._path = 'ratelimiters'
        self._name = 'name'


class Reports(Base):
    """
    Reports class for managing reports and datasets on the Appliance.

    Methods:
        __init__(client):
            Initialize the Reports class.

        createTemplate(createTimeStamp: str, template: dict, name: str) -> requests.Response:
            Create a new template with the given parameters.

        dataset(key: str, duration: Duration, query: dict, format: DataFmt, start: int, stop: int) -> Union[None, List]:
            Retrieve a dataset based on the specified key, duration, query, format, start, and stop.

        deleteReports(fname: str) -> requests.Response:
            Delete the specified report by filename.

        deleteScheduleSettings(scheduleID: str) -> requests.Response:
            Delete the specified schedule settings by its ID.

        deleteTemplate(templateID: str) -> requests.Response:
            Delete the specified template by its ID.

        GeneratedReports() -> requests.Response:
            Retrieve the generated reports.

        getMuReport(muMacAddress: str, widgetType: str, duration: str, resolution: str) -> Union[requests.Response, None]:
            Retrieve the client reports/widgets.

        getSchedulerSettings() -> requests.Response:
            Retrieve the scheduled settings.

        getTemplates() -> requests.Response:
            Retrieve the system log level.

        reportSettingScheduled(tmpNamestr: str, templateIDStr: str, scope: str, creationTimestamp: str, generateReportAction: str, runNow: bool = False, period_val: str = "3H", format: str = "Pdf", status: str = "Queued", creator: str = "admin") -> requests.Response:
            Create a report setting and run the report schedule.

        upgradedevices() -> requests.Response:
            Retrieve the device upgrade status.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Reports class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(Reports, self).__init__(client)
        self._id = 'id'
        self._path = 'reports'
        self._cache = {}

    class Duration(str, Enum):
        """
        Enumeration for different dataset durations.

        Attributes:
            d3H: Duration of 3 hours.
            d3D: Duration of 3 days.
            d14D: Duration of 14 days.
        """
        d3H = "3H",
        d3D = "3D",
        d14D = "14D"

    class DataFmt(str, Enum):
        """
        Enumeration for different dataset formats.

        Attributes:
            json: JSON format.
            msgpck: MessagePack format.
            csv: CSV format.
        """
        json = "Json",
        msgpck = "Msgpack",
        csv = "csv"

    """ create a new template with the given parameters for the template """
    """ payload is passed with timestamp along with template details """

    def createTemplate(self, createTimeStamp, template, name) -> requests.Response:
        """
        Create a new template with the given parameters.

        Args:
            createTimeStamp (str): The creation timestamp.
            template (dict): The template details.
            name (str): The name of the template.

        Returns:
            requests.Response: The response from the server.
        """
        payload = {"creationTimeStamp": createTimeStamp,
                   "customTemplate": template,
                   "name": name}
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["widgets"],
                                           json=payload)
        return resp

    def dataset(self, key='MuTable', duration: Duration = Duration.d3H, query=None, format: DataFmt = DataFmt.json,
                start=0, stop=0) -> Union[None, List]:
        """
        Retrieve a dataset based on the specified key, duration, query, format, start, and stop.

        Args:
            key (str): The key identifying the dataset.
            duration (Duration): The duration for which the dataset is retrieved.
            query (dict): Additional query parameters.
            format (DataFmt): The format in which the dataset is retrieved.
            start (int): The start index for the dataset.
            stop (int): The stop index for the dataset.

        Returns:
            Union[None, List]: The dataset retrieved from the server.
        """
        query = {'key': key,
                 'filterQuery': query,
                 'format': format,
                 'start': start,
                 'stop': stop}
        params = {'duration': duration,
                  'query': json.dumps(query)}

        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest[self._path] + "/flex",
                                           params=params)
        if not resp.ok:
            return None
        tbl = []
        for jd in resp.json():  # for 3120 like platform len jData 2 , for others 1; jd is dict with key 'frame'
            frame = jd["frame"]
            zframe = base64.b64decode(frame)
            zframe = zlib.decompress(zframe)
            if format == self.DataFmt.json:
                zframe = zframe.decode()
                tbl.append(json.loads(zframe))
            elif format == self.DataFmt.csv:
                zframe = zframe.decode()
                tbl.append(zframe)
            else:
                tbl.append(zframe)
        return tbl

    def deleteReports(self, fname) -> requests.Response:
        """
        Delete the specified report by filename.

        Args:
            fname (str): The filename of the report to delete.

        Returns:
            requests.Response: The response from the server.
        """
        payload = [fname]
        rest = self.client.rest["generated"] + "/" + "filelist"
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + rest, json=payload)
        return resp

    def deleteScheduleSettings(self, scheduleID) -> requests.Response:
        """
        Delete the specified schedule settings by its ID.

        Args:
            scheduleID (str): The ID of the schedule settings to delete.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["templateScheduled"] + "/" + scheduleID
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)
        return resp

    def deleteTemplate(self, templateID) -> requests.Response:
        """
        Delete the specified template by its ID.

        Args:
            templateID (str): The ID of the template to delete.

        Returns:
            requests.Response: The response from the server.
        """
        rest = self.client.rest["widgets"] + "/" + templateID
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + rest)
        return resp

    def GeneratedReports(self) -> requests.Response:
        """
        Retrieve the generated reports.

        Returns:
            requests.Response: The response from the server containing the generated reports.
        """
        rest = self.client.rest["generated"]  # + "/" + templateID
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + rest)
        return resp

    def getMuReport(self, muMacAddress, widgetType, duration, resolution) -> requests.Response:
        """
        Retrieve the client reports/widgets.

        Args:
            muMacAddress (str): The MAC address of the MU.
            widgetType (str): The widget type.
            duration (str): The selected duration.
            resolution (str): The selected resolution.

        Returns:
            requests.Response: The response from the server containing the client reports/widgets.
        """
        path = "/{s}?duration={d}&resolution={r}&widgetList={w}".format(s=muMacAddress, d=duration, r=resolution,
                                                                        w=widgetType)
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["mu_report"] + path)
        return resp

    def getSchedulerSettings(self) -> requests.Response:
        """
        Retrieve the scheduler settings.

        Returns:
            requests.Response: The response from the server containing the scheduler settings.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["templateScheduled"])
        return resp

    def getTemplates(self) -> requests.Response:
        """
        Retrieve the system log level.

        Returns:
            requests.Response: The response from the server containing the system log level.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["widgets"])
        return resp

    """ This method is common method for create a report setting and run the report schedule"""
    """ runNow will be false when we only create the report setting"""
    """ if runNow is True, then this method will create a report based on the report setting"""

    def reportSettingScheduled(self, tmpNamestr, templateIDStr, scope, creationTimestamp,
                               generateReportAction, runNow=False,
                               period_val="3H", format="Pdf", status="Queued", creator="admin") -> requests.Response:

        """
        Create a report setting and run the report schedule.

        Args:
            tmpNamestr (str): The template name.
            templateIDStr (str): The template ID.
            scope (str): The scope of the report.
            creationTimestamp (str): The creation timestamp.
            generateReportAction (str): The action to generate the report.
            runNow (bool): Whether to run the report immediately. Defaults to False.
            period_val (str): The period value. Defaults to "3H".
            format (str): The format of the report. Defaults to "Pdf".
            status (str): The status of the report. Defaults to "Queued".
            creator (str): The creator of the report. Defaults to "admin".

        Returns:
            requests.Response: The response from the server.
        """
        payload = {
            "name": tmpNamestr,
            "templateId": templateIDStr,
            "scope": scope,
            "period": {"value": period_val},  # Direct string format, not wrapped in an object
            "format": format,
            "runNow": runNow,  # Pass directly as a boolean
            "generatedReportAction": generateReportAction,  # Should be a string
            "creationTimestamp": creationTimestamp,
            "status": status,
            "creator": creator
        }
        rest = self.client.rest["templateScheduled"]  # + "/" + templateID
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + rest, json=payload)
        return resp

    def upgradedevices(self) -> requests.Response:
        """
        Retrieve the device upgrade status.

        Returns:
            requests.Response: The response from the server.
        """
        return self.client.requestsWrapper(actionParams.GET, self.client.url + self.client.rest["upgradedevices"])


class RfMgmtProfiles(Base):
    """
    RfMgmtProfiles class for managing RF Management Profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the RfMgmtProfiles class.

        get(key='all', path=None, query=None, encode=True):
            Retrieve RF Management Profile data.
    """

    def __init__(self, client) -> None:
        """
        Initialize the RfMgmtProfiles class.

        Args:
            client: The client instance to use for making requests.
        """
        super(RfMgmtProfiles, self).__init__(client)
        self._id = 'id'
        self._path = 'rfmgmt'
        self._name = 'name'

    def get(self, key='all', path=None, query=None, encode=True) -> list:
        """
        Retrieve RF Management Profile data.

        Args:
            key (str, optional): The key to retrieve. Default is 'all'.
            path (str, optional): The path to use for the request. Default is None.
            query (dict, optional): The query parameters to use for the request. Default is None.
            encode (bool, optional): Flag to indicate if the query should be URL encoded. Default is True.

        Returns:
            list: A list of RF Management Profiles.
        """
        return super(RfMgmtProfiles, self).get(key, path, query, encode)


class Roles(Base):
    """
    Roles class for managing RF management profiles on the Appliance.

    Methods:
        __init__(client):
            Initialize the Roles class.

        createRoleById(uuid: str) -> requests.Response:
            Creates a role by its UUID.

        modifyRoleById(uuid: str, payload: dict) -> requests.Response:
            Modify a role by its UUID by providing the payload
    """

    def __init__(self, client) -> None:
        """
        Initialize the Roles class.

        Args:
            client: The client instance to use for making requests.
        """
        super(Roles, self).__init__(client)
        self._id = 'id'
        self._path = 'roles'
        self._name = 'name'

    def createRoleById(self, uuid: str) -> requests.Response:
        """
        Creates a role by its UUID.

        Args:
            uuid: The UUID of the role to be created.
        """
        params = {
            "uuid": uuid
        }
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest[self._path] + f"/{uuid}",
                                           json=params)
        return resp

    def modifyRoleById(self, uuid: str, payload: dict) -> requests.Response:
        """
        Modify a role by its UUID by providing the payload.

        Args:
            uuid: The UUID of the role to be created.
            payload: The payload to be used for modifying the role.
        """
        resp = self.client.requestsWrapper(actionParams.PUT,
                                           self.client.url + self.client.rest[self._path] + f"/{uuid}",
                                           json=payload)
        return resp


class RTLS(Base):
    """
    RTLS class for managing RTLS (Real-Time Location System) configurations on the Appliance.

    Methods:
        __init__(client):
            Initialize the RTLS class.

        create(app_id: RTLSApplication, name: str, server_ip: str, server_port: int = None, multicast_mcast: str = None):
            Create a new RTLS configuration with the specified parameters.
    """

    def __init__(self, client) -> None:
        """
        Initialize the RTLS class.

        Args:
            client: The client instance used to interact with the Appliance.
        """
        super(RTLS, self).__init__(client)
        self._path = 'rtls'
        self._name = 'name'
        self._id = 'id'

    class RTLSApplication(str, Enum):
        """
        Enumeration for different RTLS applications.

        Attributes:
            AEROSCOUT: AeroScout application.
            EKAHAU: Ekahau application.
            CENTRAK: Centrak application.
            SONITOR: Sonitor application.
        """
        AEROSCOUT = 'AeroScout',
        EKAHAU = 'Ekahau',
        CENTRAK = 'Centrak',
        SONITOR = 'Sonitor'

    def create(self, app_id: RTLSApplication, name, server_ip, server_port=None, multicast_mcast=None) -> requests.Response:
        """
        Create a new RTLS configuration with the specified parameters.

        Args:
            app_id (RTLSApplication): The application ID for the RTLS.
            name (str): The name of the RTLS configuration.
            server_ip (str): The IP address of the RTLS server.
            server_port (int, optional): The port of the RTLS server. Defaults to None.
            multicast_mcast (str, optional): The multicast address. Defaults to None.

        Returns:
            requests.Response: The response from the server.
        """
        default = super(RTLS, self).get('default', path=self._path)[0]
        default.name = name
        default.appId = app_id
        if app_id == self.RTLSApplication.AEROSCOUT.value:
            port = server_port or 12092
            mcast = multicast_mcast or '01:0C:CC:00:00:00'
            default.aeroScout = {
                'ip': server_ip,
                'port': port,
                'mcast': mcast
            }
        elif app_id == self.RTLSApplication.EKAHAU.value:
            port = server_port or 37008
            mcast = multicast_mcast or '01:18:8E:00:00:00'
            default.ekahau = {
                'ip': server_ip,
                'port': port,
                'mcast': mcast
            }
        elif app_id == self.RTLSApplication.AEROSCOUT.CENTRAK.value:
            port = server_port or 7117
            mcast = multicast_mcast or '01:18:8E:00:00:00'
            default.centrak = {
                'ip': server_ip,
                'port': port,
                'mcast': mcast
            }
        elif app_id == self.RTLSApplication.AEROSCOUT.SONITOR.value:
            port = server_port or 2590
            mcast = multicast_mcast or '01:40:96:00:00:03'
            default.sonitor = {
                'ip': server_ip,
                'port': port,
                'mcast': mcast
            }
        resp = super(RTLS, self).createCustom(default, path=self._path)
        return resp


class Scheduler(Base):
    """
    Scheduler class for managing container schedules on the Appliance.

    Methods:
        __init__(client):
            Initialize the Scheduler class.

        clearSchedulerLogs() -> bool:
            Clear the scheduler logs.

        create(params: str) -> requests.Response:
            Create the schedule with the provided parameters.

        getEventByType(eventType: Event = Event.AGGREGATED_REPORT) -> requests.Response:
            Get the event by type.

        getSchedulesLogs() -> requests.Response:
            Get the schedule log.

        startScheduler() -> requests.Response:
            Start the scheduler.

        stopScheduler() -> requests.Response:
            Stop the scheduler.

        uninstallScheduler() -> requests.Response:
            Uninstall the scheduler.

        uploadConfigFile(file_path) -> requests.Response:
            Upload the configuration file for the scheduler.

        uploadSchedulerImage(file_path) -> requests.Response:
            Upload the scheduler image.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Scheduler class.

        Args:
            client: The client instance to interact with the Appliance.
        """
        super(Scheduler, self).__init__(client)
        self._id = 'id'
        self._path = 'containerSchedule'

    class Event(str, Enum):
        """
        Enumeration for different scheduler events.

        Attributes:
            AGGREGATED_REPORT (str): aggregated-report.
            NETWORK_STARTER (str): network-starter.
            HISTORICAL_REPORT (str): historical-report.
            NETWORK_STOPPER (str): network-stopper.
        """
        AGGREGATED_REPORT = "aggregated-report"
        NETWORK_STARTER = "network-starter"
        HISTORICAL_REPORT = "historical-report"
        NETWORK_STOPPER = "network-stopper"

    def clearSchedulerLogs(self) -> bool:
        """
        Clear the scheduler logs.

        Returns:
            bool: True if the logs were cleared successfully, False otherwise.
        """
        all_logs = self.getSchedulesLogs().json()
        for log in all_logs:
            log_id = log.get('id')
            self.client.requestsWrapper(actionParams.DELETE, self.client.url + f"apps/extreme-scheduler/api/v1/"
                                                                               f"executions/{log_id}")
        all_logs = self.getSchedulesLogs().json()
        return None if len(all_logs) > 0 else True

    def create(self, params: str) -> requests.Response:
        """
        Create the schedule with the provided parameters.

        Args:
            params (str): The parameters for creating the schedule.

        Returns:
            requests.Response: The response from the create operation.
        """
        # print("\n params =", params)
        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + self.client.rest[self._path],
                                           json=params)
        return resp

    def getEventByType(self, eventType: Event = Event.AGGREGATED_REPORT) -> requests.Response:
        """
        Get the event by type.

        Args:
            eventType (Scheduler.Event): The type of the event.

        Returns:
            requests.Response: The response containing the event data.
        """
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + f"apps/extreme-scheduler/api/v1/events/"
                                                                               f"parameters/{eventType}")
        return resp

    def getSchedulesLogs(self) -> requests.Response:
        """
        Get the schedule log.

        Returns:
            requests.Response: The response containing the schedule log.
        """
        resp = self.client.requestsWrapper(actionParams.GET,
                                           self.client.url + "apps/extreme-scheduler/api/v1/executions")
        return resp

    def startScheduler(self) -> requests.Response:
        """
        Start the scheduler.
        Returns:
            requests.Response: The response from the start operation.
        """
        path = f"{self.client.rest['apps']}/extreme-scheduler/start"
        payload = {'name': 'extreme-scheduler'}
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + path, json=payload)
        return resp

    def stopScheduler(self) -> requests.Response:
        """
        Stop the scheduler.
        Returns:
            requests.Response: The response from the stop operation.
        """
        path = f"{self.client.rest['apps']}/extreme-scheduler/stop"
        payload = {'name': 'extreme-scheduler'}
        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + path, json=payload)
        return resp

    def uninstallScheduler(self) -> requests.Response:
        """
        Uninstall the scheduler.
        Returns:
            requests.Response: The response from the uninstall operation.
        """
        path = f"{self.client.rest['apps']}/extreme-scheduler"
        resp = self.client.requestsWrapper(actionParams.DELETE, self.client.url + path)
        return resp

    def uploadConfigFile(self, file_path) -> requests.Response:
        """
        Upload the configuration file for the scheduler.
        Args:
            file_path (str): The path to the configuration file.
        Returns:
            requests.Response: The response from the upload operation.
        """
        path = f"{self.client.rest['apps']}/extreme-scheduler/config-files"

        # Convert file to binary
        with open(file_path, 'rb') as file:
            file_content = file.read()

        files = {
            'file': file_content,
            'config': 'api-keys.json'
        }

        resp = self.client.requestsWrapper(actionParams.PUT, self.client.url + path, files=files)
        return resp

    def uploadSchedulerImage(self, file_path) -> requests.Response:
        """
        Upload the scheduler image.
        Args:
            file_path: The file to be uploaded.
        Returns:
            requests.Response: The response from the upload operation.
        """
        path = f"{self.client.rest['apps']}/file?name=extreme-scheduler"

        # Convert file to binary
        with open(file_path, 'rb') as file:
            file_content = file.read()

        files = {'file': file_content}

        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + path, files=files)
        return resp


class Sites(Base):
    """
    Site Manager class for managing site-related operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the Sites class with a client.

        addApGroup(siteName, groupName, profileid: str, rfmgmtid: str) -> dict:
            Add a device group.

        addApGroupByName(siteName: str, groupName: str, profileName: str, rfName: str) -> dict:
            Add a device group by profile and RF name.

        assignApToGroup(siteName: str, groupName: str, apSerial: str) -> dict:
            Assign an AP to a group.

        create(name: str, country: str = None, features = None):
            Create a new site with the given name, country, and features.

        getByName(siteName: str) -> requests.Response:
            Retrieve a site by its name.

        getCountryList() -> dict:
            Retrieve the country list using a path parameter method.

        getSitesList():
            Retrieve the list of sites.

        getStationsList():
            Get a list of user devices with Wi-Fi capability.

        removeApFromGroup(siteName, groupName, apSerial) -> dict:
            Remove an AP from a group.

        removeApGroup(siteName: str, groupName: str) -> dict:
            Remove an AP group.

        stations(site_name) -> requests.Response:
            Get a list of stations for a specific site.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Sites class.

        Args:
            client: The client to use for operations.
        """
        super(Sites, self).__init__(client)
        self._id = 'id'
        self._path = 'sites'
        self._name = 'siteName'

    def addApGroup(self, siteName, groupName, profileid: str, rfmgmtid: str) -> dict:
        """
        Add a device group.

        Args:
            siteName (str): The name of the site.
            groupName (str): The name of the group.
            profileid (str): The profile ID.
            rfmgmtid (str): The RF management ID.

        Returns:
            dict: The response from the add operation.
        """
        s = self.get(self.refresh().nameToId(siteName))[0]
        group = {"groupName": groupName,
                 "rfMgmtPolicyId": rfmgmtid,
                 "profileId": profileid}
        s.deviceGroups.append(group)
        resp = self.set(s)
        return resp

    def addApGroupByName(self, siteName: str, groupName: str, profileName: str, rfName: str) -> dict:
        """
        Add a device group by profile and RF name.

        Args:
            siteName (str): The name of the site.
            groupName (str): The name of the group.
            profileName (str): The name of the profile.
            rfName (str): The name of the RF.

        Returns:
            dict: The response from the add operation.
        """
        profileMgr = self.client.profiles.refresh()
        rfMgr = self.client.rfmgmtprofiles.refresh()
        return self.addApGroup(siteName, groupName,
                               profileMgr.getByName(profileName).id,
                               rfMgr.getByName(rfName).id)

    def assignApToGroup(self, siteName: str, groupName: str, apSerial: str) -> dict:
        """
        Assign an AP to a group.

        Args:
            siteName (str): The name of the site.
            groupName (str): The name of the group.
            apSerial (str): The serial number of the AP.

        Returns:
            dict: The response from the assign operation.
        """
        s = self.get(self.refresh().nameToId(siteName))[0]
        for i, group in enumerate(s.deviceGroups):
            if group['groupName'] == groupName:
                group['apSerialNumbers'].append(apSerial)
                s.deviceGroups[i] = group

        resp = self.set(s)
        return resp

    def create(self, name: str, country: str = None, features = None) -> requests.Response:
        """
        Create a new site with the given name, country, and features.

        Args:
            name (str): The name of the site.
            country (str, optional): The country of the site.
            features (optional): Additional features for the site.

        Returns:
            requests.Response: The response from the create operation.
        """
        default = super(Sites, self).get('default', path=self._path)[0]
        default.siteName = name
        default.timezone = 'America/Toronto'
        if country is not None:
            default.country = country
        if features is not None:
            default.features = features

        #create new site
        resp = super(Sites, self).createCustom(default, path=self._path)
        return resp

    def getByName(self, siteName: str) -> requests.Response:
        """
        Retrieve a site by its name.

        Args:
            siteName (str): The name of the site to retrieve.

        Returns:
            requests.Response: The response containing the site data.
        """
        uuid = self.nameToId(siteName)
        return self.get(uuid)[0] if uuid is not None else None

    def getCountryList(self) -> dict:
        """
        Retrieve the country list using a path parameter method.

        Returns:
            dict: The country list.
        """
        return self.getWithPathParam(pathParam="countrylist")

    def getSitesList(self) -> list:
        """
        Retrieve the list of sites.

        Returns:
            list: The list of sites.
        """
        site_list = self.get()
        return site_list

    def getStationsList(self) -> requests.Response:
        """
        Get a list of user devices with Wi-Fi capability.

        Returns:
            requests.Response: The response containing the list of stations.
        """
        path = "management/v1/stations"
        resp = self.client.requestsWrapper(actionParams.GET, self.client.url + path + "/query?", params=None)
        return resp

    def removeApFromGroup(self, siteName, groupName, apSerial) -> dict:
        """
        Remove an AP from a group.

        Args:
            siteName (str): The name of the site.
            groupName (str): The name of the group.
            apSerial (str): The serial number of the AP.

        Returns:
            dict: The response from the remove operation.
        """
        s = self.get(self.refresh().nameToId(siteName))[0]
        for i, group in enumerate(s.deviceGroups):
            if group['groupName'] == groupName:
                group['apSerialNumbers'].remove(apSerial)
                s.deviceGroups[i] = group

        resp = self.set(s)
        return resp

    def removeApGroup(self, siteName: str, groupName: str) -> dict:
        """
        Remove an AP group.

        Args:
            siteName (str): The name of the site.
            groupName (str): The name of the group.

        Returns:
            dict: The response from the remove operation.
        """
        s = self.get(self.refresh().nameToId(siteName))[0]
        s.deviceGroups = [x for x in s.deviceGroups if x['groupName'] != groupName]
        resp = self.set(s)
        return resp

    def stations(self, site_name: str) -> requests.Response:
        """
        Get a list of stations for a specific site.

        Args:
            site_name (str): The name of the site.

        Returns:
            requests.Response: The response containing the list of stations.
        """
        siteid = self.refresh().getByName(site_name).id
        uri = "{host}{path}/{id}/stations".format(host = self.client.url,
                                                    path = self.client.rest[self._path],
                                                    id = siteid)
        resp = self.client.requestsWrapper(actionParams.GET, uri, params="")
        return resp


class TechSupport:
    """
    Tech Support class for managing tech support operations on the Appliance.

    Methods:
        __init__(client):
            Initialize the TechSupport class with a client.

        delete(name: str) -> requests.Response:
            Delete a specific tech support file.

        generate(mode="all", apNoStats=True, defaultGuiName=False) -> str:
            Generate a tech support file.

        get(name: str) -> str:
            Retrieve a specific tech support file.

        list() -> list:
            List all tech support files.

        status() -> requests.Response:
            Get the status of tech support files.

    """
    def __init__(self, client) -> None:
        """
        Initialize the TechSupport class.

        Args:
            client: The client instance to use for making requests.
        """
        self.client = client #reference to client
        self._path = "techsupp"
        self._pathString = self.client.rest[self._path]

    def delete(self, name) -> requests.Response:
        """
        Delete a specific tech support file.

        Args:
            name (str): The name of the tech support file to delete.

        Returns:
            requests.Response: The response from the delete operation.
        """
        resp = self.client.requestsWrapper(actionParams.DELETE, f"{self.client.url}{self._pathString}/file/{name}",
                                           params=None)
        return resp

    def generate(self, mode = "all", apNoStats=True, defaultGuiName=False) -> str:
        """
        Generate a tech support file.

        Args:
            mode (str): The mode for generating the file. Default is "all".
            apNoStats (bool): Flag to include or exclude AP stats. Default is True.
            defaultGuiName (bool): Flag to use the default GUI name. Default is False.

        Returns:
            str: The ID of the generated tech support file.
        """
        if defaultGuiName:
            body = {"mode":mode,"apNoStats":apNoStats}
        else:
            filename = "tech_support_sdk.{d}".format(d = datetime.today().strftime("%Y%m%d.%H%M%S"))
            body = {"filename":filename,"mode":mode,"apNoStats":apNoStats}
        resp=self.client.requestsWrapper(actionParams.POST, f"{self.client.url}{self._pathString}/generate",
                                             json=body)
        if not resp.ok:
            #print (resp.content)
            return None
        if defaultGuiName:
            return "default"
        return f'{filename}.tar.gz'

    def get(self, name: str) -> str:
        """
        Retrieve a specific tech support file.

        Args:
            name (str): The name of the tech support file to retrieve.

        Returns:
            str: The name of the retrieved tech support file.
        """
        resp = self.client.requestsWrapper(actionParams.GET, f"{self.client.url}{self._pathString}/file/{name}",
                                           params=None, stream=True)
        if not resp.ok:
            # print (resp.content)
            return None

        with open(name, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    f.flush()
        return name

    def list(self) -> dict:
        """
        List all tech support files.

        Returns:
            dict: A dictionary containing the list of tech support files.
        """
        resp=self.client.requestsWrapper(actionParams.GET, f"{self.client.url}{self._pathString}/listall")
        return json.loads(resp.content)

    def status(self)-> requests.Response:
        """
        Get the status of tech support file.

        Args:


        Returns:
            requests.Response: The response containing the status of tech support files.
        """
        resp=self.client.requestsWrapper(actionParams.GET, f"{self.client.url}{self._pathString}/status")
        return resp


class Topologies(Base):
    """
    Topologies class for managing topologies on the Appliance.

    Methods:
        __init__(client):
            Initialize the Topologies class.

        create(name: str, type: Mode = Mode.bap, vlanid=100, tagged=True, concentrators=[], port: Port = Port.none) -> requests.Response:
            Create a new topology with the provided name, type, VLAN ID, tagged status, concentrators, and port.

        createFabric(name: str, vlanid=100, isid=10) -> requests.Response:
            Create a new Fabric topology with the provided name, VLAN ID, and ISID.

        createGre(name: str, vlanid=100, concentratorList: list=[], tagged=True) -> requests.Response:
            Create a new GRE topology with the provided name, VLAN ID, concentrator list, and tagged status.

        createVlanGroup(name: str, mode: Mode, pool: list, vlanID: str) -> requests.Response:
            Create a VLAN group with the provided name, mode, pool, and VLAN ID.

        createVxlan(name: str, vlanid=100, vni=10, vtep="10.10.10.1") -> requests.Response:
            Create a new VXLAN topology with the provided name, VLAN ID, VNI, and VTEP.

        deleteTopology(name: str) -> requests.Response:
            Delete the specified topology by its name.

        setL3Mgmt(name: str, mgmt: bool, ip: str, cidr: str, foreignIp: str, dhcpMode: DhcpMode, dhcpGw: str, dhcpPool: List[str], dhcpDomain: str = "", dhcpDns: List[str] = [], dhcpWins: List[str] = []) -> requests.Response:
            Set L3 management settings for the specified topology.

        updateTopology(name: str, vlanid: int, tagged: bool = None, port: Port = Port.none, vni: int = None, vtep: str = None, concentratorList = None, isid: int = None) -> requests.Response:
            Update the specified topology with the provided settings.
    """

    def __init__(self, client) -> None:
        """
        Initialize the Topologies class.

        Args:
            client: The client instance to use for making requests.
        """
        super(Topologies, self).__init__(client)
        self._id='id'
        self._path = 'topologies'
        self._name= 'name'

    class Port(int, Enum):
        """
        Enumeration for different ports.

        Attributes:
            none (int): No port.
            port1 (int): Port 1.
            port2 (int): Port 2.
            port3 (int): Port 3.
            port4 (int): Port 4.
        """
        none = -1
        port1 = 0
        port2 = 1
        port3 = 2
        port4 = 3

    class Mode(str, Enum):
        """
        Enumeration for different topology modes.

        Attributes:
            bap (str): Bridged at AP.
            bac (str): Bridged at AC.
            fabric (str): Fabric Attach.
            vxlan (str): VXLAN.
            gre (str): GRE.
        """
        bap = "BridgedAtAp"
        bac = "BridgedAtAc"
        fabric = "FabricAttach"
        vxlan = "Vxlan"
        gre = "Gre"

    class DhcpMode(str, Enum):
        """
        Enumeration for different DHCP modes.

        Attributes:
            local (str): Local DHCP mode.
            none (str): No DHCP.
            relay (str): DHCP Relay mode.
        """
        local = "DHCPLocal"
        none = "DHCPNone"
        relay = "DHCPRelay"

    def create(self, name:str, type: Mode = Mode.bap, vlanid=100, tagged=True, concentrators=[],
                port: Port = Port.none) -> requests.Response:
        """
        Create a new topology with the provided name, type, VLAN ID, tagged status, concentrators, and port.

        Args:
            name (str): The name of the topology.
            type (Mode, optional): The type of the topology. Default is Mode.bap.
            vlanid (int, optional): The VLAN ID for the topology. Default is 100.
            tagged (bool, optional): Flag to indicate if the VLAN is tagged. Default is True.
            concentrators (list, optional): List of concentrators. Default is an empty list.
            port (Port, optional): The port for the topology. Default is Port.none.

        Returns:
            requests.Response: The response from the create operation.
        """
        #get the default site, set required fields name and timezone
        default = super(Topologies, self).get('default', path=self._path)[0]
        default.name = name
        default.vlanid = vlanid
        default.mode = type
        default.tagged = tagged
        if type == self.Mode.bac:
            default.vlanMapToEsa = port
        elif type == self.Mode.gre:
            default.concentrators = concentrators
        #create new topo
        resp = self.createCustom(default, path=self._path)
        return resp

    def createFabric(self, name: str, vlanid=100, isid=10) -> requests.Response:
        """
        Create a new Fabric topology with the provided name, VLAN ID, and ISID.

        Args:
            name (str): The name of the topology.
            vlanid (int, optional): The VLAN ID for the topology. Default is 100.
            isid (int, optional): The Fabric ISID. Default is 10.

        Returns:
            requests.Response: The response from the create operation.
        """
        self.create(name, self.Mode.bap, vlanid, tagged=True)
        vlan = super(Topologies, self).refresh().getByName(name)
        vlan.mode = self.Mode.fabric
        vlan.isid = isid
        resp = super(Topologies, self).set(vlan)
        return resp

    def createGre(self, name: str, vlanid=100, concentratorList: list = [], tagged=True) -> requests.Response:
        """
        Create a new GRE topology with the provided name, VLAN ID, concentrator list, and tagged status.

        Args:
            name (str): The name of the topology.
            vlanid (int, optional): The VLAN ID for the topology. Default is 100.
            concentratorList (list, optional): List of concentrators. Default is an empty list.
            tagged (bool, optional): Flag to indicate if the VLAN is tagged. Default is True.

        Returns:
            requests.Response: The response from the create operation.
        """
        if type(concentratorList) == str:
            concentratorList = [concentratorList]
        resp = self.create(name, self.Mode.gre, vlanid, tagged, concentrators=concentratorList)
        return resp

    def createVxlan(self, name:str, vlanid=100, vni=10, vtep="10.10.10.1") -> requests.Response:
        """
        Create a new VXLAN topology with the provided name, VLAN ID, VNI, and VTEP.

        Args:
            name (str): The name of the topology.
            vlanid (int, optional): The VLAN ID for the topology. Default is 100.
            vni (int, optional): The VXLAN Network Identifier. Default is 10.
            vtep (str, optional): The VXLAN Tunnel Endpoint. Default is "10.10.10.1".

        Returns:
            requests.Response: The response from the create operation.
        """
        self.create(name, self.Mode.bap, vlanid, tagged=False)
        vlan = super(Topologies, self).refresh().getByName(name)
        vlan.mode = self.Mode.vxlan
        vlan.vni = vni
        vlan.remoteVtepIp = vtep
        resp = super(Topologies, self).set(vlan)
        return resp

    def createVlanGroup(self, name: str, mode: Mode, pool: list, vlanID: str) -> requests.Response:
        """
        Create a VLAN group with the provided name, mode, pool, and VLAN ID.

        Args:
            name (str): The name of the VLAN group.
            mode (Mode): The mode of the VLAN group.
            pool (list): The pool of VLANs.
            vlanID (str): The VLAN ID.

        Returns:
            requests.Response: The response from the create operation.
        """
        pool_ID_list = [self.refresh().nameToId(x) for x in pool]
        payload = {
            "name": name,
            "mode": mode,
            "id": "",
            "vlanid": vlanID,
            "pool": pool_ID_list,
        }

        resp = self.client.requestsWrapper(actionParams.POST, self.client.url + self.client.rest["topologies"],
                                           json=payload)
        return resp

    def deleteTopology(self, name: str) -> requests.Response:
        """
        Delete the specified topology by its name.

        Args:
            name (str): The name of the topology.

        Returns:
            requests.Response: The response from the delete operation.
        """
        topologyID = self.refresh().nameToId(name)
        resp = self.client.requestsWrapper(actionParams.DELETE,
                                           self.client.url + self.client.rest['topologies'] + "/" + topologyID)
        return resp

    def setL3Mgmt(self, name, mgmt, ip, cidr, foreignIp,
                        dhcpMode: DhcpMode, dhcpGw, dhcpPool:List[str],
                        dhcpDomain:str = "", dhcpDns: List[str] = [], dhcpWins: List[str] = [],) -> requests.Response:
        """
        Set L3 management settings for the specified topology.

        Args:
            name (str): The name of the topology.
            mgmt (bool): Flag to enable management traffic.
            ip (str): The IP address for the topology.
            cidr (str): The CIDR for the topology.
            foreignIp (str): The foreign IP address.
            dhcpMode (DhcpMode): The DHCP mode.
            dhcpGw (str): The DHCP gateway.
            dhcpPool (List[str]): The DHCP pool.
            dhcpDomain (str, optional): The DHCP domain. Default is an empty string.
            dhcpDns (List[str], optional): The DHCP DNS servers. Default is an empty list.
            dhcpWins (List[str], optional): The DHCP WINS servers. Default is an empty list.

        Returns:
            requests.Response: The response from the set operation.
        """
        vlan = self.refresh().getByName(name)
        vlan.l3Presence = True
        vlan.enableMgmtTraffic = mgmt
        vlan.ipAddress = ip
        vlan.cidr = cidr
        vlan.dhcpMode = dhcpMode
        vlan.gateway = dhcpGw
        vlan.dhcpStartIpRange = dhcpPool[0]
        vlan.dhcpEndIpRange = dhcpPool[1]
        vlan.dhcpDomain = dhcpDomain
        vlan.dhcpDefaultLease = 36000
        vlan.dhcpMaxLease = 2592000
        vlan.dhcpDnsServers = ",".join(dhcpDns)
        vlan.wins = ",".join(dhcpWins)
        vlan.foreignIpAddress = foreignIp
        resp = self.set(vlan)
        return resp
    
    def updateTopology(self, name:str, vlanid:int, tagged:bool = None, port:Port = Port.none, vni:int = None, 
                vtep:str = None, concentratorList = None, isid:int = None) -> requests.Response:
        """
        Update the specified topology with the provided settings.

        Args:
            name (str): The name of the topology.
            vlanid (int): The VLAN ID for the topology.
            tagged (bool, optional): Flag to indicate if the VLAN is tagged. Default is None.
            port (Port, optional): The port for the topology. Default is Port.none.
            vni (int, optional): The VXLAN Network Identifier. Default is None.
            vtep (str, optional): The VXLAN Tunnel Endpoint. Default is None.
            concentratorList (list, optional): List of concentrators. Default is None.
            isid (int, optional): The Fabric ISID. Default is None.

        Returns:
            requests.Response: The response from the update operation.
        """
        vlan = super(Topologies, self).refresh().getByName(name)
        topologyID = self.refresh().nameToId(name)
        vlan.vlanid = vlanid
        if vlan.mode == self.Mode.bap:
            vlan.tagged = tagged
        elif vlan.mode == self.Mode.bac:
            vlan.tagged = tagged
            vlan.vlanMapToEsa = port
        elif vlan.mode == self.Mode.vxlan:
            vlan.vni = vni
            vlan.vtep = vtep
        elif vlan.mode == self.Mode.gre:
            vlan.tagged = tagged
            vlan.concentrators = concentratorList
        elif vlan.mode == self.Mode.fabric:
            vlan.isid = isid
        resp = self.set(vlan, topologyID, 'topologies')
        return resp
