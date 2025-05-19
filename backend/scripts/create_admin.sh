#!/bin/bash
# Script to create an admin user in the Docker container

# Check if arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 email password"
    exit 1
fi

EMAIL=$1
PASSWORD=$2

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create the __init__.py file to make scripts a proper package if it doesn't exist
touch "$SCRIPT_DIR/__init__.py"

# Check if Docker container is running
CONTAINER_ID=$(docker ps -q -f name=repport-backend)

if [ -z "$CONTAINER_ID" ]; then
    echo "Backend container is not running. Please start the containers with 'docker-compose up'."
    exit 1
fi

# Copy the script to the container
docker cp "$SCRIPT_DIR/create_admin.py" $CONTAINER_ID:/app/scripts/
docker cp "$SCRIPT_DIR/__init__.py" $CONTAINER_ID:/app/scripts/

# Run the command inside the container
echo "Creating admin user $EMAIL..."
docker exec $CONTAINER_ID python -m scripts.create_admin $EMAIL $PASSWORD

echo "Done!" 