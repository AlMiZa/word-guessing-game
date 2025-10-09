#!/bin/sh
set -e

# Create SSL directory
mkdir -p /etc/nginx/ssl

# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1"

# Set proper permissions
chmod 644 /etc/nginx/ssl/cert.pem
chmod 600 /etc/nginx/ssl/key.pem

echo "Self-signed certificate generated successfully"
