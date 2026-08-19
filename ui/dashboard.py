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
    TimeElapsedColumn,
)
from rich.text import Text
from rich import box


class DashboardUI:

    def __init__(self, console):
        self.console = console

    # ============================================================
    # TERMINAL HELPERS
    # ============================================================

    def get_terminal_width(self):

        try:
            width = self.console.size.width

            if not width:
                return 120

            return max(40, int(width))

        except Exception:
            return 120

    def get_terminal_height(self):

        try:
            height = self.console.size.height

            if not height:
                return 30

            return max(15, int(height))

        except Exception:
            return 30

    def get_content_width(self):

        width = self.get_terminal_width()

        # Leave a small safety margin so borders never
        # touch the terminal edge.
        return max(38, width - 2)

    def truncate(self, value, max_length):

        if value is None:
            return "-"

        value = str(value)

        if len(value) <= max_length:
            return value

        if max_length <= 3:
            return value[:max_length]

        return value[:max_length - 3] + "..."

    def format_number(self, value, decimals=1):

        if value is None:
            return "-"

        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)

        if number >= 9999:
            return "-"

        if number.is_integer():
            return str(int(number))

        return f"{number:.{decimals}f}"

    def format_latency(self, value):

        if value is None:
            return "-"

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return str(value)

        if numeric >= 9999:
            return "-"

        if numeric.is_integer():
            return f"{int(numeric)} ms"

        return f"{numeric:.1f} ms"

    # ============================================================
    # HEADER
    # ============================================================

    def create_header(self):

        width = self.get_content_width()

        title = Text(
            "IP SCANNER PROFESSIONAL",
            style="bold bright_cyan",
        )

        subtitle = Text(
            "Advanced Network Analysis Suite",
            style="bold white",
        )

        version = Text(
            "LIVE NETWORK MONITOR",
            style="bright_black",
        )

        group = Group(
            Align.center(title),
            Align.center(subtitle),
            Align.center(version),
        )

        return Panel(
            group,
            border_style="bright_blue",
            box=box.DOUBLE_EDGE,
            padding=(0, 1),
            width=width,
        )

    # ============================================================
    # STATISTICS
    # ============================================================

    def create_stats_panel(self, scanner):

        results = list(scanner.results)

        total = len(results)

        online_results = [
            result
            for result in results
            if result.status == "ONLINE"
        ]

        online = len(online_results)
        offline = total - online

        avg_ping = 0

        if online_results:

            avg_ping = round(
                sum(
                    float(result.avg_ping)
                    for result in online_results
                    if result.avg_ping < 9999
                )
                / max(
                    1,
                    len(
                        [
                            result
                            for result in online_results
                            if result.avg_ping < 9999
                        ]
                    ),
                ),
                2,
            )

        best_target = "N/A"

        if scanner.best_result:

            best_target = getattr(
                scanner.best_result,
                "target",
                scanner.best_result.ip,
            )

        content = Group(

            Text.from_markup(
                f"[bold cyan]TOTAL[/bold cyan]      {total}"
            ),

            Text.from_markup(
                f"[bold green]ONLINE[/bold green]     {online}"
            ),

            Text.from_markup(
                f"[bold red]OFFLINE[/bold red]    {offline}"
            ),

            Text.from_markup(
                f"[bold yellow]AVG PING[/bold yellow]   "
                f"{avg_ping} ms"
            ),

            Text.from_markup(
                f"[bold magenta]BEST[/bold magenta]       "
                f"{self.truncate(best_target, 24)}"
            ),
        )

        return Panel(
            content,
            title="[bold white]LIVE STATS[/bold white]",
            border_style="bright_magenta",
            box=box.ROUNDED,
            padding=(0, 1),
        )

    # ============================================================
    # RESULT COLORS
    # ============================================================

    def get_ping_color(self, value):

        try:
            value = float(value)
        except (TypeError, ValueError):
            return "white"

        if value >= 9999:
            return "red"

        if value <= 40:
            return "green"

        if value <= 100:
            return "yellow"

        return "red"

    def get_grade_color(self, grade):

        if grade in ("A+", "A", "B"):
            return "green"

        if grade in ("C", "D"):
            return "yellow"

        return "red"

    def get_status_color(self, status):

        if status == "ONLINE":
            return "green"

        if status == "TIMEOUT":
            return "yellow"

        return "red"

    # ============================================================
    # RESULTS TABLE - LARGE
    # ============================================================

    def create_results_table(self, scanner):

        width = self.get_terminal_width()

        if width < 105:
            return self.create_compact_results_table(
                scanner
            )

        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style="bright_cyan",
            show_lines=False,
            expand=True,
            pad_edge=False,
            collapse_padding=True,
        )

        table.add_column(
            "#",
            justify="center",
            width=4,
            no_wrap=True,
        )

        table.add_column(
            "IP",
            justify="center",
            style="cyan",
            width=16,
            no_wrap=True,
        )

        table.add_column(
            "Country",
            justify="center",
            width=11,
            no_wrap=True,
        )

        table.add_column(
            "Ping",
            justify="center",
            width=9,
            no_wrap=True,
        )

        table.add_column(
            "Loss",
            justify="center",
            width=7,
            no_wrap=True,
        )

        table.add_column(
            "Jitter",
            justify="center",
            width=8,
            no_wrap=True,
        )

        table.add_column(
            "Stability",
            justify="center",
            width=9,
            no_wrap=True,
        )

        table.add_column(
            "Grade",
            justify="center",
            width=6,
            no_wrap=True,
        )

        table.add_column(
            "TCP",
            justify="center",
            width=9,
            no_wrap=True,
        )

        table.add_column(
            "UDP",
            justify="center",
            width=9,
            no_wrap=True,
        )

        table.add_column(
            "Provider",
            justify="center",
            width=12,
            no_wrap=True,
        )

        table.add_column(
            "Status",
            justify="center",
            width=10,
            no_wrap=True,
        )

        for result in scanner.results:

            ping_color = self.get_ping_color(
                result.avg_ping
            )

            grade_color = self.get_grade_color(
                result.grade
            )

            status_color = self.get_status_color(
                result.status
            )

            country = self.truncate(
                result.country,
                11,
            )

            provider = self.truncate(
                result.provider,
                12,
            )

            table.add_row(

                str(result.rank),

                self.truncate(
                    result.ip,
                    16,
                ),

                country,

                (
                    f"[{ping_color}]"
                    f"{self.format_latency(result.avg_ping)}"
                    f"[/{ping_color}]"
                ),

                f"{self.format_number(result.packet_loss, 0)}%",

                self.format_number(
                    result.jitter,
                    1,
                ),

                self.format_number(
                    result.stability,
                    1,
                ),

                (
                    f"[{grade_color}]"
                    f"{self.truncate(result.grade, 3)}"
                    f"[/{grade_color}]"
                ),

                self.format_latency(
                    result.tcp_latency
                ),

                self.format_latency(
                    result.udp_latency
                ),

                provider,

                (
                    f"[{status_color}]"
                    f"{self.truncate(result.status, 10)}"
                    f"[/{status_color}]"
                ),
            )

        if not scanner.results:

            table.add_row(
                "-",
                "Waiting...",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-",
                "[yellow]SCANNING[/yellow]",
            )

        return table

    # ============================================================
    # COMPACT RESULTS TABLE
    # ============================================================

    def create_compact_results_table(self, scanner):

        width = self.get_terminal_width()

        table = Table(
            box=box.SIMPLE_HEAVY,
            border_style="bright_cyan",
            show_lines=False,
            expand=True,
            pad_edge=False,
            collapse_padding=True,
        )

        table.add_column(
            "#",
            justify="center",
            width=4,
            no_wrap=True,
        )

        table.add_column(
            "IP",
            justify="center",
            style="cyan",
            width=16,
            no_wrap=True,
        )

        table.add_column(
            "Ping",
            justify="center",
            width=9,
            no_wrap=True,
        )

        table.add_column(
            "Loss",
            justify="center",
            width=7,
            no_wrap=True,
        )

        table.add_column(
            "Grade",
            justify="center",
            width=7,
            no_wrap=True,
        )

        table.add_column(
            "Status",
            justify="center",
            width=10,
            no_wrap=True,
        )

        for result in scanner.results:

            ping_color = self.get_ping_color(
                result.avg_ping
            )

            grade_color = self.get_grade_color(
                result.grade
            )

            status_color = self.get_status_color(
                result.status
            )

            table.add_row(

                str(result.rank),

                self.truncate(
                    getattr(
                        result,
                        "target",
                        result.ip,
                    ),
                    16,
                ),

                (
                    f"[{ping_color}]"
                    f"{self.format_latency(result.avg_ping)}"
                    f"[/{ping_color}]"
                ),

                f"{self.format_number(result.packet_loss, 0)}%",

                (
                    f"[{grade_color}]"
                    f"{self.truncate(result.grade, 3)}"
                    f"[/{grade_color}]"
                ),

                (
                    f"[{status_color}]"
                    f"{self.truncate(result.status, 10)}"
                    f"[/{status_color}]"
                ),
            )

        if not scanner.results:

            table.add_row(
                "-",
                "Waiting...",
                "-",
                "-",
                "-",
                "[yellow]SCANNING[/yellow]",
            )

        if width < 65:
            table.expand = False

        return table

    # ============================================================
    # BEST RESULT
    # ============================================================

    def create_best_result_panel(self, scanner):

        if not scanner.best_result:

            return Panel(
                Align.center(
                    Text(
                        "No Results",
                        style="bold red",
                    )
                ),
                title="[bold white]BEST RESULT[/bold white]",
                border_style="red",
                box=box.ROUNDED,
                padding=(0, 1),
            )

        best = scanner.best_result

        target = getattr(
            best,
            "target",
            best.ip,
        )

        content = Group(

            Text.from_markup(
                f"[bold green]TARGET[/bold green]   "
                f"{self.truncate(target, 24)}"
            ),

            Text.from_markup(
                f"[bold cyan]PING[/bold cyan]     "
                f"{self.format_latency(best.avg_ping)}"
            ),

            Text.from_markup(
                f"[bold yellow]LOSS[/bold yellow]     "
                f"{best.packet_loss}%"
            ),

            Text.from_markup(
                f"[bold magenta]QUALITY[/bold magenta]  "
                f"{best.quality_score}"
            ),

            Text.from_markup(
                f"[bold white]GRADE[/bold white]    "
                f"{best.grade}"
            ),

            Text.from_markup(
                f"[bold green]COUNTRY[/bold green]  "
                f"{self.truncate(best.country, 18)}"
            ),
        )

        return Panel(
            content,
            title="[bold bright_green]BEST RESULT[/bold bright_green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
        )

    # ============================================================
    # DASHBOARD LAYOUT
    # ============================================================

    def build_layout(self, scanner):

        width = self.get_terminal_width()
        height = self.get_terminal_height()

        layout = Layout()

        # ========================================================
        # LARGE TERMINALS
        # ========================================================

        if width >= 115:

            header_size = 6

            if height < 28:
                header_size = 5

            layout.split_column(

                Layout(
                    name="header",
                    size=header_size,
                ),

                Layout(
                    name="body",
                ),
            )

            layout["body"].split_row(

                Layout(
                    name="results",
                    ratio=4,
                ),

                Layout(
                    name="sidebar",
                    ratio=1,
                    minimum_size=25,
                ),
            )

            layout["sidebar"].split_column(

                Layout(
                    name="stats",
                    ratio=1,
                ),

                Layout(
                    name="best",
                    ratio=1,
                ),
            )

            layout["header"].update(
                self.create_header()
            )

            layout["results"].update(
                self.create_results_table(scanner)
            )

            layout["stats"].update(
                self.create_stats_panel(scanner)
            )

            layout["best"].update(
                self.create_best_result_panel(scanner)
            )

            return layout

        # ========================================================
        # MEDIUM TERMINALS
        # ========================================================

        if width >= 80:

            header_size = 6

            if height < 25:
                header_size = 5

            layout.split_column(

                Layout(
                    name="header",
                    size=header_size,
                ),

                Layout(
                    name="stats",
                    size=7,
                ),

                Layout(
                    name="results",
                ),

                Layout(
                    name="best",
                    size=8,
                ),
            )

            layout["header"].update(
                self.create_header()
            )

            layout["stats"].update(
                self.create_stats_panel(scanner)
            )

            layout["results"].update(
                self.create_results_table(scanner)
            )

            layout["best"].update(
                self.create_best_result_panel(scanner)
            )

            return layout

        # ========================================================
        # SMALL TERMINALS
        # ========================================================

        header_size = 5

        if height < 20:
            header_size = 4

        layout.split_column(

            Layout(
                name="header",
                size=header_size,
            ),

            Layout(
                name="stats",
                size=7,
            ),

            Layout(
                name="results",
            ),
        )

        layout["header"].update(
            self.create_header()
        )

        layout["stats"].update(
            self.create_stats_panel(scanner)
        )

        layout["results"].update(
            self.create_compact_results_table(scanner)
        )

        return layout

    # ============================================================
    # LOADING SCREEN
    # ============================================================

    def loading_screen(self):

        progress = Progress(

            SpinnerColumn(),

            TextColumn(
                "[bold cyan]Initializing Engine...[/bold cyan]"
            ),

            BarColumn(),

            TextColumn(
                "[progress.percentage]"
                "{task.percentage:>3.0f}%"
            ),

            TimeElapsedColumn(),

            expand=True,
        )

        task = progress.add_task(
            "Loading",
            total=100,
        )

        with Live(
            progress,
            console=self.console,
            refresh_per_second=10,
            transient=True,
        ):

            for _ in range(100):

                time.sleep(0.02)

                progress.advance(task)

    # ============================================================
    # STARTUP ANIMATION
    # ============================================================

    def startup_animation(self):

        messages = [

            "Loading Scanner Core...",

            "Initializing Network Modules...",

            "Loading Dashboard...",

            "Preparing Threads...",

            "Loading GeoIP Engine...",

            "Loading Export Manager...",

            "Starting Live UI...",

            "Ready...",
        ]

        for message in messages:

            panel = Panel.fit(

                f"[bold cyan]{message}[/bold cyan]",

                border_style="bright_blue",

                padding=(1, 3),
            )

            self.console.clear()

            self.console.print(
                Align.center(panel)
            )

            time.sleep(0.35)

    # ============================================================
    # LIVE MONITOR
    # ============================================================

    def live_monitor(self, scanner):

        with Live(

            self.build_layout(scanner),

            console=self.console,

            refresh_per_second=5,

            screen=True,

            transient=False,

        ) as live:

            last_count = -1
            last_total = -1
            last_state = None

            while True:

                current_count = len(
                    scanner.results
                )

                current_total = (
                    getattr(
                        scanner,
                        "total_scanned",
                        0,
                    )
                )

                expected_total = getattr(
                    scanner,
                    "expected_total",
                    None,
                )

                stop_requested = getattr(
                    scanner,
                    "stop_scan",
                    False,
                )

                state = (
                    current_count,
                    current_total,
                    expected_total,
                    stop_requested,
                )

                if state != last_state:

                    live.update(
                        self.build_layout(scanner),
                        refresh=True,
                    )

                    last_state = state

                    last_count = current_count
                    last_total = current_total

                # ------------------------------------------------
                # Reliable completion detection.
                #
                # scanner.py sets expected_total when scanning
                # starts. If it is available, use it.
                # Otherwise fall back to the scanner state.
                # ------------------------------------------------

                if expected_total is not None:

                    finished = (
                        current_total
                        >= expected_total
                    )

                else:

                    finished = (
                        stop_requested
                        or (
                            current_count > 0
                            and current_total
                            >= current_count
                        )
                    )

                if finished:

                    live.update(
                        self.build_layout(scanner),
                        refresh=True,
                    )

                    break

                time.sleep(0.15)

    # ============================================================
    # FINAL SCREEN
    # ============================================================

    def final_screen(self, scanner):

        self.console.clear()

        self.console.print(
            self.build_layout(scanner)
        )

    # ============================================================
    # EXPORT SUCCESS
    # ============================================================

    def export_success(self, paths):

        lines = []

        for path in paths:

            lines.append(
                Text(
                    str(path),
                    style="green",
                )
            )

        if not lines:

            lines.append(
                Text(
                    "No files exported.",
                    style="yellow",
                )
            )

        group = Group(*lines)

        panel = Panel(

            group,

            title="[bold white]EXPORT SUCCESS[/bold white]",

            border_style="green",

            box=box.ROUNDED,

            padding=(1, 2),
        )

        self.console.print(panel)

    # ============================================================
    # ERROR MESSAGE
    # ============================================================

    def error_message(self, message):

        panel = Panel(

            Align.center(
                Text(
                    str(message),
                    style="bold red",
                )
            ),

            title="[bold white]ERROR[/bold white]",

            border_style="red",

            box=box.ROUNDED,

            padding=(1, 2),
        )

        self.console.print(panel)

    # ============================================================
    # SUCCESS MESSAGE
    # ============================================================

    def success_message(self, message):

        panel = Panel(

            Align.center(
                Text(
                    str(message),
                    style="bold green",
                )
            ),

            title="[bold white]SUCCESS[/bold white]",

            border_style="green",

            box=box.ROUNDED,

            padding=(1, 2),
        )

        self.console.print(panel)