from fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP()

@mcp.tool
def get_current_time():
    """Get current time"""
    return datetime.now()

def main():
    mcp.run()

if __name__ == "__main__":
    main()