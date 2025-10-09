FROM nginx:alpine

# Install openssl for certificate generation
RUN apk add --no-cache openssl

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Expose ports
EXPOSE 80 443

# Use custom entrypoint that handles certificate generation
ENTRYPOINT ["/docker-entrypoint.sh"]
