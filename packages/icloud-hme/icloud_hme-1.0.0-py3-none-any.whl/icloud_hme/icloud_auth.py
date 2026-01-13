import json
import uuid
import hashlib
import base64
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

import requests
import srp

# Constants
AUTH_ENDPOINT = "https://idmsa.apple.com/appleauth/auth"
SETUP_ENDPOINT = "https://setup.icloud.com/setup/ws/1"
HOME_ENDPOINT = "https://www.icloud.com"
WIDGET_KEY = "d39ba9916b7251055b22c7f910e2ea796ee65e98b2ddecea8f5dde8d9d1a815d"

CLIENT_BUILD_NUMBER = "2546Build34"
CLIENT_MASTERING_NUMBER = "2546Build34"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"


class ICloudSession:
    """Manages iCloud authentication and session persistence."""

    def __init__(self, credentials_file: str = "icloud_session.json", quiet: bool = False):
        self.credentials_file = Path(credentials_file)
        self.quiet = quiet
        self.session = requests.Session()
        self.client_id = str(uuid.uuid4())
        self.session_id = None
        self.scnt = None
        self.auth_attributes = None
        self.session_token = None
        self.trust_token = None
        self.dsid = None
        self.account_info = None
        self.webservices = None
        
        # Set default headers
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": HOME_ENDPOINT,
            "Referer": f"{HOME_ENDPOINT}/",
        })
    
    def _log(self, message: str):
        """Print message if not in quiet mode."""
        if not self.quiet:
            print(message)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers for Apple ID requests."""
        import time
        import json as json_module
        
        # Build device fingerprint header
        fd_client_info = json_module.dumps({
            "U": USER_AGENT,
            "L": "en-US",
            "Z": "GMT-05:00",
            "V": "1.1",
            "F": ""  # Fingerprint field - can be empty
        }, separators=(',', ':'))
        
        headers = {
            "X-Apple-Widget-Key": WIDGET_KEY,
            "X-Apple-OAuth-Client-Id": WIDGET_KEY,
            "X-Apple-OAuth-Client-Type": "firstPartyAuth",
            "X-Apple-OAuth-Redirect-URI": HOME_ENDPOINT,
            "X-Apple-OAuth-Response-Type": "code",
            "X-Apple-OAuth-Response-Mode": "web_message",
            "X-Apple-OAuth-Require-Grant-Code": "true",
            "X-Apple-Domain-Id": "3",
            "X-Apple-Locale": "en_US",
            "X-Apple-Privacy-Consent": "true",
            "X-Apple-Privacy-Consent-Accepted": "true",
            "X-Apple-Offer-Security-Upgrade": "1",
            "X-Apple-I-FD-Client-Info": fd_client_info,
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/json",
        }
        
        if self.session_id:
            headers["X-Apple-ID-Session-Id"] = self.session_id
        if self.scnt:
            headers["scnt"] = self.scnt
        if self.auth_attributes:
            headers["X-Apple-Auth-Attributes"] = self.auth_attributes
            
        # Frame ID for OAuth flow
        frame_id = str(uuid.uuid4())
        headers["X-Apple-Frame-Id"] = frame_id
        headers["X-Apple-OAuth-State"] = frame_id
        
        return headers

    def _update_auth_state(self, response: requests.Response):
        """Update authentication state from response headers."""
        if "X-Apple-ID-Session-Id" in response.headers:
            self.session_id = response.headers["X-Apple-ID-Session-Id"]
        if "scnt" in response.headers:
            self.scnt = response.headers["scnt"]
        if "X-Apple-Auth-Attributes" in response.headers:
            self.auth_attributes = response.headers["X-Apple-Auth-Attributes"]
        if "X-Apple-Session-Token" in response.headers:
            self.session_token = response.headers["X-Apple-Session-Token"]
        if "X-Apple-TwoSV-Trust-Token" in response.headers:
            self.trust_token = response.headers["X-Apple-TwoSV-Trust-Token"]

    def _srp_authenticate(self, email: str, password: str) -> Tuple[bool, str]:
        """
        Perform SRP authentication with Apple using their custom s2k protocol.
        Uses the srp library with Apple-specific settings.
        
        Based on: https://github.com/mandarons/icloudpy
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Custom password class that handles Apple's s2k key derivation
        class SrpPassword:
            def __init__(self, password: str):
                self.password = password
                self.salt = None
                self.iterations = None
                self.key_length = None

            def set_encrypt_info(self, salt: bytes, iterations: int, key_length: int):
                self.salt = salt
                self.iterations = iterations
                self.key_length = key_length

            def encode(self) -> bytes:
                # Apple's s2k: SHA256(password) -> PBKDF2
                password_hash = hashlib.sha256(self.password.encode('utf-8')).digest()
                return hashlib.pbkdf2_hmac(
                    'sha256',
                    password_hash,
                    self.salt,
                    self.iterations,
                    self.key_length
                )

        # Configure SRP library for Apple's protocol
        srp.rfc5054_enable()
        srp.no_username_in_x()
        
        # Create SRP password wrapper
        srp_password = SrpPassword(password)
        
        # Create SRP user
        usr = srp.User(
            email,
            srp_password,
            hash_alg=srp.SHA256,
            ng_type=srp.NG_2048
        )
        
        # Step 1: Get A value
        uname, a_bytes = usr.start_authentication()
        
        # Step 2: Send init request
        init_data = {
            "a": base64.b64encode(a_bytes).decode(),
            "accountName": uname,
            "protocols": ["s2k", "s2k_fo"]
        }
        
        headers = self._get_auth_headers()
        response = self.session.post(
            f"{AUTH_ENDPOINT}/signin/init",
            headers=headers,
            json=init_data
        )
        
        self._update_auth_state(response)
        
        if response.status_code != 200:
            return False, f"SRP init failed: {response.status_code} - {response.text}"
        
        init_result = response.json()
        
        # Extract server values
        salt = base64.b64decode(init_result["salt"])
        b_bytes = base64.b64decode(init_result["b"])
        iterations = init_result["iteration"]
        c_value = init_result["c"]
        protocol = init_result["protocol"]
        
        self._log(f"[*] SRP Protocol: {protocol}, Iterations: {iterations}")
        
        # Set encryption info for password derivation
        srp_password.set_encrypt_info(salt, iterations, 32)
        
        # Process challenge to get M1
        m1 = usr.process_challenge(salt, b_bytes)
        if m1 is None:
            return False, "SRP challenge processing failed"
        
        m2 = usr.H_AMK
        
        # Step 3: Complete sign-in
        complete_data = {
            "accountName": uname,
            "c": c_value,
            "m1": base64.b64encode(m1).decode(),
            "m2": base64.b64encode(m2).decode(),
            "rememberMe": True,
            "trustTokens": []
        }
        
        headers = self._get_auth_headers()
        response = self.session.post(
            f"{AUTH_ENDPOINT}/signin/complete",
            params={"isRememberMeEnabled": "true"},
            headers=headers,
            json=complete_data
        )
        
        self._update_auth_state(response)
        
        if response.status_code == 200:
            return True, "Authentication successful"
        elif response.status_code == 409:
            # 2FA required - this is success, just needs 2FA
            result = response.json()
            auth_type = result.get("authType", "unknown")
            return True, f"2FA_REQUIRED:{auth_type}"
        elif response.status_code == 401:
            return False, f"Invalid credentials"
        elif response.status_code == 403:
            # Try to get the actual error message
            try:
                error_data = response.json()
                errors = error_data.get("serviceErrors", [])
                if errors:
                    return False, errors[0].get("message", "Account locked")
            except:
                pass
            return False, f"Authentication forbidden - account may be locked"
        else:
            return False, f"SRP complete failed: {response.status_code}"

    def _verify_2fa_code(self, code: str) -> Tuple[bool, str]:
        """Verify 2FA code."""
        headers = self._get_auth_headers()
        headers["X-Apple-App-Id"] = WIDGET_KEY
        headers["Accept"] = "application/json, text/plain, */*"
        
        data = {
            "securityCode": {
                "code": code
            }
        }
        
        response = self.session.post(
            f"{AUTH_ENDPOINT}/verify/trusteddevice/securitycode",
            headers=headers,
            json=data
        )
        
        self._update_auth_state(response)
        
        if response.status_code == 204:
            return True, "2FA verification successful"
        elif response.status_code == 400:
            return False, "Invalid 2FA code"
        else:
            return False, f"2FA verification failed: {response.status_code}"

    def _trust_device(self) -> Tuple[bool, str]:
        """Trust the current device/browser."""
        headers = self._get_auth_headers()
        headers["X-Apple-App-Id"] = WIDGET_KEY
        headers["Accept"] = "application/json, text/plain, */*"
        
        response = self.session.get(
            f"{AUTH_ENDPOINT}/2sv/trust",
            headers=headers
        )
        
        self._update_auth_state(response)
        
        if response.status_code == 204:
            return True, "Device trusted"
        else:
            return False, f"Trust device failed: {response.status_code}"

    def _account_login(self) -> Tuple[bool, str]:
        """Exchange auth token for iCloud session."""
        if not self.session_token:
            return False, "No session token available"
        
        params = {
            "requestId": str(uuid.uuid4()),
            "clientBuildNumber": CLIENT_BUILD_NUMBER,
            "clientMasteringNumber": CLIENT_MASTERING_NUMBER,
            "clientId": self.client_id,
        }
        
        data = {
            "dsWebAuthToken": self.session_token,
            "accountCountryCode": "USA",
            "extended_login": True,
        }
        
        if self.trust_token:
            data["trustToken"] = self.trust_token
        
        response = self.session.post(
            f"{SETUP_ENDPOINT}/accountLogin",
            params=params,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            self.account_info = result.get("dsInfo", {})
            self.webservices = result.get("webservices", {})
            self.dsid = self.account_info.get("dsid")
            return True, "Account login successful"
        else:
            return False, f"Account login failed: {response.status_code} - {response.text}"

    def login(self, email: str, password: str, code_callback=None) -> Tuple[bool, str]:
        """
        Complete login flow.
        
        Args:
            email: Apple ID email
            password: Apple ID password
            code_callback: Optional callback function to get 2FA code.
                          If None, will prompt via input()
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Step 1: SRP Authentication
        self._log("[*] Starting SRP authentication...")
        success, message = self._srp_authenticate(email, password)
        self._log(message)
        if not success:
            return False, message
        
        # Check if 2FA is required
        if message.startswith("2FA_REQUIRED"):
            auth_type = message.split(":")[1]
            self._log(f"[*] 2FA required (type: {auth_type})")
            
            # Get 2FA code
            if code_callback:
                code = code_callback()
            else:
                code = input("Enter 2FA code: ").strip()
            
            # Verify 2FA
            self._log("[*] Verifying 2FA code...")
            success, message = self._verify_2fa_code(code)
            if not success:
                return False, message
            
            # Trust device
            self._log("[*] Trusting device...")
            success, message = self._trust_device()
            if not success:
                return False, message
        
        # Step 2: Account login to get iCloud session
        self._log("[*] Completing iCloud login...")
        success, message = self._account_login()
        if not success:
            return False, message
        
        # Save session
        self._log("[*] Saving session...")
        self.save_session()
        
        return True, f"Login successful! DSID: {self.dsid}"

    def validate_session(self) -> bool:
        """Check if current session is valid."""
        if not self.dsid:
            return False
        
        params = {
            "clientBuildNumber": CLIENT_BUILD_NUMBER,
            "clientMasteringNumber": CLIENT_MASTERING_NUMBER,
            "clientId": self.client_id,
        }
        
        try:
            response = self.session.post(
                f"{SETUP_ENDPOINT}/validate",
                params=params,
                data="null"  # iCloud expects this
            )
            
            if response.status_code == 200:
                result = response.json()
                # Check for dsInfo which indicates valid session
                if result.get("dsInfo"):
                    self.account_info = result.get("dsInfo", {})
                    self.webservices = result.get("webservices", {})
                    return True
        except Exception as e:
            pass  # Validation failed silently
        
        return False

    def save_session(self):
        """Save session data to file."""
        session_data = {
            "client_id": self.client_id,
            "dsid": self.dsid,
            "cookies": {k: v for k, v in self.session.cookies.get_dict().items()},
            "account_info": self.account_info,
            "webservices": self.webservices,
            "trust_token": self.trust_token,
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        self._log(f"[+] Session saved to {self.credentials_file}")

    def load_session(self) -> bool:
        """Load session data from file."""
        if not self.credentials_file.exists():
            return False
        
        try:
            with open(self.credentials_file, 'r') as f:
                session_data = json.load(f)
            
            self.client_id = session_data.get("client_id", str(uuid.uuid4()))
            self.dsid = session_data.get("dsid")
            self.trust_token = session_data.get("trust_token")
            self.account_info = session_data.get("account_info", {})
            self.webservices = session_data.get("webservices", {})
            
            # Restore cookies
            cookies = session_data.get("cookies", {})
            for name, value in cookies.items():
                self.session.cookies.set(name, value)
            
            self._log(f"[+] Session loaded from {self.credentials_file}")
            return True
            
        except Exception as e:
            self._log(f"[-] Failed to load session: {e}")
            return False

    def get_webservice_url(self, service: str) -> Optional[str]:
        """Get URL for a specific webservice."""
        if not self.webservices:
            return None
        
        service_info = self.webservices.get(service, {})
        return service_info.get("url")

    @property
    def is_authenticated(self) -> bool:
        """Check if we have valid credentials."""
        return self.dsid is not None and len(self.session.cookies) > 0


if __name__ == "__main__":
    # Test the authentication
    session = ICloudSession()
    
    # Try to load existing session
    if session.load_session() and session.validate_session():
        print("[+] Existing session is valid")
    else:
        print("[*] No valid session found, starting fresh login")
        email = input("Enter your Apple ID: ")
        password = input("Enter your Apple ID password: ")
        success, message = session.login(email, password)
        print(f"[{'+'if success else '-'}] {message}")

