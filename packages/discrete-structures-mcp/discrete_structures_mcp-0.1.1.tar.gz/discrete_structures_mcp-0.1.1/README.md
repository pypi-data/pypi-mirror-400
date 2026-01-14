# Discrete Structures MCP Server

A Model Context Protocol (MCP) server providing comprehensive tools for discrete mathematics education, including Boolean logic, algorithms, number theory, and cryptography.

## Features

### 🧮 Logic Tools (5 tools)
- **evaluate_boolean** - Evaluate boolean expressions with truth values
- **generate_truth_table** - Generate complete truth tables for logical expressions
- **simplify_boolean** - Simplify boolean expressions using algebraic rules
- **convert_to_cnf** - Convert expressions to Conjunctive Normal Form
- **convert_to_dnf** - Convert expressions to Disjunctive Normal Form

### 📊 Algorithm Visualizers (6 tools)
- **visualize_bubble_sort** - Step-by-step bubble sort visualization
- **visualize_quick_sort** - Quick sort with partition visualization
- **visualize_merge_sort** - Merge sort with divide-and-conquer steps
- **visualize_binary_search** - Binary search algorithm visualization
- **visualize_dijkstra** - Dijkstra's shortest path algorithm
- **visualize_bfs_dfs** - Breadth-first and depth-first search visualization

### 🔢 Number Theory Tools (5 tools)
- **is_prime** - Check if a number is prime
- **prime_factors** - Find prime factorization
- **gcd_lcm** - Calculate GCD and LCM of numbers
- **modular_arithmetic** - Perform modular arithmetic operations
- **euler_totient** - Calculate Euler's totient function

### 🔐 Cryptography Tools (5 tools)
- **caesar_cipher** - Encrypt/decrypt using Caesar cipher
- **vigenere_cipher** - Encrypt/decrypt using Vigenere cipher
- **rsa_encrypt_decrypt** - RSA encryption and decryption
- **aes_encrypt_decrypt** - AES symmetric encryption
- **generate_rsa_keys** - Generate RSA key pairs

## Installation

### Using uvx (recommended)
```bash
uvx discrete-structures-mcp
```

### Using pip
```bash
pip install discrete-structures-mcp
discrete-structures-mcp
```

### Development Installation
```bash
git clone https://github.com/ZohaibCodez/discrete-structures-ai-platform.git
cd discrete-structures-ai-platform/mcp-server
uv sync
uv run discrete-structures-mcp
```

## Usage with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "discrete-structures": {
      "command": "uvx",
      "args": ["discrete-structures-mcp"]
    }
  }
}
```

## Usage with MCP Clients

```python
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

server_params = StdioServerParameters(
    command="uvx",
    args=["discrete-structures-mcp"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # List available tools
        tools = await session.list_tools()
        print([tool.name for tool in tools.tools])
        
        # Call a tool
        result = await session.call_tool("gcd_lcm", {"numbers": "48,18"})
        print(result)
```

## Example Tool Calls

### Calculate GCD and LCM
```python
result = await session.call_tool("gcd_lcm", {
    "numbers": "48,18"
})
# Returns: {"gcd": 6, "lcm": 144}
```

### Generate Truth Table
```python
result = await session.call_tool("generate_truth_table", {
    "expression": "(A & B) | C"
})
# Returns complete truth table
```

### Visualize Bubble Sort
```python
result = await session.call_tool("visualize_bubble_sort", {
    "array": "5,2,8,1,9"
})
# Returns step-by-step sorting visualization
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Links

- [GitHub Repository](https://github.com/ZohaibCodez/discrete-structures-ai-platform)
- [Issue Tracker](https://github.com/ZohaibCodez/discrete-structures-ai-platform/issues)
- [MCP Documentation](https://modelcontextprotocol.io)
