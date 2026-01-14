# ymliu-tool

A simple utility tool by ymliu.

## Installation

```bash
pip install ymliu-tool
```

## Usage

### Echo command

```bash
ymliu-tool echo "Hello, World!"
# Output: Hello, World!
```

### Square command

```bash
ymliu-tool square 5
# Output: 5² = 25
```

### Sum command

```bash
ymliu-tool sum 1 2 3 4 5
# Output: Sum: 15
```

### Info command

```bash
ymliu-tool info
# Output: ymliu-tool v0.1.0
#         A simple utility tool by ymliu
```

## Development

```bash
# Clone the repository
git clone https://github.com/ymliu/ymliu-tool.git
cd ymliu-tool

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## License

MIT

