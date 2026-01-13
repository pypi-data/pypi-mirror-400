"""
Encryption/Decryption logic for Envy.
Supports both symmetric (Fernet/AES) and asymmetric (Age) encryption.
"""

from cryptography.fernet import Fernet
import os
import keyring
import secrets
import hashlib
from typing import Optional
from datetime import datetime, timedelta

# Keyring service name
KEYRING_SERVICE = "envy-secrets"


class EnvyCrypto:
    """Handles symmetric encryption using Fernet (AES)."""
    
    def __init__(self, key_path: str = ".envy/master.key", use_keyring: bool = True):
        self.key_path = key_path
        self.use_keyring = use_keyring
        self.key = self._load_key()

    def _load_key(self) -> bytes:
        """Load the encryption key from keyring or file."""
        # First try to load from system keyring
        if self.use_keyring:
            key = self._load_from_keyring()
            if key:
                return key
        
        # Fall back to file-based key
        if not os.path.exists(self.key_path):
            raise FileNotFoundError("Envy not initialized. Run 'envy init' first.")
        
        with open(self.key_path, "rb") as f:
            return f.read()

    def _load_from_keyring(self) -> Optional[bytes]:
        """Load key from OS keyring (Windows Credential Manager, macOS Keychain, etc.)."""
        try:
            # Get project identifier from current directory
            project_id = self._get_project_id()
            key_str = keyring.get_password(KEYRING_SERVICE, project_id)
            if key_str:
                return key_str.encode()
        except Exception:
            pass
        return None

    def _get_project_id(self) -> str:
        """Generate a unique project identifier based on the current directory."""
        cwd = os.getcwd()
        return hashlib.sha256(cwd.encode()).hexdigest()[:16]

    @classmethod
    def generate_key(cls, path: str, use_keyring: bool = True) -> bytes:
        """Generate a new Fernet key and store it securely."""
        key = Fernet.generate_key()
        
        # Store in system keyring if available
        if use_keyring:
            try:
                project_id = hashlib.sha256(os.getcwd().encode()).hexdigest()[:16]
                keyring.set_password(KEYRING_SERVICE, project_id, key.decode())
            except Exception:
                pass  # Fall back to file storage
        
        # Always create file-based backup
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(key)
        
        return key

    def encrypt(self, secret: str) -> str:
        """Encrypt a secret string."""
        f = Fernet(self.key)
        return f.encrypt(secret.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Decrypt an encrypted token."""
        f = Fernet(self.key)
        return f.decrypt(token.encode()).decode()


class SecretMetadata:
    """Handles metadata for secrets including expiration."""
    
    @staticmethod
    def create(
        value: str,
        expires_in_days: Optional[int] = None,
        created_by: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict:
        """Create metadata wrapper for a secret."""
        now = datetime.now()
        metadata = {
            "value": value,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        if expires_in_days:
            expires_at = now + timedelta(days=expires_in_days)
            metadata["expires_at"] = expires_at.isoformat()
        
        if created_by:
            metadata["created_by"] = created_by
            
        if description:
            metadata["description"] = description
        
        return metadata

    @staticmethod
    def is_expired(metadata: dict) -> bool:
        """Check if a secret has expired."""
        if "expires_at" not in metadata:
            return False
        
        expires_at = datetime.fromisoformat(metadata["expires_at"])
        return datetime.now() > expires_at

    @staticmethod
    def days_until_expiry(metadata: dict) -> Optional[int]:
        """Get days until secret expires."""
        if "expires_at" not in metadata:
            return None
        
        expires_at = datetime.fromisoformat(metadata["expires_at"])
        delta = expires_at - datetime.now()
        return max(0, delta.days)

    @staticmethod
    def is_stale(metadata: dict, stale_days: int = 90) -> bool:
        """Check if a secret is stale (hasn't been rotated in a while)."""
        if "updated_at" not in metadata:
            return False
        
        updated_at = datetime.fromisoformat(metadata["updated_at"])
        stale_threshold = datetime.now() - timedelta(days=stale_days)
        return updated_at < stale_threshold
