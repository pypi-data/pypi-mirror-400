
import json
import zlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def get_checksum(key:str|None)->int:
    # Convert last two characters of key to integer
    if key is None:
        return -1
    return int(key[-2:], 16)

def json_zip(dict, key: str | None = None):
    if not dict:
        return b''
    json_dict = json.dumps(dict).encode('utf-8')
    compressed_dict = zlib.compress(json_dict)
    
    # If key is provided, encrypt the compressed data
    if key:
        compressed_dict = _aes_encrypt(compressed_dict, key)
    
    return compressed_dict

def json_unzip(compressed_dict, key: str | None = None):
    if not compressed_dict:
        return {}
    
    # If key is provided, decrypt the compressed data first
    if key:
        compressed_dict = _aes_decrypt(compressed_dict, key)
    
    decompressed_dict = zlib.decompress(compressed_dict)
    return json.loads(decompressed_dict.decode('utf-8'))


def _aes_encrypt(data: bytes, key_hex: str) -> bytes:
    """
    Encrypt data using AES-256 in CBC mode.
    
    Args:
        data: The data to encrypt
        key_hex: A 256-bit hex key (64 hex characters)
    
    Returns:
        IV + ciphertext (IV is prepended to the ciphertext)
    """
    # Convert hex key to bytes
    key = bytes.fromhex(key_hex)
    
    if len(key) != 32:  # 256 bits = 32 bytes
        raise ValueError("Key must be 256 bits (64 hex characters)")
    
    # Generate a random 16-byte IV
    iv = os.urandom(16)
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Pad data to 16-byte boundary (PKCS7 padding)
    padded_data = _pkcs7_pad(data)
    
    # Encrypt
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    
    # Return IV + ciphertext
    return iv + ciphertext


def _aes_decrypt(data: bytes, key_hex: str) -> bytes:
    """
    Decrypt data using AES-256 in CBC mode.
    
    Args:
        data: The encrypted data (IV + ciphertext)
        key_hex: A 256-bit hex key (64 hex characters)
    
    Returns:
        The decrypted data
    """
    # Convert hex key to bytes
    key = bytes.fromhex(key_hex)
    
    if len(key) != 32:  # 256 bits = 32 bytes
        raise ValueError("Key must be 256 bits (64 hex characters)")
    
    # Extract IV and ciphertext
    iv = data[:16]
    ciphertext = data[16:]
    
    # Create cipher
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    
    # Decrypt
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    # Remove PKCS7 padding
    return _pkcs7_unpad(padded_data)


def _pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    """Add PKCS7 padding to data."""
    padding_length = block_size - (len(data) % block_size)
    padding = bytes([padding_length] * padding_length)
    return data + padding


def _pkcs7_unpad(data: bytes) -> bytes:
    """Remove PKCS7 padding from data."""
    padding_length = data[-1]
    return data[:-padding_length]