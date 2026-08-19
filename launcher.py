import os
import sys
import json
import shutil
import logging
import platform
import subprocess
from pathlib import Path

APP_NAME = "IP Scanner Professional"
VERSION = "5.0"

MIN_PYTHON = (3, 10)

BASE_DIR = Path(__file__).resolve().parent

EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

REQUIRED_PACKAGES = [
    "rich",
    "requests",
    "colorama",
    "psutil"
]

DEFAULT_CONFIG = {
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

def clear():

    os.system(
        "cls" if os.name == "nt" else "clear"
    )

def python_check():

    if sys.version_info < MIN_PYTHON:

        print(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required"
        )

        sys.exit()

def install_package(package):

    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        package
    ])

def dependency_check():

    for package in REQUIRED_PACKAGES:

        try:

            __import__(package)

        except ImportError:

            print(f"Installing {package} ...")

            install_package(package)

def create_folders():

    folders = [
        EXPORT_DIR,
        LOG_DIR,
        DATA_DIR,
        CONFIG_DIR
    ]

    for folder in folders:

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

def setup_logging():

    log_file = LOG_DIR / "scanner.log"

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )
    )

    logging.info("Logger initialized")

def create_config():

    config_path = CONFIG_DIR / "settings.json"

    if not config_path.exists():

        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                DEFAULT_CONFIG,
                file,
                indent=4
            )

def load_config():

    config_path = CONFIG_DIR / "settings.json"

    with open(
        config_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)

def detect_system():

    info = {
        "os": platform.system(),
        "release": platform.release(),
        "cpu": platform.processor(),
        "python": platform.python_version()
    }

    logging.info(f"System Info: {info}")

    return info

def optimize_terminal():

    if os.name == "nt":

        os.system("title IP Scanner Professional")

        os.system("mode con: cols=140 lines=40")

def startup():

    clear()

    print("Initializing Professional Scanner...\n")

    python_check()

    dependency_check()

    create_folders()

    setup_logging()

    create_config()

    optimize_terminal()

    system_info = detect_system()

    print("System Ready\n")

    print(f"OS: {system_info['os']}")
    print(f"Python: {system_info['python']}")

    logging.info("Startup completed")

if __name__ == "__main__":

    startup()

    from main import main

    main()