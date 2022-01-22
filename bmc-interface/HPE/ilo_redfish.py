from base import BaseboardManagementController

class ILOBMC(BaseboardManagementController):
    def reboot_server(self):
        """Overrides BaseboardManagementController.reboot_server"""
        print("Reboot ILO BMC!")
        pass

    def set_next_boot_virtual_CD(self):
        """Overrides BaseboardManagementController.set_next_boot_virtual_CD"""
        print("Attach ISO file into ILO BMC!")
        pass    