# ================================
# FILE: build_exe.py
# ================================

import shutil
import subprocess
import sys
from pathlib import Path


APP_NAME = "IPScannerProfessional"

BASE_DIR = Path(__file__).resolve().parent

DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"

MAIN_SCRIPT = BASE_DIR / "launcher.py"

CONFIG_DIR = BASE_DIR / "config"


def clean_previous_builds():

    for directory in (
        DIST_DIR,
        BUILD_DIR,
    ):

        if directory.exists():

            shutil.rmtree(
                directory
            )


def build():

    if not MAIN_SCRIPT.exists():

        raise FileNotFoundError(
            f"Missing entry point: {MAIN_SCRIPT}"
        )

    if not CONFIG_DIR.exists():

        raise FileNotFoundError(
            f"Missing config directory: {CONFIG_DIR}"
        )

    clean_previous_builds()

    # PyInstaller uses:
    # Windows -> source;destination
    # Linux/macOS -> source:destination

    data_separator = (
        ";"
        if sys.platform.startswith("win")
        else ":"
    )

    config_data = (
        f"{CONFIG_DIR}"
        f"{data_separator}"
        f"config"
    )

    command = [

        sys.executable,

        "-m",
        "PyInstaller",

        "--clean",
        "--noconfirm",

        "--onefile",
        "--console",

        "--name",
        APP_NAME,

        "--add-data",
        config_data,

        str(MAIN_SCRIPT),

    ]

    print()
    print("=" * 60)
    print("Building IP Scanner Professional")
    print("=" * 60)
    print()

    print(
        f"Python : {sys.executable}"
    )

    print(
        f"Entry  : {MAIN_SCRIPT}"
    )

    print(
        f"Output : {DIST_DIR / (APP_NAME + '.exe')}"
        if sys.platform.startswith("win")
        else
        f"Output : {DIST_DIR / APP_NAME}"
    )

    print()
    print("Running PyInstaller...")
    print()

    subprocess.run(
        command,
        cwd=BASE_DIR,
        check=True,
    )

    executable_name = (
        f"{APP_NAME}.exe"
        if sys.platform.startswith("win")
        else APP_NAME
    )

    executable_path = (
        DIST_DIR
        / executable_name
    )

    if not executable_path.exists():

        raise FileNotFoundError(
            "Build completed but "
            f"executable was not found: "
            f"{executable_path}"
        )

    print()
    print("=" * 60)
    print("BUILD SUCCESSFUL")
    print("=" * 60)
    print()
    print(
        f"Executable: {executable_path}"
    )
    print()


if __name__ == "__main__":

    try:

        build()

    except subprocess.CalledProcessError as error:

        print()
        print(
            "Build failed."
        )

        print(
            f"PyInstaller exit code: "
            f"{error.returncode}"
        )

        sys.exit(
            error.returncode
        )

    except Exception as error:

        print()
        print(
            f"Build Error: {error}"
        )

        sys.exit(1)