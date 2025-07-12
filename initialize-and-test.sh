#!/bin/bash

# Exit on error
set -e

NETBOX_VERSION=${NETBOX_VERSION:-v4.1.5}

# Test for all required programs
if ! command -v docker &> /dev/null; then
    echo "docker could not be found"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "python3 could not be found"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "pip3 could not be found"
    exit 1
fi

if ! command -v curl &> /dev/null; then
    echo "curl could not be found"
    exit 1
fi

echo "Stopping NetBox docker compose stack..."
docker compose down

echo "Cleaning up previous volumes..."
docker volume rm $(basename $PWD)_postgresql > /dev/null 2>&1 || true

echo "Creating venv..."
python3 -m venv venv

echo "Activating venv..."
source venv/bin/activate

echo "Installing requirements..."
pip3 install -r requirements.txt

echo "Starting NetBox docker compose stack..."
docker compose up -d

echo "Please wait for NetBox to be available on localhost:8080... This could take a minute."
until $(curl --output /dev/null --silent --head --fail http://localhost:8080); do
    printf '.'
    sleep 5
done

echo -e "\nNetBox is up and running!"

echo "Creating API token..."
TOKEN_OUTPUT=$(docker compose exec netbox python /opt/netbox/netbox/manage.py nbshell -c "from users.models import Token, User; admin=User.objects.get(username='admin'); token=Token.objects.create(user=admin); print(f'Token created: {token.key}')")
TOKEN=$(echo "$TOKEN_OUTPUT" | grep "Token created:" | awk '{print $3}')

if [ -z "$TOKEN" ]; then
    echo "Failed to extract token from output:"
    echo "$TOKEN_OUTPUT"
    exit 1
fi

echo "Token successfully created: $TOKEN"

# Create .env file
echo "Creating .env file..."
cat > .env << EOL
NETBOX_URL=http://localhost:8080
NETBOX_TOKEN=$TOKEN
EOL

echo "Setup complete! Environment file created with NetBox URL and token."
echo "Inserting dummy data..."
./insert_dummy_data.py

echo "Testing IPAM..."
./test-ipam.py > test_output_${NETBOX_VERSION}.txt

echo "Test complete!"
echo "Test output saved to test_output_${NETBOX_VERSION}.txt"
