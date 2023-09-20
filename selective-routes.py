"""
NOTE: 
Test file bgp-lu-command-1.txt -> show bgp nexthops -> WITH the LU route installed in the RIB.
Test file bgp-lu-command-2.txt -> show bgp nexthops -> WITHOUT the LU route installed in the RIB [no BGP vpnv4 advertisement]
Test file bgp-lu-command-3.txt -> show bgp nexthops -> WITHOUT the LU route installed in the RIB [BGP vpnv4 advertisement but the LU route is rejected due to RPL (table-policy)]
"""

test_flag = False

try:
    from cisco.script_mgmt import xrlog
    from iosxr.xrcli.xrcli_helper import *
    cli_helper = XrcliHelper(debug = True)
    syslog = xrlog.getSysLogger('BGP Labelled Unicast Selective Route Download Script') 
except:
    print("Testing on Local environment")
    test_flag = True

def getCLI():
    if test_flag == False:
        result = cli_helper.xrcli_exec("show bgp nexthops")
        if result['status'] == 'success':
            return result['output']
    else:
        return open('test-cli-outputs/bgp-lu-command-3.txt').read()
    
if __name__ == '__main__':
    print(getCLI())
