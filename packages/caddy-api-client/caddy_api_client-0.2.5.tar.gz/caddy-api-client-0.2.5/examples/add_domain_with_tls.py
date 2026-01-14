from caddy_api_client import CaddyAPIClient

def main():
    # Initialize the client
    client = CaddyAPIClient("http://localhost:2019")

    # Example domain and backend service
    domain = "example.com"  # Replace with your actual domain
    target = "nginx"  # Docker service name will resolve to container IP
    target_port = 80  # Replace with your backend service port

    try:
        # Read certificate and key PEM files
        with open('tls.crt', 'r') as f:
            certificate = f.read()
        with open('tls.key', 'r') as f:
            private_key = f.read()

        # Add domain with PEM certificate
        client.add_domain_with_tls(
            domain=domain,
            target=target,
            target_port=target_port,
            certificate=certificate,
            private_key=private_key
        )
        print(f"Successfully added domain {domain} with PEM certificate")

        # Show domain configuration
        config = client.get_domain_config(domain)
        print("\nDomain configuration:")
        print(config)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
