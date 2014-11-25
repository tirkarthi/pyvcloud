# VMware vCloud Python SDK
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# coding: utf-8

import base64
import requests
import StringIO
# from vclouddirector import VCD
from schema.vcim import serviceType, vchsType
import json

class VCA(object):

    def __init__(self):
        self.host = None
        self.token = None

    def login(self, host, username, password, token=None):
        if not (host.startswith('https://') or host.startswith('http://')):
            host = 'https://' + host
        if token:
            headers = {}
            headers["x-vchs-authorization"] = token
            headers["Accept"] = "application/xml;version=5.6"
            response = requests.get(host + "/api/vchs/services", headers=headers)
            if response.status_code == requests.codes.ok:
                self.host = host
                self.token = token
                return True
            else:
                return False
        else:
            url = host + "/api/vchs/sessions"
            encode = "Basic " + base64.encodestring(username + ":" + password)
            headers = {}
            headers["Authorization"] = encode.rstrip()
            headers["Accept"] = "application/xml;version=5.6"
            response = requests.post(url, headers=headers)
            if response.status_code == requests.codes.created:
                self.host = host
                self.token = response.headers["x-vchs-authorization"]
                return True
            else:
                return False
    
    def logout(self):
        url = self.host + "/api/vchs/session"
        headers = {}
        headers["x-vchs-authorization"] = self.token
        return requests.delete(url, headers=self._get_vchsHeaders())
        
    def _get_vchsHeaders(self):
        headers = {}
        headers["x-vchs-authorization"] = self.token
        headers["Accept"] = "application/xml;version=5.6"
        return headers
        
    def get_serviceReferences(self):
        response = requests.get(self.host + "/api/vchs/services", headers=self._get_vchsHeaders())
        serviceList = serviceType.parseString(response.content, True)
        return serviceList.get_Service()
    
    def get_vdcReferences(self, serviceReference):
        response = requests.get(serviceReference.get_href(), headers=self._get_vchsHeaders())
        compute = vchsType.parseString(response.content, True)
        return compute.get_VdcRef()
        
    def get_vdcReference(self, serviceId, vdcId):
        serviceReferences = filter(lambda serviceReference: serviceReference.get_serviceId().lower() == serviceId.lower(), self.get_serviceReferences())
        if serviceReferences:
            serviceReference = serviceReferences[0]
            vdcReferences = filter(lambda vdcRef: vdcRef.get_name().lower() == vdcId.lower(), self.get_vdcReferences(serviceReference))
            if vdcReferences:
                return (True, vdcReferences[0])
            else:
                return (False, None)
        else:
            return (False, None)        
            
    def create_vCloudSession(self, vdcReference):
        response = requests.get(vdcReference.get_href(), headers=self._get_vchsHeaders())
        compute = vchsType.parseString(response.content, True)
        link = filter(lambda link: link.get_type() == "application/xml;class=vnd.vmware.vchs.vcloudsession",
                      compute.get_Link())[0]
        response = requests.post(link.get_href(), headers = self._get_vchsHeaders())
        if response.status_code == requests.codes.created:
            vCloudSession = vchsType.parseString(response.content, True)
            return vCloudSession            
        
    # def get_gateway(self, gatewayId):
    #     vdcReference = self.get_vdcReference(gatewayId, gatewayId)
    #     if vdcReference[0] == True:
    #         vCloudSession = self.create_vCloudSession(vdcReference[1])
    #         if vCloudSession:
    #             vcd = VCD(vCloudSession, gatewayId, gatewayId)
    #             gateways = filter(lambda gateway: gateway.get_name() == gatewayId, vcd.get_gateways())
    #             if gateways:
    #                 return (True, gateways[0])
    #     return (False, None)
               
        
        
    


