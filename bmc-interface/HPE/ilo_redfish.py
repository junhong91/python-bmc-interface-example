from base import BaseboardManagementController

import sys
import json
from redfish import RedfishClient
from redfish.rest.v1 import ServerDownOrUnreachableError

class ILOBMC(BaseboardManagementController):
    def __init__(self, ip, username, password, url):
        try:
            # Create a Redfish client object
            self._redfishobj = RedfishClient(base_url=url, username=username, password=password)
            # Login with the Redfish client
            self._redfishobj.login()
        except ServerDownOrUnreachableError as excp:
            sys.stderr.write("ERROR: server not reachable or does not support RedFish.\n")
            sys.exit()

        super(ILOBMC, self).__init__(ip, username, password, url)

    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        print("Reboot ILO BMC!")
        pass

    def set_next_boot_virtual_CD(self):
        """Overrides BaseboardManagementController.set_next_boot_virtual_CD"""
        print("Attach ISO file into ILO BMC!")
        pass    