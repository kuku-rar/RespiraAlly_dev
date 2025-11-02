#!/bin/sh

# =================================================================================================
# -- Script to manage Let's Encrypt certificates for Nginx
# --
# -- This script performs the following actions:
# -- 1. Checks if a valid certificate already exists for the specified domains.
# -- 2. If no certificate is found, it creates a temporary self-signed certificate
# --    to allow Nginx to start up securely.
# -- 3. It then requests a real certificate from Let's Encrypt in the background.
# --    Once obtained, Nginx is reloaded to use the new certificate.
# -- 4. If a certificate already exists, it simply starts Nginx.
# =================================================================================================

# --- Configuration ---
#
# DOMAINS: A space-separated list of domain names for the certificate.
#          The first domain is the primary domain.
#          Example: "example.com www.example.com"
#
# EMAIL: The email address for Let's Encrypt registration and recovery.
#
# STAGING: Set to 1 to use Let's Encrypt's staging environment for testing.
#          This avoids hitting rate limits on the production servers.
#          Set to 0 for production certificates.
#
# RSA_KEY_SIZE: The size of the RSA key. Default is 4096.
#
# IMPORTANT:
# It is highly recommended to set DOMAINS and EMAIL via environment variables
# in your docker-compose file (e.g., CERTBOT_DOMAINS, CERTBOT_EMAIL)
# instead of hardcoding them here.
# The script will use environment variables if they exist.

DOMAINS=${CERTBOT_DOMAINS}
EMAIL=${CERTBOT_EMAIL}
STAGING=${CERTBOT_STAGING:-1} # Set to 1 for testing, 0 for production
RSA_KEY_SIZE=4096
DATA_PATH="/etc/letsencrypt"
WEBROOT_PATH="/var/www/certbot"

# --- Helper Functions ---

# Output a message to stderr
log_error() {
  echo "[ERROR] $1" >&2
}

# Output a message to stdout
log_info() {
  echo "[INFO] $1"
}

# --- Pre-run Checks ---
if [ -z "$DOMAINS" ]; then
  log_error "The CERTBOT_DOMAINS environment variable is not set. Please provide your domain(s)."
  exit 1
fi

if [ -z "$EMAIL" ]; then
  log_error "The CERTBOT_EMAIL environment variable is not set. Please provide your email address."
  exit 1
fi

# --- Main Logic ---

# --- Configuration Initialization ---
log_info "Initializing SSL configurations..."

# Copy SSL options if they don't exist in the volume
if [ ! -f "$DATA_PATH/options-ssl-nginx.conf" ]; then
  log_info "Copying SSL options file..."
  cp /tmp/options-ssl-nginx.conf "$DATA_PATH/options-ssl-nginx.conf"
fi

# Generate DH parameters if they don't exist
if [ ! -f "$DATA_PATH/ssl-dhparams.pem" ]; then
  log_info "Generating DH parameters (2048 bit)... This may take a while."
  openssl dhparam -out "$DATA_PATH/ssl-dhparams.pem" 2048
fi

# Export the primary domain for envsubst
export DOMAIN_NAME=$(echo "$DOMAINS" | awk '{print $1}')

# Substitute environment variables in the nginx config template
envsubst '${DOMAIN_NAME}' < /etc/nginx/templates/default.conf.template > /etc/nginx/conf.d/default.conf

# Check if the primary domain's certificate directory already exists.
if [ -d "$DATA_PATH/live/$DOMAIN_NAME" ]; then
  log_info "Certificate found for $DOMAIN_NAME. Skipping creation."
else
  log_info "No certificate found for $DOMAIN_NAME. Starting provisioning process..."

  # --- Step 1: Create a self-signed certificate for Nginx to start ---
  log_info "Generating a self-signed certificate for initial Nginx startup..."
  # Create a temporary path for the self-signed certificate.
  local_path="/tmp/self-signed"
  mkdir -p "$local_path/live/$DOMAIN_NAME"

  # Generate the self-signed certificate using OpenSSL.
  openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 365 \
    -keyout "$local_path/live/$DOMAIN_NAME/privkey.pem" \
    -out "$local_path/live/$DOMAIN_NAME/fullchain.pem" \
    -subj "/CN=localhost"

  # Temporarily use the self-signed certificate by creating a symlink.
  # This allows Nginx to start before the real certificate is available.
  ln -s "$local_path/live" "$DATA_PATH/live"
  ln -s "$local_path/archive" "$DATA_PATH/archive"

  # --- Step 2: Start Nginx in the background with the self-signed cert ---
  log_info "Starting Nginx in the background with the self-signed certificate..."
  # The `envsubst` command replaces variables in the Nginx template.
  nginx -g "daemon on;"

  # --- Step 3: Request the real certificate from Let's Encrypt ---
  log_info "Requesting Let's Encrypt certificate for $DOMAINS..."

  # Remove the temporary symlinks to avoid conflicts with Certbot
  rm -f "$DATA_PATH/live"
  rm -f "$DATA_PATH/archive"

  # Prepare Certbot command arguments
  domain_args=""
  for domain in $DOMAINS; do
    domain_args="$domain_args -d $domain"
  done

  staging_arg=""
  if [ "$STAGING" != "0" ]; then
    staging_arg="--staging"
    log_info "Using Let's Encrypt staging environment."
  fi

  # Run Certbot to obtain the certificate.
certbot certonly --webroot -w "$WEBROOT_PATH" \
    $staging_arg \
    $domain_args \
    --email "$EMAIL" \
    --rsa-key-size "$RSA_KEY_SIZE" \
    --agree-tos \
    --non-interactive

  # Check if Certbot succeeded
  if [ $? -ne 0 ]; then
    log_error "Certbot failed to obtain a certificate. Falling back to self-signed certificate."
    # Stop the background Nginx process. The script will continue and restart it with self-signed cert.
    nginx -s stop
    # Wait for nginx to stop
    while pgrep -x nginx > /dev/null; do sleep 1; done
    # Restore the self-signed certificate symlinks so nginx can start
    ln -s /tmp/self-signed/live "$DATA_PATH/live"
    ln -s /tmp/self-signed/archive "$DATA_PATH/archive"
  else
    log_info "Certificate obtained successfully."
    # Stop the background Nginx process
    log_info "Stopping background Nginx to restart in foreground with the new certificate..."
    nginx -s stop
    # Wait for nginx to stop
    while pgrep -x nginx > /dev/null; do sleep 1; done
    # The final exec will start nginx with the new cert.
  fi
fi

# --- Final Step: Start Cron and Nginx in the foreground ---

# Start the cron daemon in the background
log_info "Starting cron daemon..."
crond -b -l 8

# The `exec "$@"` command executes the command passed to this script,
# which in the docker-compose file is `nginx -g "daemon off;"`.
# This ensures Nginx runs as the main process (PID 1) in the container.
log_info "Starting Nginx in foreground..."
exec "$@"
