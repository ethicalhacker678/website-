set -e

# Start Nginx
sudo systemctl start nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx

# Print a message indicating Nginx has started
echo "Nginx started successfully."