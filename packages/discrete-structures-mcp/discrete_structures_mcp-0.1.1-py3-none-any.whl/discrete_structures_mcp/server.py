"""FastMCP-based Discrete Structures MCP Server."""
import json
from mcp.server.fastmcp import FastMCP

# Import tool implementations
from .tools.logic import (
    evaluate_boolean_tool,
    generate_truth_table_tool,
    simplify_boolean_tool,
    convert_to_cnf_tool,
    convert_to_dnf_tool,
)
from .tools.algorithms import (
    visualize_bubble_sort_tool,
    visualize_quick_sort_tool,
    visualize_merge_sort_tool,
    visualize_binary_search_tool,
    visualize_dijkstra_tool,
    visualize_bfs_dfs_tool,
)
from .tools.number_theory import (
    is_prime_tool,
    prime_factors_tool,
    gcd_lcm_tool,
    modular_arithmetic_tool,
    euler_totient_tool,
)
from .tools.cryptography import (
    caesar_cipher_tool,
    vigenere_cipher_tool,
    rsa_encrypt_decrypt_tool,
    aes_encrypt_decrypt_tool,
    generate_rsa_keys_tool,
)

# Create FastMCP server
mcp = FastMCP(
    "Discrete Structures",
    instructions="""A comprehensive MCP server for discrete mathematics education.
    
Provides 21 tools across four domains:
- Logic: Boolean algebra, truth tables, CNF/DNF conversion
- Algorithms: Sorting and graph algorithm visualizations
- Number Theory: Prime numbers, GCD/LCM, modular arithmetic
- Cryptography: Classical and modern encryption techniques
""",
)

# Register Logic Tools
@mcp.tool()
def evaluate_boolean(expression: str, values: str) -> str:
    """Evaluate a boolean expression with given variable values.
    
    Args:
        expression: Boolean expression (e.g., "A & B | C")
        values: Variable assignments as JSON (e.g., '{"A": true, "B": false, "C": true}')
    """
    return evaluate_boolean_tool(expression, values)

@mcp.tool()
def generate_truth_table(expression: str) -> str:
    """Generate a complete truth table for a boolean expression.
    
    Args:
        expression: Boolean expression (e.g., "(A & B) | C")
    """
    return generate_truth_table_tool(expression)

@mcp.tool()
def simplify_boolean(expression: str) -> str:
    """Simplify a boolean expression using algebraic rules.
    
    Args:
        expression: Boolean expression to simplify
    """
    return simplify_boolean_tool(expression)

@mcp.tool()
def convert_to_cnf(expression: str) -> str:
    """Convert boolean expression to Conjunctive Normal Form (CNF).
    
    Args:
        expression: Boolean expression to convert
    """
    return convert_to_cnf_tool(expression)

@mcp.tool()
def convert_to_dnf(expression: str) -> str:
    """Convert boolean expression to Disjunctive Normal Form (DNF).
    
    Args:
        expression: Boolean expression to convert
    """
    return convert_to_dnf_tool(expression)

# Register Algorithm Tools
@mcp.tool()
def visualize_bubble_sort(array: str) -> str:
    """Visualize bubble sort algorithm step by step.
    
    Args:
        array: Comma-separated numbers (e.g., "5,2,8,1,9")
    """
    return visualize_bubble_sort_tool(array)

@mcp.tool()
def visualize_quick_sort(array: str) -> str:
    """Visualize quick sort algorithm with partitioning steps.
    
    Args:
        array: Comma-separated numbers (e.g., "5,2,8,1,9")
    """
    return visualize_quick_sort_tool(array)

@mcp.tool()
def visualize_merge_sort(array: str) -> str:
    """Visualize merge sort algorithm with divide-and-conquer steps.
    
    Args:
        array: Comma-separated numbers (e.g., "5,2,8,1,9")
    """
    return visualize_merge_sort_tool(array)

