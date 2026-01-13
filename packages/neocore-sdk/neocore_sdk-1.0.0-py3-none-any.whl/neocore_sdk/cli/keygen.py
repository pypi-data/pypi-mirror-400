"""
CLI tool to generate Ed25519 key pairs for NeoCore Security SDK.

Usage:
    neocore-keygen
    neocore-keygen --output-dir /path/to/keys
    neocore-keygen --force
"""

import argparse
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


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
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.RESET}"

    @staticmethod
    def path(text):
        return f"{Colors.CYAN}{text}{Colors.RESET}"


def generate_ed25519_keypair(
    output_dir: Path, force: bool = False
) -> tuple[Path, Path]:
    """
    Generate Ed25519 key pair and save to PEM files.

    Args:
        output_dir: Directory to save keys
        force: Overwrite existing keys without prompting

    Returns:
        Tuple of (private_key_path, public_key_path)

    Raises:
        SystemExit: If user cancels or error occurs
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    private_key_path = output_dir / "p_a1b2c3.pem"
    public_key_path = output_dir / "pub_a1b2c3.pem"

    if (private_key_path.exists() or public_key_path.exists()) and not force:
        print(f"\n{Colors.warning('Key files already exist!')}")
        print(
            f"   Private Key: {Colors.path(private_key_path.name)} - {'EXISTS' if private_key_path.exists() else 'not found'}"
        )
        print(
            f"   Public Key:  {Colors.path(public_key_path.name)} - {'EXISTS' if public_key_path.exists() else 'not found'}"
        )

        response = input(f"\n{Colors.YELLOW}Overwrite existing keys? (Y/N):{Colors.RESET} ").strip().lower()
        if response not in ["yes", "y", "Y"]:
            print(f"\n{Colors.info('Cancelled. No files were modified.')}")
            sys.exit(0)

    print(f"\n{Colors.CYAN}●{Colors.RESET} Generating Ed25519 key pair...")

    private_key = ed25519.Ed25519PrivateKey.generate()

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(private_key_path, "wb") as f:
        f.write(private_pem)

    try:
        os.chmod(private_key_path, 0o600)
    except Exception:
        # Windows doesn't support chmod the same way
        pass

    with open(public_key_path, "wb") as f:
        f.write(public_pem)

    return private_key_path, public_key_path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Ed25519 key pair for NeoCore Security SDK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate keys in default location (~/.neocore/)
  neocore-keygen

  # Generate keys in custom directory
  neocore-keygen --output-dir /path/to/keys

  # Force overwrite existing keys
  neocore-keygen --force

  # Combine options
  neocore-keygen --output-dir /secure/keys --force

Security Notes:
  - Private key is saved with 600 permissions (owner read/write only)
  - Never commit p_a1b2c3.pem to version control
  - Add '*.pem' to your .gitignore
  - Store private keys securely in production
        """,
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / ".neocore",
        help="Directory to save keys (default: ~/.neocore)",
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing keys without prompting",
    )

    args = parser.parse_args()

    print(f"\n{Colors.BOLD}NeoCore Security SDK{Colors.RESET} - Ed25519 Key Generator")
    print(f"{Colors.DIM}{'─' * 70}{Colors.RESET}\n")

    try:
        private_path, public_path = generate_ed25519_keypair(
            output_dir=args.output_dir, force=args.force
        )

        print(f"\n{Colors.success('Key pair generated successfully!')}\n")
        print(f"{Colors.BOLD}Output Directory:{Colors.RESET}")
        print(f"  {Colors.path(args.output_dir)}\n")

        print(f"{Colors.BOLD}Generated Files:{Colors.RESET}")
        print(f"  {Colors.GREEN}●{Colors.RESET} {Colors.path(private_path.name)} {Colors.DIM}(private key - keep secret!){Colors.RESET}")
        print(f"  {Colors.GREEN}●{Colors.RESET} {Colors.path(public_path.name)} {Colors.DIM}(public key - share with API){Colors.RESET}")

        print(f"\n{Colors.BOLD}{Colors.YELLOW}Security Reminders:{Colors.RESET}")
        print(f"  {Colors.RED}•{Colors.RESET} NEVER commit {Colors.path(private_path.name)} to version control")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Add {Colors.path('p_*.pem')} to your .gitignore")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Store keys securely in production")
        print(f"  {Colors.YELLOW}•{Colors.RESET} Private key permissions: {Colors.path('600')} (owner read/write only)")

        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print(f"\n  {Colors.CYAN}1.{Colors.RESET} Read your public key:")
        print(f"     {Colors.DIM}${Colors.RESET} cat {Colors.path(public_path)}")

        print(f"\n  {Colors.CYAN}2.{Colors.RESET} Register public key with NeoCore API:")
        print(f"     {Colors.DIM}POST{Colors.RESET} {Colors.path('https://api.neosapien.xyz/api/v1/dev-keys')}")
        print(f"     {Colors.DIM}Headers:{Colors.RESET} Authorization: Bearer <firebase-jwt>")
        print(f"     {Colors.DIM}Body:{Colors.RESET} {Colors.DIM}{{\"key_id\": \"<uuid>\", \"public_key_pem\": \"<public-key>\"}}{Colors.RESET}")

        print(f"\n  {Colors.CYAN}3.{Colors.RESET} Use SDK with your private key:")
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
