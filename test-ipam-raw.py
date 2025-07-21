#!venv/bin/python

from dotenv import load_dotenv
import os
import pynetbox
from netbox import NetBoxAPI

load_dotenv()

nb = NetBoxAPI(
    url=os.getenv("NETBOX_URL"),
    token=os.getenv("NETBOX_TOKEN"),
)

# Function to check if NetBox version is above a specified version
def is_version_above(current_version, min_version):
    current_parts = [int(x) for x in current_version.split('.')]
    min_parts = [int(x) for x in min_version.split('.')]
    
    for i in range(max(len(current_parts), len(min_parts))):
        current = current_parts[i] if i < len(current_parts) else 0
        minimum = min_parts[i] if i < len(min_parts) else 0
        if current > minimum:
            return True
        elif current < minimum:
            return False
    return True

status = nb.status()
netbox_version = status["netbox_version"]

all_netbox_macs = None

all_netbox_interfaces = nb.get(f"dcim/interfaces/?device_id=1")
all_netbox_ips = nb.get(f"ipam/ip-addresses/?device_id=1")
if is_version_above(netbox_version, "4.2.0"):
    all_netbox_macs = nb.get(f"dcim/mac-addresses/?device_id=1")

print(f"Found {len(all_netbox_interfaces)} interfaces in NetBox for device 1")
print(f"Found {len(all_netbox_ips)} IP addresses in NetBox for device 1")
if all_netbox_macs:
    print(f"Found {len(all_netbox_macs)} MAC addresses in NetBox for device 1")

# This was initially how I found the problem, interfaces missing IPs, some showing too many, double ups etc.
# for ip in all_netbox_ips:
#     if ip.assigned_object and ip.assigned_object.name == "dummy4991":
#         print(ip.id, ip.address, ip.assigned_object.name)

#     if ip.assigned_object and ip.assigned_object.name == "dummy4993":
#         print(ip.id, ip.address, ip.assigned_object.name)

# So, I looped through all the IP addresses and grouped them by the interface they are assigned to, knowing that all interfaces should have 2 IP addresses, log if differs
interface_ips = {}
interface_macs = {}

for ip in all_netbox_ips:
    if ip.assigned_object and ip.assigned_object.name:
        if not interface_ips.get(ip.assigned_object.name):
            interface_ips[ip.assigned_object.name] = []
        interface_ips[ip.assigned_object.name].append(ip)

if all_netbox_macs:
    for mac in all_netbox_macs:
        if mac.assigned_object and mac.assigned_object.name:
            if not interface_macs.get(mac.assigned_object.name):
                interface_macs[mac.assigned_object.name] = []
            interface_macs[mac.assigned_object.name].append(mac)

# print length of interface_ips and accumaltive length of its ips
print(f"Found {len(interface_ips)} interfaces with {sum(len(ips) for ips in interface_ips.values())} IP addresses")
if all_netbox_macs:
    print(f"Found {len(interface_macs)} interfaces with {sum(len(macs) for macs in interface_macs.values())} MAC addresses")
print()
print("Each interface should have exactly two addresses")
print("- 172.17.0.1/32")
print("- ff1d:c7c:7b44:d39d:ab3d:6fde:f46a:4648/64")
print()
if all_netbox_macs:
    print("Each interface should have exactly one MAC address")
    print("- 18:2A:D3:65:90:2E")
    print()

for interface, ips in interface_ips.items():
    if len(ips) != 2:
        print(f"BUG: Interface {interface} has {len(ips)} IP addresses")
        for ip in ips:
            print(f"IP {ip.address} (ID: {ip.id}) is assigned to {ip.assigned_object.name}")

print()

if all_netbox_macs:
    for interface, macs in interface_macs.items():
        if len(macs) != 1:
            print(f"BUG: Interface {interface} has {len(macs)} MAC addresses")
            for mac in macs:
                print(f"MAC {mac.mac_address} (ID: {mac.id}) is assigned to {mac.assigned_object.name}")

    print()

    for interface in all_netbox_interfaces:
        if len(interface.mac_addresses) != 1:
            print(f"BUG: Interface {interface.name} has {len(interface.mac_addresses)} MAC addresses")
            for mac in interface.mac_addresses:
                print(f"MAC {mac.mac_address} (ID: {mac.id}) is assigned to {interface.name}")

print()
print("Test complete")



