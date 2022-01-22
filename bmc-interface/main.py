import HPE
import DELL
import factory
import argparse

parser = argparse.ArgumentParser(description='Attach virtual CD to BMC server.')
parser.add_argument('--type', type=str, help='BMC hardware type', required=True)
parser.add_argument('--ip', type=str, help='BMC ip address', required=True)
parser.add_argument('--user', type=str, help='BMC user name', required=True)
parser.add_argument('--password', type=str, help='BMC user password', required=True)
parser.add_argument('--url', type=str, help='Virtual CD url', required=True)

args = parser.parse_args()

if __name__ == "__main__":
    bmc_factory = factory.BMCFactory()

    try:
        bmc = bmc_factory.create_bmc(args.type)
        bmc.set_next_boot_virtual_CD()
        bmc.reboot_server()
    except:
        print("Invalid support BMC hardware.")
        