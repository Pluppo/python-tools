# python-tools
Python version: 3.6<br/>
Additional modules: netmiko<br/>
Other dependecies: ntc-templates (install in home dir with "git clone https://github.com/networktocode/ntc-templates")<br/>

get-mac-arp.py - gets arp and mac tables from router and switches, and outputs a csv file with the results.

Populate devices.csv file, example:

host,ip,device_type,mac,arp<br/>
R1,10.10.10.1,cisco_ios,,yes<br/>
SW1,10.10.10.2,cisco_ios,yes,yes<br/>
SW2,10.10.10.3,cisco_nxos,yes,

Explanation of cells:<br/>
host = hostname of device<br/>
ip = management IP of device<br/>
device_type = cisco_ios or cisco_nxos<br/>
mac = leave empty if mac address table is not needed<br/>
arp = leave empty if arp table is not needed<br/>
