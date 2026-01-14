#!/usr/bin/env python3

# File: rchf/demo.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-09
# Description: Demo script for rchf (Custom Rich Help Formatter).
# License: MIT

"""
Demo script for rchf (Custom Rich Help Formatter).

This demonstrates the features and customization options of the CustomRichHelpFormatter.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Import the formatter from the package
try:
    from . import CustomRichHelpFormatter
except:
    from rchf import CustomRichHelpFormatter  # type: ignore


def create_advanced_parser() -> argparse.ArgumentParser:
    """
    Create an advanced parser demonstrating various rchf features.
    """
    epilog_text = """
🎨 **Color Customization Examples**:

  You can customize colors via environment variables or config files:

  Export in shell:
    export RCHF_ARGS="bold cyan"
    export RCHF_HELP="bold green"
    export RCHF_METAVAR="bold yellow"

  Or create ~/.rchf/.env:
    RCHF_ARGS=bold #FFFF00
    RCHF_GROUPS=#AA55FF
    RCHF_HELP=bold #00FFFF

🔄 **Configuration File Support**:

  rchf automatically looks for configs in:
    • ~/.rchf/.env / .ini / .toml / .json / .yml
    • ~/.config/.rchf/.env / .ini / .toml / .json / .yml
    • ~/.config/.env / .ini / .toml / .json / .yml

  (On Windows: %USERPROFILE%/.rchf/ and %APPDATA%/.rchf/)

📚 **Code Example Detection**:

  The formatter automatically detects and beautifully formats code blocks:

  Basic usage:
    $ python script.py --input data.txt --output results.json

  With options:
    $ python script.py process \\
        --config settings.toml \\
        --verbose \\
        --threads 4

  Piped operations:
    $ cat data.csv | python script.py transform --format json > output.json

🔧 **Advanced Examples**:

  1. Process multiple files:
     python script.py batch-process \\
       --input-files "data/*.csv" \\
       --output-dir ./results \\
       --compress \\
       --parallel

  2. Database operations:
     python script.py db-query \\
       --host localhost \\
       --port 5432 \\
       --database mydb \\
       --query "SELECT * FROM users" \\
       --format csv

  3. API interactions:
     python script.py api-call \\
       --endpoint "https://api.example.com/v1/data" \\
       --method POST \\
       --headers '{"Authorization": "Bearer token"}' \\
       --body '{"query": "test"}'

⚠️  **Troubleshooting**:

  If colors don't appear:
    • Check terminal color support: echo $TERM
    • Force colors: export FORCE_COLOR=1
    • Enable TrueColor: export COLORTERM=truecolor

  Debug configuration loading:
    python -c "from rchf import get_config_file; print('Config:', get_config_file())"
