from caddy_api_client import CaddyAPIClient

def main():
    # Initialize the client
    client = CaddyAPIClient("http://localhost:2019")

    try:
        # Force reload of configuration
        print("\nForcing configuration reload...")
        client.reload()
        print("Done!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
