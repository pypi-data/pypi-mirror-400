from caddy_api_client import CaddyAPIClient

def main():
    client = CaddyAPIClient("http://localhost:2019")

    # Example domain and backend service
    domain = "example.com"  # Replace with your actual domain
    nginx_container_ip = "nginx"  # Docker service name will resolve to container IP
    nginx_port = 80

    try:
        # Add domain with auto TLS and security headers
        client.add_domain_with_auto_tls(
            domain=domain,
            target=nginx_container_ip,
            target_port=nginx_port,
#            enable_security_headers=True,  # Enable security headers
#            enable_hsts=True,              # Enable HSTS
#            frame_options="DENY",          # Set X-Frame-Options
#            enable_compression=True        # Enable compression
        )
        print(f"Successfully added domain {domain} with automatic TLS")

        # Get and print the domain configuration
        config = client._make_request('GET', '/config/apps/http/servers/srv0/routes').json()
        print("\nDomain configuration:")
        print(config)

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
