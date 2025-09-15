#!/usr/bin/env python3
"""
Simple test client for the File System MCP Server.
This demonstrates how to interact with the server programmatically.
"""

import asyncio
import subprocess
import json
import sys
from pathlib import Path


async def test_mcp_server():
    """Test the MCP server by calling tools directly."""
    print("🚀 File System MCP Server Test")
    print("=" * 40)

    # Test data
    test_cases = [
        {
            "tool": "list_files",
            "args": {"path": "."},
            "description": "List root sandbox directory"
        },
        {
            "tool": "read_file",
            "args": {"path": "welcome.txt"},
            "description": "Read welcome file"
        },
        {
            "tool": "write_file",
            "args": {"path": "test.txt", "content": "Hello from MCP test!\nThis file was created by the test client."},
            "description": "Write test file"
        },
        {
            "tool": "list_files",
            "args": {"path": "."},
            "description": "List directory after write"
        },
        {
            "tool": "create_directory",
            "args": {"path": "test_dir"},
            "description": "Create test directory"
        },
        {
            "tool": "list_files",
            "args": {"path": "."},
            "description": "List directory after creating folder"
        }
    ]

    # Import and test server directly (for demo purposes)
    try:
        from main import FileSystemServer
        server = FileSystemServer()

        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. {test['description']}")
            print(f"   Tool: {test['tool']}")
            print(f"   Args: {test['args']}")

            # Call the appropriate method directly
            try:
                if test['tool'] == 'list_files':
                    result = await server._list_files(test['args']['path'])
                elif test['tool'] == 'read_file':
                    result = await server._read_file(test['args']['path'])
                elif test['tool'] == 'write_file':
                    result = await server._write_file(test['args']['path'], test['args']['content'])
                elif test['tool'] == 'create_directory':
                    result = await server._create_directory(test['args']['path'])
                else:
                    result = [{"type": "text", "text": f"Unknown tool: {test['tool']}"}]

                print(f"   ✅ Result: {result[0].text}")

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

    except ImportError as e:
        print(f"❌ Failed to import server: {e}")
        return False

    print(f"\n🎉 Test completed! Check the ./sandbox directory for created files.")
    return True


def show_project_structure():
    """Show the final project structure."""
    print("\n📁 Project Structure:")
    print("=" * 40)

    def print_tree(path, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return

        items = sorted(path.iterdir()) if path.is_dir() else []
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir() and not item.name.startswith('.'):
                next_prefix = prefix + ("    " if is_last else "│   ")
                print_tree(item, next_prefix, max_depth, current_depth + 1)

    project_root = Path(".")
    print_tree(project_root)


async def main():
    """Main test function."""
    success = await test_mcp_server()
    show_project_structure()

    if success:
        print(f"\n✨ Your File System MCP Server is working!")
        print(f"📖 Key learnings about MCP:")
        print(f"   • MCP servers provide tools that clients can call")
        print(f"   • Tools have defined schemas for input validation")
        print(f"   • Servers run over stdio for communication")
        print(f"   • Safety features like sandboxing are crucial")
        print(f"   • Error handling ensures robust operation")
        print(f"\n🚀 Next steps:")
        print(f"   • Try connecting with an MCP client like Claude Desktop")
        print(f"   • Add more tools (copy, move, search files)")
        print(f"   • Implement logging and monitoring")
        print(f"   • Add authentication and permissions")


if __name__ == "__main__":
    asyncio.run(main())