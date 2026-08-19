# ================================
# FILE: main.py
# ================================

import os
import time
import threading
from pathlib import Path

from rich.console import Console

from core.scanner import (
    ProfessionalScanner
)

from ui.dashboard import (
    DashboardUI
)

from ui.menu import (
    MenuSystem
)

console = Console()

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = (
    BASE_DIR /
    "config" /
    "settings.json"
)

EXPORT_DIR = (
    BASE_DIR /
    "exports"
)

class Application:

    def __init__(self):

        self.console = console

        self.dashboard = DashboardUI(
            self.console
        )

        self.menu = MenuSystem(
            self.console,
            CONFIG_PATH
        )

        self.config = self.menu.load_config()

        self.scanner = ProfessionalScanner(
            self.config
        )

    def export_results(self):

        timestamp = str(
            int(time.time())
        )

        json_path = (
            EXPORT_DIR /
            f"scan_{timestamp}.json"
        )

        csv_path = (
            EXPORT_DIR /
            f"scan_{timestamp}.csv"
        )

        txt_path = (
            EXPORT_DIR /
            f"scan_{timestamp}.txt"
        )

        self.scanner.export_json(
            json_path
        )

        self.scanner.export_csv(
            csv_path
        )

        self.scanner.export_txt(
            txt_path
        )

        return [

            str(json_path),
            str(csv_path),
            str(txt_path)

        ]

    def save_session(self):

        summary = self.scanner.generate_summary()

        summary["time"] = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.menu.save_history(
            summary
        )

    def start_scan(self, ips):

        self.scanner = ProfessionalScanner(
            self.config
        )
        self.console.clear()

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

        time.sleep(2)

        dashboard_thread = None

        if self.config.get(
            "live_dashboard",
            True
        ):

            dashboard_thread = threading.Thread(

                target=self.dashboard.live_monitor,

                args=(self.scanner,),

                daemon=True

            )

            dashboard_thread.start()

        self.scanner.scan_ips(ips)

        if dashboard_thread:

            dashboard_thread.join(
                timeout=1
            )

        self.dashboard.final_screen(
            self.scanner
        )

        self.save_session()

        if self.config.get(
            "auto_export",
            True
        ):

            paths = self.export_results()

            self.dashboard.export_success(
                paths
            )

    def run_scan_from_input(self):

        ips = self.menu.collect_ips()

        if not ips:

            self.dashboard.error_message(
                "No IPs entered"
            )

            return

        self.start_scan(ips)

        input("\nPress ENTER...")

    def run_scan_from_txt(self):

        ips = self.menu.import_txt()

        if not ips:

            self.dashboard.error_message(
                "No valid IPs found"
            )

            return

        self.start_scan(ips)

        input("\nPress ENTER...")

    def startup(self):

        self.console.clear()

        self.menu.startup_banner()

        self.dashboard.loading_screen()

        self.dashboard.startup_animation()

    def runtime_loop(self):

        while True:

            self.console.clear()

            choice = self.menu.main_menu()

            if choice == "1":

                self.run_scan_from_input()

            elif choice == "2":

                self.run_scan_from_txt()

            elif choice == "3":

                self.menu.settings_menu()

                self.config = (
                    self.menu.load_config()
                )

            elif choice == "4":

                self.menu.show_history()

            elif choice == "5":

                self.menu.export_center()

            elif choice == "6":

                self.menu.about_page()

            elif choice == "7":

                self.console.clear()

                self.dashboard.success_message(
                    "Goodbye"
                )

                break

            else:

                self.dashboard.error_message(
                    "Invalid option"
                )

                time.sleep(1)

def main():

    app = Application()

    try:

        app.startup()

        app.runtime_loop()

    except KeyboardInterrupt:

        console.clear()

        console.print(
            "\n[bold red]Interrupted[/bold red]"
        )

    except Exception as error:

        console.clear()

        console.print(
            f"\n[bold red]Fatal Error:[/bold red] {error}"
        )

if __name__ == "__main__":

    main()