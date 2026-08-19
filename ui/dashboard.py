# ================================
# FILE: ui/dashboard.py
# ================================

import time
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.align import Align
from rich.console import Group
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeElapsedColumn
)
from rich.text import Text
from rich import box

class DashboardUI:

    def __init__(self, console):

        self.console = console

    def create_header(self):

        title = Text()

        title.append(
            "IP SCANNER PROFESSIONAL",
            style="bold bright_cyan"
        )

        subtitle = Text()

        subtitle.append(
            "Advanced Network Analysis Suite",
            style="bold white"
        )

        group = Group(
            Align.center(title),
            Align.center(subtitle)
        )

        return Panel(
            group,
            border_style="bright_blue",
            box=box.DOUBLE_EDGE
        )

    def create_stats_panel(self, scanner):

        online = len([
            x for x in scanner.results
            if x.status == "ONLINE"
        ])

        offline = len([
            x for x in scanner.results
            if x.status != "ONLINE"
        ])

        avg_ping = 0

        if online:

            avg_ping = round(

                sum(
                    x.avg_ping
                    for x in scanner.results
                    if x.status == "ONLINE"
                ) / online,

                2

            )

        best_ip = "N/A"

        if scanner.best_result:

            best_ip = scanner.best_result.ip

        stats = f"""

[bold cyan]TOTAL:[/bold cyan] {len(scanner.results)}

[bold green]ONLINE:[/bold green] {online}

[bold red]OFFLINE:[/bold red] {offline}

[bold yellow]AVG PING:[/bold yellow] {avg_ping} ms

[bold magenta]BEST IP:[/bold magenta]
{best_ip}

"""

        return Panel(
            stats,
            title="[bold white]LIVE STATS[/bold white]",
            border_style="bright_magenta",
            box=box.ROUNDED
        )

    def create_results_table(self, scanner):

        table = Table(
            box=box.DOUBLE_EDGE,
            border_style="bright_cyan",
            show_lines=True,
            expand=True
        )

        table.add_column(
            "Rank",
            justify="center",
            width=6
        )

        table.add_column(
            "IP",
            style="cyan",
            width=18
        )

        table.add_column(
            "Country",
            justify="center",
            width=12
        )

        table.add_column(
            "Ping",
            justify="center",
            width=10
        )

        table.add_column(
            "Loss",
            justify="center",
            width=8
        )

        table.add_column(
            "Jitter",
            justify="center",
            width=10
        )

        table.add_column(
            "Stability",
            justify="center",
            width=10
        )

        table.add_column(
            "Grade",
            justify="center",
            width=8
        )

        table.add_column(
            "TCP",
            justify="center",
            width=10
        )

        table.add_column(
            "UDP",
            justify="center",
            width=10
        )

        table.add_column(
            "Provider",
            justify="center",
            width=14
        )

        table.add_column(
            "Status",
            justify="center",
            width=10
        )

        for result in scanner.results:

            ping_color = "green"

            if result.avg_ping > 70:
                ping_color = "yellow"

            if result.avg_ping > 150:
                ping_color = "red"

            grade_color = "green"

            if result.grade in ["C", "D"]:
                grade_color = "yellow"

            if result.grade == "F":
                grade_color = "red"

            status_color = "green"

            if result.status != "ONLINE":
                status_color = "red"

            table.add_row(

                str(result.rank),

                result.ip,

                result.country,

                f"[{ping_color}]"
                f"{result.avg_ping} ms"
                f"[/{ping_color}]",

                f"{result.packet_loss}%",

                f"{result.jitter}",

                f"{result.stability}",

                f"[{grade_color}]"
                f"{result.grade}"
                f"[/{grade_color}]",

                f"{result.tcp_latency} ms",

                f"{result.udp_latency} ms",

                result.provider,

                f"[{status_color}]"
                f"{result.status}"
                f"[/{status_color}]"

            )

        return table

    def create_best_result_panel(self, scanner):

        if not scanner.best_result:

            return Panel(
                "No Results",
                border_style="red"
            )

        best = scanner.best_result

        content = f"""

[bold green]IP:[/bold green]
{best.ip}

[bold cyan]PING:[/bold cyan]
{best.avg_ping} ms

[bold yellow]LOSS:[/bold yellow]
{best.packet_loss}%

[bold magenta]QUALITY:[/bold magenta]
{best.quality_score}

[bold white]GRADE:[/bold white]
{best.grade}

[bold green]COUNTRY:[/bold green]
{best.country}

"""

        return Panel(
            content,
            title="[bold bright_green]BEST RESULT[/bold bright_green]",
            border_style="green",
            box=box.DOUBLE_EDGE
        )

    def build_layout(self, scanner):

        layout = Layout()

        layout.split_column(

            Layout(
                name="header",
                size=5
            ),

            Layout(
                name="body"
            )

        )

        layout["body"].split_row(

            Layout(
                name="left",
                ratio=3
            ),

            Layout(
                name="right",
                ratio=1
            )

        )

        layout["right"].split_column(

            Layout(
                name="stats"
            ),

            Layout(
                name="best"
            )

        )

        layout["header"].update(
            self.create_header()
        )

        layout["left"].update(
            self.create_results_table(scanner)
        )

        layout["stats"].update(
            self.create_stats_panel(scanner)
        )

        layout["best"].update(
            self.create_best_result_panel(scanner)
        )

        return layout

    def loading_screen(self):

        progress = Progress(

            SpinnerColumn(),

            TextColumn(
                "[bold cyan]Initializing Engine..."
            ),

            BarColumn(),

            TimeElapsedColumn()

        )

        task = progress.add_task(
            "",
            total=100
        )

        with Live(
            progress,
            refresh_per_second=10
        ):

            for i in range(100):

                time.sleep(0.02)

                progress.advance(task)

    def startup_animation(self):

        messages = [

            "Loading Scanner Core...",
            "Initializing Network Modules...",
            "Loading Dashboard...",
            "Preparing Threads...",
            "Loading GeoIP Engine...",
            "Loading Export Manager...",
            "Starting Live UI...",
            "Ready..."

        ]

        for msg in messages:

            panel = Panel.fit(

                f"[bold cyan]{msg}[/bold cyan]",

                border_style="bright_blue"

            )

            self.console.clear()

            self.console.print(
                Align.center(panel)
            )

            time.sleep(0.4)

    def live_monitor(self, scanner):

        with Live(

            self.build_layout(scanner),

            refresh_per_second=4,

            screen=True

        ) as live:

            previous = 0

            while True:

                current = len(scanner.results)

                if current != previous:

                    live.update(
                        self.build_layout(scanner)
                    )

                    previous = current

                time.sleep(0.2)

                if scanner.total_scanned >= len(
                    scanner.results
                ):

                    live.update(
                        self.build_layout(scanner)
                    )

                    break

    def final_screen(self, scanner):

        self.console.clear()

        self.console.print(
            self.build_layout(scanner)
        )

    def export_success(self, paths):

        text = ""

        for path in paths:

            text += f"\n[green]{path}[/green]"

        panel = Panel(

            text,

            title="[bold white]EXPORT SUCCESS[/bold white]",

            border_style="green"

        )

        self.console.print(panel)

    def error_message(self, message):

        panel = Panel(

            f"[bold red]{message}[/bold red]",

            title="[bold white]ERROR[/bold white]",

            border_style="red"

        )

        self.console.print(panel)

    def success_message(self, message):

        panel = Panel(

            f"[bold green]{message}[/bold green]",

            title="[bold white]SUCCESS[/bold white]",

            border_style="green"

        )

        self.console.print(panel)