#!/bin/sh
set -e

# SSL certificate directory
SSL_DIR="/etc/nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"

# Create SSL directory if it doesn't exist
mkdir -p "$SSL_DIR"

# Check if certificates already exist
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "SSL certificates already exist, skipping generation"
else
    echo "Generating new self-signed SSL certificates..."

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

    # Set proper permissions
    chmod 644 "$CERT_FILE"
    chmod 600 "$KEY_FILE"

    echo "Self-signed certificates generated successfully"
fi

# Start nginx
exec nginx -g 'daemon off;'
