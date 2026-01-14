#!/usr/bin/env python3

import sys
import json
import zlib
import base64
import hashlib
import argparse
from pathlib import Path
from urllib import request, parse

from . import __version__

COMPRESS_PREFIX = "BM1:"  # v1: compress only
ENCRYPT_PREFIX = "BM2:"   # v2: compress + encrypt
DEFAULT_PASSWORD = "123456"


DEFAULT_API_BASE = "https://api.textdb.online"
DEFAULT_READ_BASE = "https://textdb.online"
CONFIG_DIR = Path.home() / ".config" / "beam"
CONFIG_FILE = CONFIG_DIR / "config.json"


def init_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    
    with CONFIG_FILE.open("r") as f:
        return json.load(f)


def save_config(config):
    with CONFIG_FILE.open("w") as f:
        json.dump(config, f, indent=2)


def get_api_base():
    config = load_config()
    return config.get("api_base", DEFAULT_API_BASE)


def get_read_base():
    config = load_config()
    return config.get("read_base", DEFAULT_READ_BASE)


def get_or_set_key():
    config = load_config()
    
    if "key" in config:
        return config["key"]
    
    print("No key configured. Please enter your personal key:")
    print("(Recommend 20+ characters for security)")
    key = input("Key: ").strip()
    
    if len(key) < 6 or len(key) > 60:
        print("Error: key must be 6-60 characters", file=sys.stderr)
        sys.exit(1)
    
    if "/" in key:
        print("Error: key cannot contain '/'", file=sys.stderr)
        sys.exit(1)
    
    config["key"] = key
    save_config(config)
    print(f"✓ Key saved: {key}")
    print(f"Access URL: {get_read_base()}/{key}")
    
    return key


def api_update(key, value):
    encoded_value = parse.quote(value)
    url = f"{get_api_base()}/update/?key={key}&value={encoded_value}"
    
    with request.urlopen(url) as response:
        return json.loads(response.read().decode())


def api_read(key):
    url = f"{get_read_base()}/{key}"
    
    try:
        with request.urlopen(url) as response:
            if response.status == 200:
                return response.read().decode()
    except Exception:
        return None


def api_delete(key):
    url = f"{get_api_base()}/update/?key={key}&value="
    
    with request.urlopen(url) as response:
        return json.loads(response.read().decode())


def get_password():
    config = load_config()
    return config.get("password", DEFAULT_PASSWORD)


def derive_key(password, length):
    # derive a key from password using SHA256
    key = hashlib.sha256(password.encode()).digest()
    # extend key if needed
    while len(key) < length:
        key += hashlib.sha256(key).digest()
    return key[:length]


def xor_crypt(data, password):
    key = derive_key(password, len(data))
    return bytes(a ^ b for a, b in zip(data, key))


def encode_payload(text, plain=False):
    if plain:
        return text
    password = get_password()
    compressed = zlib.compress(text.encode(), level=9)
    encrypted = xor_crypt(compressed, password)
    encoded = base64.urlsafe_b64encode(encrypted).decode()
    return f"{ENCRYPT_PREFIX}{encoded}"


def decode_payload(data):
    # v2: encrypted + compressed
    if data.startswith(ENCRYPT_PREFIX):
        password = get_password()
        encoded = data[len(ENCRYPT_PREFIX):]
        encrypted = base64.urlsafe_b64decode(encoded)
        compressed = xor_crypt(encrypted, password)
        return zlib.decompress(compressed).decode()
    
    # v1: compressed only (backward compatible)
    if data.startswith(COMPRESS_PREFIX):
        encoded = data[len(COMPRESS_PREFIX):]
        compressed = base64.urlsafe_b64decode(encoded)
        return zlib.decompress(compressed).decode()
    
    # raw text (backward compatible)
    return data


