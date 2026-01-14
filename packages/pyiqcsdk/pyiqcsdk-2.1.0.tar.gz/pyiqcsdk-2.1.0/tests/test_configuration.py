from xcc.api import Client
from xcc.parts import Networks
import time
import logging
from typing import BinaryIO, NamedTuple, List, Union, Dict
import asyncio
import re
from enum import Enum
import configparser
import os

from requests.packages import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

class LabConfigParams:
    def __init__(self, cfg_filename):
        self.config = configparser.ConfigParser()
        self.config.read(cfg_filename)
    def get(self, section, attrib):
        a = self.config.get(section, attrib)
        return a

test_prefix = "LAB_sanity"
privacy = [Networks.PrivacyEnum.wpa2_psk, Networks.PrivacyEnum.wpa2_enterprise]

def nets_names():    
    netsNames = [f'{test_prefix}_{x}' for x in privacy]
    return netsNames, privacy

def _config(cfg):
    """Test XCC configuation
       Setup Site, DevGroup, Profile, Networks and Assign AP to the Site  
       
       :param cfg: configuraton  from lab_setup.cfg file
    """
    x = Client(cfg.get(section="xcc", attrib='user'), 
               cfg.get(section="xcc", attrib='pswd'),
               f'https://{cfg.get(section="xcc", attrib="xca1")}:5825/')
    
    myapserial = cfg.get(section="AP", attrib="myap")
    
    try:
        myap = x.aps.getBySerial(myapserial)
        assert (myap != None), f"AP {myap.apName} not found, creat one first"
        sites=x.sites
        LOGGER.info(f'Delete sites with prefix {test_prefix}, {sites.deleteByPrefix(test_prefix)}')
        nets =x.networks
        LOGGER.info(f'Delete networks with prefix {test_prefix}, {nets.deleteByPrefix(test_prefix)}')
        profs=x.profiles
        LOGGER.info(f'Delete profiles with prefix {test_prefix}, {profs.deleteByPrefix(test_prefix)}')

        netsNames, _ = nets_names()
        for p in privacy:
            nname = f'{test_prefix}_{p}'
            LOGGER.info(f'Create network {nname}, {nets.create(nname, ssid=None, privacy=p)}')
        #       
        profName = f"{test_prefix}-AP410"
        LOGGER.info(f'Create profile {test_prefix}-AP410, {profs.create(profName, platf="AP410")}')
        for nn in netsNames:
            LOGGER.info(f'Network create {nn}, {profs.assignNetworkByName(f"{test_prefix}-AP410", nn, radio = 1)}')
            profs.assignNetworkByName(f"{test_prefix}-AP410", nn, radio = 2)
        #
        LOGGER.info(f'Create site {test_prefix}, {sites.create(test_prefix, country="UNITED_STATES")}')
        sites.removeApGroup(test_prefix,"AP410")
        sites.addApGroupByName(test_prefix,"AP410", f"{test_prefix}-AP410", "Default Smart RF")
        LOGGER.info(f'Assign AP {myapserial} to {test_prefix}, {sites.assignApToGroup(test_prefix,"AP410", myapserial)}')
    except AssertionError as e:
        LOGGER.info(f'FAIL: xcc {cfg.get("xcc", "xca1")} got assert: {e}')

def test_configuration():
    config_file_name = f"lab_setup.cfg"
    exists = os.path.isfile(config_file_name)
    if exists:
        setup = LabConfigParams(config_file_name)
        _config(setup)
    else:
        LOGGER.info("Configuratoin file {config_file_name} not found")

#test_configuration()