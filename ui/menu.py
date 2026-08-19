# ================================
# FILE: ui/menu.py
# ================================

import os
import json
import time
from pathlib import Path

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich import box

class MenuSystem:

    def __init__(
        self,
        console,
        config_path
    ):

        self.console = console

        self.config_path = config_path

        self.history_path = (
            Path("data") / "history.json"
        )

    def load_config(self):

        with open(
            self.config_path,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    def save_config(self, config):

        with open(
            self.config_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                config,
                file,
                indent=4
            )

    def main_menu(self):

        table = Table(
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
            show_lines=True
        )

        table.add_column(
            "Option",
            justify="center",
            width=10
        )

        table.add_column(
            "Action",
            width=40
        )

        table.add_row(
            "1",
            "Start Professional Scan"
        )

        table.add_row(
            "2",
            "Import IPs From TXT"
        )

        table.add_row(
            "3",
            "Settings"
        )

        table.add_row(
            "4",
            "Scan History"
        )

        table.add_row(
            "5",
            "Export Center"
        )

        table.add_row(
            "6",
            "About"
        )

        table.add_row(
            "7",
            "Exit"
        )

        panel = Panel(

            Align.center(table),

            title="[bold white]MAIN MENU[/bold white]",

            border_style="bright_blue"

        )

        self.console.print(panel)

        return Prompt.ask(
            "\n[bold cyan]Select Option[/bold cyan]"
        )

    def collect_ips(self):

        self.console.print(

            Panel(

                "[bold cyan]ENTER IP ADDRESSES[/bold cyan]\n\n"
                "One IP per line\n"
                "Press ENTER on empty line to start",

                border_style="green"

            )

        )

        ips = []

        while True:

            ip = input("> ").strip()

            if ip == "":
                break

            ips.append(ip)

        return ips

    def import_txt(self):

        path = input(
            "\nTXT File Path: "
        ).strip()

        if not os.path.exists(path):

            self.console.print(
                "[red]File not found[/red]"
            )

            return []

        ips = []

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if line:

                    ips.append(line)

        return ips

    def settings_menu(self):

        config = self.load_config()

        while True:

            self.console.clear()

            table = Table(
                box=box.ROUNDED,
                border_style="yellow"
            )

            table.add_column(
                "Setting"
            )

            table.add_column(
                "Value"
            )

            for key, value in config.items():

                table.add_row(
                    str(key),
                    str(value)
                )

            self.console.print(

                Panel(
                    table,
                    title="[bold white]SETTINGS[/bold white]",
                    border_style="yellow"
                )

            )

            self.console.print("""

[1] Change Threads
[2] Change Timeout
[3] Change Ping Count
[4] Toggle Auto Export
[5] Toggle Live Dashboard
[6] Back

""")

            choice = input("> ").strip()

            if choice == "1":

                value = input(
                    "Threads: "
                ).strip()

                try:

                    config["threads"] = int(value)

                except:
                    pass

            elif choice == "2":

                value = input(
                    "Timeout: "
                ).strip()

                try:

                    config["timeout"] = int(value)

                except:
                    pass

            elif choice == "3":

                value = input(
                    "Ping Count: "
                ).strip()

                try:

                    config["ping_count"] = int(value)

                except:
                    pass

            elif choice == "4":

                config["auto_export"] = (
                    not config["auto_export"]
                )

            elif choice == "5":

                config["live_dashboard"] = (
                    not config["live_dashboard"]
                )

            elif choice == "6":

                self.save_config(config)

                break

            self.save_config(config)

    def save_history(self, summary):

        history = []

        if self.history_path.exists():

            try:

                with open(
                    self.history_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    history = json.load(file)

            except:

                history = []

        history.append(summary)

        with open(
            self.history_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                history,
                file,
                indent=4
            )

    def show_history(self):

        self.console.clear()

        if not self.history_path.exists():

            self.console.print(
                "[red]No history found[/red]"
            )

            return

        with open(
            self.history_path,
            "r",
            encoding="utf-8"
        ) as file:

            history = json.load(file)

        table = Table(
            box=box.DOUBLE_EDGE,
            border_style="bright_magenta",
            show_lines=True
        )

        table.add_column(
            "Date",
            width=25
        )

        table.add_column(
            "Total",
            justify="center"
        )

        table.add_column(
            "Online",
            justify="center"
        )

        table.add_column(
            "Best IP",
            width=18
        )

        for item in history:

            table.add_row(

                item.get(
                    "time",
                    "Unknown"
                ),

                str(
                    item.get(
                        "total",
                        0
                    )
                ),

                str(
                    item.get(
                        "online",
                        0
                    )
                ),

                item.get(
                    "best_ip",
                    "N/A"
                )

            )

        self.console.print(

            Panel(
                table,
                title="[bold white]SCAN HISTORY[/bold white]",
                border_style="bright_magenta"
            )

        )

        input("\nPress ENTER...")

    def export_center(self):

        exports = Path("exports")

        self.console.clear()

        table = Table(
            box=box.DOUBLE_EDGE,
            border_style="green"
        )

        table.add_column("File")

        if exports.exists():

            for file in exports.iterdir():

                table.add_row(
                    file.name
                )

        self.console.print(

            Panel(
                table,
                title="[bold white]EXPORTS[/bold white]",
                border_style="green"
            )

        )

        input("\nPress ENTER...")

    def about_page(self):

        text = """

[bold cyan]IP Scanner Professional[/bold cyan]

Advanced Network Analysis Toolkit

Features:
- Ultra Fast Scanner
- Live Dashboard
- GeoIP Detection
- ASN Detection
- TCP/UDP Analysis
- Export System
- Session History
- Real-time Ranking
- Professional UI

Developer:
Liyo

Version:
5.0

"""

        self.console.print(

            Panel(
                text,
                title="[bold white]ABOUT[/bold white]",
                border_style="bright_blue"
            )

        )

        input("\nPress ENTER...")

    def startup_banner(self):

        banner = """

██╗██████╗     ███████╗ ██████╗ █████╗ ███╗   ██╗
██║██╔══██╗    ██╔════╝██╔════╝██╔══██╗████╗  ██║
██║██████╔╝    ███████╗██║     ███████║██╔██╗ ██║
██║██╔═══╝     ╚════██║██║     ██╔══██║██║╚██╗██║
██║██║         ███████║╚██████╗██║  ██║██║ ╚████║
╚═╝╚═╝         ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝

"""
        credit = """

            [bold bright_white]
            Created By Liyo
            [/bold bright_white]

            [bright_black]
            Professional Network Analysis Suite
            [/bright_black]

            """
        panel = Panel(

            Align.center(
            f"[bold cyan]{banner}[/bold cyan]\n{credit}"
            ),

            title="[bold white]WELCOME[/bold white]",

            border_style="bright_blue"

        )

        self.console.print(panel)

        time.sleep(1.5)