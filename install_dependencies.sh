#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Update package lists to retrieve the latest version of the repository listings.
sudo apt-get update -y

# Install Nginx
sudo apt-get install -y nginx

# Install other dependencies if needed
# sudo apt-get install -y <other-dependency>

