# Code Sandbox MCP

MCP (Model Context Protocol) server for E2B code sandbox. This server provides tools to create, manage, and execute code in secure E2B sandboxes.

## Features

- **Create Sandbox**: Create new E2B sandboxes with customizable timeout and template
- **Kill Sandbox**: Terminate existing sandboxes by ID
- **Run Code**: Execute Python code in sandboxes using Jupyter Notebook syntax
- **Run Command**: Execute shell commands in sandboxes

## Installation

```bash
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

## Configuration

Create a `.env` file in the project root with your E2B credentials:

```env
E2B_API_KEY=your_api_key_here
E2B_DOMAIN=your_domain_here
```

## Usage

### Running the Server

Using MCP CLI with Inspector (for testing):

```bash
uv run mcp dev code_sandbox_mcp/server.py
```

Or using MCP CLI:

```bash
uv run mcp run code_sandbox_mcp/server.py
```

Or directly with Python:

```bash
python -m code_sandbox_mcp.server
```

Or using the installed command:

```bash
code-sandbox-mcp
```

### Available Tools

1. **create_sandbox(timeout: int = 300, template: str = None)**
   - Creates a new E2B sandbox
   - Returns the sandbox ID
   - Parameters:
     - `timeout`: Sandbox timeout in seconds (default: 300)
     - `template`: Optional template name or ID

2. **kill_sandbox(sandbox_id: str)**
   - Kills an existing sandbox
   - Returns empty string on success, error message on failure

3. **run_code(code: str, sandbox_id: str = None)**
   - Executes Python code in a sandbox
   - Uses Jupyter Notebook syntax
   - If `sandbox_id` is provided, connects to existing sandbox
   - Otherwise creates a new sandbox
   - Returns stdout and stderr

4. **run_command(command: str, sandbox_id: str = None)**
   - Executes a shell command in a sandbox
   - If `sandbox_id` is provided, connects to existing sandbox
   - Otherwise creates a new sandbox
   - Returns stdout, stderr, and exit code

## Development

This project uses:
- Python 3.10+
- E2B Code Interpreter SDK
- MCP Python SDK (FastMCP)
- python-dotenv for environment variable management

## License

MIT