def cmd_copy(args):
    key = get_or_set_key()
    text = args.text
    
    # Priority 1: explicit text argument
    if not text and not sys.stdin.isatty():
        # Priority 2: stdin (pipe)
        text = sys.stdin.read().strip()
    
    # Priority 3: system clipboard (fallback)
    if not text:
        try:
            import pyperclip
            text = pyperclip.paste()
            if not text:
                print("Error: clipboard is empty", file=sys.stderr)
                sys.exit(1)
        except ImportError:
            print("Error: no text to copy", file=sys.stderr)
            print("Tip: Install pyperclip for clipboard support: pip install pyperclip", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: failed to read clipboard: {e}", file=sys.stderr)
            sys.exit(1)
    
    original_len = len(text)
    payload = encode_payload(text, plain=args.plain)
    payload_len = len(payload)
    
    response = api_update(key, payload)
    
    if response.get('status') == 1:
        if args.plain:
            print("✓ Copied to cloud (plain text)")
        else:
            ratio = (1 - payload_len / original_len) * 100 if original_len > 0 else 0
            print(f"✓ Copied to cloud ({original_len} → {payload_len}, -{ratio:.0f}%)")
        print(f"Access URL: {get_read_base()}/{key}")
    else:
        print("Error: failed to copy", file=sys.stderr)
        sys.exit(1)


def cmd_paste(args):
    key = get_or_set_key()
    content = api_read(key)
    
    if content is None:
        print("Error: no content found", file=sys.stderr)
        sys.exit(1)
    
    try:
        content = decode_payload(content)
    except Exception:
        pass  # invalid format, use raw content
    
    print(content, end='')


def cmd_delete(args):
    key = get_or_set_key()
    response = api_delete(key)
    
    if response.get('status') == 1:
        print("✓ Deleted cloud content")
    else:
        print("Error: failed to delete", file=sys.stderr)
        sys.exit(1)


def cmd_edit(args):
    config = load_config()
    changed = False
    
    # handle server URLs
    if args.server:
        server = args.server.rstrip('/')
        # for textdb.online compatible format
        if 'textdb.online' in server or 'demo.textdb.online' in server:
            if server.startswith('https://api.'):
                config["api_base"] = server
                config["read_base"] = server.replace('//api.', '//')
            else:
                config["read_base"] = server
                config["api_base"] = server.replace('//', '//api.')
        else:
            # for custom deployment, assume api at /api path
            config["read_base"] = server
            config["api_base"] = f"{server}/api"
        changed = True
        print(f"✓ Server updated: {server}")
    
    # handle key
    if args.key:
        key = args.key
        if len(key) < 6 or len(key) > 60:
            print("Error: key must be 6-60 characters", file=sys.stderr)
            sys.exit(1)
        if "/" in key:
            print("Error: key cannot contain '/'", file=sys.stderr)
            sys.exit(1)
        config["key"] = key
        changed = True
        print(f"✓ Key updated: {key}")
        print(f"Access URL: {get_read_base()}/{key}")
    
    # handle password
    if args.password:
        config["password"] = args.password
        changed = True
        print("✓ Password updated")
    
    # interactive mode if no args
    if not args.key and not args.password and not args.server:
        current_server = config.get("read_base", DEFAULT_READ_BASE)
        current_key = config.get("key", "")
        current_pwd = config.get("password", DEFAULT_PASSWORD)
        
        print(f"Current server: {current_server}")
        print(f"Current key: {current_key}" if current_key else "No key configured")
        print(f"Current password: {current_pwd}")
        
        print("\nEnter new server URL (or press Enter to keep current):")
        print("Example: https://your-domain.com or https://demo.textdb.online")
        server = input("Server: ").strip()
        if server:
            server = server.rstrip('/')
            # for textdb.online compatible format
            if 'textdb.online' in server or 'demo.textdb.online' in server:
                if server.startswith('https://api.'):
                    config["api_base"] = server
                    config["read_base"] = server.replace('//api.', '//')
                else:
                    config["read_base"] = server
                    config["api_base"] = server.replace('//', '//api.')
            else:
                # for custom deployment, assume api at /api path
                config["read_base"] = server
                config["api_base"] = f"{server}/api"
            changed = True
        
        print("\nEnter new key (or press Enter to keep current):")
        key = input("Key: ").strip()
        if key:
            if len(key) < 6 or len(key) > 60:
                print("Error: key must be 6-60 characters", file=sys.stderr)
                sys.exit(1)
            if "/" in key:
                print("Error: key cannot contain '/'", file=sys.stderr)
                sys.exit(1)
            config["key"] = key
            changed = True
        
        print("\nEnter new password (or press Enter to keep current):")
        password = input("Password: ").strip()
        if password:
            config["password"] = password
            changed = True
    
    if changed:
        save_config(config)
        if not args.key and not args.password and not args.server:
            print("✓ Config updated")
    else:
        print("No changes made")


def main():
    init_config()
    
    parser = argparse.ArgumentParser(
        prog="bm",
        description="Beam - Cross-device clipboard tool"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='commands')
    
    # copy
    parser_copy = subparsers.add_parser('c', aliases=['copy'], help='Copy text to cloud')
    parser_copy.add_argument('text', nargs='?', help='Text to copy')
    parser_copy.add_argument('--plain', action='store_true', help='Plain text mode without encryption')
    parser_copy.set_defaults(func=cmd_copy)
    
    # paste
    parser_paste = subparsers.add_parser('p', aliases=['paste'], help='Paste text from cloud')
    parser_paste.set_defaults(func=cmd_paste)
    
    # delete
    parser_delete = subparsers.add_parser('d', aliases=['delete'], help='Delete cloud content')
    parser_delete.set_defaults(func=cmd_delete)
    
    # edit
    parser_edit = subparsers.add_parser('e', aliases=['edit'], help='Edit server/key/password')
    parser_edit.add_argument('key', nargs='?', help='New key to set')
    parser_edit.add_argument('-s', '--server', help='Set custom server URL (e.g., https://your-domain.com)')
    parser_edit.add_argument('-p', '--password', help='Set encryption password')
    parser_edit.set_defaults(func=cmd_edit)
    
    # version
    parser.add_argument('-v', '--version', action='version', version=f'beam v{__version__}')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
