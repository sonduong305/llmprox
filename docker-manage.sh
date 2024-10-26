#!/bin/bash

# Available environments
environments=("docs" "local" "production")

# Function to display usage
show_usage() {
    echo "Usage: $0 [environment] [docker-compose-commands]"
    echo "Environments: ${environments[*]}"
    echo "Example: $0 local up -d"
}

# Check if minimum arguments are provided
if [ $# -lt 2 ]; then
    show_usage
    exit 1
fi

environment=$1
shift # Remove first argument, leaving remaining for docker compose command

# Validate environment
if [[ ! " ${environments[@]} " =~ " ${environment} " ]]; then
    echo "Error: Invalid environment. Choose from: ${environments[*]}"
    exit 1
fi

# Execute docker compose command with all remaining arguments
docker compose -f "docker-compose.${environment}.yml" $@
