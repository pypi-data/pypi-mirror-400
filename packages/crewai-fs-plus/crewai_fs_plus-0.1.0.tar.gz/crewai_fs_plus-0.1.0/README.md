# CrewAI FS Plus

Enhanced filesystem tools for [CrewAI](https://www.crewai.com/) with whitelist/blacklist filtering and directory sandboxing.

## Features

- **Base Directory Sandboxing**: Restrict file operations to a specific directory
- **Whitelist Patterns**: Only allow access to files matching glob patterns
- **Blacklist Patterns**: Deny access to files matching glob patterns
- **Drop-in Replacement**: Same interface as CrewAI's built-in file tools

## Installation

```bash
pip install crewai-fs-plus
```

## Quick Start

```python
from crewai import Agent
from crewai_fs_plus import FileReadTool, FileWriteTool, FileDeleteTool, DirectoryReadTool

# Create sandboxed tools
reader = FileReadTool(
    base_directory="/path/to/project",
    whitelist=["*.py", "*.md", "docs/**"],
    blacklist=["**/secret*", "**/.env"]
)

writer = FileWriteTool(
    base_directory="/path/to/project",
    whitelist=["output/**", "logs/**"]
)

# Use with CrewAI agent
agent = Agent(
    role="Document Processor",
    goal="Process files safely within the project directory",
    tools=[reader, writer]
)
```

## Tools

### FileReadTool

Read file contents with optional line range.

```python
from crewai_fs_plus import FileReadTool

# Basic usage
reader = FileReadTool()
content = reader._run(file_path="document.txt")

# Read specific lines
content = reader._run(
    file_path="large_file.txt",
    start_line=100,
    line_count=50
)

# With sandboxing and filters
reader = FileReadTool(
    base_directory="/app/data",
    whitelist=["*.txt", "*.json"],
    blacklist=["*secret*", "*.env"]
)
```

**Parameters:**
- `file_path`: Path to the file to read
- `start_line`: Line number to start reading from (1-indexed, default: 1)
- `line_count`: Number of lines to read (default: all)

### FileWriteTool

Write content to files with overwrite protection.

```python
from crewai_fs_plus import FileWriteTool

# Basic usage
writer = FileWriteTool()
result = writer._run(
    file_path="output.txt",
    content="Hello, World!"
)

# Overwrite existing file
result = writer._run(
    file_path="output.txt",
    content="Updated content",
    overwrite=True
)

# With sandboxing - only allow writes to output directory
writer = FileWriteTool(
    base_directory="/app",
    whitelist=["output/**", "logs/**"]
)
```

**Parameters:**
- `file_path`: Path to the file to write
- `content`: Content to write
- `overwrite`: Whether to overwrite existing files (default: False)

### FileDeleteTool

Delete files and directories safely.

```python
from crewai_fs_plus import FileDeleteTool

# Delete a file
deleter = FileDeleteTool()
result = deleter._run(path="temp_file.txt")

# Delete a non-empty directory
result = deleter._run(
    path="temp_directory",
    recursive=True
)

# With sandboxing - only allow deletion in temp directories
deleter = FileDeleteTool(
    base_directory="/app",
    whitelist=["temp/**", "cache/**"],
    blacklist=["**/.git/**"]
)
```

**Parameters:**
- `path`: Path to the file or directory to delete
- `recursive`: Delete directories recursively (default: False)

### DirectoryReadTool

List directory contents with filtering.

```python
from crewai_fs_plus import DirectoryReadTool

# List all files
reader = DirectoryReadTool()
files = reader._run(directory="/path/to/dir")

# Non-recursive listing
files = reader._run(
    directory="/path/to/dir",
    recursive=False
)

# Only show Python files, exclude tests
reader = DirectoryReadTool(
    whitelist=["*.py"],
    blacklist=["test_*", "*_test.py"]
)
```

**Parameters:**
- `directory`: Path to the directory to list
- `recursive`: List contents recursively (default: True)

## Configuration

### Base Directory (Sandboxing)

The `base_directory` parameter creates a sandbox that prevents access outside of the specified directory:

```python
tool = FileReadTool(base_directory="/app/data")

# This works - path is within sandbox
tool._run(file_path="documents/file.txt")

# This fails - path is outside sandbox
tool._run(file_path="/etc/passwd")

# This fails - path escape attempt
tool._run(file_path="../../../etc/passwd")
```

### Whitelist

The `whitelist` parameter restricts access to paths matching the specified glob patterns. If the whitelist is empty (default), all paths are allowed.

```python
tool = FileReadTool(whitelist=["*.py", "*.md", "docs/**"])

# Allowed
tool._run(file_path="script.py")
tool._run(file_path="docs/guide.md")

# Blocked
tool._run(file_path="data.json")
```

### Blacklist

The `blacklist` parameter denies access to paths matching the specified glob patterns. Blacklist takes precedence over whitelist.

```python
tool = FileReadTool(blacklist=["*secret*", "*.env", "**/.git/**"])

# Blocked
tool._run(file_path="secret_config.txt")
tool._run(file_path=".env")

# Allowed
tool._run(file_path="config.txt")
```

### Combined Example

```python
from crewai_fs_plus import FileReadTool, FileWriteTool, FileDeleteTool

# Secure file reader for a web application
reader = FileReadTool(
    base_directory="/app",
    whitelist=["*.py", "*.html", "*.css", "*.js", "templates/**", "static/**"],
    blacklist=["**/secret*", "**/.env", "**/credentials*", "**/*.key"]
)

# Writer restricted to output and logs
writer = FileWriteTool(
    base_directory="/app",
    whitelist=["output/**", "logs/**", "tmp/**"]
)

# Deleter for temporary files only
deleter = FileDeleteTool(
    base_directory="/app",
    whitelist=["tmp/**", "cache/**"],
    blacklist=["**/.git/**", "**/node_modules/**"]
)
```

## Glob Pattern Reference

| Pattern | Matches |
|---------|---------|
| `*.txt` | All .txt files |
| `*.py` | All Python files |
| `docs/*` | Files directly in docs/ |
| `docs/**` | All files in docs/ recursively |
| `**/test_*` | test_ files in any directory |
| `**/*.log` | .log files in any directory |
| `*secret*` | Files containing "secret" |

## Error Handling

The tools return error messages as strings rather than raising exceptions:

```python
result = reader._run(file_path="nonexistent.txt")
# Returns: "Error: File not found: nonexistent.txt"

result = reader._run(file_path="../../../etc/passwd")
# Returns: "Error: Path '/etc/passwd' is outside the sandbox directory '/app'"

result = reader._run(file_path="secret.txt")
# Returns: "Error: Path matches blacklist pattern: /app/secret.txt"
```

For programmatic error handling, you can check if the result starts with "Error:":

```python
result = reader._run(file_path="file.txt")
if result.startswith("Error"):
    print(f"Operation failed: {result}")
else:
    print(f"Content: {result}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/MaxGfeller/crewai-fs-plus.git
cd crewai-fs-plus

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Running Tests with Coverage

```bash
pytest --cov=crewai_fs_plus --cov-report=html
```

## License

MIT License - see [LICENSE](LICENSE) for details.
