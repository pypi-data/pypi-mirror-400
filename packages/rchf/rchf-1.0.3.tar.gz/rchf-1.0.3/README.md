# rchf 🌈

**Custom Rich Help Formatter** - A beautifully styled argparse formatter with rich formatting and multi-config support

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![PyPI Version](https://img.shields.io/pypi/v/rchf.svg)
![Downloads](https://img.shields.io/pypi/dm/rchf.svg)

✨ **Make your CLI help beautiful with rich formatting** ✨

</div>

[![Screenshot](https://raw.githubusercontent.com/cumulus13/rchf/master/screenshot.png)](https://raw.githubusercontent.com/cumulus13/rchf/master/rchf.png)

## 📋 Features

- 🎨 **Rich Terminal Formatting**: Beautiful syntax highlighting for code examples
- 🎯 **Customizable Styles**: Configure colors and styles via environment variables
- 📁 **Multi-Format Config Support**: `.env`, `.ini`, `.toml`, `.json`, `.yml`
- 🖥️ **Cross-Platform**: Works on Windows, macOS, and Linux
- 🔧 **Easy Integration**: Drop-in replacement for argparse formatters
- 📝 **Smart Code Detection**: Automatically detects and formats code blocks
- 🎪 **Flexible Styling**: Customize every aspect of your help output

## 🚀 Quick Start

### Installation

```bash
pip install rchf
```

### Basic Usage

```python
#!/usr/bin/env python3

import argparse
from rchf import CustomRichHelpFormatter

parser = argparse.ArgumentParser(
    description="My Awesome CLI Tool",
    formatter_class=CustomRichHelpFormatter,
    epilog="""
Examples:
  python myapp.py process --input data.txt --output results.json
  python myapp.py validate --config config.toml --verbose
""",
)

parser.add_argument("command", help="Command to execute")
parser.add_argument("--input", "-i", help="Input file path")
parser.add_argument("--output", "-o", help="Output file path")
parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose mode")

args = parser.parse_args()
```

## 🎨 Customization

### Environment Variables

Customize colors and styles using environment variables:

```bash
# Set in your shell or .env file
export RCHF_ARGS="bold cyan"
export RCHF_GROUPS="magenta"
export RCHF_HELP="bold green"
export RCHF_METAVAR="bold yellow"
export RCHF_SYNTAX="underline"
export RCHF_TEXT="white"
export RCHF_PROG="bold blue italic"
export RCHF_DEFAULT="bold"
```

### Configuration Files

`rchf` automatically looks for configuration in multiple locations and formats:

1. **Priority Order** (Unix/macOS):
   - `~/.rchf/.env`
   - `~/.config/.rchf/.env`
   - `~/.config/.env`
   - `~/.rchf/rchf.ini/.toml/.json/.yml`
   - `~/.config/.rchf/rchf.ini/.toml/.json/.yml`
   - `~/.config/rchf.ini/.toml/.json/.yml`

2. **Priority Order** (Windows):
   - `%USERPROFILE%/.rchf/.env`
   - `%APPDATA%/.rchf/rchf.ini/.toml/.json/.yml`
   - `%USERPROFILE%/.rchf/rchf.ini/.toml/.json/.yml`

### Example Configuration Files

**.env file:**
```ini
RCHF_ARGS=bold #FFFF00
RCHF_GROUPS=#AA55FF
RCHF_HELP=bold #00FFFF
RCHF_METAVAR=bold #FF55FF
RCHF_SYNTAX=underline
RCHF_TEXT=white
RCHF_PROG=bold #00AAFF italic
RCHF_DEFAULT=bold
```

**TOML file:**
```toml
RCHF_ARGS = "bold #FFFF00"
RCHF_GROUPS = "#AA55FF"
RCHF_HELP = "bold #00FFFF"
RCHF_METAVAR = "bold #FF55FF"
RCHF_SYNTAX = "underline"
RCHF_TEXT = "white"
RCHF_PROG = "bold #00AAFF italic"
RCHF_DEFAULT = "bold"
```

**YAML file:**
```yaml
RCHF_ARGS: "bold #FFFF00"
RCHF_GROUPS: "#AA55FF"
RCHF_HELP: "bold #00FFFF"
RCHF_METAVAR: "bold #FF55FF"
RCHF_SYNTAX: "underline"
RCHF_TEXT: "white"
RCHF_PROG: "bold #00AAFF italic"
RCHF_DEFAULT: "bold"
```

## 📚 Advanced Usage

### Custom Epilog with Code Examples

```python
from rchf import CustomRichHelpFormatter

parser = argparse.ArgumentParser(
    formatter_class=lambda prog: CustomRichHelpFormatter(
        prog,
        epilog="""
Getting Started:

  Create a configuration file:

    $ echo 'RCHF_ARGS="bold cyan"' > ~/.rchf/.env

  Run your application:

    python app.py --help

  You'll see beautifully formatted help with syntax highlighting!

Advanced Examples:

  python app.py process \\
    --input large_dataset.csv \\
    --output processed_results.json \\
    --verbose

  python app.py analyze \\
    --config analysis_config.toml \\
    --threads 4 \\
    --batch-size 1000

Troubleshooting:

  If colors don't appear, ensure your terminal supports 256 colors.
  Set FORCE_COLOR=1 to force color output.
""",
    )
)
```

### Programmatic Style Customization

```python
from rchf import CustomRichHelpFormatter

class MyCustomFormatter(CustomRichHelpFormatter):
    styles = {
        "argparse.args": "bold #FF9900",  # Orange
        "argparse.groups": "#66CCFF",     # Light Blue
        "argparse.help": "italic #33FF33", # Green
        "argparse.metavar": "bold #FF66FF", # Pink
        "argparse.syntax": "bold",
        "argparse.text": "#CCCCCC",       # Light Gray
        "argparse.prog": "bold #FFFFFF",  # White
        "argparse.default": "italic",
    }
```

## 📁 Project Structure

```
rchf/
├── rchf/
│   ├── __init__.py          # Main implementation
│   └── demo.py              # Example/demo script
├── tests/                   # Test suite
├── pyproject.toml          # Build configuration
├── README.md               # This file
└── LICENSE                 # MIT License
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/cumulus13/rchf.git
cd rchf

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checking
mypy rchf/

# Format code
black rchf/
isort rchf/
ruff check --fix rchf/
```

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=rchf --cov-report=html

# Run specific test file
pytest tests/test_formatter.py -v
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of the amazing [rich](https://github.com/Textualize/rich) library
- Inspired by [rich-argparse](https://github.com/hamdanal/rich-argparse)
- Uses [envdot](https://github.com/cumulus13/envdot) for configuration loading

## 🙎 Author

[Hadi Cahyadi](mailto:cumulus13@gmail.com)
- **Issues**: [GitHub Issues](https://github.com/cumulus13/rchf/issues)
- **Email**: cumulus13@gmail.com    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

---

<div align="center">

Made with ❤️ by [Hadi Cahyadi](https://github.com/cumulus13)

</div>
```

## Notes:

1. **Package Name**: I used `rchf` (lowercase) as the package name, matching your directory structure.

2. **Dependencies**: Included `rich`, `rich-argparse`, and `envdot` based on your imports.

3. **Development Dependencies**: Added common dev tools (pytest, black, mypy, ruff, isort).

4. **Demo Script**: Added a script entry point `rchf-demo` that would point to a demo module.

5. **Configuration**: The README explains the multi-format config file support that your code implements.

6. **Styling**: Showcased how to customize styles via environment variables and different config formats.

7. **Icon**: Used 🌈 emoji in the title as an icon representing colorful/rich formatting.

You might want to create a `rchf/demo.py` file to provide an example/demo script that shows the formatter in action.