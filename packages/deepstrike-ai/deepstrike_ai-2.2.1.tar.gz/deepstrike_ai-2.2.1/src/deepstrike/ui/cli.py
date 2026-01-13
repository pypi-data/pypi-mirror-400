import asyncio
import sys
import click
from rich.console import Console

from .menu import main_menu
from .doctor import run_doctor

console = Console()


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option("2.2.1", prog_name="deepstrike-ai")
@click.option(
    "--doctor",
    is_flag=True,
    help="Run environment diagnostics and exit"
)
def cli(doctor: bool):
    """DEEPSTRIKE AI — Authorized Security Research CLI"""
    if doctor:
        result = run_doctor()
        sys.exit(result)


@cli.command()
def menu():
    """🚀 Launch interactive menu (recommended)"""
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        console.print("\n[red]Exited by user[/red]")


@cli.command()
@click.argument("target")
def pentest(target):
    """Quick pentest stub (use menu for full features)"""
    console.print(
        f"[yellow]Target:[/yellow] {target}\n"
        "[cyan]Tip:[/cyan] Use `deepstrike menu` for full functionality"
    )


def main():
    cli()


if __name__ == "__main__":
    main()
