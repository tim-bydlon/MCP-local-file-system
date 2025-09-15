#!/usr/bin/env python3
"""
A simple MCP server for file system operations.
Provides safe file operations within a sandboxed directory.
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent
from pydantic import BaseModel


class Config(BaseModel):
    name: str
    version: str
    description: str
    sandbox_path: str
    max_file_size: int
    allowed_extensions: List[str]
    read_only: bool


class FileSystemServer:
    def __init__(self, config_path: str = "config.json"):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        self.config = Config(**config_data)

        # Create sandbox directory if it doesn't exist
        self.sandbox_path = Path(self.config.sandbox_path).resolve()
        self.sandbox_path.mkdir(exist_ok=True)

        # Initialize MCP server
        self.server = Server(self.config.name)
        self._register_tools()

    def _register_tools(self):
        """Register all available tools with the MCP server."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_files",
                    description="List files and directories in a given path",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list (relative to sandbox)"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="read_file",
                    description="Read the contents of a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to read (relative to sandbox)"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="write_file",
                    description="Write content to a file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to write (relative to sandbox)"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write to the file"
                            }
                        },
                        "required": ["path", "content"]
                    }
                ),
                Tool(
                    name="create_directory",
                    description="Create a new directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to create (relative to sandbox)"
                            }
                        },
                        "required": ["path"]
                    }
                ),
                Tool(
                    name="delete_file",
                    description="Delete a file or directory",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File or directory path to delete (relative to sandbox)"
                            }
                        },
                        "required": ["path"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "list_files":
                    return await self._list_files(arguments["path"])
                elif name == "read_file":
                    return await self._read_file(arguments["path"])
                elif name == "write_file":
                    return await self._write_file(arguments["path"], arguments["content"])
                elif name == "create_directory":
                    return await self._create_directory(arguments["path"])
                elif name == "delete_file":
                    return await self._delete_file(arguments["path"])
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    def _validate_path(self, path: str) -> Path:
        """Validate and resolve a path within the sandbox."""
        # Convert to Path and resolve
        target_path = (self.sandbox_path / path).resolve()

        # Ensure the path is within the sandbox
        if not str(target_path).startswith(str(self.sandbox_path)):
            raise ValueError(f"Path '{path}' is outside the sandbox directory")

        return target_path

    async def _list_files(self, path: str) -> List[TextContent]:
        """List files and directories in the given path."""
        target_path = self._validate_path(path)

        if not target_path.exists():
            return [TextContent(type="text", text=f"Path does not exist: {path}")]

        if not target_path.is_dir():
            return [TextContent(type="text", text=f"Path is not a directory: {path}")]

        items = []
        for item in sorted(target_path.iterdir()):
            item_type = "dir" if item.is_dir() else "file"
            size = item.stat().st_size if item.is_file() else "-"
            items.append(f"{item_type:4} {size:>10} {item.name}")

        result = f"Contents of {path}:\n" + "\n".join(items)
        return [TextContent(type="text", text=result)]

    async def _read_file(self, path: str) -> List[TextContent]:
        """Read the contents of a file."""
        target_path = self._validate_path(path)

        if not target_path.exists():
            return [TextContent(type="text", text=f"File does not exist: {path}")]

        if not target_path.is_file():
            return [TextContent(type="text", text=f"Path is not a file: {path}")]

        # Check file size
        if target_path.stat().st_size > self.config.max_file_size:
            return [TextContent(type="text", text=f"File too large (max {self.config.max_file_size} bytes)")]

        try:
            content = target_path.read_text(encoding='utf-8')
            return [TextContent(type="text", text=content)]
        except UnicodeDecodeError:
            return [TextContent(type="text", text="Error: File contains non-UTF-8 content")]

    async def _write_file(self, path: str, content: str) -> List[TextContent]:
        """Write content to a file."""
        if self.config.read_only:
            return [TextContent(type="text", text="Server is in read-only mode")]

        target_path = self._validate_path(path)

        # Check file extension
        if target_path.suffix and target_path.suffix not in self.config.allowed_extensions:
            return [TextContent(type="text", text=f"File extension not allowed: {target_path.suffix}")]

        # Check content size
        if len(content.encode('utf-8')) > self.config.max_file_size:
            return [TextContent(type="text", text=f"Content too large (max {self.config.max_file_size} bytes)")]

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(content, encoding='utf-8')
        return [TextContent(type="text", text=f"File written successfully: {path}")]

    async def _create_directory(self, path: str) -> List[TextContent]:
        """Create a new directory."""
        if self.config.read_only:
            return [TextContent(type="text", text="Server is in read-only mode")]

        target_path = self._validate_path(path)

        if target_path.exists():
            return [TextContent(type="text", text=f"Path already exists: {path}")]

        target_path.mkdir(parents=True, exist_ok=True)
        return [TextContent(type="text", text=f"Directory created successfully: {path}")]

    async def _delete_file(self, path: str) -> List[TextContent]:
        """Delete a file or directory."""
        if self.config.read_only:
            return [TextContent(type="text", text="Server is in read-only mode")]

        target_path = self._validate_path(path)

        if not target_path.exists():
            return [TextContent(type="text", text=f"Path does not exist: {path}")]

        if target_path.is_file():
            target_path.unlink()
            return [TextContent(type="text", text=f"File deleted successfully: {path}")]
        elif target_path.is_dir():
            # Only delete empty directories for safety
            try:
                target_path.rmdir()
                return [TextContent(type="text", text=f"Directory deleted successfully: {path}")]
            except OSError:
                return [TextContent(type="text", text=f"Directory not empty: {path}")]
        else:
            return [TextContent(type="text", text=f"Unknown path type: {path}")]

    async def run(self):
        """Run the MCP server."""
        from mcp.server.stdio import stdio_server
        from mcp.server import InitializationOptions
        from mcp.types import ServerCapabilities

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=self.config.name,
                    server_version=self.config.version,
                    capabilities=ServerCapabilities(
                        tools={}
                    )
                )
            )


async def main():
    """Main entry point."""
    server = FileSystemServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())