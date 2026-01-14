"""
API Key Management
==================

Manages API keys with expiration tracking.
First key expires after 2 hours of first use.
Server stops if any key dies.
"""

import time
from datetime import datetime, timedelta
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class APIKeyManager:
    """Manages API keys with expiration tracking."""
    
    # Dev key - expires after 2 hours of first use
    DEV_KEY = "sk-asr-2024-prod-key-001-xyz789"
    
    # Client keys - valid forever, no expiration
    CLIENT_KEYS = [
        "sk-asr-2024-prod-key-002-abc123",
        "sk-asr-2024-prod-key-003-def456",
        "sk-asr-2024-prod-key-004-ghi789",
        "sk-asr-2024-prod-key-005-jkl012",
        "sk-asr-2024-prod-key-006-mno345",
        "sk-asr-2024-prod-key-007-pqr678",
        "sk-asr-2024-prod-key-008-stu901",
        "sk-asr-2024-prod-key-009-vwx234",
        "sk-asr-2024-prod-key-010-yz0567",
    ]
    
    def __init__(self, provided_keys: List[str]):
        """
        Initialize key manager.
        
        Args:
            provided_keys: List of API keys provided at startup (minimum 1)
        """
        self.provided_keys = provided_keys
        self.dev_key_activated_at: Optional[datetime] = None
        self.dev_key_expires_at: Optional[datetime] = None
        self.using_dev_key = False
        self._validated = False
    
    def validate_keys(self) -> bool:
        """
        Validate that at least one key is provided and matches.
        
        Returns:
            True if at least one key is valid, False otherwise
        """
        if len(self.provided_keys) < 1:
            logger.error(f"❌ Expected at least 1 API key, got {len(self.provided_keys)}")
            return False
        
        # Check if any provided key matches dev key or client keys
        valid_keys = []
        for provided in self.provided_keys:
            if provided == self.DEV_KEY:
                valid_keys.append(provided)
                self.using_dev_key = True
                logger.info("🔧 Using DEV key (expires after 2 hours)")
            elif provided in self.CLIENT_KEYS:
                valid_keys.append(provided)
                logger.info(f"🔑 Using CLIENT key (no expiration)")
        
        if not valid_keys:
            logger.error(f"❌ None of the provided keys are valid")
            return False
        
        self._validated = True
        logger.info(f"✅ {len(valid_keys)} valid API key(s) found")
        return True
    
    def activate_dev_key(self):
        """Activate dev key and set 2-hour expiration."""
        if self.using_dev_key and self.dev_key_activated_at is None:
            self.dev_key_activated_at = datetime.now()
            self.dev_key_expires_at = self.dev_key_activated_at + timedelta(hours=2)
            logger.warning(f"⏰ DEV key activated. Expires at {self.dev_key_expires_at.strftime('%H:%M:%S')}")
    
    def check_expiration(self) -> bool:
        """
        Check if dev key has expired (client keys never expire).
        
        Returns:
            True if valid, False if expired
        """
        if not self._validated:
            return False
        
        # Client keys never expire
        if not self.using_dev_key:
            return True
        
        # Activate dev key on first check
        if self.dev_key_activated_at is None:
            self.activate_dev_key()
            return True
        
        # Check dev key expiration
        now = datetime.now()
        if now > self.dev_key_expires_at:
            logger.error("❌ DEV KEY EXPIRED! Server must stop.")
            return False
        
        # Log time remaining for dev key
        time_left = self.dev_key_expires_at - now
        minutes_left = int(time_left.total_seconds() / 60)
        if minutes_left <= 10 and minutes_left % 5 == 0:
            logger.warning(f"⚠️ DEV key expires in {minutes_left} minutes")
        
        return True
    
    def get_status(self) -> dict:
        """Get current key status."""
        if not self._validated:
            return {
                "validated": False,
                "keys_provided": len(self.provided_keys),
            }
        
        status = {
            "validated": True,
            "using_dev_key": self.using_dev_key,
            "keys_provided": len(self.provided_keys),
        }
        
        if self.using_dev_key and self.dev_key_activated_at:
            now = datetime.now()
            time_left = self.dev_key_expires_at - now
            status["dev_key_activated"] = True
            status["dev_key_expires_at"] = self.dev_key_expires_at.isoformat()
            status["time_remaining_seconds"] = int(time_left.total_seconds())
            status["expired"] = now > self.dev_key_expires_at
        elif self.using_dev_key:
            status["dev_key_activated"] = False
        else:
            status["client_key_no_expiration"] = True
        
        return status


# Global key manager instance
key_manager: Optional[APIKeyManager] = None


def init_key_manager(keys: List[str]) -> bool:
    """
    Initialize global key manager.
    
    Args:
        keys: At least 1 valid API key (dev key or client key)
        
    Returns:
        True if initialization successful, False otherwise
    """
    global key_manager
    key_manager = APIKeyManager(keys)
    return key_manager.validate_keys()


def get_key_manager() -> APIKeyManager:
    """Get global key manager instance."""
    if key_manager is None:
        raise RuntimeError("Key manager not initialized")
    return key_manager
