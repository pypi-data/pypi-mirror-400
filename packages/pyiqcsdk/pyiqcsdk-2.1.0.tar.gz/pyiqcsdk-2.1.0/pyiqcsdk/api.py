#  This module is the ExCloud Appliance Data model Elements.
#   To communicate with the XCA, you first need to instantiate a client.
#   The easiest way to do that is by instantiating a Client class.

import requests
import logging
import time
import datetime

from .parts import (actionParams, AAAPolicy, AccessRules, Airdefense, AnalyticsProfiles, Appkeys, Aps, APTestRun,
                    APTestSuite, BestPracticesMgr, ChannelInspector, ConcentratorManager, ContainerTemplates, Cos,
                    GeoLocation, iotProfiles, LDAP, Licenses, Location, Mus, Networks, Pcap, PcapFiles, PlatformMgr,
                    Plans, Positioning, Profiles, Radios, Radius, Ratelimiters, Reports, RfMgmtProfiles, Roles,
                    RTLS, Sites, Scheduler, TechSupport, Topologies)


class Client:
    """
    API Client for interacting with the ExCloud Appliance.

    Methods:
        __init__(user: str, passw: str, url: str, token=None, exp="7200", max_retries=10):
            Initialize the Client class.
            The OAUTH2 token expiration time can be requested in the range of 60 seconds to 86,400 seconds (24 hours).

        delToken() -> requests.Response:
            Delete the authentication token.

        refreshToken() -> requests.Response:
            Refresh the authentication token.

        requestsWrapper(action: actionParams, request, json=None, params=None, stream=None, files=None) -> requests.Response:
            Wrapper for making HTTP requests with retry logic.

        rest_requests(action: actionParams, request, json=None, params=None, stream=None, files=None, DEBUG=False, retries=3, backoff_factor=1) -> requests.Response:
            Wrapper for making REST API requests with retry and backoff logic.

        aaapolicy() -> AAAPolicy:
            Get the AAAPolicy instance.

        accessrules() -> AccessRules:
            Get the AccessRules instance.

        airdefense() -> Airdefense:
            Get the Airdefense instance.

        analyticsprofiles() -> AnalyticsProfiles:
            Get the AnalyticsProfiles instance.

        appkeys -> Appkeys:
            Get the Appkeys instance.

        aps() -> Aps:
            Get the Aps instance.

        aptestrun() -> APTestRun:
            Get the APTestRun instance.

        aptestsuite() -> APTestSuite:
            Get the APTestSuite instance.

        bestPracticesMgr() -> BestPracticesMgr:
            Get the BestPracticesMgr instance.

        channelinspector() -> ChannelInspector:
            Get the ChannelInspector instance.

        concentratorMgr() -> ConcentratorManager:
            Get the ConcentratorManager instance.

        containerSchedule() -> Scheduler:
            Get the Scheduler instance.

        containerTemplates() -> ContainerTemplates:
            Get the ContainerTemplates instance.

        cos() -> Cos:
            Get the Cos instance.

        geolocation() -> GeoLocation:
            Get the GeoLocation instance.

        iotprofiles() -> iotProfiles:
            Get the iotProfiles instance.

        ldap() -> LDAP:
            Get the LDAP instance.

        licenses() -> Licenses:
            Get the Licenses instance.

        location() -> Location:
            Get the Location instance.

        mus() -> Mus:
            Get the Mus instance.

        networks() -> Networks:
            Get the Networks instance.

        pcap() -> Pcap:
            Get the Pcap instance.

        pcapFiles() -> PcapFiles:
            Get the PcapFiles instance.

        platformMgr() -> PlatformMgr:
            Get the PlatformMgr instance.

        plans() -> Plans:
            Get the Plans instance.

        positioning() -> Positioning:
            Get the Positioning instance.

        profiles() -> Profiles:
            Get the Profiles instance.

        radios() -> Radios:
            Get the Radios instance.

        radius() -> Radius:
            Get the Radius instance.

        ratelimiters() -> Ratelimiters:
            Get the Ratelimiters instance.

        reports() -> Reports:
            Get the Reports instance.

        rfmgmtprofiles() -> RfMgmtProfiles:
            Get the RfMgmtProfiles instance.

        roles() -> Roles:
            Get the Roles instance.

        RTLS() -> RTLS:
            Get the RTLS instance.

        sites() -> Sites:
            Get the Sites instance.

        techsupp() -> TechSupport:
            Get the TechSupport instance.

        topologies() -> Topologies:
            Get the Topologies instance.
    """
    
    def __init__(self, user: str, passw: str, url: str, token=None, exp="7200", max_retries=10) -> None:
        """
        Initialize the Client class.

        Args:
            user (str): The username for authentication.
            passw (str): The password for authentication.
            url (str): The base URL of the ExCloud Appliance.
            token (str, optional): The authentication token. Defaults to None.
            exp (str, optional): The token expiration time in seconds. Defaults to "7200".
            max_retries (int, optional): The maximum number of retries for requests. Defaults to 10.

        Usage:
            >>> from xcc.api import Client
            >>> c = Client("admin", "abcd1234", "https://10.49.31.123:5825/")
        """
        self.rest = {
            "aaapolicy": "management/v1/aaapolicy",
            "aaapolicyidmap": "management/v1/aaapolicy/nametoidmap",
            "accesseventslog": "platformmanager/v1/logging/accessevents",
            "admin": "platformmanager/v1/admin",
            "administrators": "management/v1/administrators",
            "afc": "management/v1/aps/afc/query",
            "airdefense": "management/v4/airdefense",
            "airdefenseidmap": "management/v4/airdefense/nametoidmap",
            "allowDenyList": "management/v1/accesscontrol",
            "analytics": "management/v3/analytics",
            "analyticsidmap": "management/v3/analytics/nametoidmap",
            "apimages": "platformmanager/v1/upgrades/apimages",
            "aplog": "platformmanager/v1/logging/aps/events/query",
            "appkeys": "management/v1/appkeys",
            "apps": "orchestration/v1/apps",
            "aps": "management/v1/aps",
            "apsq": "management/v1/aps/query",
            "assignfloor": "management/v1/aps/assign/floor",
            "auditlogs": "platformmanager/v1/logging/auditlogs",
            "availability": "platformmanager/v1/availability",
            "backupfileToLocal": "platformmanager/v1/configuration/backupfile",
            "bestpractices": "management/v1/bestpractices",
            "cert": "management/v1/aps/cert",
            "channelinspector": "management/v1/channelinspector",
            "cloneap": "management/v1/aps/clone",
            "concentrators": "management/v1/concentrators",
            "concentratorsdefault": "management/v1/concentrators/default",
            "concentratorsidmap": "management/v1/concentrators/nametoidmap",
            "cos": "management/v1/cos",
            "cosidmap": "management/v1/cos/nametoidmap",
            "containerSchedule": "apps/extreme-scheduler/api/v1/schedule",
            "containerTemplates": "orchestration/v1/templates",
            "createbackup": "platformmanager/v1/configuration/createbackup",
            "defaultgateway": "platformmanager/v1/routes/defaultgateway",
            "delap": "management/v1/aps/list",
            "delbackupfile": "platformmanager/v1/configuration/backupfile",
            "delImage": "/platformmanager/v1/upgrades/upgradeimage",
            "diagnosticcredentials": "access-control/v1/nac_engine_settings/diagnostic_credentials",
            "eventslog": "platformmanager/v1/logging/events/query/columns",
            "floorloc": "management/v3/sites/report/location/floor/{fid}",
            "ftpBackupTo": "platformmanager/v1/configuration/copybackupto/ftp",
            "ftpImage": "platformmanager/v1/upgrades/copyupgradefrom/ftp",
            "ftpRestoreFrom": "platformmanager/v1/configuration/copyrestorefrom/ftp",
            "generated": "management/v1/reports/generated",
            "geolocation": "management/v1/geolocation",
            "getbackuplist": "platformmanager/v1/configuration/backupfilelist",
            "getImages": "platformmanager/v1/upgrades/upgradeimagelist",
            "getInterfaces": "platformmanager/v1/interfaces",
            "hostattributes": "platformmanager/v1/hostattributes",
            "interfaces": "platformmanager/v1/interface",
            "iotprofile": "management/v3/iotprofile",
            "iotprofileidmap": "management/v3/iotprofile/nametoidmap",
            "l2ports": "platformmanager/v1/l2ports",
            "l2stats": "platformmanager/v1/report/l2ports",
            "ldap": "access-control/v1/ldap_configurations",
            "LicenseDetailsReport": "platformmanager/v1/licenses/subscription/detailsreport",
            "LicensePilot": "platformmanager/v1/license/pilot",
            "LicenseSync": "platformmanager/v1/licenses/subscription/activationupdate",
            "localupgrade": "platformmanager/v1/upgrades/dolocalupgrade/none",
            "location": "management/v1/report/location/stations",
            "logLevel": "platformmanager/v1/logging/systemloglevel",
            "manufacturing_info": "platformmanager/v1/reports/manufacturinginformation",
            "mapservices": "rfplanner/api/v1/maps",
            "mapservices-export-xml": "rfplanner/api/v1/export/xml",
            "mapservices-plan": "rfplanner/api/v1/maps/plan",
            "meshpoints": "management/v3/meshpoints",
            "meshpointstree": "management/v3/meshpoints/tree",
            "mudisassociate": "management/v1/stations/disassociate",
            "mu_report": "management/v1/report/stations",
            "muactions": "access-control/v1/end_systems",
            "muloc": "management/v1/stations/{mac}/location",
            "mus": "management/v1/stations/query",
            "mus2": "management/v2/stations/query",
            "networks": "management/v1/services",
            "networksidmap": "management/v1/services/nametoidmap",
            "network_health": "management/v1/report/sites",
            "ntp": "platformmanager/v1/ntpsettings",
            "ntpStatus": "platformmanager/v1/ntpsettings/status",
            "packetcapturefiles": "/platformmanager/v1/appacketcapturefiles",
            "packetcapturestatus": "/platformmanager/v2/appacketcapturestatus",
            "pcap": "platformmanager/v3/packetcapture",
            "pcap_files": "platformmanager/v3/packetcapture/files",
            "pcapidmap": "platformmanager/v3/packetcapture/nametoidmap",
            "ping": "platformmanager/v1/network/test/ping",
            "platformMgr": "platformmanager/v1",
            "portals": "access-control/v1/portals/locations",
            "portals_ecp": "access-control/v1/portals/ffecp/locations",
            "positioning": "management/v3/positioning",
            "positioningidmap": "management/v3/positioning/nametoidmap",
            "profiles" : "management/v3/profiles",
            "profilesidmap" : "management/v3/profiles/nametoidmap",
            "productenv": "platformmanager/v1/productenv",
            "radios": "management/v1/radios",
            "radiusDefaultAAA": "access-control/v1/aaa",
            "radiusLocal": "access-control/v1/local_password_repos/Default",
            "radiusLogin": "platformmanager/v1/radiuslogin",
            "radiusLoginV2": "platformmanager/v2/radiuslogin",
            "radiusNetworksAAA": "access-control/v1/aaa/location",
            "radiusServer": "access-control/v1/radius_servers",
            "ratelimiters": "management/v1/ratelimiters",
            "ratelimitersidmap": "management/v1/ratelimiters/nametoidmap",
            "refresh_token": "management/v1/oauth2/refreshToken",
            "reports": "management/v3/sites/report",
            "resetToDefaults": "platformmanager/v1/resettodefaults",
            "restart": "platformmanager/v1/restart",
            "restorefile": "platformmanager/v1/configuration/restorefile",
            "rfmgmt": "management/v3/rfmgmt",
            "rfmgmtidmap": "management/v3/rfmgmt/nametoidmap",
            "roles": "management/v3/roles",
            "rolesidmap": "management/v3/roles/nametoidmap",
            "routes": "platformmanager/v1/routes",
            "rtls": "management/v1/rtlsprofile",
            "rules": "access-control/v1/rules",
            "scpBackupTo": "platformmanager/v1/configuration/copybackupto/scp",
            "scpImage": "platformmanager/v1/upgrades/copyupgradefrom/scp",
            "scpRestoreFrom": "platformmanager/v1/configuration/copyrestorefrom/scp",
            "session_token": "management/v1/oauth2/token",
            "shutdown": "platformmanager/v1/shutdown",
            "sites": "management/v3/sites",
            "sitesidmap": "management/v3/sites/nametoidmap",
            "smartrf": "management/v2/aps",
            "smartrflog": "platformmanager/v1/logging/smartrf/events/query",
            "softwareActivationReport": "platformmanager/v1/license",
            "state": "management/v1/state",
            "stationlog": "platformmanager/v1/logging/stations/events/query",
            "stationQuery": "management/v1/stations/query",
            "statistics": "management/v1/report/aps",
            "syslog": "platformmanager/v1/logging/syslog",
            "syslogv2": "platformmanager/v2/logging/syslog",
            "systemtime": "platformmanager/v1/systemtime",
            "tcpdump": "platformmanager/v1/network/test/tcpdump",
            "techsupp": "platformmanager/v1/techsupport",
            "templateScheduled": "management/v1/reports/scheduled",
            "testsuites": "management/v1/apservices/testsuites",
            "testrun": "management/v1/apservices/testrun",
            "testsuitesidmap": "management/v1/apservices/testsuites/nametoidmap",
            "testrunidmap": "management/v1/apservices/testrun/nametoidmap",
            "timezone": "platformmanager/v1/timezone",
            "topologies": "management/v1/topologies",
            "topologiesidmap": "management/v1/topologies/nametoidmap",
            "traceroute": "platformmanager/v1/network/test/traceroute",
            "upgradedevices": "management/v1/report/upgrade/devices",
            "utilization": "management/v1/report/aps",
            "version": "platformmanager/v1/productversion",
            "websessiontimeout": "platformmanager/v1/websessiontimeout",
            "widgets": "management/v1/reports/templates"
        }
                
        self.url = url
        self.user = user
        self.passw = passw
        self.token = str(token)
        self.refresh_token = None
        self.resp = None
        self.max_retries = max_retries

        self.log = logging.getLogger("xcclog")
        self.log.setLevel(logging.INFO)
        # create file handler which logs even debug messages
        fh = logging.FileHandler("{0}.log".format("xccclient"), mode="w")
        fh.setLevel(logging.INFO)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(funcName)10s] %(message)s"
        )
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        # add the handlers to logger
        self.log.addHandler(ch)
        self.log.addHandler(fh)
        
        fh.close()

        if token is None:
            self.headers = None
            #get the auth token
            #some older XCC versions don't support the exp parameter, so if the exp parameter is set to the default value of 7200 seconds, 
            #then there is no need to pass it in the JSON payload
            if exp == "7200":
                data = {"grantType":"password","userId": self.user,"password": self.passw,"scope":"myScope"}
            else:
                data = {"grantType":"password","userId": self.user,"password": self.passw,"scope":"myScope", "exp": exp}
            resp = self.requestsWrapper(actionParams.POST, self.url + self.rest["session_token"], json = data)

            if resp.status_code == 200:
                self.token=str(resp.json()["access_token"])
                self.refresh_token = str(resp.json()["refresh_token"])
            else:
                logging.error(f"Could not get session token! Response code: {resp.status_code}")
                logging.error(f"Error: {resp.text}")
                self.token = None
                self.refresh_token = None
                return
            
        self.headers = {'Authorization':"Bearer " + self.token}

        #cached objects
        self._mus = self.mus
        self._aps = self.aps
        #some handy always present objects
        self.EnterpriseUserId = self.roles.refresh().nameToId("Enterprise User")
        self.bridgeAtAPId = self.topologies.refresh().nameToId("Bridged at AP untagged")
        #self.bridgeAtAPId = [x.id for x in self.topologies.get() if x.name == "Bridged at AP untagged"][0]

    def delToken(self) -> requests.Response:
        """
        Delete the authentication token.

        This method sends a request to delete the current authentication token, effectively logging out the user.

        Returns:
            requests.Response: The response from the server.

        Raises:
            requests.RequestException: If the request to delete the token fails.

        Usage:
            >>> client = Client("admin", "abcd1234", "https://10.49.31.123:5825/")
            >>> response = client.delToken()
            >>> print(response.status_code)
        """
        data = {}
        resp = self.requestsWrapper(actionParams.DELETE, self.url + self.rest["session_token"] + "/" + self.token,
                                    json=data)
        return resp

    def refreshToken(self) -> requests.Response:
        """
        Refresh the authentication token.

        This method sends a request to refresh the current authentication token using the refresh token.
        It updates the `token` and `refresh_token` attributes of the `Client` instance and sets the new
        authorization header.

        Returns:
            requests.Response: The response from the server containing the new tokens.

        Raises:
            requests.RequestException: If the request to refresh the token fails.

        Usage:
            >>> client = Client("admin", "abcd1234", "https://10.49.31.123:5825/")
            >>> response = client.refreshToken()
            >>> print(response.status_code)
        """
        data = {"grantType": "refresh_token", "userId": self.user, "refreshToken": self.refresh_token,
                "scope": "myScope"}
        resp = self.requestsWrapper(actionParams.POST, self.url + self.rest["refresh_token"], json=data)
        self.token = str(resp.json()["access_token"])
        self.refresh_token = str(resp.json()["refresh_token"])
        self.headers = {'Authorization': "Bearer " + self.token}
        return resp

    def requestsWrapper(self, action: actionParams, request, json=None, params=None, stream=None, files=None) -> requests.Response:
        """
        Wrapper for making HTTP requests with retry logic.

        Args:
            action (actionParams): The HTTP action to be performed (GET, POST, PUT, DELETE).
            request (str): The URL for the request.
            json (dict, optional): The JSON payload to be sent with the request. Defaults to None.
            params (dict, optional): The URL parameters to be sent with the request. Defaults to None.
            stream (bool, optional): Whether to stream the response content. Defaults to None.
            files (dict, optional): The files to be sent with the request. Defaults to None.

        Returns:
            requests.Response: The response from the server.

        Raises:
            Exception: If the request fails after the maximum number of retries.
        """
        trial = 0

        while trial < self.max_retries:
            try:
                if action == actionParams.GET:
                    self.resp = requests.get(request, headers=self.headers, json=json, params=params, verify=False, stream=stream, files=files)
                    return self.resp
                elif action == actionParams.POST:
                    self.resp = requests.post(request, headers=self.headers, json=json, params=params, verify=False, stream=stream, files=files)
                    return self.resp
                elif action == actionParams.PUT:
                    self.resp =  requests.put(request,  headers=self.headers, json=json, params=params, verify=False, stream=stream, files=files)
                    return self.resp
                elif action == actionParams.DELETE:
                    self.resp = requests.delete(request, headers=self.headers, json=json, params=params, verify=False, stream=stream, files=files)
                    return self.resp
                else:
                    self.resp = f'Invalid action: should be one of the following actions: {actionParams}'
                    return self.resp
            except Exception as e:
                # Retry:
                trial += 1
                logging.info(f"Retrying.... Trial {trial+1} {e}")

    def rest_requests(self, action: actionParams, request, json=None, params=None, stream=None, files=None, DEBUG=False, retries=3, backoff_factor=1) -> requests.Response:
        """
        Wrapper for making REST API requests with retry and backoff logic.

        Args:
            action (actionParams): The HTTP action to be performed (GET, POST, PUT, DELETE).
            request (str): The URL for the request.
            json (dict, optional): The JSON payload to be sent with the request. Defaults to None.
            params (dict, optional): The URL parameters to be sent with the request. Defaults to None.
            stream (bool, optional): Whether to stream the response content. Defaults to None.
            files (dict, optional): The files to be sent with the request. Defaults to None.
            DEBUG (bool, optional): Whether to log detailed request and response information. Defaults to False.
            retries (int, optional): The number of retry attempts. Defaults to 3.
            backoff_factor (int, optional): The backoff factor for retrying requests. Defaults to 1.

        Returns:
            requests.Response: The response from the server.

        Raises:
            ValueError: If the action is not supported.
            requests.RequestException: If the request fails after the maximum number of retries.
        """
        # Mapping actionParams to HTTP methods
        if action == actionParams.GET:
            method = 'GET'
        elif action == actionParams.POST:
            method = 'POST'
        elif action == actionParams.PUT:
            method = 'PUT'
        elif action == actionParams.DELETE:
            method = 'DELETE'
        else:
            raise ValueError(f"Unsupported action: {action}")

        # Prepare the request
        req = requests.Request(method, request, headers=self.headers, json=json, params=params, files=files)
        prepared = req.prepare()

        # Retry mechanism
        attempts = 0
        while attempts < retries:
            try:
                # If DEBUG is True, log request details before sending
                if DEBUG:
                    logging.info(f"<{datetime.datetime.now().ctime()}> Prepared REST Request (Attempt {attempts + 1}):")
                    logging.info(f"Rquqest Method: {prepared.method}")
                    logging.info(f"Request URL: {prepared.url}")
                    logging.info(f"Request Headers: {prepared.headers}")
                    logging.info(f"Request Body: {prepared.body}")

                # Send the prepared request
                session = requests.Session()
                response = session.send(prepared, verify=False, stream=stream)

                # If DEBUG is True, log response details after receiving
                if DEBUG:
                    logging.info(f"<{datetime.datetime.now().ctime()}> REST Response (Attempt {attempts + 1}):")
                    logging.info(f"Response status code: {response.status_code}")
                    logging.info(f"Response headers: {response.headers}")
                    logging.info(f"Response content: {response.text}")

                # Return the response if the request is successful
                return response

            except requests.RequestException as e:
                # Log the exception if DEBUG is True
                if DEBUG:
                    logging.error(f"<{datetime.datetime.now().ctime()}> Request failed with exception: {e}. Attempt {attempts + 1}")

                # Increment the attempt counter and apply backoff if more retries are allowed
                attempts += 1
                if attempts < retries:
                    time.sleep(backoff_factor * (2 ** (attempts - 1)))  # Exponential backoff
                else:
                    raise  # If total number of retries burned out, raise the exception

        return None  # This is just a safeguard, but execution will likely not reach here

    # managers
    @property
    def aaapolicy(self) -> AAAPolicy:
        """
        An object for managing AAA policy on the Appliance.

       Usage::
            >>> c.aaapolicy.get()
        """
        return AAAPolicy(client=self)

    @property
    def accessrules(self) -> AccessRules:
        """
        An object for managing AAA policy on the Appliance.

       Usage::
            >>> c.accessrules.get()
        """
        return AccessRules(client=self)

    @property
    def airdefense(self) -> Airdefense:
        """
        An object for managing airdefense on the Appliance.

        Usage:
            >>> c.airdefense.get()
        """
        return Airdefense(client=self)

    @property
    def analyticsprofiles(self) -> AnalyticsProfiles:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.analyticsprofiles.get()
        """
        return AnalyticsProfiles(client=self)

    @property
    def appkeys(self) -> Appkeys:
        """
        An object for managing App keys on the Appliance.

        Usage:
            >>> c.appkeys.get()
        """
        return Appkeys(client=self)

    @property
    def aps(self) -> Aps:
        """
        An object for managing APs on the Appliance.

        Usage:
            >>> c.aps.get()
        """
        return Aps(client=self)

    @property
    def aptestrun(self) -> APTestRun:
        """
        An object for managing AP Test Run on the Appliance.

        Usage:
            >>> c.aptestrun.get()
        """
        return APTestRun(client=self)

    @property
    def aptestsuite(self) -> APTestSuite:
        """
        An object for managing AP Test Suite on the Appliance.

        Usage:
            >>> c.aptestsuite.get()
        """
        return APTestSuite(client=self)

    @property
    def bestPracticesMgr(self) -> BestPracticesMgr:
        """
        An object for managing Best Practices on the Appliance.

        Usage:
            >>> c.bestPracticesMgr.evaluate()
        """
        return BestPracticesMgr(client=self)

    @property
    def channelinspector(self) -> ChannelInspector:
        """
        An object for channel inspector.

        Usage:
            >>> c.channelinspector.get()
        """
        return ChannelInspector(client=self)

    @property
    def concentratorMgr(self) -> ConcentratorManager:
        """
        An object for creating the concentrator configuration on the Appliance (XCC).

        Usage:
            >>> c.concentratorMgr.getConcentratorList()
        """
        return ConcentratorManager(client=self)

    @property
    def containerSchedule(self) -> Scheduler:
        """
        An object for managing schedule on the Appliance container.

        Usage:
            >>> c.containerSchedule.get()
        """
        return Scheduler(client=self)

    @property
    def containerTemplates(self) -> ContainerTemplates:
        """
        An object for managing Appliance containers.

        Usage:
            >>> c.containerTemplates.get()
        """
        return ContainerTemplates(client=self)

    @property
    def cos(self) -> Cos:
        """
        An object for managing Class Of Service on the Appliance.

        Usage:
            >>> c.cos.get()
        """
        return Cos(client=self)

    @property
    def geolocation(self) -> GeoLocation:
        """
        An object for managing Geolocation on the Appliance.

        Usage:
            >>> c.geolocation.autolocate()
        """
        return GeoLocation(client=self)

    @property
    def iotprofiles(self) -> iotProfiles:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.iotprofiles.get()
        """
        return iotProfiles(client=self)

    @property
    def ldap(self) -> LDAP:
        """
        An object for managing LDAP on the Appliance.

        Usage:
            >>> c.ldap.getConfigs()
        """
        return LDAP(client=self)

    @property
    def licenses(self) -> Licenses:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.licenses.LicensesReport()
        """
        return Licenses(client=self)

    @property
    def location(self) -> Location:
        """
        An object for managing location.

        Usage:
            >>> c.location.get("AA:BB:CC:DD:EE")
        """
        return Location(client=self)

    @property
    def mus(self) -> Mus:
        """An object for managing clients on the Appliance.

           Usage::

              >>> c.mus.get()
              [<xcc.parts.one at 0x22b861f4908>, <xcc.parts.one at 0x22b83ced108>]
        """
        return Mus(client=self)

    @property
    def networks(self) -> Networks:
        """
        An object for managing networks on the Appliance.

       Usage::
          >>> c.networks.get()
        """
        return Networks(client=self)

    @property
    def pcap(self) -> Pcap:
        """
        An object for managing packet capture on the Appliance.

        Usage:
            >>> c.pcap.startLocal("CV012408S-C0126")
        """
        return Pcap(client=self)

    @property
    def pcapFiles(self) -> PcapFiles:
        """
        An object for managing packet capture files on the Appliance.

        Usage:
            >>> c.pcapFiles.get()
        """
        return PcapFiles(client=self)

    @property
    def platformMgr(self) -> PlatformMgr:
        """
        An object for managing Platform related operations on the Appliance.

        Usage:
            >>> c.platformMgr.controllerRestart()
        """
        return PlatformMgr(client=self)

    @property
    def plans(self) -> Plans:
        """
        An object for managing plans on the Appliance.

        Usage:
            >>> c.plans.floorExport("47241d2f-977d-4b52-969d-f7593402bda5")
        """
        return Plans(client=self)

    @property
    def positioning(self) -> Positioning:
        """
        An object for managing positioning on the Appliance.

        Usage:
            >>> c.positioning.get()
        """
        return Positioning(client=self)

    @property
    def profiles(self) -> Profiles:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.profiles.get()
        """
        return Profiles(client=self)

    @property
    def radios(self) -> Radios:
        """
        An object for reading compliance data.

        Usage:
            >>> c.radios.channels()
        """
        return Radios(client=self)

    @property
    def radius(self) -> Radius:
        """
        An object for managing location.

        Usage:
            >>> c.location.get("AA:BB:CC:DD:EE")
        """
        return Radius(client=self)

    @property
    def ratelimiters(self) -> Ratelimiters:
        """
        An object for managing Rate Limiters on the Appliance.

        Usage:
            >>> c.ratelimiters.get()
        """
        return Ratelimiters(client=self)

    @property
    def reports(self) -> Reports:
        """
        An object for reading reports/datasets.

        Usage:
            >>> c.reports.dataset(key="ApTable", duration=Reports.Duration.d3H, foramt=Reports.DataFmt.json)
        """
        return Reports(client=self)

    @property
    def rfmgmtprofiles(self) -> RfMgmtProfiles:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.rfmgmtprofiles.get()
        """
        return RfMgmtProfiles(client=self)

    @property
    def roles(self) -> Roles:
        """
        An object for managing rf mgmt profiles on the Appliance.

        Usage:
            >>> c.roles.get()
        """
        return Roles(client=self)

    @property
    def RTLS(self) -> RTLS:
        """
        An object for managing RTLS profiles on the Appliance.
        Usage::
            >>> c.rtls.get()
        """
        return RTLS(client=self)

    @property
    def sites(self) -> Sites:
        """
        An object for managing sites on the Appliance.

        Usage:
            >>> c.sites.get()
        """
        return Sites(client=self)

    @property
    def techsupp(self) -> TechSupport:
        """
        An object for managing techsupport.

        Usage:
            >>> c.techsupp.get("name")
        """
        return TechSupport(client=self)

    @property
    def topologies(self) -> Topologies:
        """
        An object for managing topologies on the Appliance.

        Usage:
            >>> c.topologies.get()
        """
        return Topologies(client=self)
