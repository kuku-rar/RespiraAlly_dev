#!/bin/sh
echo "Running certbot renew..."
certbot renew --quiet --no-self-upgrade

# Reload nginx to apply the new certificate if renewed
# Use kill -HUP to gracefully reload nginx configuration
echo "Reloading nginx..."
pkill -HUP -f "nginx: master process"
