# ================================
# FILE: core/html_exporter.py
# ================================

import html
from pathlib import Path


class HTMLExporter:

    def __init__(self):

        pass

    # ============================================================
    # HELPERS
    # ============================================================

    @staticmethod
    def escape(value):

        if value is None:
            return "-"

        return html.escape(
            str(value)
        )

    @staticmethod
    def status_class(status):

        status = str(
            status
        ).upper()

        if status == "ONLINE":
            return "online"

        if status == "TIMEOUT":
            return "warning"

        return "offline"

    @staticmethod
    def grade_class(grade):

        grade = str(
            grade
        ).upper()

        if grade in (
            "A+",
            "A",
            "B",
        ):
            return "good"

        if grade in (
            "C",
            "D",
        ):
            return "warning"

        return "bad"

    # ============================================================
    # DOCUMENT
    # ============================================================

    def build_html(
        self,
        results,
        title="IP Scanner Professional Report",
    ):

        results = list(
            results or []
        )

        online = sum(
            1
            for result in results
            if getattr(
                result,
                "status",
                "",
            ) == "ONLINE"
        )

        offline = (
            len(results)
            - online
        )

        average_ping_values = [
            float(
                result.avg_ping
            )
            for result in results
            if getattr(
                result,
                "status",
                "",
            ) == "ONLINE"
            and getattr(
                result,
                "avg_ping",
                9999,
            ) < 9999
        ]

        average_ping = 0

        if average_ping_values:

            average_ping = round(
                sum(
                    average_ping_values
                )
                / len(
                    average_ping_values
                ),
                2,
            )

        rows = []

        for result in results:

            target = getattr(
                result,
                "target",
                getattr(
                    result,
                    "ip",
                    "-",
                ),
            )

            status = getattr(
                result,
                "status",
                "UNKNOWN",
            )

            grade = getattr(
                result,
                "grade",
                "F",
            )

            rows.append(
                f"""
                <tr>
                    <td>{self.escape(result.rank)}</td>
                    <td>{self.escape(target)}</td>
                    <td>{self.escape(result.hostname)}</td>
                    <td>{self.escape(result.country)}</td>
                    <td>{self.escape(result.city)}</td>
                    <td>{self.escape(result.isp)}</td>
                    <td>{self.escape(result.asn)}</td>
                    <td>{self.escape(result.avg_ping)}</td>
                    <td>{self.escape(result.packet_loss)}%</td>
                    <td>{self.escape(result.jitter)}</td>
                    <td>{self.escape(result.tcp_latency)}</td>
                    <td>{self.escape(result.udp_latency)}</td>
                    <td>
                        <span class="grade {self.grade_class(grade)}">
                            {self.escape(grade)}
                        </span>
                    </td>
                    <td>
                        <span class="status {self.status_class(status)}">
                            {self.escape(status)}
                        </span>
                    </td>
                    <td>{self.escape(result.network_score)}</td>
                </tr>
                """
            )

        rows_html = "\n".join(
            rows
        )

        if not rows_html:

            rows_html = """
            <tr>
                <td colspan="15" class="empty">
                    No scan results available.
                </td>
            </tr>
            """

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>
<title>{self.escape(title)}</title>

<style>

:root {{
    --bg: #0b0f14;
    --panel: #111820;
    --panel-2: #151f29;
    --border: #263646;
    --text: #e8f1f8;
    --muted: #8fa3b5;
    --cyan: #20d9ff;
    --green: #35e27a;
    --yellow: #ffd05a;
    --red: #ff5c68;
}}

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    background: var(--bg);
    color: var(--text);
    font-family:
        Inter,
        Segoe UI,
        Arial,
        sans-serif;
}}

.container {{
    width: min(
        1600px,
        calc(100% - 32px)
    );
    margin: 24px auto;
}}

.header {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 18px;
}}

.header h1 {{
    margin: 0 0 8px;
    color: var(--cyan);
}}

.header p {{
    margin: 0;
    color: var(--muted);
}}

.cards {{
    display: grid;
    grid-template-columns:
        repeat(
            auto-fit,
            minmax(180px, 1fr)
        );
    gap: 14px;
    margin-bottom: 18px;
}}

.card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
}}

.card .label {{
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 8px;
}}

.card .value {{
    font-size: 28px;
    font-weight: 700;
}}

.table-panel {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow-x: auto;
}}

table {{
    width: 100%;
    min-width: 1250px;
    border-collapse: collapse;
}}

th,
td {{
    padding: 11px 12px;
    border-bottom: 1px solid var(--border);
    text-align: center;
    white-space: nowrap;
}}

th {{
    background: var(--panel-2);
    color: var(--cyan);
    font-size: 13px;
}}

td {{
    color: var(--text);
    font-size: 13px;
}}

tr:hover td {{
    background: rgba(
        255,
        255,
        255,
        0.025
    );
}}

.status,
.grade {{
    display: inline-block;
    border-radius: 999px;
    padding: 4px 9px;
    font-size: 12px;
    font-weight: 700;
}}

.online,
.good {{
    background: rgba(
        53,
        226,
        122,
        0.14
    );
    color: var(--green);
}}

.warning {{
    background: rgba(
        255,
        208,
        90,
        0.14
    );
    color: var(--yellow);
}}

.offline,
.bad {{
    background: rgba(
        255,
        92,
        104,
        0.14
    );
    color: var(--red);
}}

.empty {{
    padding: 40px;
    color: var(--muted);
}}

.footer {{
    margin-top: 18px;
    color: var(--muted);
    text-align: center;
    font-size: 12px;
}}

</style>
</head>

<body>

<div class="container">

    <section class="header">
        <h1>IP Scanner Professional</h1>
        <p>Network Analysis Report</p>
    </section>

    <section class="cards">

        <div class="card">
            <div class="label">TOTAL</div>
            <div class="value">
                {len(results)}
            </div>
        </div>

        <div class="card">
            <div class="label">ONLINE</div>
            <div class="value">
                {online}
            </div>
        </div>

        <div class="card">
            <div class="label">OFFLINE</div>
            <div class="value">
                {offline}
            </div>
        </div>

        <div class="card">
            <div class="label">AVG PING</div>
            <div class="value">
                {average_ping} ms
            </div>
        </div>

    </section>

    <section class="table-panel">

        <table>

            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Target</th>
                    <th>Hostname</th>
                    <th>Country</th>
                    <th>City</th>
                    <th>ISP</th>
                    <th>ASN</th>
                    <th>Ping</th>
                    <th>Loss</th>
                    <th>Jitter</th>
                    <th>TCP</th>
                    <th>UDP</th>
                    <th>Grade</th>
                    <th>Status</th>
                    <th>Score</th>
                </tr>
            </thead>

            <tbody>
                {rows_html}
            </tbody>

        </table>

    </section>

    <div class="footer">
        Generated by IP Scanner Professional
    </div>

</div>

</body>
</html>
"""

    # ============================================================
    # WRITE
    # ============================================================

    def export(
        self,
        results,
        path,
        title="IP Scanner Professional Report",
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        content = self.build_html(
            results,
            title,
        )

        path.write_text(
            content,
            encoding="utf-8",
        )

        return path