"""Number theory tools."""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'src'))

try:
    from mcp.tools.number_theory.is_prime import is_prime as _is_prime
    from mcp.tools.number_theory.prime_factors import prime_factors as _factors
    from mcp.tools.number_theory.gcd_lcm import gcd_lcm as _gcd_lcm
    from mcp.tools.number_theory.modular_arithmetic import modular_arithmetic as _modular
    from mcp.tools.number_theory.euler_totient import euler_totient as _totient
except ImportError:
    def _is_prime(n): return {"success": False, "error": "Number theory tools not available"}
    def _factors(n): return {"success": False, "error": "Number theory tools not available"}
    def _gcd_lcm(numbers): return {"success": False, "error": "Number theory tools not available"}
    def _modular(op, a, b, m): return {"success": False, "error": "Number theory tools not available"}
    def _totient(n): return {"success": False, "error": "Number theory tools not available"}


def is_prime_tool(number: str) -> str:
    """Check if prime."""
    try:
        n = int(number)
        result = _is_prime(n)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def prime_factors_tool(number: str) -> str:
    """Find prime factors."""
    try:
        n = int(number)
        result = _factors(n)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def gcd_lcm_tool(numbers: str) -> str:
    """Calculate GCD and LCM."""
    try:
        nums = [int(x.strip()) for x in numbers.split(',')]
        result = _gcd_lcm(nums)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def modular_arithmetic_tool(operation: str, a: str, b: str, modulus: str) -> str:
    """Modular arithmetic."""
    try:
        result = _modular(operation, int(a), int(b), int(modulus))
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def euler_totient_tool(number: str) -> str:
    """Calculate Euler's totient."""
    try:
        n = int(number)
        result = _totient(n)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
