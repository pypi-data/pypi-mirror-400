"""
Smart Ed25519 private key loader with OS-specific default path resolution.

This module implements automatic key discovery similar to how OpenSSL
searches for certificates in default system locations.
"""

import os
import platform
from pathlib import Path
from typing import List, Optional

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from .exceptions import KeyLoadError, KeyNotFoundError


def get_default_key_paths() -> List[Path]:
    """
    Get list of default private key paths based on the operating system.

    Returns paths in priority order (first found will be used).

    Returns:
        List of Path objects to search for private keys

    Platform-specific paths:
        Linux/macOS:
            1. ~/.neocore/p_a1b2c3.pem (user-specific, recommended)
            2. ~/.ssh/p_a1b2c3.pem (SSH-like location)
            3. /etc/neocore/p_a1b2c3.pem (system-wide)
            4. ./p_a1b2c3.pem (current directory)

        Windows:
            1. %USERPROFILE%\\.neocore\\p_a1b2c3.pem (user-specific, recommended)
            2. %APPDATA%\neocore\\p_a1b2c3.pem (AppData)
            3. %PROGRAMDATA%\neocore\\p_a1b2c3.pem (system-wide)
            4. .\\p_a1b2c3.pem (current directory)
    """
    system = platform.system()
    paths = []

    if system in ("Linux", "Darwin"):
        home = Path.home()
        paths.extend(
            [
                home / ".neocore" / "p_a1b2c3.pem",
                home / ".ssh" / "p_a1b2c3.pem",
            ]
        )
        paths.append(Path("/etc/neocore/p_a1b2c3.pem"))

    elif system == "Windows":
        userprofile = os.environ.get("USERPROFILE")
        if userprofile:
            paths.append(Path(userprofile) / ".neocore" / "p_a1b2c3.pem")

        appdata = os.environ.get("APPDATA")
        if appdata:
            paths.append(Path(appdata) / "neocore" / "p_a1b2c3.pem")

        programdata = os.environ.get("PROGRAMDATA")
        if programdata:
            paths.append(Path(programdata) / "neocore" / "p_a1b2c3.pem")

    paths.append(Path.cwd() / "p_a1b2c3.pem")

    return paths


def find_private_key() -> Optional[Path]:
    """
    Search for private key in default locations.

    Returns:
        Path to private key file if found, None otherwise
    """
    default_paths = get_default_key_paths()

    for path in default_paths:
        if path.exists() and path.is_file():
            return path

    return None


def load_ed25519_private_key(path: Optional[str] = None) -> ed25519.Ed25519PrivateKey:
    """
    Load Ed25519 private key from file with smart path resolution.

    If no path is provided, automatically searches default locations.

    Args:
        path: Optional explicit path to private key PEM file.
              If None, searches default OS-specific locations.

    Returns:
        Ed25519PrivateKey object

    Raises:
        KeyNotFoundError: If no key found in default locations (when path=None)
        KeyLoadError: If key file exists but cannot be loaded or is invalid

    Examples:
        # Auto-discover from default locations
        >>> key = load_ed25519_private_key()

        # Explicit path
        >>> key = load_ed25519_private_key("/secure/vault/my-key.pem")
    """
    if path:
        key_path = Path(path)

        if not key_path.exists():
            raise KeyLoadError(
                "Private key file not found",
                key_path=str(key_path),
                reason="File does not exist at the specified path",
            )

        if not key_path.is_file():
            raise KeyLoadError(
                "Private key path is not a file",
                key_path=str(key_path),
                reason="Path exists but is a directory, not a file",
            )

    else:
        key_path: Optional[Path] = find_private_key()

        if key_path is None:
            default_paths = get_default_key_paths()

            raise KeyNotFoundError(
                "No private key found in default locations", searched_paths=default_paths
            )

    try:
        with open(key_path, "rb") as f:
            key_data = f.read()

        private_key = serialization.load_pem_private_key(key_data, password=None)

        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise KeyLoadError(
                "Invalid key type - not an Ed25519 private key",
                key_path=str(key_path),
                reason=f"Found {type(private_key).__name__}, expected Ed25519PrivateKey",
            )

        return private_key

    except KeyLoadError:
        raise
    except Exception as e:
        raise KeyLoadError(
            "Failed to load private key", key_path=str(key_path), reason=str(e)
        ) from e


def load_ed25519_public_key(pem_data: str) -> ed25519.Ed25519PublicKey:
    """
    Load Ed25519 public key from PEM string.

    Args:
        pem_data: Public key in PEM format (string)

    Returns:
        Ed25519PublicKey object

    Raises:
        KeyLoadError: If key cannot be loaded or is not Ed25519
    """
    try:
        pem_bytes = pem_data.encode("utf-8") if isinstance(pem_data, str) else pem_data
        public_key = serialization.load_pem_public_key(pem_bytes)

        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            raise KeyLoadError(
                "Invalid key type - not an Ed25519 public key",
                reason=f"Found {type(public_key).__name__}, expected Ed25519PublicKey",
            )

        return public_key

    except KeyLoadError:
        raise
    except Exception as e:
        raise KeyLoadError("Failed to load public key", reason=str(e)) from e
