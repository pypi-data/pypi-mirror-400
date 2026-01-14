from caddy_api_client import CaddyAPIClient

def main():
    # Initialize the client
    client = CaddyAPIClient("http://localhost:2019")

    # Example domain
    domain = "example.com"

    try:
        # Delete domain configuration
        client.delete_domain(domain)
        print(f"Successfully deleted domain {domain}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
