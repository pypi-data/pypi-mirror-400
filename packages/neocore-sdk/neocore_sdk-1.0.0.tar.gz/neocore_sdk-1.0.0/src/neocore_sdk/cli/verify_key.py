"""
CLI tool to verify Ed25519 private key files.

Usage:
    neocore-verify-key /path/to/p_a1b2c3.pem
    neocore-verify-key  # Auto-discovers from default locations
"""

import argparse
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from ..key_loader import find_private_key, get_default_key_paths


# Industry-standard terminal colors
class Colors:
    """ANSI color codes for terminal output."""
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}✓{Colors.RESET} {text}"

    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}⚠{Colors.RESET} {text}"

    @staticmethod
    def error(text):
        return f"{Colors.RED}✗{Colors.RESET} {text}"

    @staticmethod
    def info(text):
        return f"{Colors.CYAN}ℹ{Colors.RESET} {text}"

    @staticmethod
    def path(text):
        return f"{Colors.CYAN}{text}{Colors.RESET}"


def verify_private_key(key_path: Path) -> dict:
    """
    Verify Ed25519 private key and extract information.

    Args:
        key_path: Path to private key file

    Returns:
        Dict with key information

    Raises:
        Exception: If key is invalid
    """
    with open(key_path, "rb") as f:
        key_data = f.read()

    try:
        private_key = serialization.load_pem_private_key(key_data, password=None)
    except Exception as e:
        raise ValueError(f"Failed to load PEM key: {str(e)}")

    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        raise ValueError(f"Key is not Ed25519. Found: {type(private_key).__name__}")

    public_key = private_key.public_key()

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    try:
        file_stat = key_path.stat()
        permissions = oct(file_stat.st_mode)[-3:]
    except Exception:
        permissions = "N/A"

    return {
        "path": str(key_path),
        "type": "Ed25519 Private Key",
        "valid": True,
        "public_key_pem": public_pem.decode("utf-8"),
        "permissions": permissions,
        "size_bytes": len(key_data),
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Verify Ed25519 private key for NeoCore Security SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Verify specific key file
  neocore-verify-key /path/to/p_a1b2c3.pem

  # Auto-discover and verify from default locations
  neocore-verify-key

Default search locations:
  Linux/macOS:
    - ~/.neocore/p_a1b2c3.pem
    - ~/.ssh/p_a1b2c3.pem
    - /etc/neocore/p_a1b2c3.pem
    - ./p_a1b2c3.pem

  Windows:
    - %USERPROFILE%\\.neocore\\p_a1b2c3.pem
    - %APPDATA%\\neocore\\p_a1b2c3.pem
    - %PROGRAMDATA%\\neocore\\p_a1b2c3.pem
    - .\\p_a1b2c3.pem
        """,
    )

    parser.add_argument(
        "key_path",
        nargs="?",
        type=Path,
        help="Path to private key file (auto-discovers if not provided)",
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}NeoCore Security SDK{Colors.RESET} - Key Verification")
    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}\n")

    try:
        if args.key_path:
            key_path = args.key_path
            if not key_path.exists():
                print(f"\n{Colors.error(f'File not found: {key_path}')}")
                sys.exit(1)
        else:
            print(f"{Colors.info('Searching for private key in default locations...')}\n")
            default_paths = get_default_key_paths()
            for path in default_paths:
                status = f"{Colors.GREEN}✓{Colors.RESET}" if path.exists() else f"{Colors.DIM}○{Colors.RESET}"
                print(f"  {status} {Colors.path(path)}")

            key_path = find_private_key()
            if key_path is None:
                print(f"\n{Colors.error('No private key found in default locations.')}")
                print(f"\n{Colors.BOLD}Solutions:{Colors.RESET}")
                print(f"  • Generate keys: {Colors.CYAN}neocore-keygen{Colors.RESET}")
                print(f"  • Specify path: {Colors.CYAN}neocore-verify-key /path/to/key.pem{Colors.RESET}")
                sys.exit(1)

            print(f"\n{Colors.success(f'Found: {Colors.path(key_path)}')}")

        print(f"\n{Colors.CYAN}●{Colors.RESET} Verifying key...")
        info = verify_private_key(key_path)

        print(f"\n{Colors.success('Valid Ed25519 private key!')}\n")

        print(f"{Colors.BOLD}Key Information:{Colors.RESET}")
        print(f"  {Colors.DIM}Path:{Colors.RESET}        {Colors.path(info['path'])}")
        print(f"  {Colors.DIM}Type:{Colors.RESET}        {info['type']}")
        print(f"  {Colors.DIM}Size:{Colors.RESET}        {info['size_bytes']} bytes")
        print(f"  {Colors.DIM}Permissions:{Colors.RESET} {info['permissions']}")

        if info["permissions"] not in ["600", "N/A"]:
            perms = info["permissions"]
            path = info['path']
            print(f"\n{Colors.warning(f'Insecure permissions: {perms}')} ")
            print(f"  {Colors.DIM}Recommended:{Colors.RESET} 600 (owner read/write only)")
            print(f"  {Colors.DIM}Fix with:{Colors.RESET} chmod 600 {Colors.path(path)}")

        print(f"\n{Colors.BOLD}Corresponding Public Key:{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}")
        for line in info["public_key_pem"].strip().split("\n"):
            print(f"{Colors.DIM}{line}{Colors.RESET}")
        print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}")

        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"\n  {Colors.CYAN}1.{Colors.RESET} Register your public key:")
        print(f"     {Colors.DIM}POST{Colors.RESET} {Colors.path('https://api.neosapien.xyz/api/v1/dev-keys')}")
        print(f"\n  {Colors.CYAN}2.{Colors.RESET} Use the SDK:")
        print(f"     {Colors.DIM}from neocore_sdk import NeoCoreClient{Colors.RESET}")
        print(f"     {Colors.DIM}client = NeoCoreClient(key_id=\"<uuid>\"){Colors.RESET}")

        print(f"\n{Colors.DIM}{'─' * 70}{Colors.RESET}")
        sys.exit(0)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.warning('Cancelled by user')}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.error(f'Error: {str(e)}')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
