# Use official n8n image
FROM n8nio/n8n:latest

# Enable basic authentication (optional but recommended)
ENV N8N_BASIC_AUTH_ACTIVE=true
ENV N8N_BASIC_AUTH_USER=admin
ENV N8N_BASIC_AUTH_PASSWORD=admin123

# Expose port
EXPOSE 5678

# Default command to run n8n
ENTRYPOINT ["tini", "--"]
CMD ["n8n"]

