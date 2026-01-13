"""
Command-line interface for json2toon.
"""
import json
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from .core import json_to_toon, toon_to_json, get_conversion_stats
from .config import get_default_config, load_config

app = typer.Typer(
    name="json2toon",
    help="Convert between JSON and TOON formats"
)
console = Console()


@app.command("to-toon")
def cli_json_to_toon(
    input_file: Path = typer.Argument(
        ...,
        help="Input JSON file"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output TOON file (default: stdout)"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file"
    ),
    pretty: bool = typer.Option(
        False,
        "--pretty",
        "-p",
        help="Pretty-print output with syntax highlighting"
    )
) -> None:
    """
    Convert JSON file to TOON format.
    """
    try:
        # Load config
        config = (
            load_config(config_file)
            if config_file
            else get_default_config()
        )
        
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert
        toon_output = json_to_toon(data, config)
        
        # Output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(toon_output)
            console.print(
                f"[green]OK[/green] Converted to {output_file}"
            )
        else:
            if pretty:
                syntax = Syntax(
                    toon_output,
                    "yaml",
                    theme="monokai",
                    line_numbers=True
                )
                console.print(syntax)
            else:
                console.print(toon_output)
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("to-json")
def cli_toon_to_json(
    input_file: Path = typer.Argument(
        ...,
        help="Input TOON file"
    ),
    output_file: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output JSON file (default: stdout)"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file"
    ),
    pretty: bool = typer.Option(
        True,
        "--pretty/--no-pretty",
        "-p/-P",
        help="Pretty-print JSON output"
    )
) -> None:
    """
    Convert TOON file to JSON format.
    """
    try:
        # Load config
        config = (
            load_config(config_file)
            if config_file
            else get_default_config()
        )
        
        # Read input
        with open(input_file, 'r', encoding='utf-8-sig') as f:
            toon_content = f.read()
        
        # Convert
        data = toon_to_json(toon_content, config)
        
        # Format JSON
        json_output = json.dumps(
            data,
            indent=2 if pretty else None
        )
        
        # Output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            console.print(
                f"[green]OK[/green] Converted to {output_file}"
            )
        else:
            if pretty:
                syntax = Syntax(
                    json_output,
                    "json",
                    theme="monokai",
                    line_numbers=True
                )
                console.print(syntax)
            else:
                console.print(json_output)
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("report")
def cli_report(
    input_file: Path = typer.Argument(
        ...,
        help="Input JSON file"
    ),
    config_file: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file"
    ),
    format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format: table, text, json, markdown"
    )
) -> None:
    """
    Generate token comparison report.
    """
    try:
        # Load config
        config = (
            load_config(config_file)
            if config_file
            else get_default_config()
        )
        
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get stats
        stats = get_conversion_stats(data, config, format)
        
        # Display
        if format == "table":
            table = Table(title="Token Comparison Report")
            table.add_column("Format", style="cyan")
            table.add_column("Tokens", justify="right", style="magenta")
            
            table.add_row("JSON", str(stats["json_tokens"]))
            table.add_row("TOON", str(stats["toon_tokens"]))
            table.add_row(
                "Savings",
                f"{stats['savings']} "
                f"({stats['savings_percent']:.1f}%)",
                style="green"
            )
            
            console.print(table)
        else:
            console.print(stats["report"])
    
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
