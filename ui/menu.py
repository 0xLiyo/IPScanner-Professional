# ================================
# FILE: ui/menu.py
# ================================

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

from rich import box
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table


class MenuSystem:
    """
    Handles the application's interactive terminal menus,
    configuration, target input, TXT imports, history and exports.
    """

    def __init__(self, console, config_path):
        self.console = console
        self.config_path = Path(config_path)

        # Keep all runtime data relative to the project directory.
        self.base_dir = self.config_path.parent.parent

        self.history_path = (
            self.base_dir / "data" / "history.json"
        )

        self.exports_path = (
            self.base_dir / "exports"
        )

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------

    def load_config(self) -> dict:
        """Load configuration from settings.json."""

        try:
            if not self.config_path.exists():
                self.config_path.parent.mkdir(
                    parents=True,
                    exist_ok=True
                )

                default_config = {
                    "threads": 300,
                    "timeout": 1,
                    "ping_count": 3,
                    "theme": "default",
                    "auto_export": True,
                    "auto_save_logs": True,
                    "live_dashboard": True,
                    "udp_enabled": True,
                    "tcp_enabled": True
                }

                self.save_config(default_config)
                return default_config

            with open(
                self.config_path,
                "r",
                encoding="utf-8"
            ) as file:
                config = json.load(file)

            if not isinstance(config, dict):
                raise ValueError("Configuration must be a JSON object.")

            return config

        except Exception as error:
            self.console.print(
                f"[bold red]Configuration Error:[/bold red] {error}"
            )

            return {
                "threads": 300,
                "timeout": 1,
                "ping_count": 3,
                "theme": "default",
                "auto_export": True,
                "auto_save_logs": True,
                "live_dashboard": True,
                "udp_enabled": True,
                "tcp_enabled": True
            }

    def save_config(self, config: dict) -> bool:
        """Save configuration safely."""

        try:
            self.config_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            temporary_path = self.config_path.with_suffix(
                ".tmp"
            )

            with open(
                temporary_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    config,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_path,
                self.config_path
            )

            return True

        except Exception as error:

            self.console.print(
                f"[bold red]Failed to save configuration:[/bold red] "
                f"{error}"
            )

            return False

    # ---------------------------------------------------------
    # MAIN MENU
    # ---------------------------------------------------------

    def main_menu(self) -> str:

        table = Table(
            box=box.ROUNDED,
            border_style="bright_cyan",
            show_lines=True,
            expand=False
        )

        table.add_column(
            "Option",
            justify="center",
            no_wrap=True
        )

        table.add_column(
            "Action",
            no_wrap=True
        )

        options = [
            ("1", "Start Professional Scan"),
            ("2", "Import Targets From TXT"),
            ("3", "Settings"),
            ("4", "Scan History"),
            ("5", "Export Center"),
            ("6", "About"),
            ("7", "Exit")
        ]

        for option, action in options:
            table.add_row(
                option,
                action
            )

        panel = Panel(
            Align.center(table),
            title="[bold white]MAIN MENU[/bold white]",
            border_style="bright_blue",
            padding=(1, 2)
        )

        self.console.print(
            Align.center(panel)
        )

        return Prompt.ask(
            "\n[bold cyan]Select Option[/bold cyan]",
            choices=[
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7"
            ],
            show_choices=False
        )

    # ---------------------------------------------------------
    # TARGET PARSING
    # ---------------------------------------------------------

    @staticmethod
    def normalize_target(target: str) -> Optional[str]:
        """
        Normalize an IPv4 target.

        Supported:
            1.1.1.1
            1.1.1.1:443

        Returns:
            normalized target or None
        """

        target = target.strip()

        if not target:
            return None

        # Remove accidental surrounding quotes.
        if (
            len(target) >= 2
            and target[0] == target[-1]
            and target[0] in ("\"", "'")
        ):
            target = target[1:-1].strip()

        # IPv4 + optional port.
        parts = target.rsplit(":", 1)

        ip = parts[0].strip()

        if not MenuSystem.validate_ipv4(ip):
            return None

        if len(parts) == 2:

            port_text = parts[1].strip()

            if not port_text.isdigit():
                return None

            port = int(port_text)

            if not 1 <= port <= 65535:
                return None

            return f"{ip}:{port}"

        return ip

    @staticmethod
    def validate_ipv4(ip: str) -> bool:

        parts = ip.split(".")

        if len(parts) != 4:
            return False

        for part in parts:

            if not part.isdigit():
                return False

            if len(part) > 3:
                return False

            try:
                value = int(part)
            except ValueError:
                return False

            if value < 0 or value > 255:
                return False

        return True

    @staticmethod
    def parse_target(target: str) -> tuple[str, Optional[int]]:
        """
        Convert:

            1.1.1.1
        into:
            ("1.1.1.1", None)

        and:

            1.1.1.1:443
        into:
            ("1.1.1.1", 443)
        """

        normalized = MenuSystem.normalize_target(target)

        if normalized is None:
            raise ValueError(
                f"Invalid target: {target}"
            )

        if ":" in normalized:

            ip, port = normalized.rsplit(
                ":",
                1
            )

            return ip, int(port)

        return normalized, None

    # ---------------------------------------------------------
    # MANUAL TARGET INPUT
    # ---------------------------------------------------------

    def collect_ips(self) -> list[str]:

        self.console.print(
            Panel(
                "[bold cyan]ENTER SCAN TARGETS[/bold cyan]\n\n"
                "Supported formats:\n"
                "  • 1.1.1.1\n"
                "  • 1.1.1.1:443\n\n"
                "Enter one target per line.\n"
                "Press ENTER on an empty line to start scanning.",
                border_style="green",
                padding=(1, 2)
            )
        )

        targets = []

        while True:

            try:
                value = input("> ").strip()

            except (EOFError, KeyboardInterrupt):
                break

            if not value:
                break

            normalized = self.normalize_target(value)

            if normalized is None:

                self.console.print(
                    f"[bold red]Invalid target:[/bold red] "
                    f"{value}"
                )

                continue

            if normalized not in targets:
                targets.append(normalized)

        self.console.print(
            f"\n[bright_black]Loaded "
            f"{len(targets)} valid target(s).[/bright_black]"
        )

        return targets

    # ---------------------------------------------------------
    # TXT IMPORT
    # ---------------------------------------------------------

    def import_txt(self) -> list[str]:

        self.console.print(
            Panel(
                "[bold cyan]IMPORT TARGETS FROM TXT[/bold cyan]\n\n"
                "Supported formats:\n"
                "  • 1.1.1.1\n"
                "  • 1.1.1.1:443\n\n"
                "Enter the full path to your TXT file.",
                border_style="bright_blue",
                padding=(1, 2)
            )
        )

        path_input = input(
            "\nTXT File Path: "
        ).strip()

        if not path_input:
            return []

        # Handle paths pasted with surrounding quotes.
        path_input = path_input.strip()

        if (
            len(path_input) >= 2
            and path_input[0] == path_input[-1]
            and path_input[0] in ("\"", "'")
        ):
            path_input = path_input[1:-1].strip()

        file_path = Path(
            os.path.expandvars(
                os.path.expanduser(
                    path_input
                )
            )
        )

        if not file_path.is_file():

            self.console.print(
                Panel(
                    f"[bold red]File not found[/bold red]\n\n"
                    f"{file_path}",
                    border_style="red"
                )
            )

            return []

        targets = []

        valid_count = 0
        invalid_count = 0
        duplicate_count = 0

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8-sig",
                errors="replace"
            ) as file:

                for line_number, raw_line in enumerate(
                    file,
                    start=1
                ):

                    line = raw_line.strip()

                    if not line:
                        continue

                    # Ignore common comment formats.
                    if line.startswith(
                        ("#", ";", "//")
                    ):
                        continue

                    normalized = self.normalize_target(
                        line
                    )

                    if normalized is None:

                        invalid_count += 1

                        continue

                    if normalized in targets:

                        duplicate_count += 1

                        continue

                    targets.append(normalized)
                    valid_count += 1

        except OSError as error:

            self.console.print(
                f"[bold red]Unable to read file:[/bold red] "
                f"{error}"
            )

            return []

        summary = Table(
            box=box.ROUNDED,
            border_style="bright_cyan",
            expand=False
        )

        summary.add_column(
            "Metric",
            style="bold white"
        )

        summary.add_column(
            "Count",
            justify="right"
        )

        summary.add_row(
            "Valid targets",
            str(valid_count)
        )

        summary.add_row(
            "Invalid lines",
            str(invalid_count)
        )

        summary.add_row(
            "Duplicates",
            str(duplicate_count)
        )

        summary.add_row(
            "Total loaded",
            str(len(targets))
        )

        self.console.print(
            Panel(
                summary,
                title="[bold white]IMPORT SUMMARY[/bold white]",
                border_style="bright_blue"
            )
        )

        return targets

    # ---------------------------------------------------------
    # SETTINGS
    # ---------------------------------------------------------

    def settings_menu(self):

        config = self.load_config()

        while True:

            self.console.clear()

            table = Table(
                box=box.ROUNDED,
                border_style="yellow",
                show_lines=True,
                expand=False
            )

            table.add_column(
                "Setting",
                style="bold white"
            )

            table.add_column(
                "Value",
                style="cyan"
            )

            for key, value in config.items():

                table.add_row(
                    str(key),
                    str(value)
                )

            self.console.print(
                Align.center(
                    Panel(
                        table,
                        title="[bold white]SETTINGS[/bold white]",
                        border_style="yellow"
                    )
                )
            )

            self.console.print(
                """
[bold cyan][1][/bold cyan] Change Threads
[bold cyan][2][/bold cyan] Change Timeout
[bold cyan][3][/bold cyan] Change Ping Count
[bold cyan][4][/bold cyan] Toggle Auto Export
[bold cyan][5][/bold cyan] Toggle Live Dashboard
[bold cyan][6][/bold cyan] Toggle TCP
[bold cyan][7][/bold cyan] Toggle UDP
[bold cyan][8][/bold cyan] Back
"""
            )

            choice = input(
                "> "
            ).strip()

            # Threads
            if choice == "1":

                value = input(
                    "Threads (1-1000): "
                ).strip()

                try:

                    threads = int(value)

                    if 1 <= threads <= 1000:
                        config["threads"] = threads
                    else:
                        self.console.print(
                            "[red]Threads must be between "
                            "1 and 1000.[/red]"
                        )
                        time.sleep(1)

                except ValueError:

                    self.console.print(
                        "[red]Invalid number.[/red]"
                    )
                    time.sleep(1)

            # Timeout
            elif choice == "2":

                value = input(
                    "Timeout in seconds (1-60): "
                ).strip()

                try:

                    timeout = int(value)

                    if 1 <= timeout <= 60:
                        config["timeout"] = timeout
                    else:
                        self.console.print(
                            "[red]Timeout must be between "
                            "1 and 60 seconds.[/red]"
                        )
                        time.sleep(1)

                except ValueError:

                    self.console.print(
                        "[red]Invalid number.[/red]"
                    )
                    time.sleep(1)

            # Ping count
            elif choice == "3":

                value = input(
                    "Ping Count (1-20): "
                ).strip()

                try:

                    ping_count = int(value)

                    if 1 <= ping_count <= 20:
                        config["ping_count"] = ping_count
                    else:
                        self.console.print(
                            "[red]Ping count must be between "
                            "1 and 20.[/red]"
                        )
                        time.sleep(1)

                except ValueError:

                    self.console.print(
                        "[red]Invalid number.[/red]"
                    )
                    time.sleep(1)

            # Auto export
            elif choice == "4":

                config["auto_export"] = not config.get(
                    "auto_export",
                    True
                )

            # Live dashboard
            elif choice == "5":

                config["live_dashboard"] = not config.get(
                    "live_dashboard",
                    True
                )

            # TCP
            elif choice == "6":

                config["tcp_enabled"] = not config.get(
                    "tcp_enabled",
                    True
                )

            # UDP
            elif choice == "7":

                config["udp_enabled"] = not config.get(
                    "udp_enabled",
                    True
                )

            # Back
            elif choice == "8":

                self.save_config(config)
                break

            else:

                self.console.print(
                    "[red]Invalid option.[/red]"
                )
                time.sleep(1)

            self.save_config(config)

    # ---------------------------------------------------------
    # HISTORY
    # ---------------------------------------------------------

    def save_history(self, summary: dict):

        try:

            self.history_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            history = []

            if self.history_path.exists():

                try:

                    with open(
                        self.history_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        loaded = json.load(file)

                        if isinstance(loaded, list):
                            history = loaded

                except (
                    json.JSONDecodeError,
                    OSError
                ):

                    history = []

            history.append(summary)

            # Keep the history file manageable.
            history = history[-100:]

            temporary_path = (
                self.history_path.with_suffix(
                    ".tmp"
                )
            )

            with open(
                temporary_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    history,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_path,
                self.history_path
            )

        except Exception as error:

            self.console.print(
                f"[bold red]History Error:[/bold red] "
                f"{error}"
            )

    def show_history(self):

        self.console.clear()

        if not self.history_path.exists():

            self.console.print(
                Panel(
                    "[yellow]No scan history found.[/yellow]",
                    border_style="yellow"
                )
            )

            input("\nPress ENTER...")
            return

        try:

            with open(
                self.history_path,
                "r",
                encoding="utf-8"
            ) as file:

                history = json.load(file)

        except Exception as error:

            self.console.print(
                f"[red]Unable to read history:[/red] "
                f"{error}"
            )

            input("\nPress ENTER...")
            return

        if not isinstance(history, list) or not history:

            self.console.print(
                "[yellow]No scan history found.[/yellow]"
            )

            input("\nPress ENTER...")
            return

        table = Table(
            box=box.ROUNDED,
            border_style="bright_magenta",
            show_lines=True,
            expand=True
        )

        table.add_column(
            "Date",
            ratio=2
        )

        table.add_column(
            "Total",
            justify="center",
            ratio=1
        )

        table.add_column(
            "Online",
            justify="center",
            ratio=1
        )

        table.add_column(
            "Offline",
            justify="center",
            ratio=1
        )

        table.add_column(
            "Avg Ping",
            justify="center",
            ratio=1
        )

        table.add_column(
            "Best IP",
            ratio=2
        )

        for item in history:

            table.add_row(
                str(
                    item.get(
                        "time",
                        "Unknown"
                    )
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

                str(
                    item.get(
                        "offline",
                        0
                    )
                ),

                str(
                    item.get(
                        "average_ping",
                        0
                    )
                ),

                str(
                    item.get(
                        "best_ip",
                        "N/A"
                    )
                )
            )

        self.console.print(
            Panel(
                table,
                title="[bold white]SCAN HISTORY[/bold white]",
                border_style="bright_magenta",
                padding=(1, 1)
            )
        )

        input("\nPress ENTER...")

    # ---------------------------------------------------------
    # EXPORT CENTER
    # ---------------------------------------------------------

    def export_center(self):

        self.console.clear()

        table = Table(
            box=box.ROUNDED,
            border_style="green",
            show_lines=True,
            expand=True
        )

        table.add_column(
            "#",
            justify="center",
            width=5
        )

        table.add_column(
            "File",
            ratio=3
        )

        table.add_column(
            "Type",
            ratio=1
        )

        table.add_column(
            "Size",
            justify="right",
            ratio=1
        )

        files = []

        if self.exports_path.exists():

            files = sorted(
                [
                    file
                    for file in self.exports_path.iterdir()
                    if file.is_file()
                ],
                key=lambda item: item.stat().st_mtime,
                reverse=True
            )

        if not files:

            table.add_row(
                "-",
                "No exported files",
                "-",
                "-"
            )

        else:

            for index, file in enumerate(
                files,
                start=1
            ):

                suffix = file.suffix.lower().replace(
                    ".",
                    ""
                ).upper()

                try:
                    size = file.stat().st_size

                    if size < 1024:
                        size_text = f"{size} B"

                    elif size < 1024 * 1024:
                        size_text = (
                            f"{size / 1024:.1f} KB"
                        )

                    else:
                        size_text = (
                            f"{size / (1024 * 1024):.1f} MB"
                        )

                except OSError:
                    size_text = "Unknown"

                table.add_row(
                    str(index),
                    file.name,
                    suffix,
                    size_text
                )

        self.console.print(
            Panel(
                table,
                title="[bold white]EXPORT CENTER[/bold white]",
                border_style="green",
                padding=(1, 1)
            )
        )

        input("\nPress ENTER...")

    # ---------------------------------------------------------
    # ABOUT
    # ---------------------------------------------------------

    def about_page(self):

        self.console.clear()

        text = """
[bold cyan]IP Scanner Professional[/bold cyan]

Advanced Network Analysis Toolkit

[bold white]Core Features[/bold white]

• Multi-threaded IPv4 scanning
• IP / IP:PORT target support
• Live terminal dashboard
• Reverse DNS
• GeoIP information
• ISP / ASN detection
• TCP connectivity analysis
• UDP connectivity analysis
• Packet-loss measurement
• Jitter analysis
• Stability and consistency scoring
• Quality scoring
• Real-time ranking
• JSON / CSV / TXT exports
• Session history
• Configurable scanner engine

[bold white]Developer[/bold white]

Liyo

[bold white]Version[/bold white]

5.0
"""

        self.console.print(
            Align.center(
                Panel(
                    text,
                    title="[bold white]ABOUT[/bold white]",
                    border_style="bright_blue",
                    padding=(1, 3)
                )
            )
        )

        input("\nPress ENTER...")

    # ---------------------------------------------------------
    # STARTUP
    # ---------------------------------------------------------

    def startup_banner(self):

        banner = r"""
██╗██████╗
██║██╔══██╗
██║██████╔╝
██║██╔═══╝
██║██║
╚═╝╚═╝
"""

        credit = """
[bold bright_white]Created By Liyo[/bold bright_white]

[bright_black]Professional Network Analysis Suite[/bright_black]
"""

        content = (
            f"[bold cyan]{banner}[/bold cyan]\n"
            f"{credit}"
        )

        panel = Panel(
            Align.center(content),
            title="[bold white]WELCOME[/bold white]",
            border_style="bright_blue",
            padding=(1, 3)
        )

        self.console.print(
            Align.center(panel)
        )

        time.sleep(1.5)