from base import BaseboardManagementController

import sys
import json
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError
from .get_resource_directory import get_resource_directory

class ILOBMC(BaseboardManagementController):
    def __init__(self, ip, username, password, url):
        super(ILOBMC, self).__init__(ip, username, password, url)

        self._redfishobj = RedfishClient(base_url=url, username=username, password=password)
        try:
            self._redfishobj.login()
        except ServerDownOrUnreachableError as excp:
            sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
            sys.exit()
        self._resource_instances = get_resource_directory(self._redfishobj)

    def __del__(self):
        self._redfishobj.logout()

    def reboot_server(self):
        """Overrides"""
        sys_data = None

        for i in self._resource_instances:
            # Find the relevant URI
            if '#ComputerSystem.' in i['@odata.type']:
                sys_uri = i['@odata.id']
                sys_data = self._redfishobj.get(sys_uri)

        if sys_data is None:
            sys.stderr.write("Failure getting redfish Computer System uri...")
            return

        self._ilo_reboot(sys_data)

    def set_next_boot_virtual_CD(self):
        """Overrides"""
        virt_media_uri = None

        for i in self._resource_instances:
            # Find the relevant URI
            if '#VirtualMediaCollection.' in i['@odata.type']:
                virt_media_uri = i['@odata.id']
        
        if virt_media_uri is None:
            sys.stderr.write("Failure getting redfish VirtualMediaCollection uri...")
            return

        virt_media_data = self._redfishobj.get(virt_media_uri)
        for virt_media_slot in virt_media_data.obj['Members']:
            virt_cd_data = self._redfishobj.get(virt_media_slot['@odata.id'])

            if "CD" in virt_cd_data.dict['MediaTypes']:
                self._ilo_unmount_iso(virt_cd_data)
                self._ilo_mount_iso(virt_cd_data)
                self._ilo_set_on_next_server_reset(virt_cd_data)
    
    def _ilo_reboot(self, sys_data):
        uri = sys_data.obj['Actions']['#ComputerSystem.Reset']['target']
        body = dict()
        body['Action'] = 'ComputerSystem.Reset'
        body['ResetType'] = "ForceRestart"
        
        resp = self._redfishobj.post(uri, body)
        if resp.status == 400:
            try:
                print(json.dumps(resp.obj['error']['@Message.ExtendedInfo'], indent=4, \
                                                                                    sort_keys=True))
            except Exception as excp:
                sys.stderr.write("A response error occurred, unable to access iLO Extended "
                                "Message Info...")
        elif resp.status != 200:
            sys.stderr.write("An http response of \'%s\' was returned.\n" % resp.status)
        else:
            print("Success!\n")
            print(json.dumps(resp.dict, indent=4, sort_keys=True))

    def _ilo_unmount_iso(self, virt_cd_data):
        uri = virt_cd_data.obj['Actions']['#VirtualMedia.EjectMedia']['target']
        resp = self._redfishobj.post(uri, {})
        if not resp.status == 200:
            sys.stderr.write("Failure unmounting old iso")

    def _ilo_mount_iso(self, virt_cd_data):
        uri = virt_cd_data.obj['Actions']['#VirtualMedia.InsertMedia']['target']
        body = {"Image": self.url}
        resp = self._redfishobj.post(uri, body)
        if resp.status == 400:
            try:
                print(json.dumps(resp.obj['error']['@Message.ExtendedInfo'], indent=4, \
                                                                        sort_keys=True))
            except Exception as excp:
                sys.stderr.write("A response error occurred, unable to access iLO"
                                "Extended Message Info...")
        elif resp.status != 200:
            sys.stderr.write("An http response of \'%s\' was returned.\n" % resp.status)
        else:
            print("Success!\n")
            print(json.dumps(resp.dict, indent=4, sort_keys=True))
    
    def _ilo_set_on_next_server_reset(self, virt_cd_data):
        uri = virt_cd_data.obj['@odata.id'], patch_body
        body = {}
        body["Oem"] = {"Hpe": {"BootOnNextServerReset": True}}
        resp = self._redfishobj.patch(uri, body)
        if not resp.status == 200:
            sys.stderr.write("Failure setting BootOnNextServerReset")