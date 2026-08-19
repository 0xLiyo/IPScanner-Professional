# ================================
# FILE: main.py
# ================================

import threading
import time
from pathlib import Path

from rich.console import Console

from core.scanner import ProfessionalScanner
from ui.dashboard import DashboardUI
from ui.menu import MenuSystem


console = Console()

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = (
    BASE_DIR
    / "config"
    / "settings.json"
)

EXPORT_DIR = (
    BASE_DIR
    / "exports"
)

DATA_DIR = (
    BASE_DIR
    / "data"
)


class Application:

    def __init__(self):

        self.console = console

        # --------------------------------------------------------
        # Runtime directories
        # --------------------------------------------------------

        EXPORT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        DATA_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # UI
        # --------------------------------------------------------

        self.dashboard = DashboardUI(
            self.console
        )

        self.menu = MenuSystem(
            self.console,
            CONFIG_PATH,
        )

        # --------------------------------------------------------
        # Config
        # --------------------------------------------------------

        self.config = self.menu.load_config()

        # --------------------------------------------------------
        # Scanner
        # --------------------------------------------------------

        self.scanner = ProfessionalScanner(
            self.config
        )

    # ============================================================
    # EXPORT
    # ============================================================

    def export_results(self):

        timestamp = str(
            int(time.time())
        )

        json_path = (
            EXPORT_DIR
            / f"scan_{timestamp}.json"
        )

        csv_path = (
            EXPORT_DIR
            / f"scan_{timestamp}.csv"
        )

        txt_path = (
            EXPORT_DIR
            / f"scan_{timestamp}.txt"
        )

        exported = []

        try:

            self.scanner.export_json(
                json_path
            )

            exported.append(
                json_path
            )

        except Exception as error:

            self.console.print(
                f"[bold red]"
                f"JSON export failed:"
                f"[/bold red] {error}"
            )

        try:

            self.scanner.export_csv(
                csv_path
            )

            exported.append(
                csv_path
            )

        except Exception as error:

            self.console.print(
                f"[bold red]"
                f"CSV export failed:"
                f"[/bold red] {error}"
            )

        try:

            self.scanner.export_txt(
                txt_path
            )

            exported.append(
                txt_path
            )

        except Exception as error:

            self.console.print(
                f"[bold red]"
                f"TXT export failed:"
                f"[/bold red] {error}"
            )

        return [
            str(path)
            for path in exported
        ]

    # ============================================================
    # SESSION
    # ============================================================

    def save_session(self):

        try:

            summary = (
                self.scanner.generate_summary()
            )

            summary["time"] = time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            if self.config.get(
                "auto_save_logs",
                True,
            ):

                self.menu.save_history(
                    summary
                )

        except Exception as error:

            self.console.print(
                f"[bold red]"
                f"Failed to save session:"
                f"[/bold red] {error}"
            )

    # ============================================================
    # START SCAN
    # ============================================================

    def start_scan(self, targets):

        # --------------------------------------------------------
        # Fresh scanner instance for every scan
        # --------------------------------------------------------

        self.scanner = ProfessionalScanner(
            self.config
        )

        self.console.clear()

        # --------------------------------------------------------
        # Pre-scan screen
        # --------------------------------------------------------

        self.console.print(
            """
[bold bright_cyan]
Please Wait...
[/bold bright_cyan]

[bold white]
Initializing Professional Scan Engine
[/bold white]

[bright_black]
Analyzing Targets...
Preparing Threads...
Starting Network Modules...
[/bright_black]
"""
        )

        time.sleep(1.2)

        dashboard_thread = None

        # --------------------------------------------------------
        # Live Dashboard
        # --------------------------------------------------------

        if self.config.get(
            "live_dashboard",
            True,
        ):

            dashboard_thread = threading.Thread(
                target=self.dashboard.live_monitor,
                args=(self.scanner,),
                daemon=True,
            )

            dashboard_thread.start()

        # --------------------------------------------------------
        # Scan
        # --------------------------------------------------------

        try:

            self.scanner.scan_ips(
                targets
            )

        except KeyboardInterrupt:

            self.scanner.stop()

            if dashboard_thread:

                dashboard_thread.join(
                    timeout=2
                )

            raise

        except Exception as error:

            self.scanner.stop()

            self.console.print(
                f"[bold red]"
                f"Scan Error:"
                f"[/bold red] {error}"
            )

        # --------------------------------------------------------
        # Wait for dashboard thread
        # --------------------------------------------------------

        if dashboard_thread:

            dashboard_thread.join(
                timeout=3
            )

        # --------------------------------------------------------
        # Final result screen
        # --------------------------------------------------------

        self.dashboard.final_screen(
            self.scanner
        )

        # --------------------------------------------------------
        # Save history
        # --------------------------------------------------------

        self.save_session()

        # --------------------------------------------------------
        # Auto export
        # --------------------------------------------------------

        if self.config.get(
            "auto_export",
            True,
        ):

            paths = self.export_results()

            if paths:

                self.dashboard.export_success(
                    paths
                )

    # ============================================================
    # MANUAL SCAN
    # ============================================================

    def run_scan_from_input(self):

        targets = (
            self.menu.collect_ips()
        )

        if not targets:

            self.dashboard.error_message(
                "No valid targets entered"
            )

            time.sleep(1.5)

            return

        self.start_scan(
            targets
        )

        input(
            "\nPress ENTER..."
        )

    # ============================================================
    # TXT SCAN
    # ============================================================

    def run_scan_from_txt(self):

        targets = (
            self.menu.import_txt()
        )

        if not targets:

            self.dashboard.error_message(
                "No valid targets found"
            )

            time.sleep(1.5)

            return

        self.start_scan(
            targets
        )

        input(
            "\nPress ENTER..."
        )

    # ============================================================
    # STARTUP
    # ============================================================

    def startup(self):

        self.console.clear()

        self.menu.startup_banner()

        self.dashboard.loading_screen()

        self.dashboard.startup_animation()

    # ============================================================
    # MAIN LOOP
    # ============================================================

    def runtime_loop(self):

        while True:

            self.console.clear()

            choice = self.menu.main_menu()

            # ----------------------------------------------------
            # Scan
            # ----------------------------------------------------

            if choice == "1":

                self.run_scan_from_input()

            # ----------------------------------------------------
            # TXT Import
            # ----------------------------------------------------

            elif choice == "2":

                self.run_scan_from_txt()

            # ----------------------------------------------------
            # Settings
            # ----------------------------------------------------

            elif choice == "3":

                self.menu.settings_menu()

                self.config = (
                    self.menu.load_config()
                )

            # ----------------------------------------------------
            # History
            # ----------------------------------------------------

            elif choice == "4":

                self.menu.show_history()

            # ----------------------------------------------------
            # Export Center
            # ----------------------------------------------------

            elif choice == "5":

                self.menu.export_center()

            # ----------------------------------------------------
            # About
            # ----------------------------------------------------

            elif choice == "6":

                self.menu.about_page()

            # ----------------------------------------------------
            # Exit
            # ----------------------------------------------------

            elif choice == "7":

                self.console.clear()

                self.dashboard.success_message(
                    "Goodbye"
                )

                break

            # ----------------------------------------------------
            # Safety fallback
            # ----------------------------------------------------

            else:

                self.dashboard.error_message(
                    "Invalid option"
                )

                time.sleep(1)

    # ============================================================
    # RUN
    # ============================================================

    def run(self):

        self.startup()

        self.runtime_loop()


# ================================================================
# ENTRY POINT
# ================================================================

def main():

    app = Application()

    try:

        app.run()

    except KeyboardInterrupt:

        console.clear()

        console.print(
            "\n[bold red]"
            "Interrupted"
            "[/bold red]"
        )

    except Exception as error:

        console.clear()

        console.print(
            "\n[bold red]"
            "Fatal Error:"
            "[/bold red] "
            f"{error}"
        )


if __name__ == "__main__":

    main()