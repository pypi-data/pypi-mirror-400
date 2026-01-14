# Caddy API Client

A Python client for managing Caddy server configurations through its API.

## Installation

### Production Installation (Recommended)

For production workloads, it's recommended to install the package from PyPI:

```bash
pip install caddy-api-client
```

### Development Installation

For development or if you need to modify the client:

1. Clone the repository:
```bash
git clone https://github.com/migetapp/caddy-api-client.git
cd caddy-api-client
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Usage

```python
from caddy_api_client import CaddyAPIClient

# Initialize the client
client = CaddyAPIClient("http://localhost:2019")  # Default Caddy admin endpoint

# Add a domain with automatic TLS (Let's Encrypt/ZeroSSL) and www redirect
client.add_domain_with_auto_tls(
    domain="example.org",
    target="nginx",
    target_port=80,
    redirect_mode="domain_to_www",  # Redirects example.org to www.example.org
    enable_security_headers=True,    # Adds security headers
    enable_hsts=True                 # Enables HSTS
)

# Add a domain with www to non-www redirect
client.add_domain_with_auto_tls(
    domain="www.example.net",
    target="192.168.10.101",
    target_port=80,
    redirect_mode="www_to_domain"  # Redirects www.example.net to example.net
)

# Add a domain with custom TLS certificates using PEM data
with open('cert.pem', 'r') as f:
    certificate = f.read()
with open('key.pem', 'r') as f:
    private_key = f.read()

client.add_domain_with_tls(
    domain="example.net",
    target="192.168.10.101",
    target_port=80,
    certificate=certificate,
    private_key=private_key
)

# Get domain configuration
config = client.get_domain_config("example.com")
print(config)

# Update domain configuration
client.update_domain(
    domain="example.com",
    target="172.16.0.2",
    target_port=8080,
    redirect_mode="domain_to_www"  # Add or update redirect configuration
)

# Delete domain
client.delete_domain("example.com")  # Removes domain and its redirect configuration

## Features

- Add domains with TLS certificates using PEM data
- Add domains with automatic TLS (Let's Encrypt/ZeroSSL)
- Configure domain redirects:
  - www to non-www (`www_to_domain`)
  - non-www to www (`domain_to_www`)
- Security features:
  - Security headers (Server, X-Frame-Options, etc.)
  - HTTP Strict Transport Security (HSTS)
  - HTTP to HTTPS redirect
  - Path-based security rules
- Delete domain configurations (preserves other domain configurations)
- Get domain configurations
- Update domain configurations
- Support for HTTP/2 and HTTP/3

## Error Handling

The client includes comprehensive error handling for API requests. All methods will raise exceptions with descriptive messages if something goes wrong during the API calls.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.

Copyright 2025 Krzysztof Taraszka and The Miget Authors.
