import base64
import hashlib
from Crypto.Cipher import DES


def des_encrypt(text: str, key: str) -> str:
    md5_hex = hashlib.md5(key.encode("utf-8")).hexdigest().upper()
    key_iv = md5_hex[:8].encode("ascii")
    data = text.encode("utf-8")
    pad_len = 8 - (len(data) % 8)
    data += bytes([pad_len]) * pad_len
    cipher = DES.new(key_iv, DES.MODE_CBC, iv=key_iv)
    encrypted = cipher.encrypt(data)
    return "".join(f"{b:02X}" for b in encrypted)

def des_decrypt(text: str, key: str) -> str:
    md5_hex = hashlib.md5(key.encode("utf-8")).hexdigest().upper()
    key_iv = md5_hex[:8].encode("ascii")
    encrypted = bytes.fromhex(text)
    cipher = DES.new(key_iv, DES.MODE_CBC, iv=key_iv)
    decrypted = cipher.decrypt(encrypted)
    pad_len = decrypted[-1]
    decrypted = decrypted[:-pad_len]
    return decrypted.decode("utf-8")


# if __name__ == "__main__":
#     text = "hello world"
#     key = "12345678"
#     encrypted = des_encrypt(text, key)
#     print(encrypted)
#     decrypted = des_decrypt(encrypted, key)
#     print(decrypted)