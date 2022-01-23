from base import BaseboardManagementController

import sys
import json
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError
from .get_resource_directory import get_resource_directory

class ILOBMC(BaseboardManagementController):
    MEDIA_TYPE = "CD"
    BOOT_ON_NEXT_SERVER_RESET = True

    def __init__(self, ip, username, password, url):
        # Create a Redfish client object
        self._redfishobj = RedfishClient(base_url=url, username=username, password=password)
        try:
            # Login with the Redfish client
            self._redfishobj.login()
        except ServerDownOrUnreachableError as excp:
            sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
            sys.exit()

        super(ILOBMC, self).__init__(ip, username, password, url)

    def __del__(self):
        self._redfishobj.logout()

    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        instances = get_resource_directory(self._redfishobj)
        for i in instances:
            #Find the relevant URI
            if '#ComputerSystem.' in i['@odata.type']:
                sys_uri = i['@odata.id']
                sys_resp = self._redfishobj.get(sys_uri)

        if sys_resp:
            sys_reboot_uri = sys_resp.obj['Actions']['#ComputerSystem.Reset']['target']
            body = dict()
            body['Action'] = 'ComputerSystem.Reset'
            body['ResetType'] = "ForceRestart"
            resp = self._redfishobj.post(sys_reboot_uri, body)
            #If iLO responds with soemthing outside of 200 or 201 then lets check the iLO extended info
            #error message to see what went wrong
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

    def set_next_boot_virtual_CD(self):
        """Overrides BaseboardManagementController.set_next_boot_virtual_CD"""
        instances = get_resource_directory(self._redfishobj)
        for i in instances:
            #Find the relevant URI
            if '#VirtualMediaCollection.' in i['@odata.type']:
                virt_media_uri = i['@odata.id']

        if virt_media_uri:
            virt_media_resp = self._redfishobj.get(virt_media_uri)
            for virt_media_slot in virt_media_resp.obj['Members']:
                data = self._redfishobj.get(virt_media_slot['@odata.id'])
                
                if MEDIA_TYPE in data.dict['MediaTypes']:
                    virt_media_mount_uri = data.obj['Actions']['#VirtualMedia.InsertMedia']['target']
                    post_body = {"Image": self.url}
                    resp = self._redfishobj.post(virt_media_mount_uri, post_body)
                    
                    if BOOT_ON_NEXT_SERVER_RESET is not None:
                        patch_body = {}
                        patch_body["Oem"] = {"Hpe": {"BootOnNextServerReset": \
                                                BOOT_ON_NEXT_SERVER_RESET}}
                        boot_resp = self._redfishobj.patch(data.obj['@odata.id'], patch_body)
                        if not boot_resp.status == 200:
                            sys.stderr.write("Failure setting BootOnNextServerReset")
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
