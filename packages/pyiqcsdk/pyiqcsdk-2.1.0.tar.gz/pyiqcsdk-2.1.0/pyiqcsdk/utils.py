import logging
import asyncio
from enum import Enum
from contextlib import contextmanager, asynccontextmanager
import time

logger = logging.getLogger(__name__)


class Results(Enum):
    PASSED = 'Passed'
    FAILED = 'Failed'
    SKIPPED = 'Skipped'

@contextmanager
def waitfor(condition, value, done: str ="", timeout = 20):
    """Wait for condition till it returns value up to timeout.
       On exit print PASS "done" message.
        
        :param condition: lambda function 
        :param value: stop condition (conditon() == value)
        :param done: message to print when success
        :param timeout: count in 5 sec intervals 
        :rtype: response status code

        Usage::   
            #wait for capture becomes active, stop the capture and download
            with waitfor(
                     condition = lambda: next((pf["id"] for pf in x.pcap.active() if pf["id"] == cap.id), None), 
                     value = cap.id, 
                     done="Packet capture stopped and downloaded"):
                x.pcap.stop(cap.id)
                res = x.pcapFiles.download(cap.storage["localStorage"])
                assert res == 200
    """
    newstatus = condition()
    count = 0
    while (newstatus != value):
        logger.info(f'{newstatus} != {value}')
        newstatus = condition()
        time.sleep(5)
        count +=1
        assert (count < timeout), f'{done} waited too long for {value}'
    yield
    logger.info(f'PASSED {done}')

@asynccontextmanager
async def awaitfor(condition, value, done: str ="", timeout = 20):
    """Wait for condition till it returns value up to timeout.
       On exit print PASS "done" message.
        
        :param condition: lambda function 
        :param value: stop condition (conditon() == value)
        :param done: message to print when success
        :param timeout: count in 5 sec intervals 
        :rtype: response status code

        Usage::   
            #wait for capture becomes active, stop the capture and download
            with waitfor(
                     condition = lambda: next((pf["id"] for pf in x.pcap.active() if pf["id"] == cap.id), None), 
                     value = cap.id, 
                     done="Packet capture stopped and downloaded"):
                x.pcap.stop(cap.id)
                res = x.pcapFiles.download(cap.storage["localStorage"])
                assert res == 200
    """
    newstatus = condition()
    count = 0
    while (newstatus != value):
        logger.info(f'Retry {done}: {newstatus} != {value}')
        newstatus = condition()
        await asyncio.sleep(5)
        count +=1
        assert (count < timeout), f'{done} waited too long for {value}'
    yield
    logger.info(f'PASSED {done}')
