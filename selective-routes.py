"""
NOTE: 
Test file bgp-lu-command-1.txt -> show bgp nexthops -> WITH the LU route installed in the RIB.
Test file bgp-lu-command-2.txt -> show bgp nexthops -> WITHOUT the LU route installed in the RIB [no BGP vpnv4 advertisement]
Test file bgp-lu-command-3.txt -> show bgp nexthops -> WITHOUT the LU route installed in the RIB [BGP vpnv4 advertisement but the LU route is rejected due to RPL (table-policy)]
"""
import re
test_flag = False
import sys

try:
    from cisco.script_mgmt import xrlog
    from iosxr.xrcli.xrcli_helper import *
    cli_helper = XrcliHelper(debug = True)
    syslog = xrlog.getSysLogger('BGP Labelled Unicast Selective Route Download Script') 
except:
    print("Testing on Local environment\n")
    test_flag = True

def getCLI():
    if test_flag == False:
        result = cli_helper.xrcli_exec("show bgp nexthops")
        if result['status'] == 'success':
            return result['output']
        else:
            sys.exit("Error in executing show bgp nexthops")
    else:
        return open('test-cli-outputs/bgp-lu-command-3.txt').read()

def extractIP(raw_cli_output):
    r = re.finditer(r'((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))\.((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))\.((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))\.((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))\s+\[UR\]', raw_cli_output) # Attempt to extract the IP address from the CLI output
    ips = [re.split(r'\s+', raw_cli_output[i.start():i.end()])[0] for i in r]
    return ips

def generatePrefixList(ips):
    prefix_list = []
    for ip in ips:
        prefix_list.append(ip + "/32")
    return prefix_list

if __name__ == '__main__':
    #test_string = getCLI()
    ipList = extractIP(getCLI())
    if len(ipList) == 0:
        print("No IP addresses found in the CLI output")
    else:
        print("IP addresses found in the CLI output")
        print(ipList)
        print("Generating prefix-list")
        print(generatePrefixList(ipList))
    #print(extractIP(getCLI()))