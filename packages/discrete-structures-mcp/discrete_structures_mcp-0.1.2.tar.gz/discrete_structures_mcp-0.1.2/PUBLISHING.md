# Publishing Guide for Discrete Structures MCP Server

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org
2. **GitHub Repository**: Ensure code is pushed to https://github.com/ZohaibCodez/discrete-structures-ai-platform
3. **Build Tools**: Install `uv` and `build`

## Steps to Publish

### 1. Build the Package

```bash
cd mcp-server
uv build
```

This creates `dist/` folder with:
- `discrete_structures_mcp-0.1.0.tar.gz` (source distribution)
- `discrete_structures_mcp-0.1.0-py3-none-any.whl` (wheel)

### 2. Test Locally

```bash
# Install locally
uv pip install -e .

# Test the server
discrete-structures-mcp
```

### 3. Upload to PyPI

```bash
# Install twine
uv pip install twine

# Upload to PyPI
uv run twine upload dist/*
```

Enter your PyPI username and password when prompted.

### 4. Verify Installation

```bash
# Install from PyPI
uvx discrete-structures-mcp

# Or with pip
pip install discrete-structures-mcp
discrete-structures-mcp
```

## Submit to MCP Registry

Once published to PyPI, submit your server to the official MCP registry:

### Option 1: Community Submission
1. Visit https://github.com/modelcontextprotocol/servers
2. Create a new issue with title: "Add discrete-structures-mcp server"
3. Provide:
   - Package name: `discrete-structures-mcp`
   - PyPI link: https://pypi.org/project/discrete-structures-mcp/
   - Description: "Discrete Structures tools for logic, algorithms, number theory, and cryptography"
   - Installation: `uvx discrete-structures-mcp`
   - Repository: https://github.com/ZohaibCodez/discrete-structures-ai-platform

### Option 2: Direct PR
1. Fork https://github.com/modelcontextprotocol/servers
2. Add entry to `servers/python/servers.json`:

```json
{
  "name": "discrete-structures",
  "displayName": "Discrete Structures",
  "description": "Tools for logic, algorithms, number theory, and cryptography education",
  "author": "ZohaibCodez",
  "homepage": "https://github.com/ZohaibCodez/discrete-structures-ai-platform",
  "packageName": "discrete-structures-mcp",
  "installCommand": "uvx discrete-structures-mcp",
  "categories": ["education", "mathematics", "computer-science"],
  "tags": ["logic", "algorithms", "cryptography", "number-theory"]
}
```

3. Submit pull request

### Option 3: MCP Hub Submission
1. Visit https://github.com/mcp
2. Look for submission guidelines
3. Follow their process for adding to the official registry

## Maintenance

### Update Version
1. Edit `pyproject.toml` - increment version
2. Edit `discrete_structures_mcp/__init__.py` - update `__version__`
3. Rebuild and republish

### Add GitHub Release
```bash
git tag v0.1.0
git push origin v0.1.0
```

Create release on GitHub with changelog.

## Marketing

Once published and listed:
1. ✅ Add badge to main README: ![PyPI](https://img.shields.io/pypi/v/discrete-structures-mcp)
2. ✅ Tweet/post about the release
3. ✅ Add to MCP community Discord
4. ✅ Create demo video showing usage with Claude Desktop
5. ✅ Write blog post about the tools

## Troubleshooting

**Error: Package already exists**
- Increment version number in `pyproject.toml`

**Error: Import failures**
- Test locally first: `uv run python -c "from discrete_structures_mcp import server"`
- Check all dependencies in `pyproject.toml`

**MCP server not responding**
- Test with: `echo '{"jsonrpc":"2.0","method":"initialize","id":1}' | discrete-structures-mcp`
- Check server logs

## Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
