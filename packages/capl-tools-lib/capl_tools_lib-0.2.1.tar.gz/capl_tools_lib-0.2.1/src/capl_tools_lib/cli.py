import typer
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from rich.console import Console
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import your internal logic
from capl_tools_lib.processor import CaplProcessor

app = typer.Typer(
    name="capl_tools",
    help="A powerful CLI for parsing and manipulating CAPL files.",
    add_completion=False,
)

@app.command()
def scan(
    path: Annotated[Path, typer.Argument(help="Path to the .can file")],
    summary: bool = typer.Option(False, "--summary", "-s", help="Show only a summary")
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
def transform(
    path: Path, 
    output: Annotated[Optional[Path], typer.Option(help="Output file path")] = None
):
    """
    Modify CAPL code programmatically (e.g., refactoring or injecting code).
    """
    typer.echo(f"Transforming {path}...")
    # TODO: Link to your editor.py logic
    if output:
        typer.echo(f"Saved to {output}")

def main():
    """Entry point for the CLI."""
    app()

if __name__ == "__main__":
    main()