# -*- coding: utf-8 -*-
# Copyright (C) 2023-2025 TU-Dresden (ZIH)
# ralf.klammer@tu-dresden.de
# moritz.wilhelm@tu-dresden.de
import logging

import json
import os
import secrets

from typing import Optional

# Removed unused import of Path
from pathlib import Path

log = logging.getLogger(__name__)


class SecretKeyManager:
    """Manages the secret key for Flask sessions."""

    def __init__(self, base_path: str, env_var: str = "FLASK_SECRET_KEY"):
        # Initialize with the base path and environment variable name
        self.env_var = env_var
        self.secret_file = Path(base_path) / ".secret_key"
        self._secret_key: Optional[str] = None

    @property
    def secret_key(self) -> str:
        """Returns the secret key or generates a new one if it doesn't exist."""
        if self._secret_key is None:
            self._secret_key = self._get_or_create_key()
        return self._secret_key

    def _get_or_create_key(self) -> str:
        """Fetches the key from the environment or file, or creates a new one."""
        # 1. Try to get the key from the environment variable
        if env_key := os.environ.get(self.env_var):
            log.info(f"Using secret key from {self.env_var}")
            return env_key

        # 2. Try to load the key from the saved file
        try:
            if self.secret_file.exists():
                with open(self.secret_file) as f:
                    log.info(f"Loading secret key from {self.secret_file}")
                    return json.load(f)
        except Exception as e:
            log.warning(f"Could not load secret key: {e}")

        # 3. Generate a new key
        new_key = secrets.token_hex(32)
        log.info("Generating a new secret key")

        try:
            # Create the directory if it doesn't exist
            self.secret_file.parent.mkdir(parents=True, exist_ok=True)

            # Save the key to the file
            with open(self.secret_file, "w") as f:
                json.dump(new_key, f)

            # Set file permissions
            self.secret_file.chmod(0o600)

            log.info(f"New secret key saved to {self.secret_file}")
            return new_key

        except Exception as e:
            log.warning(f"Could not save secret key: {e}")
            return new_key
