# ================================
# FILE: ui/graphs.py
# ================================

from rich.bar import Bar
from rich.table import Table
from rich.panel import Panel
from rich.console import Group
from rich.text import Text
from rich import box


class GraphsUI:

    def __init__(self):

        pass

    # ============================================================
    # GENERIC BAR
    # ============================================================

    @staticmethod
    def normalize(
        value,
        maximum,
    ):

        try:
            value = float(value)
            maximum = float(maximum)
        except (
            TypeError,
            ValueError,
        ):
            return 0

        if maximum <= 0:
            return 0

        return max(
            0,
            min(
                1,
                value / maximum,
            ),
        )

    # ============================================================
    # QUALITY GRAPH
    # ============================================================

    def quality_graph(
        self,
        results,
    ):

        results = list(
            results or []
        )

        table = Table(
            box=box.SIMPLE,
            expand=True,
            show_header=True,
        )

        table.add_column(
            "Target",
            style="cyan",
            no_wrap=True,
        )

        table.add_column(
            "Quality",
            justify="center",
        )

        table.add_column(
            "Score",
            justify="right",
        )

        for result in results[:10]:

            score = getattr(
                result,
                "quality_score",
                0,
            )

            score = max(
                0,
                min(
                    100,
                    float(score),
                ),
            )

            table.add_row(

                str(
                    getattr(
                        result,
                        "target",
                        result.ip,
                    )
                ),

                Bar(
                    size=20,
                    value=self.normalize(
                        score,
                        100,
                    ),
                    begin="",
                    end="",
                ),

                f"{score:.1f}",

            )

        if not results:

            table.add_row(
                "No results",
                "-",
                "-",
            )

        return Panel(
            table,
            title="[bold cyan]QUALITY[/bold cyan]",
            border_style="cyan",
        )

    # ============================================================
    # LATENCY GRAPH
    # ============================================================

    def latency_graph(
        self,
        results,
    ):

        results = list(
            results or []
        )

        table = Table(
            box=box.SIMPLE,
            expand=True,
            show_header=True,
        )

        table.add_column(
            "Target",
            style="cyan",
            no_wrap=True,
        )

        table.add_column(
            "Latency",
            justify="center",
        )

        table.add_column(
            "ms",
            justify="right",
        )

        valid_values = [
            float(
                getattr(
                    result,
                    "avg_ping",
                    9999,
                )
            )
            for result in results
            if float(
                getattr(
                    result,
                    "avg_ping",
                    9999,
                )
            ) < 9999
        ]

        maximum = max(
            valid_values,
            default=1,
        )

        for result in results[:10]:

            latency = float(
                getattr(
                    result,
                    "avg_ping",
                    9999,
                )
            )

            if latency >= 9999:

                table.add_row(
                    str(
                        getattr(
                            result,
                            "target",
                            result.ip,
                        )
                    ),
                    "-",
                    "-",
                )

                continue

            table.add_row(

                str(
                    getattr(
                        result,
                        "target",
                        result.ip,
                    )
                ),

                Bar(
                    size=20,
                    value=self.normalize(
                        latency,
                        maximum,
                    ),
                    begin="",
                    end="",
                ),

                f"{latency:.1f}",

            )

        if not results:

            table.add_row(
                "No results",
                "-",
                "-",
            )

        return Panel(
            table,
            title="[bold cyan]LATENCY[/bold cyan]",
            border_style="cyan",
        )

    # ============================================================
    # SUMMARY GRAPH
    # ============================================================

    def summary_graph(
        self,
        scanner,
    ):

        results = list(
            getattr(
                scanner,
                "results",
                [],
            )
        )

        online = sum(
            1
            for result in results
            if result.status == "ONLINE"
        )

        offline = (
            len(results)
            - online
        )

        total = max(
            1,
            len(results),
        )

        online_ratio = (
            online / total
        )

        offline_ratio = (
            offline / total
        )

        online_bar = Bar(
            size=25,
            value=online_ratio,
            begin="",
            end="",
        )

        offline_bar = Bar(
            size=25,
            value=offline_ratio,
            begin="",
            end="",
        )

        content = Group(

            Text(
                f"ONLINE   {online:>5}  ",
                style="green",
            ),

            online_bar,

            Text(
                f"\nOFFLINE  {offline:>5}  ",
                style="red",
            ),

            offline_bar,

        )

        return Panel(
            content,
            title="[bold cyan]SCAN STATUS[/bold cyan]",
            border_style="cyan",
        )