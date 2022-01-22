from bmc_interface import BaseboardManagementController

import HPE
import DELL

class BMCFactory:
    def create_bmc(self, bmc_type) -> BaseboardManagementController:
        """Create bmc server based on hardware type"""
        if bmc_type == "DELL":
            return DELL.IDRACBMC()
        if bmc_type == "HPE":
            return HPE.ILOBMC()
        
        return None
