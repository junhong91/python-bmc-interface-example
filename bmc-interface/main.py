import HPE
import DELL
import factory

if __name__ == "__main__":
    bmc_factory = factory.BMCFactory()

    try:
        bmc = bmc_factory.create_bmc("DELL")
        bmc.attach_iso()
        bmc.reboot_server()
    except:
        print("Invalid support BMC hardware.")
        