"""Command-line interface for RRC Field Rules Parser."""

from pathlib import Path
from typing import Annotated

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from rrc_field_rules import __version__
from rrc_field_rules.config import ParserConfig
from rrc_field_rules.exceptions import HealthCheckError, RRCParserError
from rrc_field_rules.models import AVAILABLE_TABLES
from rrc_field_rules.parser import FieldRulesParser

app = typer.Typer(
    name="rrc-field-rules",
    help="Parse Texas RRC field rules from Oracle database to JSON.",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        rprint(f"[bold blue]rrc-field-rules[/bold blue] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = None,
) -> None:
    """RRC Field Rules Parser - Extract Texas RRC field rules to JSON."""
    pass


@app.command()
def check(
    host: Annotated[str, typer.Option(help="Oracle host")] = "localhost",
    port: Annotated[int, typer.Option(help="Oracle port")] = 1521,
    service: Annotated[str, typer.Option(help="Oracle service name")] = "FREEPDB1",
    user: Annotated[str, typer.Option(help="Oracle username")] = "PROD_OG_OWNR",
    password: Annotated[
        str, typer.Option(help="Oracle password", prompt=True, hide_input=True)
    ] = ...,
) -> None:
    """Check database connectivity (health check)."""
    config = ParserConfig(
        host=host, port=port, service=service, user=user, password=password
    )

    rprint(f"\n[bold]Connecting to:[/bold] {config.connection_string}")

    try:
        parser = FieldRulesParser(config)
        if parser.check_health():
            rprint("\n[bold green]✅ Database connection successful![/bold green]")

            # Show table counts
            table = Table(title="Available Tables")
            table.add_column("Table", style="cyan")
            table.add_column("Row Count", justify="right", style="green")

            for table_name in AVAILABLE_TABLES:
                count = parser.get_table_count(table_name)
                table.add_row(table_name, str(count))

            console.print(table)
            parser.close()
    except HealthCheckError as e:
        rprint(f"\n[bold red]❌ Health check failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None
    except RRCParserError as e:
        rprint(f"\n[bold red]❌ Connection error:[/bold red] {e}")
        raise typer.Exit(code=1) from None


@app.command()
def export(
    output: Annotated[
        Path, typer.Argument(help="Output JSON file path")
    ] = Path("./rrc_field_rules.json"),
    table: Annotated[
        str | None,
        typer.Option("--table", "-t", help="Export specific table only"),
    ] = None,
    limit: Annotated[
        int | None,
        typer.Option("--limit", "-l", help="Limit records per table"),
    ] = None,
    expand_codes: Annotated[
        bool,
        typer.Option(
            "--expand-codes",
            "-e",
            help="Expand coded values to human-readable text (e.g., 'O' -> 'Oil')",
        ),
    ] = False,
    host: Annotated[str, typer.Option(help="Oracle host")] = "localhost",
    port: Annotated[int, typer.Option(help="Oracle port")] = 1521,
    service: Annotated[str, typer.Option(help="Oracle service name")] = "FREEPDB1",
    user: Annotated[str, typer.Option(help="Oracle username")] = "PROD_OG_OWNR",
    password: Annotated[
        str, typer.Option(help="Oracle password", prompt=True, hide_input=True)
    ] = ...,
) -> None:
    """Export field rules data to JSON file."""
    config = ParserConfig(
        host=host,
        port=port,
        service=service,
        user=user,
        password=password,
        expand_codes=expand_codes,
    )

    # Validate table name if provided
    if table and table.lower() not in AVAILABLE_TABLES:
        rprint(f"[bold red]❌ Unknown table:[/bold red] {table}")
        rprint(f"Available tables: {', '.join(AVAILABLE_TABLES)}")
        raise typer.Exit(code=1)

    rprint(f"\n[bold]Connecting to:[/bold] {config.connection_string}")

    try:
        with FieldRulesParser(config) as parser:
            if table:
                rprint(f"[bold]Exporting table:[/bold] {table}")
                count = parser.export_table_to_json(table, output, limit)
                rprint(
                    f"\n[bold green]✅ Exported {count} records to {output}[/bold green]"
                )
            else:
                rprint("[bold]Exporting all tables...[/bold]")
                counts = parser.export_all_to_json(output, limit)

                table_display = Table(title="Export Summary")
                table_display.add_column("Table", style="cyan")
                table_display.add_column("Records", justify="right", style="green")

                total = 0
                for tbl_name, count in counts.items():
                    table_display.add_row(tbl_name, str(count))
                    total += count

                table_display.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
                console.print(table_display)

                rprint(f"\n[bold green]✅ Exported to {output}[/bold green]")

    except RRCParserError as e:
        rprint(f"\n[bold red]❌ Export failed:[/bold red] {e}")
        raise typer.Exit(code=1) from None


@app.command("list-tables")
def list_tables() -> None:
    """List available tables."""
    table = Table(title="Available Tables")
    table.add_column("Table Name", style="cyan")
    table.add_column("Description", style="dim")

    descriptions = {
        "og_field": "Oil & Gas Field master records",
        "og_field_info": "Field information with discovery dates, county codes",
        "og_field_rule": "Field-specific spacing and acreage rules",
        "og_std_field_rule": "Statewide standard field rules by depth",
    }

    for table_name in AVAILABLE_TABLES:
        table.add_row(table_name, descriptions.get(table_name, ""))

    console.print(table)


if __name__ == "__main__":
    app()
