import HPE
import DELL

if __name__ == "__main__":
    dell_bmc = DELL.IDRACBMC()
    dell_bmc.reboot_server()
    dell_bmc.attach_iso()

    hpe_bmc = HPE.ILOBMC()
    hpe_bmc.reboot_server()
    hpe_bmc.attach_iso()