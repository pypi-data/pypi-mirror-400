#!/usr/bin/env python3

# File: rchf/rchf/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-01-07
# Description: A beautifully styled argparse formatter with rich formatting and multi-config support
# License: MIT

from rich_argparse import RawDescriptionRichHelpFormatter, _lazy_rich as rr#, RichHelpFormatter
from typing import ClassVar
from rich.syntax import Syntax
import argparse
import os
import sys
from envdot import load_env  # type: ignore
from pathlib import Path  # type: ignore

def get_config_file():
    config_file = None
    if sys.platform == 'win32':
        config_file_list = [
            Path(os.path.expandvars('%USERPROFILE%')) / '.rchf' / Path('.env'),

            Path(os.path.expandvars('%APPDATA%')) / '.rchf' / f"{Path(__file__).stem}.ini",
            Path(os.path.expandvars('%USERPROFILE%')) / '.rchf' / f"{Path(__file__).stem}.ini",

            Path(os.path.expandvars('%APPDATA%')) / '.rchf' / f"{Path(__file__).stem}.toml",
            Path(os.path.expandvars('%USERPROFILE%')) / '.rchf' / f"{Path(__file__).stem}.toml",

            Path(os.path.expandvars('%APPDATA%')) / '.rchf' / f"{Path(__file__).stem}.json",
            Path(os.path.expandvars('%USERPROFILE%')) / '.rchf' / f"{Path(__file__).stem}.json",

            Path(os.path.expandvars('%APPDATA%')) / '.rchf' / f"{Path(__file__).stem}.yml",
            Path(os.path.expandvars('%USERPROFILE%')) / '.rchf' / f"{Path(__file__).stem}.yml",

        ]
    else:    
        config_file_list = [
            Path(os.path.expanduser('~')) / '.rchf' / Path('.env'),
            Path(os.path.expanduser('~')) / '.config' / '.rchf' / Path('.env'),
            Path(os.path.expanduser('~')) / '.config' / Path('.env'),

            Path(os.path.expanduser('~')) / '.rchf' / f"{Path(__file__).stem}.ini",
            Path(os.path.expanduser('~')) / '.config' / '.rchf' / f"{Path(__file__).stem}.ini",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.ini",
            
            Path(os.path.expanduser('~')) / '.rchf' / f"{Path(__file__).stem}.toml",
            Path(os.path.expanduser('~')) / '.config' / '.rchf' / f"{Path(__file__).stem}.toml",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.toml",
            
            Path(os.path.expanduser('~')) / '.rchf' / f"{Path(__file__).stem}.json",
            Path(os.path.expanduser('~')) / '.config' / '.rchf' / f"{Path(__file__).stem}.json",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.json",
            
            Path(os.path.expanduser('~')) / '.rchf' / f"{Path(__file__).stem}.yml",
            Path(os.path.expanduser('~')) / '.config' / '.rchf' / f"{Path(__file__).stem}.yml",
            Path(os.path.expanduser('~')) / '.config' / f"{Path(__file__).stem}.yml",
            
            ]
    for cf in config_file_list:
        if cf.is_file():
            config_file = cf
            break
        
    if config_file and not config_file.parent.is_dir():
        config_file.parent.mkdir(parents=True, exist_ok=True)

    config_file = config_file or Path(__file__).parent / Path('.env')

    return config_file

load_env(get_config_file())

class CustomRichHelpFormatter(RawDescriptionRichHelpFormatter):
    """A custom argparse:formatter_class with modified styles."""

    def __init__(self, prog, epilog=None, width=None, max_help_position=24, indent_increment=2):
        super().__init__(prog)
        if epilog is not None:
            self.epilog = epilog
        if width is not None:
            self.width = width
        self._max_help_position = max_help_position
        self._indent_increment = indent_increment
        
    styles: ClassVar[dict[str, rr.StyleType]] = {
        "argparse.args": os.getenv("RCHF_ARGS", "bold #FFFF00"),  # Changed from cyan
        "argparse.groups": os.getenv("RCHF_GROUPS", "#AA55FF"),   # Changed from dark_orange
        "argparse.help": os.getenv("RCHF_HELP", "bold #00FFFF"),    # Changed from default
        "argparse.metavar": os.getenv("RCHF_METAVAR", "bold #FF55FF"), # Changed from dark_cyan
        "argparse.syntax": os.getenv("RCHF_SYNTAX", "underline"), # Changed from bold
        "argparse.text": os.getenv("RCHF_TEXT", "white"),   # Changed from default
        "argparse.prog": os.getenv("RCHF_PROG", "bold #00AAFF italic"),     # Changed from grey50
        "argparse.default": os.getenv("RCHF_DEFAULT", "bold"), # Changed from italic
    }
    
    def format_help(self):
        help_text = super().format_help()
        # Add a newline in front of the usage if not there
        if not help_text.lstrip().startswith("Usage:"):
            # Cari posisi Usage
            idx = help_text.find("Usage:")
            if idx > 0:
                help_text = help_text[:idx] + "\n" + help_text[idx:]
            elif idx == 0:
                help_text = "\n" + help_text
        elif not help_text.startswith("\n"):
            help_text = "\n" + help_text
        return help_text
    
    def _rich_fill_text(self, text: rr.Text, width: int, indent: rr.Text) -> rr.Text:
        # Split per baris, pertahankan baris kosong
        lines = text.plain.splitlines()
        return rr.Text("\n").join(
            indent + rr.Text(line, style=text.style) for line in lines
        ) + "\n\n"
        
    def add_text(self, text):
        if text is argparse.SUPPRESS or text is None:
            return
        if isinstance(text, str):
            lines = text.strip().splitlines()
            indent = " " * getattr(self, "_current_indent", 2)
            if len(indent) < 2:
                indent = " " * 2
            # Detection: If all rows are commands (python, $, or spaces), display all as syntax
            is_all_code = all(
                l.strip().startswith(("python", "$")) or l.startswith("  ") for l in lines if l.strip()
            )
            # print(f"Detected all code: {is_all_code}, lines: {lines}")
            if len(lines) > 0 and (is_all_code or len(lines) > 1):
                # If there is a title (the first line is not an order), display the title
                if len(lines) > 1 and not (lines[0].strip().startswith(("python", "$")) or lines[0].startswith("  ")):
                    # print(f"Adding title: {lines[0]}")
                    self.add_renderable(rr.Text(lines[0], style="#007F74 bold"))
                    code_lines = lines[1:]
                else:
                    # print("No title detected, using all lines as code.")
                    code_lines = lines
                # Add indentation to all line code
                code = "\n".join(f"{indent}{l.strip()}" for l in code_lines)
                if code.strip():
                    self.add_renderable(
                        Syntax(code, "bash", theme="fruity", line_numbers=False)
                    )
                return
            else:
                text = rr.Text(text, style=self.styles["argparse.text"])
        super().add_text(text)  # type: ignore
