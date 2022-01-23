from base import BaseboardManagementController

import sys
import json
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError
from .get_resource_directory import get_resource_directory

class ILOBMC(BaseboardManagementController):\
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
        sys_resp = None

        for i in self._resource_instances:
            # Find the relevant URI
            if '#ComputerSystem.' in i['@odata.type']:
                sys_uri = i['@odata.id']
                sys_resp = self._redfishobj.get(sys_uri)

        if sys_resp is None:
            sys.stderr.write("Failed to get redfish Computer System uri...")
            return

        sys_reboot_uri = sys_resp.obj['Actions']['#ComputerSystem.Reset']['target']
        body = dict()
        body['Action'] = 'ComputerSystem.Reset'
        body['ResetType'] = "ForceRestart"

        # REDFISH: Request rebooting
        resp = self._redfishobj.post(sys_reboot_uri, body)
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
        """Overrides"""
        virt_media_uri = None

        for i in self._resource_instances:
            # Find the relevant URI
            if '#VirtualMediaCollection.' in i['@odata.type']:
                virt_media_uri = i['@odata.id']
        
        if virt_media_uri is None:
            sys.stderr.write("Failed to get redfish VirtualMediaCollection uri...")
            return

        virt_media_resp = self._redfishobj.get(virt_media_uri)
        for virt_media_slot in virt_media_resp.obj['Members']:
            data = self._redfishobj.get(virt_media_slot['@odata.id'])

            if "CD" in data.dict['MediaTypes']:
                virt_media_unmount_uri = data.obj['Actions']['#VirtualMedia.EjectMedia']['target']
                virt_media_mount_uri = data.obj['Actions']['#VirtualMedia.InsertMedia']['target']
  
                # REDFISH: Remove old mounted iso
                unmount_resp = self._redfishobj.post(virt_media_unmount_uri, {})
                if not unmount_resp.status == 200:
                    sys.stderr.write("Failure unmounting old iso")

                # REDFISH: Mount new iso
                post_body = {"Image": self.url}
                mount_resp = self._redfishobj.post(virt_media_mount_uri, post_body)
                if mount_resp.status == 400:
                    try:
                        print(json.dumps(mount_resp.obj['error']['@Message.ExtendedInfo'], indent=4, \
                                                                                sort_keys=True))
                    except Exception as excp:
                        sys.stderr.write("A response error occurred, unable to access iLO"
                                        "Extended Message Info...")
                elif mount_resp.status != 200:
                    sys.stderr.write("An http response of \'%s\' was returned.\n" % mount_resp.status)
                else:
                    print("Success!\n")
                    print(json.dumps(mount_resp.dict, indent=4, sort_keys=True))

                # REDFISH: Set boot on server reset
                patch_body = {}
                patch_body["Oem"] = {"Hpe": {"BootOnNextServerReset": True}}
                boot_resp = self._redfishobj.patch(data.obj['@odata.id'], patch_body)
                if not boot_resp.status == 200:
                    sys.stderr.write("Failure setting BootOnNextServerReset")
