# ================================
# FILE: launcher.py
# ================================

import json
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path


APP_NAME = "IP Scanner Professional"
VERSION = "5.0.0"

MIN_PYTHON = (3, 10)

# ================================================================
# APPLICATION PATHS
# ================================================================

# PyInstaller --onefile extracts the application to a temporary
# runtime directory. Runtime-generated files must NOT be stored
# there, otherwise they disappear when the executable closes.
#
# Therefore:
#   Source mode  -> project directory
#   EXE mode     -> directory containing the EXE
#
if getattr(sys, "frozen", False):

    BASE_DIR = Path(
        sys.executable
    ).resolve().parent

else:

    BASE_DIR = Path(
        __file__
    ).resolve().parent


EXPORT_DIR = (
    BASE_DIR
    / "exports"
)

LOG_DIR = (
    BASE_DIR
    / "logs"
)

DATA_DIR = (
    BASE_DIR
    / "data"
)

CONFIG_DIR = (
    BASE_DIR
    / "config"
)

CONFIG_PATH = (
    CONFIG_DIR
    / "settings.json"
)


# ================================================================
# DEPENDENCIES
# ================================================================

REQUIRED_PACKAGES = [
    "rich",
    "requests",
    "colorama",
    "psutil",
]


# ================================================================
# DEFAULT CONFIG
# ================================================================

DEFAULT_CONFIG = {

    "threads": 300,

    "timeout": 1,

    "ping_count": 3,

    "theme": "default",

    "auto_export": True,

    "auto_save_logs": True,

    "live_dashboard": True,

    "udp_enabled": True,

    "tcp_enabled": True,

    "logging_enabled": True,

}


# ================================================================
# TERMINAL
# ================================================================

def clear():

    os.system(
        "cls"
        if os.name == "nt"
        else "clear"
    )


def optimize_terminal():

    if os.name != "nt":
        return

    try:

        os.system(
            "title IP Scanner Professional"
        )

    except Exception:
        pass

    # Do NOT force a fixed terminal width.
    #
    # The dashboard is responsive and should adapt to the user's
    # current terminal size instead of forcing 140 columns.
    #
    # Only increase the height when Windows CMD allows it.
    try:

        os.system(
            "mode con: lines=40"
        )

    except Exception:
        pass


# ================================================================
# PYTHON CHECK
# ================================================================

def python_check():

    if sys.version_info < MIN_PYTHON:

        print(
            f"Python "
            f"{MIN_PYTHON[0]}."
            f"{MIN_PYTHON[1]}+ "
            f"required."
        )

        sys.exit(1)


# ================================================================
# PACKAGE INSTALLATION
# ================================================================

def install_package(package):

    try:

        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                package,
            ]
        )

        return True

    except subprocess.CalledProcessError:

        return False

    except Exception:

        return False


def dependency_check():

    # A PyInstaller executable already contains its Python
    # dependencies. It should never try to install packages
    # into the user's Python environment.
    if getattr(
        sys,
        "frozen",
        False,
    ):

        return True

    missing = []

    for package in REQUIRED_PACKAGES:

        try:

            __import__(
                package
            )

        except ImportError:

            missing.append(
                package
            )

    if not missing:
        return True

    print(
        "\nMissing dependencies detected:\n"
    )

    for package in missing:

        print(
            f"  - {package}"
        )

    print(
        "\nAttempting automatic installation...\n"
    )

    failed = []

    for package in missing:

        print(
            f"Installing {package} ..."
        )

        if not install_package(
            package
        ):

            failed.append(
                package
            )

    if failed:

        print(
            "\nFailed to install:\n"
        )

        for package in failed:

            print(
                f"  - {package}"
            )

        print(
            "\nRun:\n"
            "pip install -r requirements.txt\n"
        )

        return False

    # Verify again after installation.
    still_missing = []

    for package in REQUIRED_PACKAGES:

        try:

            __import__(
                package
            )

        except ImportError:

            still_missing.append(
                package
            )

    if still_missing:

        print(
            "\nSome dependencies are still missing:\n"
        )

        for package in still_missing:

            print(
                f"  - {package}"
            )

        return False

    return True


# ================================================================
# FOLDERS
# ================================================================

