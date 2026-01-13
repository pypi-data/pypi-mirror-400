#!/usr/bin/env python3
import os
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich import print as rprint

from .. import __version__, config
from ..tor import TorProxy

# ================= SAFE OPTIONAL AI IMPORT =================
try:
    from deepstrike.ai.multi_agent import MultiAIAgent
    AI_AVAILABLE = True
except Exception:
    MultiAIAgent = None
    AI_AVAILABLE = False
# ===========================================================

from ..modules.crypto_recovery import DarkWebCryptoHunter
from ..modules.darkweb_scraper import DarkWebScraper

console = Console()

BANNER = f"""
  ▓█████▄ ▓█████ ▓█████  ██▓███    ██████ ▄▄▄█████▓ ██▀███   ██▓ ██ ▄█▀▓█████ 
▒██▀ ██▌▓█   ▀ ▓█   ▀ ▓██░  ██▒▒██    ▒ ▓  ██▒ ▓▒▓██ ▒ ██▒▓██▒ ██▄█▒ ▓█   ▀ 
░██   █▌▒███   ▒███   ▓██░ ██▓▒░ ▓██▄   ▒ ▓██░ ▒░▓██ ░▄█ ▒▒██▒▓███▄░ ▒███   
░▓█▄   ▌▒▓█  ▄ ▒▓█  ▄ ▒██▄█▓▒ ▒  ▒   ██▒░ ▓██▓ ░ ▒██▀▀█▄  ░██░▓██ █▄ ▒▓█  ▄ 
░▒████▓ ░▒████▒░▒████▒▒██▒ ░  ░▒██████▒▒  ▒██▒ ░ ░██▓ ▒██▒░██░▒██▒ █▄░▒████▒
 ▒▒▓  ▒ ░░ ▒░ ░░░ ▒░ ░▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░  ▒ ░░   ░ ▒▓ ░▒▓░░▓  ▒ ▒▒ ▓▒░░ ▒░ ░
 ░ ▒  ▒  ░ ░  ░ ░ ░  ░░▒ ░     ░ ░▒  ░ ░    ░      ░▒ ░ ▒░ ▒ ░░ ░▒ ▒░ ░ ░  ░
 ░ ░  ░    ░      ░   ░░       ░  ░  ░    ░        ░░   ░  ▒ ░░ ░░ ░    ░   
   ░       ░  ░   ░  ░               ░              ░      ░  ░  ░      ░  ░
 ░                                                                          
             AI-Powered Pentest v{__version__}
"""

def require_ai():
    if not AI_AVAILABLE:
        rprint(
            "[bold red]❌ AI features not installed[/bold red]\n"
            "[yellow]Install with:[/yellow] pip install deepstrike-ai[ai]"
        )
        return False
    return True


async def main_menu():
    TorProxy.setup()

    while True:
        console.clear()
        print(BANNER)

        menu = Table(title=" Select Operation")
        menu.add_column("Option", style="cyan")
        menu.add_column("Description")

        menu.add_row("1", " Autonomous Pentest")
        menu.add_row("2", " Dark Web Crypto Hunt")
        menu.add_row("3", " Dark Web Scraper")
        menu.add_row("4", " AI Attack Planner")
        menu.add_row("5", " TOR Status")
        menu.add_row("0", " Exit")

        console.print(menu)

        choice = Prompt.ask(
            "[bold green]Choose option[/bold green]",
            choices=["0", "1", "2", "3", "4", "5"]
        )

        if choice == "1":
            if require_ai():
                await pentest_menu()
        elif choice == "2":
            await crypto_hunt_menu()
        elif choice == "3":
            await scraper_menu()
        elif choice == "4":
            if require_ai():
                await ai_planner_menu()
        elif choice == "5":
            await tor_status()
        elif choice == "0":
            rprint("[bold red]👋 Goodbye![/bold red]")
            break

        input("\nPress Enter to continue...")


async def pentest_menu():
    target = Prompt.ask(" Enter target IP/domain")
    agent = MultiAIAgent()
    plan = await agent.plan_attack({"target": target})

    table = Table(title=" AI Attack Plan")
    table.add_column("Phase")
    table.add_column("Tools")

    for phase, tools in plan.items():
        table.add_row(phase.capitalize(), ", ".join(tools))

    console.print(table)


async def crypto_hunt_menu():
    paths = Prompt.ask(" Enter paths to scan").split()
    hunter = DarkWebCryptoHunter()
    findings = await hunter.hunt(paths)

    if findings:
        table = Table(title=" Crypto Finds")
        table.add_column("Type")
        table.add_column("Value")
        table.add_column("Balance")

        for f in findings:
            table.add_row(
                f["type"],
                f["value"][:30] + "...",
                str(f.get("balance", 0)),
            )

        console.print(table)
    else:
        rprint("[red] No crypto found[/red]")


async def scraper_menu():
    query = Prompt.ask(" Dark web search query")
    scraper = DarkWebScraper()

    if Confirm.ask("Download files?"):
        results = await scraper.scrape(query, download=True)
        rprint(f"[green]Downloaded {len(results)} items[/green]")


async def ai_planner_menu():
    target = Prompt.ask(" Target for AI planning")
    agent = MultiAIAgent()
    plan = await agent.plan_attack({"target": target})
    rprint(plan)


async def tor_status():
    ip = TorProxy.get_ip()
    TorProxy.renew_circuit()
    rprint(f"[green]TOR IP: {ip}[/green]")

