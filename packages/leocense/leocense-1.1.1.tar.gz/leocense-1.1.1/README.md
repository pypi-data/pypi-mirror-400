# Leocense Python SDK

The official Python SDK for [Leocense](https://leocense.com), the complete software licensing and distribution platform. This SDK allows you to verify licenses, implement hardware-locked device fingerprinting, and manage licenses/products programmatically.

## Table of Contents
- [Installation](#installation)
- [Getting Started](#getting-started)
- [Client-Side Usage (Verification)](#client-side-usage-verification)
  - [Verify License](#verify-license)
  - [Verify with Hardware Locking](#verify-with-hardware-locking)
  - [Check for Updates](#check-for-updates)
- [Server-Side Usage (Management)](#server-side-usage-management)
  - [Create License](#create-license)
  - [Get/List Licenses](#getlist-licenses)
  - [Activate/Block License](#activateblock-license)
  - [Manage Products](#manage-products)
- [Response Structure](#response-structure)
- [Integration Best Practices](#integration-best-practices)
- [Changelog](#changelog)

---

## Installation

Install the package via pip:

```bash
pip install leocense
```

## Getting Started

Import `LeocenseClient` from the package.

```python
from leocense import LeocenseClient
```

There are two main ways to initialize the client:

1.  **Public/Client Mode**: No API key required. Used inside your desktop or CLI application to verify licenses.
    ```python
    client = LeocenseClient()
    ```

2.  **Management/Admin Mode**: API Key required. Used on your backend server to create/manage licenses.
    ```python
    client = LeocenseClient(api_key="YOUR_SECRET_API_KEY")
    ```

**Note**: You can also specify a custom base URL if you are using a self-hosted instance:
```python
client = LeocenseClient(api_key="API_KEY", base_url="https://your-custom-domain.com")
```

---

## Client-Side Usage (Verification)

These methods are safe to use in your distributed application. They do NOT require an API Key.

### Verify License

Checks if a license key is valid, active, and not expired. This **does not** bind the license to a specific device.

**Use Case**: Lightweight check on app startup or web portal login.

```python
result = client.verify_license("LICENSE-KEY-123", "PRODUCT-ID-456")

if result.get("success") and result.get("valid"):
    print("License is valid!")
    print("App:", result.get("appName"))
    print("Owner:", result.get("ownerName"))
    print("Expiry:", result.get("expiryDate"))
else:
    print("Verification failed:", result.get("message"))
```

### Verify with Hardware Locking

This is the **recommended** method for desktop/CLI apps. It generates a unique, weighted hardware fingerprint (Motherboard, Disk, CPU, MAC) of the user's machine, sends it to Leocense, and binds the license to that device.

**Use Case**: Preventing license sharing. The license will be locked to the first device(s) it is used on, up to the `allowedDevices` limit.

```python
try:
    result = client.verify_license_with_device("LICENSE-KEY-123", "PRODUCT-ID-456")

    if result.get("success") and result.get("valid"):
        print("License active on this device.")
        print("Variant:", result.get("variantName"))
        print("Info:", result.get("data")) # Contains full details
    else:
        # Handle specific failure reasons
        reason = result.get("reason")
        if reason == "device_limit_blocked":
            print("License used on too many devices.")
        elif reason == "expired":
            print("License has expired.")
        elif reason == "blocked":
            print("License has been blocked by the vendor.")
        else:
            print("Invalid license:", result.get("message"))

except Exception as e:
    print("Network or System Error:", e)
```

### Check for Updates

Checks if a newer version of your product is available.

**Use Case**: Showing an "Update Available" notification in your app.

```python
update = client.check_update("PRODUCT-ID-456", "1.0.0") # Current App Version

if update and update.get("updateAvailable"):
    print("New version found:", update.get("latestVersion"))
    print("Changelog:", update.get("changelog"))
    print("Download here:", update.get("downloadUrl"))

### Verify Access Token

Verifies an encrypted access token returned by the verify endpoint.

```python
result = client.verify_access_token("ey...")

if result.get("success") and result.get("valid"):
    data = result.get("data")
    # Access nested token/license info
    print("Token valid for product:", data.get("token", {}).get("productId"))
    print("License ID:", data.get("license", {}).get("id"))
    print("Download URL:", data.get("downloadUrl"))
else:
    print("Invalid token")
```
```

---

## Server-Side Usage (Management)

These methods **require an API Key** with `write` permissions. NEVER use these in your client-side code distributed to users.

### Create License

Generates a new license key for a customer.

**Use Case**: Automating license creation after a Stripe/PayPal payment webhook.

```python
from leocense import LeocenseClient

admin_client = LeocenseClient(api_key="YOUR_ADMIN_API_KEY")

def generate_license_for_customer():
    try:
        new_license = admin_client.create_license({
            "productId": "PRODUCT-ID-456",
            "ownerName": "John Doe",
            "email": "john@example.com", # Optional: Customer email
            "expiryDate": "2025-12-31T23:59:59Z", # Optional: Set expiration
            "limitDevices": True, # Enable hardware locking
            "allowedDevices": 2,  # Allow use on 2 devices
            "metadata": {         # Custom data
                "plan": "pro",
                "source": "stripe"
            }
        })

        print("Created License:", new_license.get("licenseKey"))
    except Exception as e:
        print("Failed to create license:", e)
```

### Get/List Licenses

Retrieve details about specific licenses or list all licenses.

```python
# Get single license
license_data = admin_client.get_license("LICENSE-ID")

# List all licenses
all_licenses = admin_client.get_licenses()
```

### Activate/Block License

Control the status of issued licenses (e.g., if a refund occurs or a subscription is cancelled).

```python
# Block a license (Prevent further verifications)
admin_client.block_license("LICENSE-ID")

# Reactivate a blocked license
admin_client.activate_license("LICENSE-ID")

# Delete a license permanently
admin_client.delete_license("LICENSE-ID")
```

### Manage Products

Create and retrieve products programmatically.

```python
new_product = admin_client.create_product({
    "name": "My Awesome App",
    "version": "1.0.0",
    "downloadUrl": "https://example.com/download/app-v1.zip"
})
```

---

## Response Structure

The SDK methods return a dictionary following this structure:

```python
{
    "success": True,       # True if request succeeded
    "valid": True,         # True if license is valid (for verification)
    "message": "...",      # Error message if any
    "data": { ... },       # Full license details
    # Convenience keys merged from data:
    "reason": "...",
    "accessToken": "...",
    "appName": "...",
    "variantName": "...",
    "ownerName": "...",
    "ownerEmail": "...",
    "expiryDate": "...",
    "downloadUrl": "...",
    "properties": "..."
}
```

---

## Integration Best Practices

1.  **Local Caching**: After a successful `verify_license_with_device`, you should cache the result (and potentially the `accessToken` or `expiryDate`) locally in a secure file (encrypted/pickled). This allows your app to work offline for a grace period.
2.  **Graceful Failures**: Always handle network errors (`try/except`). If the Leocense server is unreachable, decide if you want to allow access (soft fail) or block access (hard fail) based on your security needs.
3.  **Security**: Obfuscate your `productId` in your client code. Do NOT ship your Admin API Key in your client application.

---

## Changelog

### v1.1.1
- **Enhanced Device Fingerprinting**: Added `hostname` capture to `verify_license_with_device()`.
- **Robust Hostname Detection**: Now supports Windows, macOS, and Linux (including Kali) using multiple fallback methods (`socket`, `platform`, shell `hostname`).
