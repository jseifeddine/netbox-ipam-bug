# NetBox IPAM Bug Reproduction

This repository contains a test environment to reproduce and verify a specific IPAM (IP Address Management) bug in NetBox where IP addresses may not be correctly assigned to interfaces when creating them in bulk.

## Bug Description

The issue occurs when:
- A large number of interfaces are created (10,000 in this test)
- The same IP addresses are assigned to multiple interfaces
- Some interfaces end up with incorrect IP address assignments (missing IPs or having too many)

## Requirements

- Docker and Docker Compose
- Python 3.x
- Git
- curl

## Quick Start

1. Clone this repository:
   ```
   git clone https://github.com/jseifeddine/netbox-ipam-bug.git
   cd netbox-ipam-bug
   ```

2. Run the initialization and test script:
   ```
   ./initialize-and-test.sh
   ```

This script will:
- Create a Python virtual environment
- Install required dependencies (pynetbox, python-dotenv)
- Start the NetBox Docker stack
- Create an API token for authentication
- Insert dummy test data (10,000 interfaces with the same IP addresses assigned to each)
- Run the test cases to verify IP address assignments
- Output results to a text file

## Customizing NetBox Version

You can specify a different NetBox version by setting the `NETBOX_VERSION` environment variable:

```
NETBOX_VERSION=v4.3.3 ./initialize-and-test.sh
```

The default version used is v4.1.5.

## Repository Contents

- `docker-compose.yml` - Docker Compose configuration for NetBox
- `initialize-and-test.sh` - Main script to set up environment and run tests
- `insert_dummy_data.py` - Script to populate NetBox with test data (creates a device with 10,000 interfaces and assigns the same IP addresses to each)
- `test-ipam.py` - Test script to verify IPAM functionality and detect assignment issues
- `requirements.txt` - Python dependencies (pynetbox, python-dotenv)

## Test Results

After running the tests, results will be saved to a text file named `test_output_[VERSION].txt` in the repository directory. This file will show if any interfaces have incorrect IP address assignments (should have exactly 2 IPs per interface).
