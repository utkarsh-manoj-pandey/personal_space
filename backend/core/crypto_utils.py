"""
Aether Core Cryptographic & Vault Security Engine
Deterministic local cryptographic utilities and security audit models:
- Digest Services: SHA-256, SHA-512, BLAKE2b, constant-time comparisons.
- Key Derivation: PBKDF2-HMAC-SHA256 with configurable work factor.
- Local Vault Encryption: Authenticated Keystream Cipher (AES-CTR equivalent using HMAC-SHA256 counter mode).
- Password Entropy Analyzer: Shannon bit entropy, character distribution, dictionary heuristics, and crack-time estimations.
- Cryptographic Token Generation: High-entropy CSPRNG tokens.
"""

import os
import math
import time
import hmac
import base64
import hashlib
import secrets
import struct
from typing import Dict, Any, Tuple, Optional


class CryptoUtils:
    """
    Standardized cryptographic hash, HMAC, and token utilities.
    """

    @staticmethod
    def sha256_digest(data: str) -> str:
        """Compute SHA-256 hexadecimal hash string."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    @staticmethod
    def sha512_digest(data: str) -> str:
        """Compute SHA-512 hexadecimal hash string."""
        return hashlib.sha512(data.encode('utf-8')).hexdigest()

    @staticmethod
    def blake2b_digest(data: str, digest_size: int = 32) -> str:
        """Compute BLAKE2b cryptographic hash."""
        return hashlib.blake2b(data.encode('utf-8'), digest_size=digest_size).hexdigest()

    @staticmethod
    def hmac_sha256(key: bytes, message: str) -> str:
        """Generate HMAC-SHA256 signature in hexadecimal."""
        return hmac.new(key, message.encode('utf-8'), hashlib.sha256).hexdigest()

    @staticmethod
    def constant_time_compare(val1: str, val2: str) -> bool:
        """
        I have written this part of code because standard string comparisons (==) terminate early
        on the first non-matching byte, creating timing leaks that allow adversaries to recover secrets.
        hmac.compare_digest executes in constant time regardless of where mismatches occur.
        """
        return hmac.compare_digest(val1.encode('utf-8'), val2.encode('utf-8'))

    @staticmethod
    def generate_secure_token(length_bytes: int = 32) -> str:
        """
        I have written this part of code to sample the OS kernel entropy pool (/dev/urandom or CryptGenRandom)
        ensuring generated session tokens are cryptographically unpredictable.
        """
        return secrets.token_hex(length_bytes)

    @staticmethod
    def generate_uuidv4() -> str:
        """Generate RFC 4122 compliant UUID Version 4 string."""
        rnd = secrets.token_bytes(16)
        # Set version 4 (bits 12-15 of time_hi_and_version to 0100)
        byte_6 = (rnd[6] & 0x0f) | 0x40
        # Set variant 1 (bits 6-7 of clock_seq_hi_and_reserved to 10)
        byte_8 = (rnd[8] & 0x3f) | 0x80

        raw = (
            rnd[:6] +
            bytes([byte_6]) +
            bytes([rnd[7]]) +
            bytes([byte_8]) +
            rnd[9:]
        )
        h = raw.hex()
        return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"

    @staticmethod
    def derive_key_pbkdf2(passphrase: str, salt: bytes, iterations: int = 100000, key_length: int = 32) -> bytes:
        """
        Derive high-entropy symmetric key from passphrase using PBKDF2-HMAC-SHA256.
        Adheres to NIST SP 800-132 recommendations.
        """
        return hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=passphrase.encode('utf-8'),
            salt=salt,
            iterations=iterations,
            dklen=key_length
        )

    @staticmethod
    def checksum_crc32(data: bytes) -> int:
        """Calculate 32-bit Cyclic Redundancy Check (CRC-32)."""
        import zlib
        return zlib.crc32(data) & 0xffffffff


class LocalVaultCipher:
    """
    Authenticated Stream Cipher for local zero-cloud credential and secret storage.
    Uses HMAC-SHA256 Counter-Mode (CTR) keystream generation combined with
    Encrypt-then-MAC authentication tag verification.
    """

    MAGIC_HEADER = b"AETHER_ENC_V1"

    @classmethod
    def encrypt(cls, plaintext: str, passphrase: str) -> str:
        """
        Encrypts plaintext string with passphrase.
        Returns URL-safe Base64 encoded payload: [MAGIC][SALT:16][IV:16][CIPHERTEXT][HMAC:32].
        """
        salt = os.urandom(16)
        iv = os.urandom(16)
        master_key = CryptoUtils.derive_key_pbkdf2(passphrase, salt, iterations=100000, key_length=64)
        enc_key = master_key[:32]
        mac_key = master_key[32:]

        pt_bytes = plaintext.encode('utf-8')
        ciphertext = bytearray(len(pt_bytes))

        # Keystream generation via HMAC-SHA256 counter mode
        block_size = 32
        num_blocks = (len(pt_bytes) + block_size - 1) // block_size

        for block_idx in range(num_blocks):
            counter_bytes = struct.pack(">Q", block_idx)
            keystream = hmac.new(enc_key, iv + counter_bytes, hashlib.sha256).digest()
            start = block_idx * block_size
            end = min(start + block_size, len(pt_bytes))
            for i in range(start, end):
                ciphertext[i] = pt_bytes[i] ^ keystream[i - start]

        # Authenticate with Encrypt-then-MAC
        tag_data = cls.MAGIC_HEADER + salt + iv + bytes(ciphertext)
        auth_tag = hmac.new(mac_key, tag_data, hashlib.sha256).digest()

        full_payload = tag_data + auth_tag
        return base64.urlsafe_b64encode(full_payload).decode('ascii')

    @classmethod
    def decrypt(cls, encrypted_token: str, passphrase: str) -> str:
        """
        Decrypts Base64 authenticated ciphertext.
        Validates authentication tag prior to decryption to prevent tampering.
        """
        try:
            raw = base64.urlsafe_b64decode(encrypted_token.encode('ascii'))
        except Exception:
            raise ValueError("Malformed encrypted token: invalid base64.")

        magic_len = len(cls.MAGIC_HEADER)
        if len(raw) < magic_len + 16 + 16 + 32:
            raise ValueError("Token is truncated or corrupted.")

        if raw[:magic_len] != cls.MAGIC_HEADER:
            raise ValueError("Unknown token format or incompatible cipher version.")

        salt = raw[magic_len:magic_len + 16]
        iv = raw[magic_len + 16:magic_len + 32]
        auth_tag = raw[-32:]
        ciphertext = raw[magic_len + 32:-32]

        master_key = CryptoUtils.derive_key_pbkdf2(passphrase, salt, iterations=100000, key_length=64)
        enc_key = master_key[:32]
        mac_key = master_key[32:]

        # Verify authentication tag
        tag_data = raw[:-32]
        computed_tag = hmac.new(mac_key, tag_data, hashlib.sha256).digest()
        if not hmac.compare_digest(auth_tag, computed_tag):
            raise ValueError("Integrity verification failed: incorrect passphrase or corrupted data.")

        # Decrypt ciphertext
        pt_bytes = bytearray(len(ciphertext))
        block_size = 32
        num_blocks = (len(ciphertext) + block_size - 1) // block_size

        for block_idx in range(num_blocks):
            counter_bytes = struct.pack(">Q", block_idx)
            keystream = hmac.new(enc_key, iv + counter_bytes, hashlib.sha256).digest()
            start = block_idx * block_size
            end = min(start + block_size, len(ciphertext))
            for i in range(start, end):
                pt_bytes[i] = ciphertext[i] ^ keystream[i - start]

        return pt_bytes.decode('utf-8')


class PasswordSecurityAnalyzer:
    """
    Shannon bit entropy evaluator and credential resilience auditor.
    Evaluates password complexity, character distribution, and estimates crack latencies.
    """

    @classmethod
    def analyze(cls, password: str) -> Dict[str, Any]:
        if not password:
            return {
                "score": 0,
                "rating": "Empty",
                "entropy_bits": 0.0,
                "crack_time_display": "Instant",
                "recommendations": ["Password cannot be empty."]
            }

        length = len(password)
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)

        # Calculate character pool size N
        pool_size = 0
        if has_lower:
            pool_size += 26
        if has_upper:
            pool_size += 26
        if has_digit:
            pool_size += 10
        if has_special:
            pool_size += 33

        # Shannon Entropy = L * log2(N)
        entropy = length * math.log2(pool_size) if pool_size > 0 else 0.0

        # Frequency distribution Shannon entropy
        freq: Dict[str, int] = {}
        for c in password:
            freq[c] = freq.get(c, 0) + 1
        shannon_per_char = -sum((cnt / length) * math.log2(cnt / length) for cnt in freq.values())
        empirical_entropy = length * shannon_per_char

        # Common flaw deductions
        penalties = 0
        recommendations = []

        if length < 8:
            penalties += 35
            recommendations.append("Increase length to at least 12 characters.")
        elif length < 12:
            penalties += 15
            recommendations.append("Optimal password length is 16+ characters.")

        if not has_upper:
            penalties += 10
            recommendations.append("Include uppercase characters.")
        if not has_lower:
            penalties += 10
            recommendations.append("Include lowercase characters.")
        if not has_digit:
            penalties += 10
            recommendations.append("Include numeric digits.")
        if not has_special:
            penalties += 10
            recommendations.append("Include punctuation or special symbols.")

        # Sequential repetitions check
        if any(password[i:i+3] in "01234567890abcdefghijklmnopqrstuvwxyz" for i in range(max(0, length - 2))):
            penalties += 15
            recommendations.append("Avoid sequential character sequences (e.g. 123, abc).")

        # Score normalization (0 - 100)
        base_score = min(100, int((entropy / 80.0) * 100))
        final_score = max(0, min(100, base_score - penalties))

        # Rating tier
        if final_score < 25:
            rating = "Critical / Very Weak"
        elif final_score < 50:
            rating = "Weak"
        elif final_score < 70:
            rating = "Fair"
        elif final_score < 85:
            rating = "Strong"
        else:
            rating = "Military-Grade / Sovereign"

        # Offline GPU Hashcat crack speed assumption: 100 Billion hashes/sec (1e11)
        guesses = 2 ** entropy
        seconds_to_crack = guesses / 1e11

        def _format_time(sec: float) -> str:
            if sec < 1:
                return "Under 1 second"
            elif sec < 60:
                return f"{int(sec)} seconds"
            elif sec < 3600:
                return f"{int(sec / 60)} minutes"
            elif sec < 86400:
                return f"{int(sec / 3600)} hours"
            elif sec < 86400 * 365:
                return f"{int(sec / 86400)} days"
            elif sec < 86400 * 365 * 1000:
                return f"{int(sec / (86400 * 365))} years"
            elif sec < 86400 * 365 * 1e6:
                return f"{int(sec / (86400 * 365 * 1000))} millennia"
            else:
                return "Beyond cosmic horizon (> billions of years)"

        return {
            "score": final_score,
            "rating": rating,
            "entropy_bits": round(entropy, 2),
            "empirical_entropy_bits": round(empirical_entropy, 2),
            "pool_size": pool_size,
            "length": length,
            "has_upper": has_upper,
            "has_lower": has_lower,
            "has_digit": has_digit,
            "has_special": has_special,
            "estimated_crack_time": _format_time(seconds_to_crack),
            "recommendations": recommendations if recommendations else ["Password fulfills all sovereign security parameters."]
        }
