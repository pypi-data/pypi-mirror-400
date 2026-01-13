import json
import logging

from dotenv import load_dotenv
from e2b_code_interpreter import Sandbox
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("code-sandbox-mcp")

app = FastMCP("code-sandbox-mcp")


@app.tool()
def create_sandbox(timeout: int = 300, template: str = None) -> str:
    """
    Create a new E2B sandbox and return its ID.
    
    Args:
        timeout: Timeout for the sandbox in seconds, default is 300 seconds
        template: Optional template name or ID to use for creating the sandbox. If not provided, the default template is used.
    
    Returns:
        JSON string containing the sandbox ID
    """
    logger.info(f"Creating new sandbox with timeout={timeout}, template={template}")
    
    try:
        create_kwargs = {"timeout": timeout}
        if template:
            create_kwargs["template"] = template
        
        sbx = Sandbox.create(**create_kwargs)
        sandbox_id = sbx.sandbox_id
        logger.info(f"Sandbox created successfully with ID: {sandbox_id}")
        
        result = {
            "sandbox_id": sandbox_id,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = f"Error creating sandbox: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result = {
            "error": error_msg,
        }
        return json.dumps(result, indent=2)


@app.tool()
def kill_sandbox(sandbox_id: str) -> str:
    """
    Kill an E2B sandbox by its ID.
    
    Args:
        sandbox_id: The ID of the sandbox to kill
        
    Returns:
        JSON string containing error message if failed, empty string if successful
    """
    logger.info(f"Killing sandbox: {sandbox_id}")
    
    try:
        success = Sandbox.kill(sandbox_id)
        if success:
            logger.info(f"Sandbox {sandbox_id} killed successfully")
            return ""
        else:
            error_msg = f"Sandbox {sandbox_id} not found or already killed"
            logger.warning(error_msg)
            result = {
                "error": error_msg,
            }
            return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = f"Error killing sandbox: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result = {
            "error": error_msg,
        }
        return json.dumps(result, indent=2)


@app.tool()
def run_command(command: str, sandbox_id: str = None) -> str:
    """
    Run a shell command in an E2B sandbox.
    
    Args:
        command: Shell command to execute
        sandbox_id: Optional sandbox ID to connect to an existing sandbox. If not provided, a new sandbox will be created.
    
    Returns:
        JSON string containing stdout, stderr, and exit code from command execution
    """
    logger.info(f"Executing command: {command[:100]}...")
    
    try:
        if sandbox_id:
            logger.info(f"Connecting to existing sandbox: {sandbox_id}")
            sbx = Sandbox.connect(sandbox_id)
        else:
            logger.info("Creating new sandbox for command execution")
            sbx = Sandbox.create()
        
        result_obj = sbx.commands.run(command)
        logger.info(f"Command execution completed with exit code: {result_obj.exit_code}")
        
        result = {
            "stdout": result_obj.stdout,
            "stderr": result_obj.stderr,
            "exit_code": result_obj.exit_code,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result = {
            "stdout": "",
            "stderr": error_msg,
            "exit_code": -1,
        }
        return json.dumps(result, indent=2)


@app.tool()
def run_code(code: str, sandbox_id: str = None) -> str:
    """
    Run python code in a secure sandbox by E2B. Using the Jupyter Notebook syntax.
    
    Args:
        code: Python code to execute
        sandbox_id: Optional sandbox ID to connect to an existing sandbox. If not provided, a new sandbox will be created.
        
    Returns:
        JSON string containing stdout and stderr from code execution
    """
    logger.info(f"Executing code: {code[:100]}...")
    
    try:
        if sandbox_id:
            logger.info(f"Connecting to existing sandbox: {sandbox_id}")
            sbx = Sandbox.connect(sandbox_id)
        else:
            logger.info("Creating new sandbox for code execution")
            sbx = Sandbox.create()
        
        execution = sbx.run_code(code)
        logger.info(f"Execution completed: {execution}")
        
        result = {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
        }
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        logger.error(error_msg, exc_info=True)
        result = {
            "stdout": "",
            "stderr": error_msg,
        }
        return json.dumps(result, indent=2)


def main():
    """Main entry point for the MCP server."""
    logger.info("Starting MCP server: code-sandbox-mcp")
    logger.info("Transport mode: stdio")
    
    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

