"""
Main entry point for MCP Universe Simulator.
"""
import uvicorn
from api.mcp_exposer.server import create_mcp_server
from tools.create_example_apps import create_example_apps

def main():
    """
    Main entry point.
    - Generates example apps if they don't exist.
    - Starts the MCP Universe Simulator server.
    """
    print("--- MCP Universe Simulator ---")
    
    # Generate example apps to ensure the server has content to serve
    print("\nChecking for example apps...")
    try:
        create_example_apps()
    except Exception as e:
        print(f"Could not create example apps: {e}")
        print("Please ensure dependencies are installed with 'pip install -r requirements.txt'")

    # Get the FastAPI app
    server = create_mcp_server()
    
    print("\nStarting MCP Universe Simulator server...")
    print("Server running at http://127.0.0.1:8000")
    print("API docs available at http://127.0.0.1:8000/docs")
    
    # Run the server
    uvicorn.run(server, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
