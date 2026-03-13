import base64
from typing import Tuple
from sympy import randprime, gcd, mod_inverse

def _generate_prime(bits: int) -> int:
    return randprime(2**(bits - 1), 2**bits)


def generate_keys(bits: int = 512) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    p = _generate_prime(bits)
    q = _generate_prime(bits)
    while q == p:
        q = _generate_prime(bits)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if gcd(e, phi) != 1:
        e = 3
        while e < phi and gcd(e, phi) != 1:
            e += 2
        if gcd(e, phi) != 1:
            raise ValueError("Не удалось подобрать открытый показатель e")

    d = mod_inverse(e, phi)
    return (e, n), (d, n)


def _max_block_size(n: int) -> int:
    return (n.bit_length() - 1) // 8


def encrypt_text(plaintext: str, e: int, n: int) -> str:
    if not plaintext:
        return ""
    if n <= 0 or e <= 0:
        raise ValueError("Некорректные значения ключа")

    data = plaintext.encode("utf-8")
    block_size = _max_block_size(n)
    if block_size <= 0:
        raise ValueError("Слишком маленький модуль n для шифрования")

    cipher_bytes = bytearray()
    for i in range(0, len(data), block_size):
        chunk = data[i:i + block_size]
        m = int.from_bytes(chunk, "big")
        if m >= n:
            raise ValueError("Блок сообщения больше модуля n")
        c = pow(m, e, n)
        block_len = (n.bit_length() + 7) // 8
        cipher_bytes.extend(c.to_bytes(block_len, "big"))

    return base64.b64encode(cipher_bytes).decode("utf-8")


def decrypt_text(ciphertext: str, d: int, n: int) -> str:
    if not ciphertext.strip():
        return ""
    if n <= 0 or d <= 0:
        raise ValueError("Некорректные значения ключа")

    try:
        cipher_bytes = base64.b64decode(ciphertext)
    except Exception as e:
        raise ValueError("Некорректный Base64 шифртекст") from e

    block_len = (n.bit_length() + 7) // 8
    data_bytes = bytearray()

    for i in range(0, len(cipher_bytes), block_len):
        chunk = cipher_bytes[i:i + block_len]
        c = int.from_bytes(chunk, "big")
        m = pow(c, d, n)

        if m == 0:
            m_bytes = b'\x00'
        else:
            m_bytes = m.to_bytes((m.bit_length() + 7) // 8, "big")

        data_bytes.extend(m_bytes)

    try:
        return data_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Не удалось декодировать текст (ошибка UTF-8)") from exc

