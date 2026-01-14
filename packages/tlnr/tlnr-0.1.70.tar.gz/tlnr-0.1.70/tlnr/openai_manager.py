"""OpenAI API key management for tlnr."""

import os
import getpass
from pathlib import Path
from typing import Optional


class OpenAIKeyManager:
    """Manages OpenAI API key storage, validation, and retrieval."""

    def __init__(self):
        self.key_file = Path.home() / ".terminal_tutor_openai_key"

    def get_api_key(self) -> Optional[str]:
        """
        Get API key from storage or prompt user.

        Returns:
            API key string or None if unavailable/invalid
        """
        # 1. Try loading from file
        key = self._load_key_from_file()
        if key:
            # Test if key works
            if self._validate_key(key):
                return key
            else:
                print("⚠️  Stored API key is invalid or expired")
                print("💡 Please enter a new API key\n")

        # 2. Prompt user for new key
        key = self._prompt_for_key()
        if key:
            # Test new key
            print("✅ Testing API key...", end=" ", flush=True)
            if self._validate_key(key):
                print("Valid!")
                self._save_key(key)
                return key
            else:
                print("❌ Invalid!")
                print("❌ API key validation failed. Please check your key and try again.")
                return None

        return None

    def has_api_key(self) -> bool:
        """Check if API key exists without prompting user."""
        return bool(self._load_key_from_file())

    def _load_key_from_file(self) -> Optional[str]:
        """
        Load API key from ~/.terminal_tutor_openai_key

        Returns:
            API key string or None if file doesn't exist
        """
        try:
            if self.key_file.exists():
                key = self.key_file.read_text().strip()
                if key:
                    return key
        except Exception:
            pass
        return None

    def _save_key(self, key: str):
        """
        Save API key to file with secure permissions (600).

        Args:
            key: OpenAI API key to save
        """
        try:
            # Write key to file
            self.key_file.write_text(key)

            # Set file permissions to 600 (user read/write only)
            os.chmod(self.key_file, 0o600)

            print(f"✅ API key saved securely to {self.key_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save API key to file: {e}")

    def _validate_key(self, key: str) -> bool:
        """
        Test API key by calling OpenAI API (list models).

        Args:
            key: OpenAI API key to validate

        Returns:
            True if key is valid, False otherwise
        """
        try:
            import openai
        except ImportError:
            # OpenAI package not installed
            return False

        try:
            client = openai.OpenAI(api_key=key)

            # Quick test: list models (fast, low cost)
            client.models.list()
            return True

        except openai.AuthenticationError:
            # Invalid API key
            return False
        except openai.APIError:
            # API error, but key might be valid (assume valid)
            return True
        except Exception:
            # Other errors (network, timeout, etc.)
            return False

    def _prompt_for_key(self) -> Optional[str]:
        """
        Interactive prompt for API key entry.

        Returns:
            API key entered by user or None if cancelled
        """
        print("🔑 OpenAI API key not found.\n")
        print("To use natural language search, you need an OpenAI API key.")
        print("Get one here: https://platform.openai.com/api-keys\n")

        try:
            # Use getpass for secure (hidden) input
            key = getpass.getpass("Enter your OpenAI API key (input hidden): ")
            key = key.strip()

            if not key:
                print("❌ No key entered. Cancelled.")
                return None

            return key

        except (KeyboardInterrupt, EOFError):
            print("\n❌ Cancelled by user.")
            return None

    def clear_key(self):
        """Remove stored API key file."""
        try:
            if self.key_file.exists():
                self.key_file.unlink()
                print(f"✅ API key removed from {self.key_file}")
            else:
                print("ℹ️  No API key file found.")
        except Exception as e:
            print(f"❌ Error removing API key: {e}")
