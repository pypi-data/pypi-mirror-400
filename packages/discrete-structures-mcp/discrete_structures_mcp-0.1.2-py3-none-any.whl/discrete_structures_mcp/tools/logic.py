"""Logic tools - Boolean algebra operations."""
import json
import sys
import os

# Add backend to path to import existing tools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend', 'src'))

try:
    from mcp.tools.logic.evaluate_boolean import evaluate_boolean as _eval_bool
    from mcp.tools.logic.generate_truth_table import generate_truth_table as _gen_table
    from mcp.tools.logic.simplify_boolean import simplify_boolean as _simplify
    from mcp.tools.logic.convert_to_cnf import convert_to_cnf as _to_cnf
    from mcp.tools.logic.convert_to_dnf import convert_to_dnf as _to_dnf
except ImportError:
    # Fallback implementations
    def _eval_bool(expression, values):
        return {"success": False, "error": "Logic tools not available"}
    
    def _gen_table(expression):
        return {"success": False, "error": "Logic tools not available"}
    
    def _simplify(expression):
        return {"success": False, "error": "Logic tools not available"}
    
    def _to_cnf(expression):
        return {"success": False, "error": "Logic tools not available"}
    
    def _to_dnf(expression):
        return {"success": False, "error": "Logic tools not available"}


def evaluate_boolean_tool(expression: str, values: str) -> str:
    """Evaluate boolean expression."""
    try:
        values_dict = json.loads(values)
        result = _eval_bool(expression, values_dict)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def generate_truth_table_tool(expression: str) -> str:
    """Generate truth table."""
    try:
        result = _gen_table(expression)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def simplify_boolean_tool(expression: str) -> str:
    """Simplify boolean expression."""
    try:
        result = _simplify(expression)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def convert_to_cnf_tool(expression: str) -> str:
    """Convert to CNF."""
    try:
        result = _to_cnf(expression)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


def convert_to_dnf_tool(expression: str) -> str:
    """Convert to DNF."""
    try:
        result = _to_dnf(expression)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})
