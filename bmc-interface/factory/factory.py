from base import BaseboardManagementController

import HPE
import DELL

class BMCFactory:
    def create_bmc(self, bmc_type, ip, username, password, url) -> BaseboardManagementController:
        """Create bmc server based on hardware type"""
        if bmc_type == "DELL":
            return DELL.IDRACBMC(ip, username, password, url)
        if bmc_type == "HPE":
            return HPE.ILOBMC(ip, username, password, url)
        
        return None
