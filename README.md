# Sandboxed File System MCP Server

A secure Model Context Protocol (MCP) server that provides file system operations within a sandboxed directory. This extension allows Claude Desktop to safely interact with files while maintaining strict security boundaries.

## Features

### 🔒 Security First
- **Sandboxed Operations**: All file operations are restricted to a configured sandbox directory
- **Path Validation**: Prevents directory traversal attacks and unauthorized access
- **File Size Limits**: Configurable maximum file size (default: 10MB)
- **Extension Filtering**: Only allows specific file extensions for security
- **Read-Only Mode**: Optional mode to prevent any write operations

### 📁 File System Tools

The server provides 5 essential file system tools:

1. **`list_files`** - List files and directories in a given path
   - Shows file type, size, and name
   - Sorted alphabetically for easy browsing

2. **`read_file`** - Read the contents of a file
   - UTF-8 encoding support
   - Size validation before reading
   - Error handling for non-text files

3. **`write_file`** - Write content to a file
   - Creates parent directories automatically
   - Validates file extensions and size
   - Overwrites existing files safely

4. **`create_directory`** - Create new directories
   - Supports nested directory creation
   - Checks for existing paths

5. **`delete_file`** - Delete files or directories
   - Files are deleted immediately
   - Directories must be empty (safety feature)
   - Prevents accidental data loss

### ⚙️ Configuration Options

- **Sandbox Path**: Choose where files can be accessed (default: extension's sandbox folder)
- **Read-Only Mode**: Toggle to prevent all write operations
- **Allowed Extensions**: `.txt`, `.json`, `.md`, `.py`, `.js`, `.html`, `.css`
- **Max File Size**: 10MB limit for individual files

## Installation

### Install the MCPB Extension

1. **Download the Extension**
   - Download `MCP_dev.mcpb` from this repository

2. **Install in Claude Desktop**
   - Open Claude Desktop
   - Go to **Settings** → **Extensions** → **Advanced Settings**
   - Click **Add Extension**
   - Select the `MCP_dev.mcpb` file
   - Configure your preferences:
     - **Sandbox Directory**: Choose where files will be stored
     - **Read-Only Mode**: Enable to prevent write operations

### Configuration

During installation, you can configure:

- **Sandbox Directory**: The root directory where all file operations will be contained
  - Default: `{extension-folder}/sandbox`
  - Can be changed to any directory you have access to

- **Read-Only Mode**: Prevents any file modifications
  - Default: `false` (write operations allowed)
  - Set to `true` for read-only access

## Usage Examples

Once installed, you can ask Claude to perform file operations:

### Basic Operations
```
"Create a directory called 'projects'"
"List the files in the current directory"
"Read the contents of config.json"
"Write a hello world program to hello.py"
```

### Advanced Usage
```
"Create a project structure with folders for src, docs, and tests"
"Read all Python files and summarize their functions"
"Create a README file with project documentation"
"Organize files by moving them to appropriate directories"
```

## Security Features

### Sandbox Containment
- All operations are restricted to the configured sandbox directory
- Path validation prevents `../` directory traversal attacks
- Absolute paths outside the sandbox are blocked

### File Safety
- File size limits prevent memory exhaustion
- Extension filtering blocks potentially dangerous file types
- Read-only mode available for safe browsing
- Empty directory requirement for deletion prevents data loss

### Error Handling
- Graceful handling of permission errors
- Clear error messages for debugging
- Automatic recovery from network issues
- Comprehensive logging for troubleshooting

## File Structure

```
MCP_dev/
├── server/
│   ├── main.py           # Main MCP server implementation
│   └── config.json       # Server configuration
├── sandbox/              # Default sandbox directory
│   ├── welcome.txt       # Sample files
│   ├── test.txt
│   ├── docs/             # Sample directories
│   ├── projects/
│   └── test_dir/
├── .venv/                # Python virtual environment
├── MCP_dev.mcpb          # Built MCPB extension package
├── manifest.json         # MCPB extension manifest
├── requirements.txt      # Python dependencies
├── test_client.py        # Test client for development
└── README.md            # This file
```

## Technical Details

### MCP Protocol
- Uses Model Context Protocol (MCP) for communication
- JSON-RPC over stdio transport
- Protocol version: 2025-06-18

### Python Implementation
- Built with `@modelcontextprotocol/sdk`
- Python 3.8+ compatible
- Async/await architecture for performance

## Troubleshooting

### Common Issues

**Extension won't install**
- Ensure you have the latest Claude Desktop version
- Check file permissions on the MCPB file
- Try restarting Claude Desktop

**"Server disconnected" errors**
- Check the Claude Desktop logs: `~/Library/Logs/Claude/`
- Verify Python is available in the extension environment
- Ensure sandbox directory is accessible

**Permission errors**
- Make sure the sandbox directory is writable
- Check if read-only mode is enabled
- Verify file extension is allowed

### Debug Information

Extension logs are available at:
- **macOS**: `~/Library/Logs/Claude/mcp-server-Sandboxed File System Server.log`
- **Windows**: `%APPDATA%\Claude\Logs\`
- **Linux**: `~/.local/share/claude/logs/`

## Development

### Building from Source

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd MCP_dev
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Test the server**
   ```bash
   python server/main.py --sandbox ./sandbox
   ```

4. **Build MCPB package**
   ```bash
   mcpb pack
   ```


**Note**: This extension provides powerful file system access. Always review and understand the permissions you're granting before installation.