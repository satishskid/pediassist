#!/bin/bash
# Generate SSL certificates for development

CERT_DIR="docker/configs/ssl"
mkdir -p "$CERT_DIR"

echo "Generating SSL certificates..."

# Generate private key
openssl genrsa -out "$CERT_DIR/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.csr" -subj "/C=US/ST=State/L=City/O=PediAssist/CN=localhost"

# Generate self-signed certificate
openssl x509 -req -days 365 -in "$CERT_DIR/cert.csr" -signkey "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem"

# Clean up
rm "$CERT_DIR/cert.csr"

echo "SSL certificates generated successfully!"
echo "Certificate: $CERT_DIR/cert.pem"
echo "Private key: $CERT_DIR/key.pem"
echo ""
echo "WARNING: These are self-signed certificates for development only!"
echo "For production, use proper SSL certificates from a Certificate Authority."
