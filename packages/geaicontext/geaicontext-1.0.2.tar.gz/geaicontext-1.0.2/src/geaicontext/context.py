import os
from fastmcp import FastMCP
import logging
from typing import Any, Coroutine, Callable
import time
from .tools.retrieve import retrieve_user_context
from .tools.save import save_user_context
from .clients.mongo_client import get_mongo_client
from .clients.redis_client import get_redis_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tool_wrapper(fn: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
    """A decorator to wrap MCP tools with logging and error handling."""
    async def wrapper(*args, **kwargs):
        tool_name = fn.__name__
        customer_id = kwargs.get("customer_id", args[0] if args else "N/A")
        logger.info(
            f"Invoking tool: {tool_name}",
            extra={"tool_name": tool_name, "customer_id": customer_id}
        )
        start_time = time.perf_counter()
        try:
            result = await fn(*args, **kwargs)
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            logger.info(
                f"Tool {tool_name} completed successfully in {duration:.2f}ms",
                extra={"tool_name": tool_name, "customer_id": customer_id, "duration_ms": duration}
            )
            return result
        except Exception as e:
            end_time = time.perf_counter()
            duration = (end_time - start_time) * 1000
            logger.error(
                f"Tool {tool_name} failed after {duration:.2f}ms: {e}",
                extra={"tool_name": tool_name, "customer_id": customer_id, "duration_ms": duration, "error": str(e)},
                exc_info=True
            )
            # Return structured error response
            error_type = type(e).__name__
            return {
                "success": False,
                "error_type": error_type,
                "error_message": str(e),
                "user_message": f"An error occurred while processing your request: {str(e)}"
            }
    return wrapper    

# Configuration

server_name = os.getenv("SERVER_NAME", "Context MCP")

mcp =FastMCP(
        name=server_name
    )

@mcp.tool()
async def save_context(customer_id: str, context: dict) -> dict[str, Any]:
    """
    Save user context to cache and database.
    
    Args:
        customer_id: The customer's unique identifier.
        context: The context data to save.
    
    Returns:
        A dictionary indicating success or failure with a message.
    """
    wrapped_fn = tool_wrapper(save_user_context)
    result = await wrapped_fn(customer_id, context)
    
    if isinstance(result, dict) and result.get("success") is False:
        # Error response from wrapper
        return result
    
    # result is a tuple (success: bool, message: str)
    success, message = result
    
    if success:
        return {
            "success": True,
            "message": message
        }
    else:
        return {
            "success": False,
            "error_type": "ValidationError",
            "error_message": message,
            "user_message": message
        }

@mcp.tool()
async def retrieve_context(customer_id: str) -> dict[str, Any]:
     """
    Retrieve user context from cache or database.
    
    Args:
        customer_id: The customer's unique identifier.
    
    Returns:
        A dictionary containing the user context if found, or an error response.
    """
     wrapped_fn = tool_wrapper(retrieve_user_context)
     result = await wrapped_fn(customer_id)
    
     if result is None:
        return {
            "success": False,
            "error_type": "NotFound",
            "error_message": f"No context found for customer_id: {customer_id}",
            "user_message": "No context found for this customer."
        }
     elif isinstance(result, dict) and result.get("success") is False:
        # Error response from wrapper
        return result
     else:
        return {
            "success": True,
            "data": result
        }

# WRAP THE RUN COMMAND IN A FUNCTION
def main():
    logger.info("Context server started.")
    mcp.run()
    

if __name__ == "__main__":
        main()
