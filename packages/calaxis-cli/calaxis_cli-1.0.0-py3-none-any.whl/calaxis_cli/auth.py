"""
Calaxis CLI Authentication Manager

Cross-platform secure token storage with:
- System keyring (Windows Credential Manager, macOS Keychain, Linux Secret Service)
- File-based fallback with restricted permissions
- Automatic token refresh
- Device fingerprinting for security
"""

import os
import sys
import json
import hashlib
import platform
import logging
import getpass
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import keyring for secure storage
try:
    import keyring
    HAS_KEYRING = True
except ImportError:
    HAS_KEYRING = False
    logger.debug("keyring not available, using file-based storage")

# Try to import requests
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class CLIAuthManager:
    """
    Manages CLI authentication with the Calaxis platform.

    Features:
    - Secure token storage (keyring or encrypted file)
    - Automatic token refresh
    - Device fingerprinting
    - Cross-platform support (Windows, macOS, Linux)
    """

    SERVICE_NAME = "calaxis-cli"
    TOKEN_FILE = "credentials.json"

    def __init__(self, api_url: str = None):
        """
        Initialize auth manager.

        Args:
            api_url: Calaxis API URL (or uses CALAXIS_API_URL env var)
        """
        if not HAS_REQUESTS:
            raise ImportError("requests library is required. Install with: pip install requests")

        self.api_url = api_url or os.environ.get(
            "CALAXIS_API_URL",
            "https://api.calaxis.ai"
        )
        self.config_dir = self._get_config_dir()
        self.token_file = self.config_dir / self.TOKEN_FILE
        self._cached_token: Optional[Dict] = None

    def _get_config_dir(self) -> Path:
        """
        Get platform-specific configuration directory.

        Returns:
            Path: Configuration directory path
        """
        system = platform.system()

        if system == "Windows":
            # Windows: %APPDATA%\calaxis
            base = Path(os.environ.get("APPDATA", Path.home()))
        elif system == "Darwin":  # macOS
            # macOS: ~/Library/Application Support/calaxis
            base = Path.home() / "Library" / "Application Support"
        else:
            # Linux/Unix: ~/.config/calaxis
            xdg_config = os.environ.get("XDG_CONFIG_HOME")
            base = Path(xdg_config) if xdg_config else Path.home() / ".config"

        config_dir = base / "calaxis"
        config_dir.mkdir(parents=True, exist_ok=True)

        return config_dir

    def _get_device_fingerprint(self) -> str:
        """
        Generate unique device fingerprint for security.

        Returns:
            str: SHA-256 hash of device identifiers
        """
        components = [
            platform.node(),  # Hostname
            platform.system(),  # OS
            platform.machine(),  # CPU architecture
            getpass.getuser(),  # Username
        ]

        # Add MAC address if available
        try:
            import uuid
            components.append(str(uuid.getnode()))
        except:
            pass

        fingerprint_data = ":".join(components)
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]

    def _get_device_name(self) -> str:
        """
        Get human-readable device name.

        Returns:
            str: Device name like "MacBook-Pro-CLI"
        """
        hostname = platform.node().split(".")[0]
        system = platform.system()

        if system == "Darwin":
            system = "macOS"

        return f"{hostname}-{system}-CLI"

    # =========================================================================
    # TOKEN STORAGE
    # =========================================================================

    def _store_tokens(self, tokens: Dict[str, Any]) -> bool:
        """
        Store tokens securely.

        Tries keyring first (most secure), falls back to file storage.

        Args:
            tokens: Token dict with access_token, refresh_token, expires_at, etc.

        Returns:
            bool: True if stored successfully
        """
        try:
            if HAS_KEYRING:
                # Use system keyring (most secure)
                keyring.set_password(
                    self.SERVICE_NAME,
                    "tokens",
                    json.dumps(tokens)
                )
                logger.debug("Tokens stored in system keyring")
                self._cached_token = tokens
                return True

        except Exception as e:
            logger.debug(f"Keyring storage failed: {e}, using file storage")

        # Fallback to file-based storage
        try:
            with open(self.token_file, "w") as f:
                json.dump(tokens, f, indent=2)

            # Restrict file permissions (Unix only)
            if platform.system() != "Windows":
                self.token_file.chmod(0o600)  # Owner read/write only

            logger.debug(f"Tokens stored in {self.token_file}")
            self._cached_token = tokens
            return True

        except Exception as e:
            logger.error(f"Failed to store tokens: {e}")
            return False

    def _load_tokens(self) -> Optional[Dict[str, Any]]:
        """
        Load tokens from storage.

        Returns:
            dict: Token dict or None if not found
        """
        # Return cached token if available
        if self._cached_token:
            return self._cached_token

        # Try keyring first
        if HAS_KEYRING:
            try:
                token_json = keyring.get_password(self.SERVICE_NAME, "tokens")
                if token_json:
                    self._cached_token = json.loads(token_json)
                    return self._cached_token
            except Exception as e:
                logger.debug(f"Keyring load failed: {e}")

        # Try file storage
        try:
            if self.token_file.exists():
                with open(self.token_file, "r") as f:
                    self._cached_token = json.load(f)
                    return self._cached_token
        except Exception as e:
            logger.debug(f"File load failed: {e}")

        return None

    def _clear_tokens(self) -> bool:
        """
        Clear all stored tokens.

        Returns:
            bool: True if cleared successfully
        """
        self._cached_token = None

        # Clear keyring
        if HAS_KEYRING:
            try:
                keyring.delete_password(self.SERVICE_NAME, "tokens")
            except Exception:
                pass

        # Clear file
        try:
            if self.token_file.exists():
                self.token_file.unlink()
        except Exception:
            pass

        return True

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    def login(
        self,
        email: str,
        password: str,
        api_key: str = None
    ) -> Dict[str, Any]:
        """
        Authenticate with the Calaxis platform.

        Supports both email/password and API key authentication.

        Args:
            email: User email (or None if using API key)
            password: User password (or None if using API key)
            api_key: API key for automated authentication

        Returns:
            dict: Login response with tokens and user info

        Raises:
            ValueError: If credentials are invalid
            requests.RequestException: If API request fails
        """
        endpoint = f"{self.api_url}/api/cli/v1/auth/login"

        payload = {
            "device_name": self._get_device_name(),
            "device_fingerprint": self._get_device_fingerprint(),
        }

        if api_key:
            payload["api_key"] = api_key
        else:
            if not email or not password:
                raise ValueError("Email and password required")
            payload["email"] = email
            payload["password"] = password

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code == 401:
                raise ValueError("Invalid credentials")
            elif response.status_code == 403:
                raise ValueError("Account locked or disabled")
            elif response.status_code >= 400:
                error_detail = response.json().get("detail", "Unknown error")
                raise ValueError(f"Login failed: {error_detail}")

            data = response.json()

            # Store tokens
            tokens = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "token_type": data.get("token_type", "bearer"),
                "expires_in": data["expires_in"],
                "expires_at": (
                    datetime.utcnow() + timedelta(seconds=data["expires_in"])
                ).isoformat(),
                "user_id": data["user_id"],
                "user_email": data["user_email"],
                "pricing_tier": data.get("pricing_tier", "free"),
                "device_fingerprint": self._get_device_fingerprint(),
            }

            self._store_tokens(tokens)

            logger.info(f"Logged in as {data['user_email']}")

            return {
                "success": True,
                "user_id": data["user_id"],
                "email": data["user_email"],
                "tier": data.get("pricing_tier", "free"),
            }

        except requests.RequestException as e:
            logger.error(f"Login request failed: {e}")
            raise

    def logout(self) -> bool:
        """
        Clear stored credentials.

        Returns:
            bool: True if logout successful
        """
        self._clear_tokens()
        logger.info("Logged out successfully")
        return True

    def is_authenticated(self) -> bool:
        """
        Check if user is currently authenticated.

        Returns:
            bool: True if valid tokens exist
        """
        token = self.get_token()
        return token is not None

    def get_token(self) -> Optional[str]:
        """
        Get current access token, refreshing if needed.

        Returns:
            str: Valid access token or None
        """
        tokens = self._load_tokens()
        if not tokens:
            return None

        # Check if token is expired
        if self._is_token_expired(tokens):
            # Try to refresh
            try:
                self._refresh_token(tokens)
                tokens = self._load_tokens()
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")
                return None

        return tokens.get("access_token")

    def _is_token_expired(self, tokens: Dict) -> bool:
        """Check if access token is expired or near expiry."""
        expires_at_str = tokens.get("expires_at")
        if not expires_at_str:
            return True

        try:
            expires_at = datetime.fromisoformat(expires_at_str)
            # Consider expired if less than 5 minutes remaining
            buffer = timedelta(minutes=5)
            return datetime.utcnow() > (expires_at - buffer)
        except ValueError:
            return True

    def _refresh_token(self, tokens: Dict) -> Dict:
        """
        Refresh the access token using refresh token.

        Args:
            tokens: Current token dict with refresh_token

        Returns:
            dict: New token dict
        """
        refresh_token = tokens.get("refresh_token")
        if not refresh_token:
            raise ValueError("No refresh token available")

        endpoint = f"{self.api_url}/api/cli/v1/auth/refresh"

        response = requests.post(
            endpoint,
            json={"refresh_token": refresh_token},
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        if response.status_code == 401:
            # Refresh token expired, need to re-login
            self._clear_tokens()
            raise ValueError("Session expired, please login again")

        response.raise_for_status()
        data = response.json()

        # Update stored tokens
        tokens["access_token"] = data["access_token"]
        tokens["expires_in"] = data["expires_in"]
        tokens["expires_at"] = (
            datetime.utcnow() + timedelta(seconds=data["expires_in"])
        ).isoformat()

        self._store_tokens(tokens)

        logger.debug("Token refreshed successfully")
        return tokens

    # =========================================================================
    # USER INFO
    # =========================================================================

    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """
        Get stored user information.

        Returns:
            dict: User info or None if not authenticated
        """
        tokens = self._load_tokens()
        if not tokens:
            return None

        return {
            "user_id": tokens.get("user_id"),
            "email": tokens.get("user_email"),
            "tier": tokens.get("pricing_tier"),
            "expires_at": tokens.get("expires_at"),
        }

    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests.

        Returns:
            dict: Headers dict with Authorization header
        """
        token = self.get_token()
        if not token:
            return {}

        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def get_api_url(self) -> str:
        """Get configured API URL."""
        return self.api_url

    def set_api_url(self, url: str):
        """
        Set API URL (useful for development).

        Args:
            url: New API URL
        """
        self.api_url = url

    def get_config_path(self) -> Path:
        """Get path to config directory."""
        return self.config_dir

    def verify_device(self) -> bool:
        """
        Verify current device matches stored fingerprint.

        Returns:
            bool: True if device matches
        """
        tokens = self._load_tokens()
        if not tokens:
            return False

        stored_fingerprint = tokens.get("device_fingerprint")
        if not stored_fingerprint:
            return True  # No fingerprint stored, allow

        return stored_fingerprint == self._get_device_fingerprint()


# Global auth manager instance
_auth_manager: Optional[CLIAuthManager] = None


def get_auth_manager(api_url: str = None) -> CLIAuthManager:
    """
    Get or create the global auth manager instance.

    Args:
        api_url: Optional API URL override

    Returns:
        CLIAuthManager: Auth manager instance
    """
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = CLIAuthManager(api_url=api_url)
    return _auth_manager


def login(email: str, password: str, api_url: str = None) -> Dict[str, Any]:
    """
    Convenience function for login.

    Args:
        email: User email
        password: User password
        api_url: Optional API URL override

    Returns:
        dict: Login result
    """
    return get_auth_manager(api_url).login(email, password)


def logout() -> bool:
    """Convenience function for logout."""
    return get_auth_manager().logout()


def is_authenticated() -> bool:
    """Check if authenticated."""
    return get_auth_manager().is_authenticated()


def get_token() -> Optional[str]:
    """Get current access token."""
    return get_auth_manager().get_token()


def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers."""
    return get_auth_manager().get_auth_headers()
