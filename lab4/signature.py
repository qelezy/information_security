import base64
import hashlib
import math


def hash_file(path: str) -> int:
    with open(path, "rb") as f:
        digest = hashlib.file_digest(f, "sha512")
    return int.from_bytes(digest.digest(), "big")


def sign_file(file_path: str, signature_path: str, n: int, d: int) -> None:
    file_hash = hash_file(file_path)
    if file_hash >= n:
        raise ValueError("Хэш больше модуля n (увеличьте размер ключа)")

    sig_int = pow(file_hash, d, n)
    sig_bytes = sig_int.to_bytes(math.ceil(sig_int.bit_length() / 8), "big")
    sig_b64 = base64.b64encode(sig_bytes).decode("ascii")
    with open(signature_path, "w", encoding="utf-8") as f:
        f.write(sig_b64)


def verify_file(file_path: str, signature_path: str, n: int, e: int) -> bool:
    file_hash = hash_file(file_path)
    if file_hash >= n:
        return False

    try:
        sig_b64 = open(signature_path, "r", encoding="utf-8").read().strip()
        sig_bytes = base64.b64decode(sig_b64, validate=True)
    except Exception as exc:
        raise ValueError("Некорректный файл подписи") from exc

    sig_int = int.from_bytes(sig_bytes, "big")
    recovered_hash = pow(sig_int, e, n)
    return recovered_hash == file_hash

