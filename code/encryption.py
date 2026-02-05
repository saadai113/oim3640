"""
Encryption Implementation Examples
Demonstrates symmetric and asymmetric encryption with real-world considerations
"""

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import os
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
        Derive encryption key from password using PBKDF2
        
        Limitations:
        - Weak passwords still produce weak security
        - 100k iterations is minimum, not ideal (consider Argon2 instead)
        - Salt must be stored alongside encrypted data
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    @staticmethod
    def encrypt(plaintext: bytes, key: bytes):
        """
        Encrypt data using AES-256-GCM
        
        Returns: (ciphertext, nonce, tag)
        
        Critical: You MUST store nonce and tag to decrypt
        """
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        
        return ciphertext, nonce, encryptor.tag
    
    @staticmethod
    def decrypt(ciphertext: bytes, key: bytes, nonce: bytes, tag: bytes):
        """
        Decrypt AES-256-GCM data
        
        Failure modes:
        - Wrong key: raises InvalidTag exception
        - Tampered data: raises InvalidTag exception
        - Wrong nonce: produces garbage output
        """
        cipher = Cipher(
            algorithms.AES(key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        return plaintext


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
        Save private key to file
        
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
        
        with open(filename, 'wb') as f:
            f.write(pem)
    
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
    def encrypt(plaintext: bytes, public_key):
        """
        Encrypt large data using hybrid approach:
        1. Generate random AES key
        2. Encrypt data with AES
        3. Encrypt AES key with RSA
        
        Returns: (encrypted_aes_key, ciphertext, nonce, tag)
        """
        # Generate random AES key for this message
        aes_key = AESEncryption.generate_key()
        
        # Encrypt the actual data with AES
        ciphertext, nonce, tag = AESEncryption.encrypt(plaintext, aes_key)
        
        # Encrypt the AES key with RSA
        encrypted_aes_key = RSAEncryption.encrypt(aes_key, public_key)
        
        return encrypted_aes_key, ciphertext, nonce, tag
    
    @staticmethod
    def decrypt(encrypted_aes_key: bytes, ciphertext: bytes, 
                nonce: bytes, tag: bytes, private_key):
        """Decrypt hybrid-encrypted data"""
        # Decrypt the AES key using RSA
        aes_key = RSAEncryption.decrypt(encrypted_aes_key, private_key)
        
        # Decrypt the data using AES
        plaintext = AESEncryption.decrypt(ciphertext, aes_key, nonce, tag)
        
        return plaintext


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
    
    ciphertext, nonce, tag = AESEncryption.encrypt(plaintext, key)
    print(f"Encrypted: {base64.b64encode(ciphertext).decode()}")
    
    decrypted = AESEncryption.decrypt(ciphertext, key, nonce, tag)
    print(f"Decrypted: {decrypted.decode()}")
    print(f"Match: {plaintext == decrypted}\n")
    
    print("=== Password-based Encryption ===")
    password = "weak_password_123"  # In reality, most users choose worse
    derived_key, salt = AESEncryption.derive_key_from_password(password)
    
    ciphertext, nonce, tag = AESEncryption.encrypt(plaintext, derived_key)
    
    # To decrypt, you need the same password and salt
    same_key, _ = AESEncryption.derive_key_from_password(password, salt)
    decrypted = AESEncryption.decrypt(ciphertext, same_key, nonce, tag)
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
    
    enc_key, ciphertext, nonce, tag = HybridEncryption.encrypt(
        large_plaintext, public_key
    )
    
    decrypted = HybridEncryption.decrypt(
        enc_key, ciphertext, nonce, tag, private_key
    )
    print(f"Successfully encrypted and decrypted {len(large_plaintext)} bytes")
    print(f"Match: {large_plaintext == decrypted}")
    
    print("\n=== Common Failure Scenarios ===")
    
    # Wrong key
    try:
        wrong_key = AESEncryption.generate_key()
        AESEncryption.decrypt(ciphertext, wrong_key, nonce, tag)
    except Exception as e:
        print(f"Wrong key error: {type(e).__name__}")
    
    # Tampered data
    try:
        tampered = ciphertext[:-1] + b'X'
        AESEncryption.decrypt(tampered, key, nonce, tag)
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