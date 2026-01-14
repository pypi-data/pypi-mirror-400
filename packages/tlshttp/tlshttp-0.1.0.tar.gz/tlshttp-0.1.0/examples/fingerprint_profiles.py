"""Example of using different browser fingerprint profiles."""

import tlshttp


def main():
    # Test different browser profiles
    profiles = [
        ("chrome_120", "Chrome 120"),
        ("firefox_120", "Firefox 120"),
        ("safari_16_0", "Safari 16"),
        ("chrome_133", "Chrome 133 (Latest)"),
    ]

    print("Testing TLS fingerprints with different browser profiles:\n")

    for profile_id, name in profiles:
        with tlshttp.Client(profile=profile_id) as client:
            response = client.get("https://tls.peet.ws/api/all")

            if response.status_code == 200:
                data = response.json()
                ja3 = data.get("tls", {}).get("ja3", "N/A")
                http_version = data.get("http_version", "N/A")
                print(f"{name}:")
                print(f"  JA3 (first 60 chars): {ja3[:60]}...")
                print(f"  HTTP Version: {http_version}")
                print()

    # Using profile constants
    print("\nUsing profile constants:")
    print(f"Chrome.LATEST = {tlshttp.Chrome.LATEST}")
    print(f"Firefox.DEFAULT = {tlshttp.Firefox.DEFAULT}")
    print(f"Safari.IOS_LATEST = {tlshttp.Safari.IOS_LATEST}")


if __name__ == "__main__":
    main()
