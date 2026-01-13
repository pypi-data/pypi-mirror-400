from __future__ import annotations

from pathlib import Path
from typing import NewType
from getpass import getpass
import sys

Plaintext = NewType("Plaintext", str)
Key = NewType("Key", str)
CipherHex = NewType("CipherHex", str)

RESET = "\x1b[0m"
BOLD = "\x1b[1m"
RED = "\x1b[31m"
GREEN = "\x1b[32m"
CYAN = "\x1b[36m"
YELLOW = "\x1b[33m"

def info(msg: str) -> None:
    print(f"{CYAN}[i]{RESET} {msg}")

def ok(msg: str) -> None:
    print(f"{GREEN}[ok]{RESET} {msg}")

def warn(msg: str) -> None:
    print(f"{YELLOW}[!]{RESET} {msg}")

def err(msg: str) -> None:
    print(f"{RED}[x]{RESET} {msg}")

# ---------- core xor ----------
def _xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("Key must not be empty")
    k = len(key)
    return bytes(b ^ key[i % k] for i, b in enumerate(data))

def encrypt_file_to_hex(
    plaintext_path: str | Path,
    key: Key,
    out_path: str | Path,
    *,
    encoding: str = "utf-8",
) -> None:
    p = Path(plaintext_path).expanduser()
    s = p.read_text(encoding=encoding)
    data = s.encode(encoding)
    kbytes = key.encode("utf-8")
    cipher_hex = _xor_bytes(data, kbytes).hex()
    Path(out_path).expanduser().write_text(cipher_hex, encoding="ascii")

def decrypt_file_from_hex(
    cipher_hex_path: str | Path,
    key: Key,
    out_path: str | Path,
    *,
    encoding: str = "utf-8",
) -> None:
    p = Path(cipher_hex_path).expanduser()
    ch = p.read_text(encoding="ascii").strip()
    data = bytes.fromhex(ch)
    kbytes = key.encode("utf-8")
    plain = _xor_bytes(data, kbytes).decode(encoding)
    Path(out_path).expanduser().write_text(plain, encoding=encoding)

class XorCipher:
    def __init__(self, key: Key):
        if not key:
            raise ValueError("Key must not be empty")
        self._k = key.encode("utf-8")

    def encrypt_to_hex(self, plaintext: Plaintext, *, encoding: str = "utf-8") -> CipherHex:
        return CipherHex(_xor_bytes(plaintext.encode(encoding), self._k).hex())

    def decrypt_from_hex(self, cipher_hex: CipherHex, *, encoding: str = "utf-8") -> Plaintext:
        return Plaintext(_xor_bytes(bytes.fromhex(cipher_hex), self._k).decode(encoding))

# ---------- menu ----------
def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{BOLD}{prompt}{RESET}{suffix}: ").strip()
    return default if (default is not None and val == "") else val

def banner() -> None:
    print(f"{BOLD}{CYAN}XOR Tool{RESET}  {YELLOW}(encrypts to ASCII hex, decrypts back){RESET}")

def menu() -> None:
    banner()
    while True:
        print()
        print(f"{BOLD}Choose:{RESET}")
        print("  1) Encrypt file -> hex file")
        print("  2) Decrypt hex file -> text file")
        print("  3) Quit")

        choice = input("> ").strip()
        if choice == "1":
            try:
                pt_path = ask("Plaintext file", "plaintext")
                out_path = ask("Output hex file", "key")
                key_str = getpass("XOR key (hidden): ").strip()
                if not key_str:
                    err("Key cannot be empty")
                    continue
                info(f"Encrypting {pt_path} -> {out_path}")
                encrypt_file_to_hex(pt_path, Key(key_str), out_path)
                ok("Done. Hex written.")
            except FileNotFoundError as e:
                err(f"File not found: {e.filename}")
            except Exception as e:
                err(f"{type(e).__name__}: {e}")

        elif choice == "2":
            try:
                hex_path = ask("Input hex file", "key")
                out_path = ask("Output plaintext file", "plaintext.restored")
                key_str = getpass("XOR key (hidden): ").strip()
                if not key_str:
                    err("Key cannot be empty")
                    continue
                info(f"Decrypting {hex_path} -> {out_path}")
                decrypt_file_from_hex(hex_path, Key(key_str), out_path)
                ok("Done. Plaintext written.")
            except FileNotFoundError as e:
                err(f"File not found: {e.filename}")
            except ValueError as e:
                err(f"Bad hex or key. {e}")
            except Exception as e:
                err(f"{type(e).__name__}: {e}")

        elif choice == "3" or choice.lower() in {"q", "quit", "exit"}:
            warn("Bye.")
            sys.exit(0)
        else:
            warn("Invalid choice")

__all__ = [
    "Plaintext",
    "Key",
    "CipherHex",
    "XorCipher",
    "encrypt_file_to_hex",
    "decrypt_file_from_hex",
    "menu",
    "info",
    "ok",
    "warn",
    "err",
]

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print()
        warn("Interrupted")