def create_folders():

    folders = [

        EXPORT_DIR,

        LOG_DIR,

        DATA_DIR,

        CONFIG_DIR,

    ]

    for folder in folders:

        try:

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

        except Exception as error:

            print(
                f"Unable to create "
                f"{folder}: {error}"
            )

            return False

    return True


# ================================================================
# LOGGING
# ================================================================

def setup_logging():

    try:

        LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_file = (
            LOG_DIR
            / "scanner.log"
        )

        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format=(
                "%(asctime)s | "
                "%(levelname)s | "
                "%(message)s"
            ),
            encoding="utf-8",
        )

        logging.info(
            "========================================"
        )

        logging.info(
            "%s v%s starting",
            APP_NAME,
            VERSION,
        )

        return True

    except Exception as error:

        print(
            f"Logging setup failed: {error}"
        )

        return False


# ================================================================
# CONFIGURATION
# ================================================================

def merge_config(defaults, current):

    if not isinstance(
        current,
        dict,
    ):

        return defaults.copy()

    merged = defaults.copy()

    for key, value in current.items():

        merged[key] = value

    return merged


def create_config():

    try:

        CONFIG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        # --------------------------------------------------------
        # Create config when missing
        # --------------------------------------------------------

        if not CONFIG_PATH.exists():

            with open(
                CONFIG_PATH,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    DEFAULT_CONFIG,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            logging.info(
                "Default configuration created"
            )

            return True

        # --------------------------------------------------------
        # Validate / upgrade existing config
        # --------------------------------------------------------

        try:

            with open(
                CONFIG_PATH,
                "r",
                encoding="utf-8",
            ) as file:

                current = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            OSError,
        ):

            current = {}

        merged = merge_config(
            DEFAULT_CONFIG,
            current,
        )

        # Write only when the configuration actually differs.
        if merged != current:

            temporary_path = (
                CONFIG_PATH.with_suffix(
                    ".tmp"
                )
            )

            with open(
                temporary_path,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    merged,
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            os.replace(
                temporary_path,
                CONFIG_PATH,
            )

            logging.info(
                "Configuration updated"
            )

        return True

    except Exception as error:

        print(
            f"Configuration setup failed: "
            f"{error}"
        )

        return False


def load_config():

    try:

        if not CONFIG_PATH.exists():

            create_config()

        with open(
            CONFIG_PATH,
            "r",
            encoding="utf-8",
        ) as file:

            config = json.load(
                file
            )

        return merge_config(
            DEFAULT_CONFIG,
            config,
        )

    except Exception as error:

        logging.error(
            "Configuration load error: %s",
            error,
        )

        return DEFAULT_CONFIG.copy()


# ================================================================
# SYSTEM INFORMATION
# ================================================================

def detect_system():

    info = {

        "os": platform.system(),

        "release": platform.release(),

        "machine": platform.machine(),

        "cpu": platform.processor(),

        "python": platform.python_version(),

    }

    logging.info(
        "System Info: %s",
        info,
    )

    return info


# ================================================================
# STARTUP
# ================================================================

def startup():

    clear()

    print(
        f"{APP_NAME} v{VERSION}"
    )

    print(
        "Initializing Professional Scanner...\n"
    )

    # ------------------------------------------------------------
    # Python
    # ------------------------------------------------------------

    python_check()

    # ------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------

    if not create_folders():

        print(
            "\nFailed to prepare "
            "application directories."
        )

        return False

    # ------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------

    if not setup_logging():

        print(
            "\nWarning: logging "
            "could not be initialized."
        )

    # ------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------

    if not dependency_check():

        print(
            "\nDependency check failed."
        )

        return False

    # ------------------------------------------------------------
    # Config
    # ------------------------------------------------------------

    if not create_config():

        print(
            "\nFailed to prepare configuration."
        )

        return False

    # ------------------------------------------------------------
    # Terminal
    # ------------------------------------------------------------

    optimize_terminal()

    # ------------------------------------------------------------
    # System
    # ------------------------------------------------------------

    system_info = detect_system()

    print(
        "\nSystem Ready\n"
    )

    print(
        f"OS: {system_info['os']}"
    )

    print(
        f"Python: {system_info['python']}"
    )

    print(
        f"Architecture: "
        f"{system_info['machine']}"
    )

    print(
        f"Application Directory: "
        f"{BASE_DIR}"
    )

    logging.info(
        "Startup completed successfully"
    )

    return True


# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":

    if startup():

        from main import main

        main()