from bmc_interface import BaseboardManagementController

class IDRACBMC(BaseboardManagementController):
    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        print("Reboot IDRAC BMC!")
        pass

    def attach_iso(self):
        """Overrides BaseboardManagementController.attach_iso"""
        print("Attach ISO file into IDRAC BMC!")
        pass    