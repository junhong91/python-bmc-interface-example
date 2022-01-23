from base import BaseboardManagementController

import sys
import json
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError
from .get_resource_directory import get_resource_directory

class ILOBMC(BaseboardManagementController):
    DISABLE_RESOURCE_DIR = False
    
    def __init__(self, ip, username, password, url):
        # Create a Redfish client object
        self._redfishobj = RedfishClient(base_url=url, username=username, password=password)
        super(ILOBMC, self).__init__(ip, username, password, url)

    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        try:
            # Login with the Redfish client
            self._redfishobj.login()
        except ServerDownOrUnreachableError as excp:
            sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
            sys.exit()

        systems_members_response = None

        resource_instances = get_resource_directory(self._redfishobj)
        if DISABLE_RESOURCE_DIR or not resource_instances:
            #if we do not have a resource directory or want to force it's non use to find the
            #relevant URI
            systems_uri = self._redfishobj.root.obj['Systems']['@odata.id']
            systems_response = self._redfishobj.get(systems_uri)
            systems_uri = next(iter(systems_response.obj['Members']))['@odata.id']
            systems_response = self._redfishobj.get(systems_uri)
        else:
            for instance in resource_instances:
                #Use Resource directory to find the relevant URI
                if '#ComputerSystem.' in instance['@odata.type']:
                    systems_uri = instance['@odata.id']
                    systems_response = self._redfishobj.get(systems_uri)

        if systems_response:
            system_reboot_uri = systems_response.obj['Actions']['#ComputerSystem.Reset']['target']
            body = dict()
            body['Action'] = 'ComputerSystem.Reset'
            body['ResetType'] = "ForceRestart"
            resp = self._redfishobj.post(system_reboot_uri, body)
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

        self._redfishobj.logout()
        pass

    def set_next_boot_virtual_CD(self):
        """Overrides BaseboardManagementController.set_next_boot_virtual_CD"""
        print("Attach ISO file into ILO BMC!")
        pass    