"""

    # Create parser with CustomRichHelpFormatter
    parser = argparse.ArgumentParser(
        prog="rchf-demo",
        description="""
        🌈 **Custom Rich Help Formatter Demo**

        A demonstration of beautiful, customizable CLI help formatting.
        This tool showcases the advanced features of rchf including
        syntax highlighting, multi-format config support, and smart
        code detection.
        """,
        epilog=epilog_text,
        formatter_class=lambda prog: CustomRichHelpFormatter(
            prog,
            epilog=epilog_text,
            width=90,  # Control width for better readability
            max_help_position=30,  # Align help text nicely
            indent_increment=2,
        ),
        add_help=False,  # We'll add help manually to control formatting
    )

    # Add help option with custom formatting
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit",
    )

    # Main command group
    parser.add_argument(
        "command",
        nargs="?",
        default="show",
        choices=["show", "config", "colors", "demo", "export"],
        help="Command to execute (default: %(default)s)",
    )

    # Action arguments
    action_group = parser.add_argument_group(
        "Action Options", "Control what the demo shows"
    )
    action_group.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)",
    )
    action_group.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress non-essential output",
    )
    action_group.add_argument(
        "--force-color",
        action="store_true",
        help="Force color output even if not in terminal",
    )

    # Display arguments
    display_group = parser.add_argument_group(
        "Display Options", "Control how output is displayed"
    )
    display_group.add_argument(
        "--width",
        type=int,
        default=None,
        help="Set output width (default: auto-detect)",
    )
    display_group.add_argument(
        "--no-wrap",
        action="store_true",
        help="Disable text wrapping",
    )
    display_group.add_argument(
        "--theme",
        default="fruity",
        choices=["fruity", "monokai", "vim", "native", "tango"],
        help="Syntax highlighting theme (default: %(default)s)",
    )

    # Configuration arguments
    config_group = parser.add_argument_group(
        "Configuration", "Manage rchf configuration"
    )
    config_group.add_argument(
        "--config-file",
        type=Path,
        help="Use specific configuration file",
    )
    config_group.add_argument(
        "--show-config",
        action="store_true",
        help="Show loaded configuration",
    )
    config_group.add_argument(
        "--create-config",
        action="store_true",
        help="Create example configuration file",
    )

    # Export arguments
    export_group = parser.add_argument_group(
        "Export Options", "Export configuration and examples"
    )
    export_group.add_argument(
        "--export-env",
        action="store_true",
        help="Export current settings as .env file",
    )
    export_group.add_argument(
        "--export-toml",
        action="store_true",
        help="Export current settings as TOML file",
    )
    export_group.add_argument(
        "--export-json",
        action="store_true",
        help="Export current settings as JSON file",
    )
    export_group.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for exports",
    )

    return parser


def show_current_styles() -> None:
    """Display current style configuration."""
    from rich.console import Console
    from rich.table import Table
    from rich import box

    console = Console()

    # Create a table showing current styles
    table = Table(
        title="Current rchf Style Configuration",
        box=box.ROUNDED,
        header_style="bold magenta",
        title_style="bold cyan",
    )

    table.add_column("Style Key", style="bold yellow", width=20)
    table.add_column("Environment Variable", style="dim", width=25)
    table.add_column("Current Value", style="green", width=40)
    table.add_column("Preview", style="bold", width=30)

    # Style definitions
    styles = {
        "argparse.args": ("RCHF_ARGS", "bold #FFFF00", "--argument"),
        "argparse.groups": ("RCHF_GROUPS", "#AA55FF", "Group Title"),
        "argparse.help": ("RCHF_HELP", "bold #00FFFF", "Help text"),
        "argparse.metavar": ("RCHF_METAVAR", "bold #FF55FF", "METAVAR"),
        "argparse.syntax": ("RCHF_SYNTAX", "underline", "underline text"),
        "argparse.text": ("RCHF_TEXT", "white", "Normal text"),
        "argparse.prog": ("RCHF_PROG", "bold #00AAFF italic", "program-name"),
        "argparse.default": ("RCHF_DEFAULT", "bold", "(default: value)"),
    }

    for key, (env_var, default_value, preview) in styles.items():
        # Get actual value from environment or use default
        import os

        actual_value = os.getenv(env_var, default_value)
        table.add_row(key, env_var, actual_value, preview)

    console.print(table)
    console.print("\n💡 Tip: Set these variables in your shell or config file to customize colors!\n")


def show_config_locations() -> None:
    """Display configuration file search locations."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax

    console = Console()

    # Show config search paths
    config_code = """# rchf Configuration File Search Order:

## Unix/macOS:
1. ~/.rchf/.env
2. ~/.config/.rchf/.env
3. ~/.config/.env
4. ~/.rchf/rchf.ini/.toml/.json/.yml
5. ~/.config/.rchf/rchf.ini/.toml/.json/.yml
6. ~/.config/rchf.ini/.toml/.json/.yml

## Windows:
1. %USERPROFILE%/.rchf/.env
2. %APPDATA%/.rchf/rchf.ini/.toml/.json/.yml
3. %USERPROFILE%/.rchf/rchf.ini/.toml/.json/.yml

## Current detected config file:"""
    
    # Import here to avoid circular imports
    from rchf import get_config_file
    
    config_file = get_config_file()
    config_code += f"\n{config_file}"
    
    console.print(
        Panel.fit(
            Syntax(config_code, "bash", theme="fruity"),
            title="📁 Configuration Files",
            border_style="blue",
        )
    )


def create_example_config(output_file: Optional[Path] = None) -> None:
    """Create example configuration files."""
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    if not output_file:
        output_file = Path.home() / ".rchf" / ".env"
        output_file.parent.mkdir(parents=True, exist_ok=True)

    env_content = """# rchf Configuration File
# Customize your CLI help colors and styles

# Argument names (e.g., --help, --version)
RCHF_ARGS=bold #FFFF00

# Group titles
RCHF_GROUPS=#AA55FF

# Help text
RCHF_HELP=bold #00FFFF

# Metavars (e.g., FILE, DIR)
RCHF_METAVAR=bold #FF55FF

# Syntax elements
RCHF_SYNTAX=underline

# Regular text
RCHF_TEXT=white

# Program name
RCHF_PROG=bold #00AAFF italic

# Default values
RCHF_DEFAULT=bold

# Available color formats:
# • Named colors: red, green, blue, cyan, magenta, yellow, white
# • Hex colors: #FF0000, #00FF00, #0000FF
# • RGB colors: rgb(255,0,0)
# • Styles: bold, italic, underline, blink, reverse, conceal
"""

    output_file.write_text(env_content)
    console.print(f"[green]✓[/green] Created example config at: {output_file}")
    console.print("[yellow]📝 Reload your shell or restart terminal to apply changes[/yellow]")


