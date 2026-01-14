from typing import overload
import pandas as pd
import os
import requests
import json
from datetime import datetime, timedelta
import nemreader
from bs4 import BeautifulSoup
from functools import reduce
import tempfile
import logging

logger = logging.getLogger('sapnmeterdatalib')

class LoginError(Exception):
    """Raised when login fails."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass
class AuthError(Exception):
    """Raised when failed to retrieved csrf and/or authorization."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass
class FetchError(Exception):
    """Raised when failed to retrieved meterdata."""
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    pass

class login:
    def __init__(self, email:str, password:str):
        self.email = email
        CADSiteLogin_url = 'https://customer.portal.sapowernetworks.com.au/meterdata/CADSiteLogin'
        CADSiteLogin_response = requests.post(CADSiteLogin_url)

        if CADSiteLogin_response.status_code == 200:
            soup = BeautifulSoup(CADSiteLogin_response.text, 'html.parser')
            ViewState = soup.find('input', {'type': 'hidden', 'id': 'com.salesforce.visualforce.ViewState'})['value']  # type: ignore
            ViewStateMAC = soup.find('input', {'type': 'hidden', 'id': 'com.salesforce.visualforce.ViewStateMAC'})['value']  # type: ignore
        else:
            raise LoginError("failed to access login page")

        if ViewState[:2] != "i:" or ViewStateMAC[:3] != "AGV":
            raise LoginError("failed to retrieve ViewState or ViewStateMAC")
        
        CADSiteLogin_url = 'https://customer.portal.sapowernetworks.com.au/meterdata/CADSiteLogin'
        CADSiteLogin_form_data = {
            "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm": "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm",
            "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:username": email,
            "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:password": password,
            "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:loginButton": "Login",
            "com.salesforce.visualforce.ViewState": ViewState,
            "com.salesforce.visualforce.ViewStateMAC": ViewStateMAC
        }
        CADSiteLogin_response = requests.post(CADSiteLogin_url, data=CADSiteLogin_form_data)

        if(CADSiteLogin_response.status_code == 200):
            logger.info("successfully logged in")
        else:
            raise LoginError("failed to login")
        text = CADSiteLogin_response.text
        self.sid = text[text.find("sid="):text.find("&",text.find("sid="))].replace("%21", "!")
        self.methods = {}
        link = text[text.find(".handleRedirect('")+17:text.find("'); }",text.find(".handleRedirect('")+17)]
        requests.get(link)
    def _updatedownloadNMIDataKeys(self):
        cadenergydashboard_url = "https://customer.portal.sapowernetworks.com.au/meterdata/CADRequestMeterData"
        cadenergydashboard_headers = {
            "Cookie": self.sid
        }

        cadenergydashboard_response = requests.get(cadenergydashboard_url, headers=cadenergydashboard_headers)
        cadenergydashboard_response_data = cadenergydashboard_response.text
        logger.debug(cadenergydashboard_response_data)
        cadenergydashboard_raw = cadenergydashboard_response_data[cadenergydashboard_response_data.find('{"name":"downloadNMIData"'):cadenergydashboard_response_data.find('"}',cadenergydashboard_response_data.find('{"name":"downloadNMIData"'))+2]
        downloadNMIData = json.loads(cadenergydashboard_raw)
        if 'csrf' in downloadNMIData and 'authorization' in downloadNMIData:
            logger.info('successfully retrieved csrf & authorization')
        else:
            raise AuthError('failed to retrieved csrf and/or authorization')

        self.methods[downloadNMIData['name']] = {}
        self.methods[downloadNMIData['name']]['csrf'] = downloadNMIData['csrf']
        self.methods[downloadNMIData['name']]['authorization'] = downloadNMIData['authorization']
    def _updategetNMIAssignmentsKeys(self):
        cadenergydashboard_url = "https://customer.portal.sapowernetworks.com.au/meterdata/CADAccountPage"
        cadenergydashboard_headers = {
            "Cookie": self.sid
        }
        cadenergydashboard_response = requests.get(cadenergydashboard_url, headers=cadenergydashboard_headers)
        cadenergydashboard_response_data = cadenergydashboard_response.text
        logger.debug(cadenergydashboard_response_data)
        cadenergydashboard_raw = cadenergydashboard_response_data[cadenergydashboard_response_data.find('{"name":"getNMIAssignments"'):cadenergydashboard_response_data.find('"}',cadenergydashboard_response_data.find('{"name":"getNMIAssignments"'))+2]
        getNMIAssignments = json.loads(cadenergydashboard_raw)
        if 'csrf' in getNMIAssignments and 'authorization' in getNMIAssignments:
            logger.info('successfully retrieved csrf & authorization')
        else:
            raise AuthError('failed to retrieved csrf and/or authorization')

        self.methods[getNMIAssignments['name']] = {}
        self.methods[getNMIAssignments['name']]['csrf'] = getNMIAssignments['csrf']
        self.methods[getNMIAssignments['name']]['authorization'] = getNMIAssignments['authorization']

    def getNMIs(self):
        self._updategetNMIAssignmentsKeys()
        getNMIAssignments_data = {
            "action":"CADEnergyDashboardController",
            "method":'getNmiAssignments',
            "type":"rpc",
            "tid":2,
            "data":None,
            "ctx": {
                "csrf": self.methods['getNMIAssignments']['csrf'],
                "vid":"06628000004kHTx",
                "ns":"",
                "ver":35,
                "authorization": self.methods['getNMIAssignments']['authorization']
            }
        }
        getNMIAssignments_headers = {
            "Content-Type": "application/json",
            "Referer":"https://customer.portal.sapowernetworks.com.au/meterdata/CADEnergyDashboard",
            "Cookie": self.sid
        }
        getNMIAssignments_url = "https://customer.portal.sapowernetworks.com.au/meterdata/apexremote"
        getNMIAssignments_response = requests.post(getNMIAssignments_url, headers=getNMIAssignments_headers, json=getNMIAssignments_data)
        getNMIAssignments_response_data = getNMIAssignments_response.text
        logger.debug(getNMIAssignments_response_data)
        getNMIAssignments = json.loads(getNMIAssignments_response_data)
        nmis = []
        print(getNMIAssignments)
        for nmi in getNMIAssignments[0]['result']:
            nmis.append(nmi['theNMI'])
        return nmis

