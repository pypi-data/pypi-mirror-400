#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from getpass import getpass
from pathlib import Path

from . import (
    Key,
    encrypt_file_to_hex,
    decrypt_file_from_hex,
    menu,
    err,
    ok,
    info,
)


def main() -> None:
    """Main entry point for xoryx CLI."""
    parser = argparse.ArgumentParser(
        prog="xoryx",
        description="XOR encryption/decryption tool - encrypts to ASCII hex",
        epilog="Run without arguments for interactive mode",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Encrypt subcommand
    encrypt_parser = subparsers.add_parser(
        "encrypt",
        aliases=["enc", "e"],
        help="Encrypt a file to hex format",
    )
    encrypt_parser.add_argument("input", help="Input plaintext file")
    encrypt_parser.add_argument("output", help="Output hex file")
    encrypt_parser.add_argument(
        "-k", "--key",
        help="Encryption key (if not provided, will prompt securely)",
    )
    encrypt_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding (default: utf-8)",
    )
    
    # Decrypt subcommand
    decrypt_parser = subparsers.add_parser(
        "decrypt",
        aliases=["dec", "d"],
        help="Decrypt a hex file back to plaintext",
    )
    decrypt_parser.add_argument("input", help="Input hex file")
    decrypt_parser.add_argument("output", help="Output plaintext file")
    decrypt_parser.add_argument(
        "-k", "--key",
        help="Decryption key (if not provided, will prompt securely)",
    )
    decrypt_parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding (default: utf-8)",
    )
    
    # Interactive subcommand
    interactive_parser = subparsers.add_parser(
        "interactive",
        aliases=["i", "menu"],
        help="Launch interactive menu mode",
    )
    
    args = parser.parse_args()
    
    # If no command provided, launch interactive mode
    if args.command is None:
        try:
            menu()
        except KeyboardInterrupt:
            print()
            err("Interrupted")
            sys.exit(130)
        return
    
    # Handle interactive mode
    if args.command in ("interactive", "i", "menu"):
        try:
            menu()
        except KeyboardInterrupt:
            print()
            err("Interrupted")
            sys.exit(130)
        return
    
    # Handle encrypt command
    if args.command in ("encrypt", "enc", "e"):
        try:
            # Get key
            if args.key:
                key_str = args.key
            else:
                key_str = getpass("Enter encryption key (hidden): ").strip()
            
            if not key_str:
                err("Key cannot be empty")
                sys.exit(1)
            
            # Validate input file exists
            input_path = Path(args.input).expanduser()
            if not input_path.exists():
                err(f"Input file not found: {args.input}")
                sys.exit(1)
            
            info(f"Encrypting {args.input} -> {args.output}")
            encrypt_file_to_hex(
                args.input,
                Key(key_str),
                args.output,
                encoding=args.encoding,
            )
            ok(f"Encrypted to {args.output}")
            
        except FileNotFoundError as e:
            err(f"File not found: {e.filename}")
            sys.exit(1)
        except Exception as e:
            err(f"{type(e).__name__}: {e}")
            sys.exit(1)
    
    # Handle decrypt command
    elif args.command in ("decrypt", "dec", "d"):
        try:
            # Get key
            if args.key:
                key_str = args.key
            else:
                key_str = getpass("Enter decryption key (hidden): ").strip()
            
            if not key_str:
                err("Key cannot be empty")
                sys.exit(1)
            
            # Validate input file exists
            input_path = Path(args.input).expanduser()
            if not input_path.exists():
                err(f"Input file not found: {args.input}")
                sys.exit(1)
            
            info(f"Decrypting {args.input} -> {args.output}")
            decrypt_file_from_hex(
                args.input,
                Key(key_str),
                args.output,
                encoding=args.encoding,
            )
            ok(f"Decrypted to {args.output}")
            
        except FileNotFoundError as e:
            err(f"File not found: {e.filename}")
            sys.exit(1)
        except ValueError as e:
            err(f"Invalid hex format or decryption error: {e}")
            sys.exit(1)
        except Exception as e:
            err(f"{type(e).__name__}: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

