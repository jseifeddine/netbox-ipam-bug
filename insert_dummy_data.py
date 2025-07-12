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

