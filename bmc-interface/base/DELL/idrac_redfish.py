from base import BaseboardManagementController

class IDRACBMC(BaseboardManagementController):
    def reboot_server(self):
        """Overrides"""
        print("Reboot IDRAC BMC!")

    def set_next_boot_virtual_CD(self):
        """Overrides"""
        print("Attach ISO file into IDRAC BMC!")