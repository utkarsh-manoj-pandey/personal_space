"""
Automated Test Suite for Cryptographic Primitives & Local Vault Security
Validates cryptographic hashing, PBKDF2 key derivation, authenticated stream cipher,
and password entropy security auditing.
"""

import pytest
from backend.core.crypto_utils import (
    CryptoUtils,
    LocalVaultCipher,
    PasswordSecurityAnalyzer
)


def test_hash_functions_and_hmac():
    msg = "Aether Sovereignty Protocol"
    h256 = CryptoUtils.sha256_digest(msg)
    h512 = CryptoUtils.sha512_digest(msg)
    b2b = CryptoUtils.blake2b_digest(msg)

    assert len(h256) == 64
    assert len(h512) == 128
    assert len(b2b) == 64

    # HMAC
    key = b"secret-pass-key-32-bytes-long!!!"
    sig = CryptoUtils.hmac_sha256(key, msg)
    assert len(sig) == 64
    assert CryptoUtils.constant_time_compare(sig, sig) is True
    assert CryptoUtils.constant_time_compare(sig, "invalid_sig") is False


def test_pbkdf2_key_derivation():
    salt = b"16_bytes_salt_!!"
    key1 = CryptoUtils.derive_key_pbkdf2("MyPassphrase", salt, iterations=1000, key_length=32)
    key2 = CryptoUtils.derive_key_pbkdf2("MyPassphrase", salt, iterations=1000, key_length=32)
    key3 = CryptoUtils.derive_key_pbkdf2("DifferentPass", salt, iterations=1000, key_length=32)

    assert key1 == key2
    assert key1 != key3
    assert len(key1) == 32


def test_local_vault_authenticated_encryption():
    secret_note = "CONFIDENTIAL: Sovereign coordinates at 45.0N, 35.0W. Zero cloud telemetry."
    passphrase = "MasterKeyOmegaVaultPassphrase!2026"

    # Encrypt
    encrypted_token = LocalVaultCipher.encrypt(secret_note, passphrase)
    assert isinstance(encrypted_token, str)
    assert secret_note not in encrypted_token

    # Decrypt
    decrypted = LocalVaultCipher.decrypt(encrypted_token, passphrase)
    assert decrypted == secret_note

    # Wrong passphrase must raise ValueError
    with pytest.raises(ValueError):
        LocalVaultCipher.decrypt(encrypted_token, "WrongPassphrase")

    # Tampered ciphertext must raise ValueError
    tampered = encrypted_token[:-5] + "AAAAA"
    with pytest.raises(ValueError):
        LocalVaultCipher.decrypt(tampered, passphrase)


def test_password_security_analyzer():
    # Weak password
    weak_res = PasswordSecurityAnalyzer.analyze("123456")
    assert weak_res["score"] < 40
    assert "Weak" in weak_res["rating"]

    # Sovereign military-grade password
    strong_res = PasswordSecurityAnalyzer.analyze("Kx9#mQ!8vL$2pW@7zT^4")
    assert strong_res["entropy_bits"] > 80.0
    assert strong_res["score"] >= 80
    assert strong_res["has_upper"] is True
    assert strong_res["has_lower"] is True
    assert strong_res["has_digit"] is True
    assert strong_res["has_special"] is True


def test_secure_tokens_and_uuidv4():
    tok = CryptoUtils.generate_secure_token(32)
    assert len(tok) == 64

    uuid_str = CryptoUtils.generate_uuidv4()
    assert len(uuid_str) == 36
    assert uuid_str[14] == '4'  # Version 4
    assert uuid_str[19] in ('8', '9', 'a', 'b')  # Variant 1