@mcp.tool()
def visualize_binary_search(array: str, target: str) -> str:
    """Visualize binary search algorithm.
    
    Args:
        array: Comma-separated sorted numbers (e.g., "1,2,5,8,9")
        target: Number to search for
    """
    return visualize_binary_search_tool(array, target)

@mcp.tool()
def visualize_dijkstra(graph: str, start: str) -> str:
    """Visualize Dijkstra's shortest path algorithm.
    
    Args:
        graph: Graph as adjacency list JSON (e.g., '{"A": {"B": 4, "C": 2}}')
        start: Starting node
    """
    return visualize_dijkstra_tool(graph, start)

@mcp.tool()
def visualize_bfs_dfs(graph: str, start: str, algorithm: str) -> str:
    """Visualize BFS or DFS graph traversal.
    
    Args:
        graph: Graph as adjacency list JSON (e.g., '{"A": ["B", "C"]}')
        start: Starting node
        algorithm: Either "bfs" or "dfs"
    """
    return visualize_bfs_dfs_tool(graph, start, algorithm)

# Register Number Theory Tools
@mcp.tool()
def is_prime(number: str) -> str:
    """Check if a number is prime.
    
    Args:
        number: Integer to check
    """
    return is_prime_tool(number)

@mcp.tool()
def prime_factors(number: str) -> str:
    """Find prime factorization of a number.
    
    Args:
        number: Integer to factorize
    """
    return prime_factors_tool(number)

@mcp.tool()
def gcd_lcm(numbers: str) -> str:
    """Calculate GCD and LCM of numbers.
    
    Args:
        numbers: Comma-separated integers (e.g., "48,18,24")
    """
    return gcd_lcm_tool(numbers)

@mcp.tool()
def modular_arithmetic(operation: str, a: str, b: str, modulus: str) -> str:
    """Perform modular arithmetic operations.
    
    Args:
        operation: Operation type (add, subtract, multiply, power, inverse)
        a: First number
        b: Second number (not used for inverse)
        modulus: Modulus value
    """
    return modular_arithmetic_tool(operation, a, b, modulus)

@mcp.tool()
def euler_totient(number: str) -> str:
    """Calculate Euler's totient function φ(n).
    
    Args:
        number: Integer to calculate totient for
    """
    return euler_totient_tool(number)

# Register Cryptography Tools
@mcp.tool()
def caesar_cipher(text: str, shift: str, mode: str) -> str:
    """Encrypt or decrypt using Caesar cipher.
    
    Args:
        text: Text to process
        shift: Shift amount (0-25)
        mode: Either "encrypt" or "decrypt"
    """
    return caesar_cipher_tool(text, shift, mode)

@mcp.tool()
def vigenere_cipher(text: str, key: str, mode: str) -> str:
    """Encrypt or decrypt using Vigenere cipher.
    
    Args:
        text: Text to process
        key: Cipher key (alphabetic)
        mode: Either "encrypt" or "decrypt"
    """
    return vigenere_cipher_tool(text, key, mode)

@mcp.tool()
def rsa_encrypt_decrypt(text: str, key: str, mode: str) -> str:
    """Encrypt or decrypt using RSA.
    
    Args:
        text: Text to process
        key: RSA key as JSON (e.g., '{"n": 3233, "e": 17}')
        mode: Either "encrypt" or "decrypt"
    """
    return rsa_encrypt_decrypt_tool(text, key, mode)

@mcp.tool()
def aes_encrypt_decrypt(text: str, key: str, mode: str) -> str:
    """Encrypt or decrypt using AES.
    
    Args:
        text: Text to process
        key: Encryption key (will be hashed to 256 bits)
        mode: Either "encrypt" or "decrypt"
    """
    return aes_encrypt_decrypt_tool(text, key, mode)

@mcp.tool()
def generate_rsa_keys(bits: str) -> str:
    """Generate RSA key pair.
    
    Args:
        bits: Key size in bits (e.g., "1024", "2048")
    """
    return generate_rsa_keys_tool(bits)


def main():
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
