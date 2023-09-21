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
        nexthops = cli_helper.xrcli_exec("show bgp nexthops")
        prefixsets = cli_helper.xrcli_exec("show run prefix-set LU-allow-prefixes")
        if nexthops['status'] == 'success' and prefixsets['status'] == 'success':
            return {"nexthops": nexthops['output'], "prefixsets": prefixsets['output']}
        else:
            sys.exit("Error in executing show bgp nexthops")
    else:
        f,g = open('test-cli-outputs/bgp-lu-command-4.txt'), open('test-cli-outputs/prefix-set-2.txt')
        nexthops,prefixsets = f.read(),g.read()
        f.close()
        g.close()
        return {"nexthops": nexthops, "prefixsets": prefixsets}
"""
TODO: Do in-depth testing of regex matching (any alphanumeric inputs for IP addresses)
"""
def extractIP(raw_cli_output):
    r = re.finditer(r'((25[0-5])\.|(2[0-4][0-9]\.)|(1[0-9][0-9]\.)|(\b[0-9][0-9]\.\b)|(\b[0-9]\.\b)){3}((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))\s+\[UR\]', raw_cli_output) # Attempt to extract the IP address from the CLI output
    IPs = [re.split(r'\s+', raw_cli_output[i.start():i.end()])[0] for i in r]
    return IPs

def extractPrefixSets(raw_cli_output):
    r = re.finditer(r'((25[0-5])\.|(2[0-4][0-9]\.)|(1[0-9][0-9]\.)|(\b[0-9][0-9]\.\b)|(\b[0-9]\.\b)){3}((25[0-5])|(2[0-4][0-9])|(1[0-9][0-9])|(\b[0-9][0-9]\b)|(\b[0-9]\b))/(\b3[0-2]\b|\b[1-2][0-9]\b|\b[0-9]\b)',raw_cli_output)
    IPs = [re.split(r'\s+', raw_cli_output[i.start():i.end()])[0] for i in r]
    return IPs

def generatePrefixList(IPs):
    prefix_list = []
    for ip in IPs:
        prefix_list.append(ip + "/32")
    return prefix_list 

def generateApplyConfig(prefixList):
    prefixSet = "prefix-set LU-allow-prefixes \n"
    for ip in prefixList:
        prefixSet = prefixSet + ip + ","
    return prefixSet[:-1] + " end-set"

def commitApplyConfig(config):
    r = cli_helper.xr_apply_config_string(config)
    if r['status'] == 'success':
        print("Successfully applied the prefix-set config")
    else:
        print("Error in applying the prefix-set config")

if __name__ == '__main__':
    ipList_LU = extractIP(getCLI()['nexthops'])
    old_PrefixList = extractPrefixSets(getCLI()['prefixsets'])

    if len(ipList_LU) == 0:
        print("No IP addresses found in the show bgp nexthops CLI output")
    else:
        print("IP addresses found in the show bgp next hops CLI output")
        print(ipList_LU)
        print("Generating prefix-list")
        prefixList = list(set(generatePrefixList(ipList_LU) + old_PrefixList))
        print(prefixList)

        prefixSet = generateApplyConfig(prefixList)

        if test_flag == False:
            commitApplyConfig(prefixSet)