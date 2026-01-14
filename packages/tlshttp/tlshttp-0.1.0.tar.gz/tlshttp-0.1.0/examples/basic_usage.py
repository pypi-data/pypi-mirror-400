"""Basic usage example for tlshttp."""

import tlshttp


def main():
    # Create a client with Chrome 120 fingerprint
    with tlshttp.Client(profile="chrome_120") as client:
        # Simple GET request
        response = client.get("https://httpbin.org/get")
        print(f"Status: {response.status_code}")
        print(f"HTTP Version: {response.http_version}")
        print(f"Origin: {response.json()['origin']}")

        # GET with query parameters
        response = client.get(
            "https://httpbin.org/get",
            params={"key": "value", "page": "1"},
        )
        print(f"\nWith params: {response.json()['args']}")

        # POST with JSON
        response = client.post(
            "https://httpbin.org/post",
            json={"message": "Hello, World!", "number": 42},
        )
        print(f"\nPOST response: {response.json()['json']}")

        # POST with form data
        response = client.post(
            "https://httpbin.org/post",
            data={"username": "john", "password": "secret"},
        )
        print(f"\nForm data: {response.json()['form']}")

        # Custom headers
        response = client.get(
            "https://httpbin.org/headers",
            headers={"X-Custom-Header": "custom-value"},
        )
        print(f"\nHeaders sent: {response.json()['headers']}")


if __name__ == "__main__":
    main()
