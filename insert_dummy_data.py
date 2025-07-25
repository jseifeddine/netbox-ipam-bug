#!venv/bin/python

from dotenv import load_dotenv
import os
import pynetbox

load_dotenv()

INTERFACE_COUNT = 10000

nb = pynetbox.api(
    url=os.getenv("NETBOX_URL"),
    token=os.getenv("NETBOX_TOKEN")
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
netbox_version = status["netbox-version"]

# Helper function to get or create objects
def get_or_create(endpoint, **kwargs):
    try:
        obj = endpoint.create(**kwargs)
        print(f"Created {kwargs.get('name', kwargs.get('model', 'object'))}")
        return obj
    except pynetbox.core.query.RequestError as e:
        print(f"Error creating {kwargs.get('name', 'object')}: {e}")
        # Try to get the object if it already exists
        filters = {k: v for k, v in kwargs.items() if k in ['name', 'slug']}
        if filters:
            existing = list(endpoint.filter(**filters))
            if existing:
                print(f"Using existing {kwargs.get('name', 'object')}")
                return existing[0]
        raise

print(f"Creating device role...")
# Create device role
try:
    device_role = get_or_create(nb.dcim.device_roles,
        name="dummy switch role",
        slug="dummy-switch-role",
        color="ff0000"
    )
except Exception as e:
    print(f"Failed to create device role: {e}")
    exit(1)

print(f"Creating manufacturer...")
# Create manufacturer
try:
    manufacturer = get_or_create(nb.dcim.manufacturers,
        name="dummy switch manufacturer",
        slug="dummy-switch-manufacturer"
    )
except Exception as e:
    print(f"Failed to create manufacturer: {e}")
    exit(1)

print(f"Creating device type...")
# Create device type
try:
    device_type = get_or_create(nb.dcim.device_types,
        model="dummy switch device type",
        slug="dummy-switch-device-type",
        manufacturer=manufacturer.id
    )
except Exception as e:
    print(f"Failed to create device type: {e}")
    exit(1)

print(f"Creating site...")
# Create site
try:
    site = get_or_create(nb.dcim.sites,
        name="dummy site",
        slug="dummy-site"
    )
except Exception as e:
    print(f"Failed to create site: {e}")
    exit(1)

print(f"Creating device...")
# Create device
try:
    device = get_or_create(nb.dcim.devices,
        name="dummy switch",
        device_type=device_type.id,
        role=device_role.id,
        site=site.id
    )
except Exception as e:
    print(f"Failed to create device: {e}")
    exit(1)

# Create 500 interfaces in bulk
interface_data = []
for i in range(INTERFACE_COUNT):
    interface_data.append({
        "device": device.id,
        "name": f"dummy{i}",
        "type": "1000base-t"
    })

print(f"Creating {len(interface_data)} interfaces...")
try:
    interfaces = nb.dcim.interfaces.create(interface_data)
    print(f"Created {len(interfaces)} interfaces")
except pynetbox.core.query.RequestError as e:
    print(f"Error creating interfaces: {e}")
    # If bulk creation fails, try to get existing interfaces
    interfaces = []
    for i in range(INTERFACE_COUNT):
        try:
            interface = nb.dcim.interfaces.get(device_id=device.id, name=f"dummy{i}")
            if interface:
                interfaces.append(interface)
        except:
            pass
    print(f"Found {len(interfaces)} existing interfaces")

if not interfaces:
    print("No interfaces to assign IP addresses to")
    exit(1)

ip_data = []
for interface in interfaces:
    ip_data.append({
        "address": "172.17.0.1/32",
        "assigned_object_type": "dcim.interface",
        "assigned_object_id": interface.id
    })
    ip_data.append({
        "address": "ff1d:0c7c:7b44:d39d:ab3d:6fde:f46a:4648/64",
        "assigned_object_type": "dcim.interface",
        "assigned_object_id": interface.id
    })

# Create the same IP address for all interfaces in bulk
print(f"Creating {len(ip_data)} IP addresses for {len(interfaces)} interfaces...")
try:
    ip_addresses = nb.ipam.ip_addresses.create(ip_data)
    print(f"Created {len(ip_addresses)} IP addresses")
except pynetbox.core.query.RequestError as e:
    print(f"Error creating IP addresses: {e}")

# Create MAC addresses for all interfaces in bulk
mac_data = []
for interface in interfaces:
    mac_data.append({
        "mac_address": "18:2A:D3:65:90:2E",
        "assigned_object_type": "dcim.interface",
        "assigned_object_id": interface.id
    })

if is_version_above(netbox_version, "4.2.0"):
    print(f"Creating {len(mac_data)} MAC addresses for {len(interfaces)} interfaces...")
    try:
        mac_addresses = nb.dcim.mac_addresses.create(mac_data)
        print(f"Created {len(mac_addresses)} MAC addresses")
    except pynetbox.core.query.RequestError as e:
        print(f"Error creating MAC addresses: {e}")
        mac_addresses = []

    # Set MAC addresses as primary for their interfaces
    if mac_addresses:
        print(f"Setting primary MAC addresses for interfaces...")
        interfaces_to_update = []
        
        for interface, mac in zip(interfaces, mac_addresses):
            interfaces_to_update.append({
                'id': interface.id,
                'primary_mac_address': mac.id
            })
        
        try:
            updated_interfaces = nb.dcim.interfaces.update(interfaces_to_update)
            print(f"Updated {len(updated_interfaces)} interfaces with primary MAC addresses")
        except pynetbox.core.query.RequestError as e:
            print(f"Error setting primary MAC addresses: {e}")