def export_config(format: str, output: Optional[Path] = None) -> None:
    """Export configuration in different formats."""
    from rich.console import Console
    import json
    import os

    console = Console()

    # Collect current settings
    settings = {}
    env_vars = [
        "RCHF_ARGS",
        "RCHF_GROUPS",
        "RCHF_HELP",
        "RCHF_METAVAR",
        "RCHF_SYNTAX",
        "RCHF_TEXT",
        "RCHF_PROG",
        "RCHF_DEFAULT",
    ]

    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            settings[var] = value

    if format == "env":
        content = "\n".join(f"{key}={value}" for key, value in settings.items())
        extension = ".env"
    elif format == "toml":
        content = "# rchf Configuration\n\n"
        content += "\n".join(f'{key} = "{value}"' for key, value in settings.items())
        extension = ".toml"
    elif format == "json":
        content = json.dumps(settings, indent=2)
        extension = ".json"
    else:
        console.print(f"[red]Error: Unknown format '{format}'[/red]")
        return

    if output:
        output_file = output
    else:
        output_file = Path.cwd() / f"rchf-config{extension}"

    output_file.write_text(content)
    console.print(f"[green]✓[/green] Exported {format.upper()} config to: {output_file}")


def main() -> None:
    """Main entry point for the demo."""
    parser = create_advanced_parser()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        sys.argv.append("--help")
    
    try:
        args = parser.parse_args()
    except SystemExit:
        # Help was shown, exit cleanly
        return

    from rich.console import Console
    console = Console()

    # Execute command
    if args.command == "show":
        show_current_styles()
        
        if args.verbose:
            show_config_locations()
            
            if args.verbose > 1:
                console.print("\n[bold cyan]Debug Information:[/bold cyan]")
                console.print(f"Python: {sys.version}")
                console.print(f"Platform: {sys.platform}")
                
    elif args.command == "config":
        show_config_locations()
        
        if args.show_config:
            from rchf import get_config_file
            config_file = get_config_file()
            if config_file.exists():
                console.print(f"\n[bold]Config file content:[/bold]")
                console.print(Syntax(config_file.read_text(), "ini", theme=args.theme))
            else:
                console.print(f"[yellow]Config file not found: {config_file}[/yellow]")
                
        if args.create_config:
            create_example_config(args.config_file)
            
    elif args.command == "colors":
        from rich.text import Text
        
        console.print("\n[bold cyan]Available Color Examples:[/bold cyan]\n")
        
        # Show color examples
        colors = [
            ("#FFFF00", "Yellow (RCHF_ARGS)"),
            ("#AA55FF", "Purple (RCHF_GROUPS)"),
            ("#00FFFF", "Cyan (RCHF_HELP)"),
            ("#FF55FF", "Pink (RCHF_METAVAR)"),
            ("#00AAFF", "Blue (RCHF_PROG)"),
            ("white", "White (RCHF_TEXT)"),
        ]
        
        for color, description in colors:
            text = Text(f"  ■ {description}", style=color)
            console.print(text)
            
        console.print("\n[yellow]💡 Tip: Use hex codes (#RRGGBB) or named colors[/yellow]")
        
    elif args.command == "demo":
        # Show a demo of the formatter with various features
        console.print("[bold green]🚀 Running rchf formatter demo...[/bold green]\n")
        
        # Create and show a simple parser
        demo_parser = argparse.ArgumentParser(
            prog="demo-tool",
            description="A demonstration of rchf features",
            formatter_class=CustomRichHelpFormatter,
            epilog="""
Examples with code highlighting:

  Basic usage:
    $ demo-tool --input file.txt --output result.json

  Advanced processing:
    $ demo-tool process \\
        --config config.yaml \\
        --workers 8 \\
        --timeout 30s \\
        --retry 3

  Pipeline example:
    $ cat logfile.txt | demo-tool filter --level ERROR | demo-tool format --json
            """,
        )
        
        demo_parser.add_argument("--input", "-i", help="Input file path")
        demo_parser.add_argument("--output", "-o", help="Output file path")
        demo_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        demo_parser.add_argument("--config", type=Path, help="Configuration file")
        
        # Show the help
        demo_parser.print_help()
        
    elif args.command == "export":
        if args.export_env:
            export_config("env", args.output)
        elif args.export_toml:
            export_config("toml", args.output)
        elif args.export_json:
            export_config("json", args.output)
        else:
            console.print("[yellow]Please specify export format (--export-env, --export-toml, --export-json)[/yellow]")
    
    # Show footer if not quiet
    if not args.quiet:
        console.print("\n" + "═" * 60)
        console.print("[bold cyan]✨ rchf Demo Complete![/bold cyan]")
        console.print("[dim]Learn more: https://github.com/cumulus13/rchf[/dim]")
        console.print("[dim]Report issues: https://github.com/cumulus13/rchf/issues[/dim]")


if __name__ == "__main__":
    main()