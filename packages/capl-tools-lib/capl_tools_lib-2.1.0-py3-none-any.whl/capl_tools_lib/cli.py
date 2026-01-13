import typer
from toon import encode as toon_encode
from enum import Enum
from pathlib import Path
from typing import Optional, Any
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import your internal logic
from capl_tools_lib.processor import CaplProcessor

def _project_element(el: Any, include_lines: bool = False) -> dict:
    """
    Projects the element data into a dictionary. 
    Following SRP: The CLI handles presentation filtering.
    """
    data = el.to_dict()
    if not include_lines:
        # Strip physical location data for a 'clean' logical view
        data.pop("start_line", None)
        data.pop("end_line", None)
    return data

class ElementType(str, Enum):
    TestCase = "TestCase"
    Function = "Function"
    Handler = "Handler"
    TestFunction = "TestFunction"
    Include = "CaplInclude"
    Variable = "CaplVariable"
    TestGroup = "TestGroup"

app = typer.Typer(
    name="capl_tools",
    help="A powerful CLI for parsing and manipulating CAPL files.",
    add_completion=False,
)

@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    toon_output: bool = typer.Option(False, "--toon", help="Output structure in TOON"),
    full: bool = typer.Option(False, "--full", help="Include physical line numbers in the output")
):
    """
    List the logical structure of a CAPL file (Names, Signatures, and Types).
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    console = Console()
    processor = CaplProcessor(path)
    elements = processor.scan()

    if toon_output:
        # Create a lean list of dictionaries based on the 'full' flag
        data = [_project_element(el, include_lines=full) for el in elements]
        typer.echo(toon_encode(data))
        return

    # Human-readable table
    table = Table(title=f"Structure: {path.name}", box=None)
    table.add_column("Type", style="cyan")
    table.add_column("Signature", style="magenta")
    if full:
        table.add_column("Lines", style="green", justify="right")

    for el in elements:
        row = [el.__class__.__name__, el.display_name]
        if full:
            row.append(f"{el.start_line}-{el.end_line}")
        table.add_row(*row)

    console.print(table)
    console.print(f"\n[dim]Found {len(elements)} elements. Use 'stats' for a high-level summary.[/dim]")

@app.command()
def stats(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    machine: bool = typer.Option(False, "--machine", "-m", help="Single-line output (e.g., TestCase:15|Function:3)")
):
    """
    Get a highly compressed inventory of the CAPL file content.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    elements = processor.scan()
    
    from collections import Counter
    counts = Counter(el.__class__.__name__ for el in elements)

    if machine:
        # Super-compressed format for AI pipe usage or quick scripting
        summary_str = "|".join([f"{k}:{v}" for k, v in sorted(counts.items())])
        typer.echo(summary_str)
        return

    # Visual summary for humans
    console = Console()
    summary_table = Table(show_header=True, header_style="bold magenta", box=None)
    summary_table.add_column("Element Type")
    summary_table.add_column("Count", justify="right")

    for type_name, count in sorted(counts.items()):
        summary_table.add_row(type_name, str(count))

    console.print(Panel(
        summary_table, 
        title=f"Inventory: {path.name}", 
        expand=False, 
        border_style="cyan"
    ))

@app.command()
def remove(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    element_type: Annotated[ElementType, typer.Option("--type", "-t", help="Type of element to remove")],
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the element to remove")]
):
    """
    Remove a specific element by its type and name.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    
    if element_type == ElementType.TestGroup:
        count = processor.remove_test_group(name)
    else:
        count = processor.remove_element(element_type.value, name)
    
    if count > 0:
        processor.save()
        typer.secho(f"Successfully removed {count} elements of type '{element_type.value}' named '{name}' in {path.name}.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"No elements found matching type '{element_type.value}' and name '{name}'.", fg=typer.colors.YELLOW)


@app.command()
def get(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    name: Annotated[str, typer.Argument(help="Name of the element to fetch")],
    element_type: Annotated[str, typer.Option("--type", "-t", help="Type of element (e.g. TestCase, Function, Handler)")]
):
    """
    Fetch the raw code of a specific element.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    code = processor.get_element_code(element_type, name)
    
    if code:
        # Print raw code to stdout (important for AI pipe usage)
        typer.echo(code, nl=False)
    else:
        typer.secho(f"Error: Element '{name}' of type '{element_type}' not found.", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command()
def insert(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    location: Annotated[str, typer.Option("--location", "-l", help="Location: 'after:<name>', 'section:<name>', or 'line:<num>'")],
    source: Annotated[Optional[Path], typer.Option("--source", "-s", help="Path to code snippet (omit to read from stdin)")] = None,
    element_type: Annotated[Optional[ElementType], typer.Option("--type", "-t", help="Type of element being inserted")] = None,
):
    """
    Insert code into a CAPL file using semantic anchoring.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Read code from file or stdin
    if source:
        if not source.exists():
            typer.secho(f"Error: Source file {source} not found.", fg=typer.colors.RED)
            raise typer.Exit(code=1)
        code = source.read_text()
    else:
        # Read from stdin
        typer.echo("Reading code from stdin (Press Ctrl+Z/Ctrl+D to finish)...", err=True)
        import sys
        code = sys.stdin.read()

    if not code:
        typer.secho("Error: No code provided to insert.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    try:
        line = processor.insert(location, code, element_type=element_type.value if element_type else None)
        processor.save()
        typer.secho(f"Successfully inserted {element_type.value if element_type else 'code'} at line {line} in {path.name}.", fg=typer.colors.GREEN)
    except ValueError as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()