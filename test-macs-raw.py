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

DEVICE_ID = 1

all_netbox_macs = list(nb.get(f"dcim/mac-addresses/?device_id={DEVICE_ID}"))
all_netbox_interfaces = list(nb.get(f"dcim/interfaces/?device_id={DEVICE_ID}"))

print(f"Found {len(all_netbox_macs)} MAC addresses in NetBox for device {DEVICE_ID} from dcim.mac_addresses endpoint.")
print(f"Found {len(all_netbox_interfaces)} interfaces in NetBox for device {DEVICE_ID} from dcim.interfaces endpoint.")

mac_interfaces = {}
interface_macs = {}

for mac in all_netbox_macs:
    if mac.assigned_object and mac.assigned_object.name:
        if not mac_interfaces.get(mac.assigned_object.name):
            mac_interfaces[mac.assigned_object.name] = []
        mac_interfaces[mac.assigned_object.name].append(mac)

total_macs = sum(len(macs) for macs in mac_interfaces.values())
print(f"Found {total_macs} MAC addresses on {len(mac_interfaces)} interfaces with from dcim.mac_addresses endpoint.")

for interface in all_netbox_interfaces:
    if interface.mac_addresses:
        if not interface_macs.get(interface.name):
            interface_macs[interface.name] = []
        for mac in interface.mac_addresses:
            interface_macs[interface.name].append(mac)

total_macs_from_interface = sum(len(macs) for macs in interface_macs.values())
print(f"Found {total_macs_from_interface} MAC addresses on {len(interface_macs)} interfaces from dcim.interfaces endpoint.")

# Expose bug in mac / interface counts returned from different endpoints

# total_macs is the total number of MAC addresses on the device from the dcim.mac_addresses endpoint
# total_macs_from_interface is the total number of MAC addresses on all interfaces from the dcim.interfaces endpoint
if total_macs != total_macs_from_interface:
    print(f"BUG: Total MAC addresses from dcim.mac_addresses endpoint ({total_macs}) does not match total MAC addresses from dcim.interfaces endpoint ({total_macs_from_interface})")

# mac_interfaces[mac.assigned_object.name] -> list of MAC addresses from the dcim.mac_addresses endpoint
# interface_macs[interface.name] -> list of MAC addresses from the dcim.interfaces endpoint
if len(mac_interfaces) != len(interface_macs):
    print(f"BUG: Total interfaces from dcim.mac_addresses endpoint ({len(mac_interfaces)}) does not match total interfaces from dcim.interfaces endpoint ({len(interface_macs)})")

print()
print("Test complete")
