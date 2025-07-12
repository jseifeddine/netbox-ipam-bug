#!venv/bin/python

from dotenv import load_dotenv
import os
import pynetbox

load_dotenv()

nb = pynetbox.api(
    url=os.getenv("NETBOX_URL"),
    token=os.getenv("NETBOX_TOKEN")
)

all_netbox_ips = list(nb.ipam.ip_addresses.filter(device_id=1))

print(f"Found {len(all_netbox_ips)} IP addresses in NetBox for device 1")

# This was initially how I found the problem, interfaces missing IPs, some showing too many, double ups etc.
# for ip in all_netbox_ips:
#     if ip.assigned_object and ip.assigned_object.name == "dummy4991":
#         print(ip.id, ip.address, ip.assigned_object.name)

#     if ip.assigned_object and ip.assigned_object.name == "dummy4993":
#         print(ip.id, ip.address, ip.assigned_object.name)

# So, I looped through all the IP addresses and grouped them by the interface they are assigned to, knowing that all interfaces should have 2 IP addresses, log if differs
interface_ips = {}

for ip in all_netbox_ips:
    if ip.assigned_object and ip.assigned_object.name:
        if not interface_ips.get(ip.assigned_object.name):
            interface_ips[ip.assigned_object.name] = []
        interface_ips[ip.assigned_object.name].append(ip)

# print length of interface_ips and accumaltive length of its ips
print(f"Found {len(interface_ips)} interfaces with {sum(len(ips) for ips in interface_ips.values())} IP addresses")
print()
print("Each interface should have exactly two addresses")
print("- 172.17.0.1/32")
print("- ff1d:c7c:7b44:d39d:ab3d:6fde:f46a:4648/64")
print()

for interface, ips in interface_ips.items():
    if len(ips) != 2:
        print(f"BUG: Interface {interface} has {len(ips)} IP addresses")
        for ip in ips:
            print(f"IP {ip.address} (ID: {ip.id}) is assigned to {ip.assigned_object.name}")

print()
print("Test complete")



