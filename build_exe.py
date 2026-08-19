import os
import subprocess

APP_NAME = "IPScannerProfessional"

def build():

    command = [

        "pyinstaller",

        "--onefile",

        "--console",

        "--name",
        APP_NAME,

        "launcher.py"

    ]

    subprocess.run(command)

if __name__ == "__main__":

    build()