class meter:
    def __init__(self, NMI:int, login_details:login):
        self.nmi = NMI
        self.login_details = login_details
    def getdata(self, startdate:datetime = datetime.today() - timedelta(2), enddate:datetime = datetime.today()):
        self.login_details._updatedownloadNMIDataKeys()
        downloadNMIData_data = {
            "action": "CADRequestMeterDataController",
            "method": 'downloadNMIData',
            "data": [
                self.nmi,
                "SAPN",
                startdate.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                enddate.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "Customer Access NEM12",
                "Detailed Report (CSV)",
                0
            ],
            "type": "rpc",
            "tid": 5,
            "ctx": {
                "csrf": self.login_details.methods['downloadNMIData']['csrf'],
                "vid": "06628000004kHU7",
                "ns": "",
                "ver": 35,
                "authorization": self.login_details.methods['downloadNMIData']['authorization']
            }
        }
        downloadNMIData_headers = {
            "referer": "https://customer.portal.sapowernetworks.com.au/meterdata/apex/cadenergydashboard"
        }
        downloadNMIData_url = "https://customer.portal.sapowernetworks.com.au/meterdata/apexremote"

        downloadNMIData_response = requests.post(downloadNMIData_url, headers=downloadNMIData_headers, json=downloadNMIData_data)
        downloadNMIData = json.loads(downloadNMIData_response.text)
        if 'message' in downloadNMIData[0]['result']:
            raise FetchError(downloadNMIData[0]['result']['message'])
        else:
            logger.info('successfully retrieved meterdata')
        self.data = downloadNMIData[0]['result']['results']

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(self.data)
            temp_path = f.name
        self.dataframes = nemreader.output_as_data_frames(temp_path, split_days=True, set_interval=None, strict=False)
        os.remove(temp_path)

        df = self.dataframes[0][1].drop(columns=['t_start', 'quality_method', 'evt_code', 'evt_desc'])
        for col in df.drop(columns=['t_end']).columns:
            df = df.rename(columns={col: f"{self.nmi}_{col}"})
        df.set_index('t_end', inplace=True)
        df.index = pd.to_datetime(df.index)
        df.columns = pd.MultiIndex.from_tuples([(str(self.nmi), c[-2:]) for c in df.columns], names=['meter', 'channel'])
        return df
        
@overload
def getall(meterlist: list[meter], start: datetime, end: datetime) -> pd.DataFrame: ...

@overload
def getall(meterlist: list[int], start: datetime, end: datetime, login_obj: login) -> pd.DataFrame: ...

def getall(meterlist, start, end, login_obj=None):
    meters = {}
    data = {}
    df = {}
    if isinstance(meterlist[0], meter):
        for nmi in meterlist:
            meters[nmi.nmi] = nmi
        nmis = list(meters.keys())
    else:
        if login_obj is None:
            raise ValueError("login must be provided when meterlist contains NMIs")
        for nmi in meterlist:
            meters[nmi] = meter(nmi, login_obj)
        nmis = meterlist
    for nmi in nmis:
        df[nmi] = meters[nmi].getdata(start, end)
    merged_df = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True, how='outer'), df.values())
    return merged_df