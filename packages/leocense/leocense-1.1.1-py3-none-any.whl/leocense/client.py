
import requests
from .device import get_device_fingerprint

class LeocenseClient:
    def __init__(self, api_key=None, base_url="https://leocense.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _handle_response(self, response):
        try:
            data = response.json()
            if response.status_code >= 400:
                # Ensure consistent error shape even if server just sends message
                return {
                    "success": False,
                    "valid": False,
                    "message": data.get("message", "Request failed"),
                    "reason": data.get("data", {}).get("reason")
                }
            return data
        except ValueError:
            return {"success": False, "valid": False, "reason": "Invalid JSON response", "message": "Invalid JSON response"}

    def verify_license(self, license_key, product_id):
        """
        Verifies a license key without binding it to the current device.
        """
        try:
            url = f"{self.base_url}/api/v1/verify"
            payload = {
                "licenseKey": license_key,
                "productId": product_id
            }
            response = self.session.post(url, json=payload)
            data = self._handle_response(response)
            
            if data.get("success"):
                result = data.get("data", {})
                # Merge data into top level for convenience
                return {"valid": result.get("valid"), "success": True, "data": result, **result}
            
            return {
                "valid": False, 
                "success": False, 
                "message": data.get("message"), 
                "reason": data.get("reason")
            }
        except Exception as e:
            return {"valid": False, "success": False, "reason": str(e), "message": str(e)}

    def verify_license_with_device(self, license_key, product_id):
        """
        Verifies a license key AND binds/validates the current device.
        Uses hardware-locked fingerprinting.
        """
        try:
            fingerprint = get_device_fingerprint()
            url = f"{self.base_url}/api/v1/verify"
            payload = {
                "licenseKey": license_key,
                "productId": product_id,
                "deviceFingerprint": fingerprint
            }
            response = self.session.post(url, json=payload)
            data = self._handle_response(response)

            if data.get("success"):
                result = data.get("data", {})
                return {"valid": result.get("valid"), "success": True, "data": result, **result}
            
            return {
                "valid": False, 
                "success": False, 
                "message": data.get("message"), 
                "reason": data.get("reason")
            }
        except Exception as e:
            return {"valid": False, "success": False, "reason": str(e), "message": str(e)}

    def verify_access_token(self, access_token):
        try:
            url = f"{self.base_url}/api/v1/verify/access-token"
            payload = {"accessToken": access_token}
            response = self.session.post(url, json=payload)
            data = self._handle_response(response)
            
            if data.get("success"):
                result = data.get("data", {})
                return {"valid": True, "success": True, "data": result, **result}
            
            return {"valid": False, "success": False, "message": data.get("message")}
        except Exception as e:
            return {"valid": False, "success": False, "reason": str(e), "message": str(e)}

    def check_update(self, product_id, current_version):
        try:
            url = f"{self.base_url}/api/v1/check-update/{product_id}"
            params = {"currentVersion": current_version}
            response = self.session.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None

    # Management Methods

    def _ensure_api_key(self):
        if not self.api_key:
            raise ValueError("API Key is required for this operation.")

    def create_license(self, payload):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses"
        response = self.session.post(url, json=payload)
        return self._handle_response(response)

    def get_license(self, license_id):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses/{license_id}"
        response = self.session.get(url)
        return self._handle_response(response)

    def get_licenses(self):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses"
        response = self.session.get(url)
        return self._handle_response(response)

    def activate_license(self, license_id):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses/{license_id}/activate"
        response = self.session.post(url)
        return self._handle_response(response)

    def block_license(self, license_id):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses/{license_id}/block"
        response = self.session.post(url)
        return self._handle_response(response)

    def delete_license(self, license_id):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/licenses/{license_id}"
        response = self.session.delete(url)
        return self._handle_response(response)

    def create_product(self, payload):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/products"
        response = self.session.post(url, json=payload)
        return self._handle_response(response)

    def get_products(self):
        self._ensure_api_key()
        url = f"{self.base_url}/api/v1/products"
        response = self.session.get(url)
        return self._handle_response(response)
