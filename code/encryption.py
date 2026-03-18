"""
Encryption Implementation Examples
Demonstrates symmetric and asymmetric encryption with real-world considerations
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
from argon2.low_level import hash_secret_raw, Type
import os
import stat
import pathlib
import base64


class AESEncryption:
    """
    AES-256 encryption using GCM mode (provides both encryption and authentication)
    
    Real-world issues:
    - Key management is your problem (losing keys = losing data)
    - Nonce reuse catastrophically breaks security
    - No key rotation built in
    - Memory may not be securely wiped
    """
    
    @staticmethod
    def generate_key():
        """Generate a random 256-bit key"""
        return os.urandom(32)
    
    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None):
        """
        Derive encryption key from password using Argon2id

        Limitations:
        - Weak passwords still produce weak security
        - Salt must be stored alongside encrypted data
        """
        if salt is None:
            salt = os.urandom(16)

        key = hash_secret_raw(
            secret=password.encode(),
            salt=salt,
            time_cost=2,
            memory_cost=65536,  # 64 MB
            parallelism=2,
            hash_len=32,
            type=Type.ID
        )
        return key, salt
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes) -> bytes:
        """
        Encrypt data using AES-256-GCM

        Returns a single blob: nonce (12 bytes) + tag (16 bytes) + ciphertext
        Critical: Use decrypt() to unpack — do not split manually
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return nonce + encryptor.tag + ciphertext

    @staticmethod
    def decrypt(data: bytes, key: bytes) -> bytes:
        """
        Decrypt AES-256-GCM data

        Expects blob produced by encrypt(): nonce + tag + ciphertext

        Failure modes:
        - Wrong key: raises InvalidTag exception
        - Tampered data: raises InvalidTag exception
        """
        nonce, tag, ciphertext = data[:12], data[12:28], data[28:]
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()


class RSAEncryption:
    """
    RSA asymmetric encryption
    
    Limitations:
    - Can only encrypt small amounts of data (max ~200 bytes with 2048-bit key)
    - Much slower than symmetric encryption
    - Key generation is computationally expensive
    - Private key compromise = total failure
    """
    
    
    @staticmethod
    def generate_keypair(key_size=2048):
        """
        Generate RSA key pair
        
        Note: 2048-bit is minimum acceptable, 4096-bit is better but slower
        Quantum computers will eventually break this entirely
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        return private_key, public_key
    
    @staticmethod
    def encrypt(plaintext: bytes, public_key):
        """
        Encrypt with RSA-OAEP
        
        Max plaintext size = (key_size / 8) - 2 - (2 * hash_length)
        For 2048-bit key with SHA256: ~190 bytes max
        """
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
    
    @staticmethod
    def decrypt(ciphertext: bytes, private_key):
        """Decrypt with RSA private key"""
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return plaintext
    
    @staticmethod
    def save_private_key(private_key, filename, password=None):
        """
        Save private key to file with owner-only permissions (600)

        Warning: Unencrypted keys on disk are a liability
        Even with password, file permissions matter
        """
        encryption_algorithm = serialization.BestAvailableEncryption(
            password.encode()
        ) if password else serialization.NoEncryption()

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm
        )

        path = pathlib.Path(filename)
        path.write_bytes(pem)
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # owner read/write only
    
    @staticmethod
    def load_private_key(filename, password=None):
        """Load private key from file"""
        with open(filename, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=password.encode() if password else None,
                backend=default_backend()
            )
        return private_key


class HybridEncryption:
    """
    Hybrid encryption: RSA for key exchange, AES for data
    
    This is how real systems work (TLS, PGP, etc.)
    
    Downsides:
    - More complex = more ways to mess up
    - Still vulnerable to implementation bugs
    - Doesn't solve key distribution problem
    """
    
    @staticmethod
    def encrypt(plaintext: bytes, public_key) -> tuple[bytes, bytes]:
        """
        Encrypt large data using hybrid approach:
        1. Generate random AES key
        2. Encrypt data with AES (returns single blob)
        3. Encrypt AES key with RSA

        Returns: (encrypted_aes_key, aes_blob)
        """
        aes_key = AESEncryption.generate_key()
        aes_blob = AESEncryption.encrypt(plaintext, aes_key)
        encrypted_aes_key = RSAEncryption.encrypt(aes_key, public_key)
        return encrypted_aes_key, aes_blob

    @staticmethod
    def decrypt(encrypted_aes_key: bytes, aes_blob: bytes, private_key) -> bytes:
        """Decrypt hybrid-encrypted data"""
        aes_key = RSAEncryption.decrypt(encrypted_aes_key, private_key)
        return AESEncryption.decrypt(aes_blob, aes_key)


def demonstration():
    """
    Demonstration of encryption approaches
    
    What this doesn't show you:
    - Secure key storage (hardware security modules, key management systems)
    - Key rotation strategies
    - Secure memory handling
    - Side-channel attack resistance
    - Compliance requirements (FIPS, GDPR, etc.)
    """
    
    print("=== AES Symmetric Encryption ===")
    key = AESEncryption.generate_key()
    plaintext = b"Secret message that needs encrypting"

    aes_blob = AESEncryption.encrypt(plaintext, key)
    print(f"Encrypted: {base64.b64encode(aes_blob).decode()}")

    decrypted = AESEncryption.decrypt(aes_blob, key)
    print(f"Decrypted: {decrypted.decode()}")
    print(f"Match: {plaintext == decrypted}\n")

    print("=== Password-based Encryption (Argon2id) ===")
    password = "weak_password_123"  # In reality, most users choose worse
    derived_key, salt = AESEncryption.derive_key_from_password(password)

    aes_blob = AESEncryption.encrypt(plaintext, derived_key)

    # To decrypt, you need the same password and salt
    same_key, _ = AESEncryption.derive_key_from_password(password, salt)
    decrypted = AESEncryption.decrypt(aes_blob, same_key)
    print(f"Decrypted: {decrypted.decode()}\n")

    print("=== RSA Asymmetric Encryption ===")
    private_key, public_key = RSAEncryption.generate_keypair()

    # Small message (RSA limitation)
    small_msg = b"Small secret"
    encrypted = RSAEncryption.encrypt(small_msg, public_key)
    decrypted = RSAEncryption.decrypt(encrypted, private_key)
    print(f"Decrypted: {decrypted.decode()}\n")

    print("=== Hybrid Encryption (Recommended for large data) ===")
    large_plaintext = b"A" * 10000  # 10KB of data

    enc_key, aes_blob = HybridEncryption.encrypt(large_plaintext, public_key)
    decrypted = HybridEncryption.decrypt(enc_key, aes_blob, private_key)
    print(f"Successfully encrypted and decrypted {len(large_plaintext)} bytes")
    print(f"Match: {large_plaintext == decrypted}")

    print("\n=== Common Failure Scenarios ===")

    # Wrong key
    try:
        wrong_key = AESEncryption.generate_key()
        AESEncryption.decrypt(aes_blob, wrong_key)
    except Exception as e:
        print(f"Wrong key error: {type(e).__name__}")

    # Tampered data
    try:
        tampered = aes_blob[:-1] + b'X'
        AESEncryption.decrypt(tampered, key)
    except Exception as e:
        print(f"Tampered data error: {type(e).__name__}")

    # Data too large for RSA
    try:
        huge_data = b"A" * 500
        RSAEncryption.encrypt(huge_data, public_key)
    except Exception as e:
        print(f"RSA size limit error: {type(e).__name__}")


if __name__ == "__main__":
    demonstration()