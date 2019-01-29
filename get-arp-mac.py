#!/usr/bin/env python3.6

from netmiko import Netmiko
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException
from getpass import getpass
import re
import csv
import datetime
import readline
import sys

#Define dictionary for replacing interface strings:
int_dict = {'Port-channel': 'Po', 'FastEthernet': 'Fa', 'GigabitEthernet': 'Gi', 'TenGigabitEthernet': 'Te'}
nospace_dict = {' ': '_', ':': '-'}
novlan_dict = {'Vlan': ''}

#Define function for replacing characters from dictionary:
def multiple_replace(dict, text):
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

#Define functions for appendind dictionaries to mac_arp list:
def append_mac(show_mac, show_status):
    for mac_entry in show_mac:
        if device['device_type'] == 'cisco_ios':
            port = multiple_replace(int_dict, mac_entry['destination_port']) #Replace long interface names with short names (example: 'GigabitEthernet' to 'Gi')
            mac = mac_entry['destination_address']
            vlan =  mac_entry['vlan']
        elif device['device_type'] == 'cisco_nxos':
            port = mac_entry['ports']
            mac = mac_entry['mac']
            vlan =  mac_entry['vlan']
        for status_entry in show_status:
            if status_entry['port'] == port: #Match interface from show interface status with show mac address-table to exctract relevant port description
                des = status_entry['name']
                mac_arp.append({'mac': mac, 'vlan': vlan, 'switch': name, 'port': port, 'description': des, 'IP': '', 'vrf': ''})

def append_arp(show_arp):				
    for arp_entry in show_arp:
        mac = arp_entry['mac']
        vlan = multiple_replace(novlan_dict, arp_entry['interface'])
        ip = arp_entry['address']
        mac_arp.append({'mac': mac, 'vlan': vlan, 'switch': name, 'port': '', 'description': 'ARP', 'IP': ip, 'vrf': vrf})


#Get username and password
username = input('Username: ') 
password = getpass()

#Import devices from csv, required fields: host,ip,device_type,mac,arp. Keep mac and arp blank if not neeed
with open('devices.csv') as f: 
    device_list = [{k: v for k,v in row.items()} for row in csv.DictReader(f, skipinitialspace=True)]

#Initialize mac_arp list:
mac_arp=[]

#Get and process data from devices
for device in device_list:
    name =  device['host']
    ip = device['ip']
    device_type = device['device_type']
    print('Getting data from ' + device['host'])
    #Connect to device using info from device.csv and entered credentials, handle timeout and authentication exceptions
    try:
        net_connect = Netmiko(ip=ip, username=username, password=password, device_type=device_type)
    except NetMikoTimeoutException as timeout_error:
        print('*'*80)
        print(timeout_error)
        print('*'*80)
        sys.exit(1)
    except NetMikoAuthenticationException as auth_error:
        print('*'*80)
        print(auth_error)
        print('*'*80)
        sys.exit(1)
    #Get list of vrf
    show_vrf = net_connect.send_command('show vrf', use_textfsm=True)
    #Check that data is list before continuing (error output will be str)
    if (show_vrf) == list:
        #Get arp table for each vrf
        for vrf in show_vrf:
            vrf = vrf['name']
            show_arp = net_connect.send_command('show ip arp vrf ' + vrf, use_textfsm=True)
            #Check that data is list before appending (empty arp will be str)
            if type(show_arp) == list:
                append_arp(show_arp)
        #For IOS, get default arp table
        if device_type == 'cisco_ios':
            vrf = 'default'
            show_arp = net_connect.send_command('show ip arp', use_textfsm=True)
            append_arp(show_arp)
    #Collect show mac address-table and show interface status
    show_mac = net_connect.send_command('show mac address-table', use_textfsm=True)
    show_status = net_connect.send_command('show interface status', use_textfsm=True)
    append_mac(show_mac, show_status)
    #Disconnect from device
    net_connect.disconnect()

#Define output csv keys and filename
csv_keys = mac_arp[0].keys()
filename = 'output/mac_arp_' + multiple_replace(nospace_dict, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '.csv'

#Output data to csv
with open(filename, 'w') as f:
    dict_writer = csv.DictWriter(f, csv_keys)
    dict_writer.writeheader()
    dict_writer.writerows(mac_arp)

print('Done!')

