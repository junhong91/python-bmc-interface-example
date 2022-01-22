from bmc_interface import BaseboardManagementController

class IDRACBMC(BaseboardManagementController):
    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        print("Reboot IDRAC BMC!")
        pass

    def set_next_boot_virtual_CD(self):
        """Overrides BaseboardManagementController.set_next_boot_virtual_CD"""
        print("Attach ISO file into IDRAC BMC!")
        pass    