class BaseboardManagementController:
    def __init__(self, ip, username, password, url):
        self.ip = ip
        self.username = username
        self.password = password
        self.url = url

    def reboot_server(self):
        """Reboot BMC server"""
        """Sub BMC Class must implement reboot_server() method"""
        raise NotImplementedError

    def set_next_boot_virtual_CD(self):
        """Attach ISO file into BMC server"""
        """Sub BMC Class must implement set_next_boot_virtual_CD() method"""
        raise NotImplementedError