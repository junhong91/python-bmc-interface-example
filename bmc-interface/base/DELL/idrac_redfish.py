from base import BaseboardManagementController

class IDRACBMC(BaseboardManagementController):
    def reboot_server(self):
        """Overrides"""
        response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % self.ip,verify=False,auth=(self.username, self.password))
        data = response.json()
        print("\n- INFO, Current server power state is: %s" % data['PowerState'])
        if data['PowerState'] == "On":
            url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % self.ip
            payload = {'ResetType': 'GracefulShutdown'}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, auth=(self.username, self.password))
            statusCode = response.status_code
            if statusCode == 204:
                print("- PASS, Command passed to gracefully power OFF server, code return is %s" % statusCode)
                time.sleep(10)
            else:
                print("\n- FAIL, Command failed to gracefully power OFF server, status code is: %s\n" % statusCode)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
            count = 0
            while True:
                response = requests.get('https://%s/redfish/v1/Systems/System.Embedded.1/' % self.ip, verify=False, auth=(self.username, self.password))
                data = response.json()
                if data['PowerState'] == "Off":
                    print("- PASS, GET command passed to verify server is in OFF state")
                    break
                elif count == 20:
                    print("- INFO, unable to graceful shutdown the server, will perform forced shutdown now")
                    url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % self.ip
                    payload = {'ResetType': 'ForceOff'}
                    headers = {'content-type': 'application/json'}
                    response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, auth=(self.username, self.password))
                    statusCode = response.status_code
                    if statusCode == 204:
                        print("- PASS, Command passed to forcefully power OFF server, code return is %s" % statusCode)
                        time.sleep(15)
                    else:
                        print("\n- FAIL, Command failed to gracefully power OFF server, status code is: %s\n" % statusCode)
                        print("Extended Info Message: {0}".format(response.json()))
                        sys.exit()
                    
                else:
                    time.sleep(2)
                    count+=1
                    continue
                
            payload = {'ResetType': 'On'}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, auth=(self.username, self.password))
            statusCode = response.status_code
            if statusCode == 204:
                print("- PASS, Command passed to power ON server, code return is %s" % statusCode)
            else:
                print("\n- FAIL, Command failed to power ON server, status code is: %s\n" % statusCode)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
        elif data['PowerState'] == "Off":
            url = 'https://%s/redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset' % self.ip
            payload = {'ResetType': 'On'}
            headers = {'content-type': 'application/json'}
            response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, auth=(self.username, self.password))
            statusCode = response.status_code
            if statusCode == 204:
                print("- PASS, Command passed to power ON server, code return is %s" % statusCode)
            else:
                print("\n- FAIL, Command failed to power ON server, status code is: %s\n" % statusCode)
                print("Extended Info Message: {0}".format(response.json()))
                sys.exit()
        else:
            print("- FAIL, unable to get current server power state to perform either reboot or power on")
            sys.exit()

    def set_next_boot_virtual_CD(self):
        """Overrides"""
        url = 'https://%s/redfish/v1/Systems/System.Embedded.1' % self.ip
        payload = {"Boot":{"BootSourceOverrideTarget":self.url}}
        headers = {'content-type': 'application/json'}
        response = requests.patch(url, data=json.dumps(payload), headers=headers, verify=False,auth=(self.username, self.password))
        data = response.json()
        statusCode = response.status_code
        time.sleep(5)
        if statusCode == 200:
            print("\n- PASS, PATCH command passed to set next boot onetime boot device to: \"%s\"" % self.url)
        else:
            print("\n- FAIL, Command failed, errror code is %s" % statusCode)
            detail_message=str(response.__dict__)
            print(detail_message)
            sys.exit()