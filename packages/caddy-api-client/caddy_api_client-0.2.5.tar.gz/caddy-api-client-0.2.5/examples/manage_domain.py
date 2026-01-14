from caddy_api_client import CaddyAPIClient

def main():
    # Initialize the client
    client = CaddyAPIClient("http://localhost:2019")

    # Domain configuration
    domain = "example.com"  # Replace with your actual domain
    target = "nginx"  # Docker service name will resolve to container IP
    target_port = 80  # Replace with your backend service port

    try:
        # Update domain with auto TLS
        print(f"\nUpdating {domain} with auto TLS...")
        client.update_domain(
            domain=domain,
            target=target,
            target_port=target_port,
            certificate="auto"
        )
        print(f"Successfully updated {domain} with auto TLS")

        # Show updated configuration
        config = client.get_domain_config(domain)
        print("\nUpdated configuration:")
        print(config)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()