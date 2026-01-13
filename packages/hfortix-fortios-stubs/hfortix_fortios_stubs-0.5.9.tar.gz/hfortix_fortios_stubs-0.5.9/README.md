# hfortix-fortios-stubs

Type stubs for the `hfortix-fortios` package - providing comprehensive type hints for FortiOS API interactions.

## What are type stubs?

Type stubs (`.pyi` files) provide type information for Python code, enabling:
- **Better IDE autocomplete and IntelliSense** - Get accurate suggestions while coding
- **Static type checking** - Catch errors before runtime with tools like mypy, pyright, and pylance
- **Enhanced documentation** - See parameter types and return values directly in your IDE
- **Improved code quality** - Write safer, more maintainable code with type safety

## Installation

### Automatic Installation (Recommended)

This package is automatically installed when you install `hfortix-fortios`:

```bash
pip install hfortix-fortios
```

### Manual Installation

If you need to install the stubs separately:

```bash
pip install hfortix-fortios-stubs
```

## Usage

No additional setup required. Once installed, your IDE and type checkers will automatically discover and use these stubs.

### Example

```python
from hfortix_fortios import FortiOSClient

# Your IDE will now provide accurate type hints and autocomplete
client = FortiOSClient(host="192.168.1.1", api_key="your-api-key")

# Full type safety for all API operations
policy = client.cmdb.firewall.policy.get(policyid=1)
```

## Compatibility

This package must match the version of `hfortix-fortios` you're using:
- `hfortix-fortios-stubs==0.5.4` → `hfortix-fortios==0.5.4`

## What's Included

Type stubs for all FortiOS API endpoints:
- **CMDB** (Configuration Management Database) - 886+ endpoints
- **Monitor** - 295+ endpoints  
- **Service** - Service-related endpoints
- **Log** - 38+ logging endpoints

Each endpoint includes complete type information for:
- Request parameters
- Response models
- Query filters
- Pydantic models with validation

## Benefits

### For IDEs
- PyCharm, VSCode, and other editors get full IntelliSense support
- Instant parameter hints and documentation
- Jump-to-definition for all API methods

### For Type Checkers
- mypy, pyright, and pylance can verify your code
- Catch type errors before runtime
- Ensure API calls use correct parameters

### For Developers
- Faster development with accurate autocomplete
- Fewer bugs through static type checking
- Better code documentation and maintainability

## Requirements

- Python 3.10 or higher
- Compatible with `hfortix-fortios` version 0.5.4

## License

MIT License - Free to use in open source and commercial projects

## Links

- [Documentation](https://hfortix.readthedocs.io)
- [GitHub Repository](https://github.com/hermanwjacobsen/hfortix)
- [Issue Tracker](https://github.com/hermanwjacobsen/hfortix/issues)
- [PyPI - hfortix-fortios](https://pypi.org/project/hfortix-fortios/)

## Contributing

Issues and pull requests are welcome! Please see the main repository for contribution guidelines.
