from base import BaseboardManagementController

import sys
import json
import time
import requests

class IDRACBMC(BaseboardManagementController):
    def __init__(self, ip, username, password, url):
        super(IDRACBMC, self).__init__(ip, username, password, url)

        self.dell_base_url = "https://%s/redfish/v1/Systems/System.Embedded.1/" % self.ip
        self.headers = {'content-type': 'application/json'}

    def reboot_server(self):
        """Overrides"""
        response = requests.get(self.dell_base_url, verify=False, auth=(self.username, self.password))
        data = response.json()
        print("\n- INFO, Current server power state is: %s" % data['PowerState'])
        if data['PowerState'] == "On":
            url = "%sActions/ComputerSystem.Reset" % self.dell_base_url
            payload = {'ResetType': 'GracefulShutdown'}
            response = requests.post(url, data=json.dumps(payload), headers=self.headers, verify=False, auth=(self.username, self.password))
            if response.status_code == 204:
                print("- PASS, Command passed to gracefully power OFF server, code return is %s" % response.status_code)
                time.sleep(10)
            else:
                print("\n- FAIL, Command failed to gracefully power OFF server, status code is: %s\n" % response.status_code)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
            count = 0
            while True:
                response = requests.get(self.dell_base_url, verify=False, auth=(self.username, self.password))
                data = response.json()
                if data['PowerState'] == "Off":
                    print("- PASS, GET command passed to verify server is in OFF state")
                    break
                elif count == 20:
                    print("- INFO, unable to graceful shutdown the server, will perform forced shutdown now")
                    url = "%sActions/ComputerSystem.Reset" % self.dell_base_url
                    payload = {'ResetType': 'ForceOff'}
                    response = requests.post(url, data=json.dumps(payload), headers=self.headers, verify=False, auth=(self.username, self.password))
                    if response.status_code == 204:
                        print("- PASS, Command passed to forcefully power OFF server, code return is %s" % response.status_code)
                        time.sleep(15)
                    else:
                        print("\n- FAIL, Command failed to gracefully power OFF server, status code is: %s\n" % response.status_code)
                        print("Extended Info Message: {0}".format(response.json()))
                        sys.exit()
                else:
                    time.sleep(2)
                    count+=1
                    continue
                
            payload = {'ResetType': 'On'}
            response = requests.post(url, data=json.dumps(payload), headers=self.headers, verify=False, auth=(self.username, self.password))
            if response.status_code == 204:
                print("- PASS, Command passed to power ON server, code return is %s" % response.status_code)
            else:
                print("\n- FAIL, Command failed to power ON server, status code is: %s\n" % response.status_code)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
        elif data['PowerState'] == "Off":
            url = '%sActions/ComputerSystem.Reset' % self.dell_base_url
            payload = {'ResetType': 'On'}
            response = requests.post(url, data=json.dumps(payload), headers=self.headers, verify=False, auth=(self.username, self.password))
            if response.status_code == 204:
                print("- PASS, Command passed to power ON server, code return is %s" % response.status_code)
            else:
                print("\n- FAIL, Command failed to power ON server, status code is: %s\n" % response.status_code)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
        else:
            print("- FAIL, unable to get current server power state to perform either reboot or power on")
            sys.exit()

    def set_next_boot_virtual_CD(self):
        """Overrides"""
        url = self.dell_base_url
        payload = {"Boot":{"BootSourceOverrideTarget":self.url}}
        response = requests.patch(url, data=json.dumps(payload), headers=self.headers, verify=False,auth=(self.username, self.password))
        data = response.json()
        time.sleep(5)
        if response.status_code == 200:
            print("\n- PASS, PATCH command passed to set next boot onetime boot device to: \"%s\"" % self.url)
        else:
            print("\n- FAIL, Command failed, errror code is %s" % response.status_code)
            detail_message=str(response.__dict__)
            print(detail_message)
            sys.exit()