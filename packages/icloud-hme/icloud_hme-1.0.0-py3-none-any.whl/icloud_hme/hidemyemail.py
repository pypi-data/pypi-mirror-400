import uuid
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from .icloud_auth import ICloudSession

CLIENT_BUILD_NUMBER = "2546Build17"
CLIENT_MASTERING_NUMBER = "2546Build17"


class HideMyEmailGenerator:
    """Generate and manage HideMyEmail addresses using iCloud+."""

    def __init__(self, session: ICloudSession, output_file: str = "generated_emails.json", quiet: bool = False):
        self.session = session
        self.output_file = Path(output_file)
        self.quiet = quiet
        self.generated_emails: List[Dict[str, Any]] = []
        self.service_url = None
        self.user_partition = None
        
        # Load previously generated emails
        self._load_generated_emails()
    
    def _log(self, message: str):
        """Print message if not in quiet mode."""
        if not self.quiet:
            print(message)

    def _get_service_url(self) -> str:
        """Get the HideMyEmail service URL."""
        if self.service_url:
            return self.service_url
        
        # Try to get from webservices
        url = self.session.get_webservice_url("premiummailsettings")
        if url:
            self.service_url = url.rstrip("/")
            # Extract partition from URL (e.g., p128-maildomainws.icloud.com)
            return self.service_url
        
        # Fallback - use default partition from account info
        partition = 128  # Default
        if self.session.account_info:
            # Try to extract partition from dsInfo
            pass
        
        self.service_url = f"https://p{partition}-maildomainws.icloud.com"
        return self.service_url

    def _get_request_params(self) -> Dict[str, str]:
        """Get common request parameters."""
        return {
            "clientBuildNumber": CLIENT_BUILD_NUMBER,
            "clientMasteringNumber": CLIENT_MASTERING_NUMBER,
            "clientId": self.session.client_id,
            "dsid": self.session.dsid,
        }

    def _load_generated_emails(self):
        """Load previously generated emails from file."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r') as f:
                    self.generated_emails = json.load(f)
                self._log(f"[+] Loaded {len(self.generated_emails)} previously generated emails")
            except Exception as e:
                self._log(f"[-] Failed to load generated emails: {e}")
                self.generated_emails = []

    def _save_generated_emails(self):
        """Save generated emails to file."""
        with open(self.output_file, 'w') as f:
            json.dump(self.generated_emails, f, indent=2)

    def list_emails(self) -> List[Dict[str, Any]]:
        """
        List all existing HideMyEmail addresses.
        
        Returns:
            List of email dictionaries
        """
        service_url = self._get_service_url()
        
        response = self.session.session.get(
            f"{service_url}/v2/hme/list",
            params=self._get_request_params()
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                emails = result.get("result", {}).get("hmeEmails", [])
                forward_to = result.get("result", {}).get("forwardToEmails", [])
                self._log(f"[+] Found {len(emails)} existing HideMyEmail addresses")
                self._log(f"[+] Forwarding to: {', '.join(forward_to)}")
                return emails
        
        self._log(f"[-] Failed to list emails: {response.status_code}")
        return []

    def generate_email(self, lang_code: str = "en-us") -> Optional[str]:
        """
        Generate a new HideMyEmail address.
        
        Note: This generates a temporary address that needs to be reserved
        to become permanent.
        
        Args:
            lang_code: Language code for email generation (affects email words)
        
        Returns:
            Generated email address or None if failed
        """
        service_url = self._get_service_url()
        
        data = {"langCode": lang_code}
        
        response = self.session.session.post(
            f"{service_url}/v1/hme/generate",
            params=self._get_request_params(),
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                email = result.get("result", {}).get("hme")
                self._log(f"[+] Generated: {email}")
                return email
        
        self._log(f"[-] Failed to generate email: {response.status_code} - {response.text}")
        return None

    def reserve_email(self, email: str, label: str = "", note: str = "") -> bool:
        """
        Reserve a generated email address (make it permanent).
        
        Args:
            email: The generated email address to reserve
            label: Label/name for the email (e.g., "Shopping")
            note: Optional note
        
        Returns:
            True if reserved successfully
        """
        service_url = self._get_service_url()
        
        data = {
            "hme": email,
            "label": label or email.split("@")[0],
            "note": note
        }
        
        response = self.session.session.post(
            f"{service_url}/v1/hme/reserve",
            params=self._get_request_params(),
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                self._log(f"[+] Reserved: {email}")
                return True
            else:
                error = result.get("error", {})
                self._log(f"[-] Reserve failed: {error.get('errorMessage', 'Unknown error')}")
                # Check if we need to retry
                retry_after = error.get("retryAfter", 0)
                if retry_after > 0:
                    self._log(f"[*] Rate limited, retry after {retry_after} seconds")
                return False
        
        self._log(f"[-] Failed to reserve email: {response.status_code}")
        return False

    def deactivate_email(self, anonymous_id: str) -> bool:
        """
        Deactivate a HideMyEmail address.
        
        Args:
            anonymous_id: The anonymousId of the email to deactivate
        
        Returns:
            True if deactivated successfully
        """
        service_url = self._get_service_url()
        
        data = {"anonymousId": anonymous_id}
        
        response = self.session.session.post(
            f"{service_url}/v1/hme/deactivate",
            params=self._get_request_params(),
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                self._log(f"[+] Deactivated email: {anonymous_id}")
                return True
        
        self._log(f"[-] Failed to deactivate: {response.status_code}")
        return False

    def reactivate_email(self, anonymous_id: str) -> bool:
        """
        Reactivate a deactivated HideMyEmail address.
        
        Args:
            anonymous_id: The anonymousId of the email to reactivate
        
        Returns:
            True if reactivated successfully
        """
        service_url = self._get_service_url()
        
        data = {"anonymousId": anonymous_id}
        
        response = self.session.session.post(
            f"{service_url}/v1/hme/reactivate",
            params=self._get_request_params(),
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                self._log(f"[+] Reactivated email: {anonymous_id}")
                return True
        
        self._log(f"[-] Failed to reactivate: {response.status_code}")
        return False

    def delete_email(self, anonymous_id: str) -> bool:
        """
        Delete a HideMyEmail address permanently.
        
        Args:
            anonymous_id: The anonymousId of the email to delete
        
        Returns:
            True if deleted successfully
        """
        service_url = self._get_service_url()
        
        data = {"anonymousId": anonymous_id}
        
        response = self.session.session.post(
            f"{service_url}/v1/hme/delete",
            params=self._get_request_params(),
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                self._log(f"[+] Deleted email: {anonymous_id}")
                return True
        
        self._log(f"[-] Failed to delete: {response.status_code}")
        return False

    def generate_multiple(
        self, 
        count: int, 
        reserve: bool = False,
        label_prefix: str = "generated",
        delay: float = 1.0
    ) -> List[str]:
        """
        Generate multiple HideMyEmail addresses.
        
        Args:
            count: Number of emails to generate
            reserve: Whether to reserve (make permanent) the emails
            label_prefix: Prefix for labels when reserving
            delay: Delay between requests in seconds (to avoid rate limiting)
        
        Returns:
            List of generated email addresses
        """
        generated = []
        
        self._log(f"[*] Generating {count} email(s)...")
        
        for i in range(count):
            email = self.generate_email()
            
            if email:
                if reserve:
                    label = f"{label_prefix}_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    if self.reserve_email(email, label):
                        generated.append(email)
                        self.generated_emails.append({
                            "email": email,
                            "label": label,
                            "reserved": True,
                            "created_at": datetime.now().isoformat()
                        })
                    else:
                        # If reservation fails, still track the generated email
                        generated.append(email)
                        self.generated_emails.append({
                            "email": email,
                            "label": label,
                            "reserved": False,
                            "created_at": datetime.now().isoformat()
                        })
                else:
                    generated.append(email)
                    self.generated_emails.append({
                        "email": email,
                        "reserved": False,
                        "created_at": datetime.now().isoformat()
                    })
                
                # Save after each successful generation
                self._save_generated_emails()
            
            # Delay between requests
            if i < count - 1:
                time.sleep(delay)
        
        self._log(f"\n[+] Generated {len(generated)} email(s)")
        return generated


def main():
    """CLI interface for HideMyEmail generator."""
    import argparse
    
    parser = argparse.ArgumentParser(description="iCloud HideMyEmail Generator")
    parser.add_argument("--list", "-l", action="store_true", help="List existing emails")
    parser.add_argument("--generate", "-g", type=int, default=0, help="Number of emails to generate")
    parser.add_argument("--reserve", "-r", action="store_true", help="Reserve generated emails (make permanent)")
    parser.add_argument("--label", default="generated", help="Label prefix for reserved emails")
    parser.add_argument("--delay", "-d", type=float, default=2.0, help="Delay between requests (seconds)")
    parser.add_argument("--session-file", "-s", default="icloud_session.json", help="Session file path")
    parser.add_argument("--output", "-o", default="generated_emails.json", help="Output file for generated emails")
    
    args = parser.parse_args()
    
    # Initialize session
    session = ICloudSession(credentials_file=args.session_file)
    
    # Try to load existing session
    if not session.load_session():
        print("[-] No saved session found. Please login first.")
        email = input("Apple ID Email: ").strip()
        password = input("Apple ID Password: ").strip()
        
        success, message = session.login(email, password)
        if not success:
            print(f"[-] Login failed: {message}")
            return
        print(f"[+] {message}")
    else:
        # Validate the session
        if not session.validate_session():
            print("[-] Saved session expired. Please login again.")
            email = input("Apple ID Email: ").strip()
            password = input("Apple ID Password: ").strip()
            
            success, message = session.login(email, password)
            if not success:
                print(f"[-] Login failed: {message}")
                return
            print(f"[+] {message}")
        else:
            print("[+] Session validated successfully")
    
    # Check if HideMyEmail is available
    if not session.account_info.get("isHideMyEmailFeatureAvailable"):
        print("[-] HideMyEmail feature is not available for this account")
        print("    (iCloud+ subscription required)")
        return
    
    # Initialize generator
    generator = HideMyEmailGenerator(session, output_file=args.output)
    
    # List emails
    if args.list:
        emails = generator.list_emails()
        if emails:
            print("\n=== Existing HideMyEmail Addresses ===")
            for email in emails:
                status = "active" if email.get("isActive") else "deactivated"
                print(f"  - {email['hme']} ({email.get('label', 'no label')}) [{status}]")
    
    # Generate emails
    if args.generate > 0:
        generated = generator.generate_multiple(
            count=args.generate,
            reserve=args.reserve,
            label_prefix=args.label,
            delay=args.delay
        )
        
        if generated:
            print("\n=== Generated Emails ===")
            for email in generated:
                print(f"  - {email}")
            
            print(f"\nEmails saved to: {args.output}")


if __name__ == "__main__":
    main()

