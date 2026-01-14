"""Cryptography tools."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'src'))

try:
    from mcp.tools.cryptography.caesar_cipher import caesar_cipher as _caesar
    from mcp.tools.cryptography.vigenere_cipher import vigenere_cipher as _vigenere
    from mcp.tools.cryptography.rsa_encrypt_decrypt import rsa_encrypt_decrypt as _rsa
    from mcp.tools.cryptography.aes_encrypt_decrypt import aes_encrypt_decrypt as _aes
    from mcp.tools.cryptography.generate_rsa_keys import generate_rsa_keys as _gen_keys
except ImportError:
    def _caesar(text, shift, mode): return {"success": False, "error": "Crypto tools not available"}
    def _vigenere(text, key, mode): return {"success": False, "error": "Crypto tools not available"}
    def _rsa(text, key, mode): return {"success": False, "error": "Crypto tools not available"}
    def _aes(text, key, mode): return {"success": False, "error": "Crypto tools not available"}
    def _gen_keys(bits): return {"success": False, "error": "Crypto tools not available"}


def caesar_cipher_tool(text: str, shift: str, mode: str) -> str:
    """Caesar cipher."""
    try:
        result = _caesar(text, int(shift), mode)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def vigenere_cipher_tool(text: str, key: str, mode: str) -> str:
    """Vigenere cipher."""
    try:
        result = _vigenere(text, key, mode)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def rsa_encrypt_decrypt_tool(text: str, key: str, mode: str) -> str:
    """RSA encryption."""
    try:
        key_dict = json.loads(key)
        result = _rsa(text, key_dict, mode)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def aes_encrypt_decrypt_tool(text: str, key: str, mode: str) -> str:
    """AES encryption."""
    try:
        result = _aes(text, key, mode)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def generate_rsa_keys_tool(bits: str) -> str:
    """Generate RSA keys."""
    try:
        result = _gen_keys(int(bits))
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
