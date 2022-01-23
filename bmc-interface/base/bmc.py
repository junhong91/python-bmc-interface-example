class BaseboardManagementController:
    def __init__(self, ip, username, password, url):
        self.ip = ip
        self.username = username
        self.password = password
        self.url = url

    def reboot_server(self):
        """Reboot BMC server"""
        raise NotImplementedError

    def set_next_boot_virtual_CD(self):
        """Attach ISO file into BMC server"""
        raise NotImplementedError