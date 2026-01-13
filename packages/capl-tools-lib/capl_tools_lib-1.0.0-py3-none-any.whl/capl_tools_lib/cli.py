import typer
import json
from enum import Enum
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import your internal logic
from capl_tools_lib.processor import CaplProcessor

class ElementType(str, Enum):
    TestCase = "TestCase"
    Function = "Function"
    Handler = "Handler"
    TestFunction = "TestFunction"
    Include = "CaplInclude"
    Variable = "CaplVariable"

app = typer.Typer(
    name="capl_tools",
    help="A powerful CLI for parsing and manipulating CAPL files.",
    add_completion=False,
)

@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    summary: bool = typer.Option(False, "--summary", "-s", help="Show only a summary"),
    json_output: bool = typer.Option(False, "--json", help="Output results in JSON format")
):
    """
    Scan a CAPL file and list all detected elements (TestCases, Functions, etc.)
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    console = Console()
    processor = CaplProcessor(path)
    elements = processor.scan()

    if json_output:
        # Serialize elements to JSON and print
        data = [el.to_dict() for el in elements]
        typer.echo(json.dumps(data, indent=2))
        return

    typer.echo(f"Found {len(elements)} elements in {path.name}:")

    
    if summary:
        from collections import Counter
        counts = Counter(el.__class__.__name__ for el in elements)
        
        # Create a mini-table for the summary
        summary_table = Table(show_header=True, header_style="bold magenta", box=None)
        summary_table.add_column("Element Type", width=20)
        summary_table.add_column("Count", justify="right")

        for type_name, count in counts.items():
            summary_table.add_row(type_name, str(count))

        # Wrap it in a nice Panel
        console.print(Panel(
            summary_table, 
            title=f"[bold]Summary: {path.name}[/bold]", 
            expand=False,
            border_style="cyan"
        ))
        return
    
    table = Table(title=f"Elements in {path.name}")

    table.add_column("Type", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Lines", style="green")

    for el in elements:
        table.add_row(
            el.__class__.__name__,
            el.display_name,
            f"{el.start_line}-{el.end_line}"
        )

    console.print(table)

@app.command()
def remove_group(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    group: Annotated[str, typer.Argument(help="Name of the test group to remove")]
):
    """
    Remove all test cases belonging to a specific test group.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    count = processor.remove_test_group(group)
    
    if count > 0:
        processor.save()
        typer.secho(f"Successfully removed {count} test cases from group '{group}' in {path.name}.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"No test cases found in group '{group}'.", fg=typer.colors.YELLOW)
        

@app.command()
def remove(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    element_type: Annotated[str, typer.Option("--type", "-t", help="Type of element to remove (e.g. TestCase, Function, Handler)")],
    name: Annotated[str, typer.Option("--name", "-n", help="Name of the element to remove")]
):
    """
    Remove a specific element by its type and name.
    """
    if not path.exists():
        typer.secho(f"Error: File {path} not found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    processor = CaplProcessor(path)
    count = processor.remove_element(element_type, name)
    
    if count > 0:
        processor.save()
        typer.secho(f"Successfully removed {count} elements of type '{element_type}' named '{name}' in {path.name}.", fg=typer.colors.GREEN)
    else:
        typer.secho(f"No elements found matching type '{element_type}' and name '{name}'.", fg=typer.colors.YELLOW)


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