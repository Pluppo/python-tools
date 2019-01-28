# python-tools
Python version: 3.6
Additional modules: netmiko
Other dependecies: ntc-templates (install in home dir with "git clone https://github.com/networktocode/ntc-templates")

get-mac-arp.py - gets arp and mac tables from router and switches, and outputs a csv file with the results.

Populate devices.csv file, example:

host,ip,device_type,mac,arp
R1,10.10.10.1,cisco_ios,,yes
SW1,10.10.10.2,cisco_ios,yes,yes
SW2,10.10.10.3,cisco_nxos,yes,

Explanation of cells:
host = hostname of device
ip = management IP of device
device_type = cisco_ios or cisco_nxos
mac = leave empty if mac address table is not needed
arp = leave empty if arp table is not needed
