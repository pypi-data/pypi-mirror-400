"""
Ed25519 cryptographic operations for request signing.
"""

from cryptography.hazmat.primitives.asymmetric import ed25519

from .exceptions import SigningError


def sign_payload(private_key: ed25519.Ed25519PrivateKey, message: bytes) -> str:
    """
    Sign a message using Ed25519 private key.

    Args:
        private_key: Ed25519 private key object
        message: Message bytes to sign (typically canonical request string)

    Returns:
        Signature as hex-encoded string

    Raises:
        SigningError: If signing fails

    Examples:
        >>> from neocore_sdk.key_loader import load_ed25519_private_key
        >>> key = load_ed25519_private_key("p_a1b2c3.pem")
        >>> signature = sign_payload(key, b"message to sign")
        >>> print(signature)
        '3a7b8c9d...'  # hex-encoded signature
    """
    try:
        signature_bytes = private_key.sign(message)
        signature_hex = signature_bytes.hex()
        return signature_hex
    except Exception as e:
        raise SigningError(f"Failed to sign payload: {str(e)}")


def verify_signature(
    public_key: ed25519.Ed25519PublicKey, signature_hex: str, message: bytes
) -> bool:
    """
    Verify an Ed25519 signature.

    Note: This is typically done server-side, but included here for completeness.

    Args:
        public_key: Ed25519 public key object
        signature_hex: Signature as hex-encoded string
        message: Original message bytes that were signed

    Returns:
        True if signature is valid, False otherwise

    Examples:
        >>> from neocore_sdk.key_loader import load_ed25519_public_key
        >>> public_pem = "-----BEGIN PUBLIC KEY-----\\n..."
        >>> key = load_ed25519_public_key(public_pem)
        >>> is_valid = verify_signature(key, signature_hex, message)
    """
    try:
        signature_bytes = bytes.fromhex(signature_hex)
        public_key.verify(signature_bytes, message)
        return True
    except Exception:
        return False
