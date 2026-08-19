# IP Scanner Professional

A Python-based network analysis and scanning toolkit with a responsive terminal dashboard, configurable scanning engine, IPv4/IP:PORT target support, session history, and multi-format reporting.

The project uses a modular architecture that separates the scanning engine, terminal UI, configuration, reporting utilities, and application bootstrap.

> ⚠️ **Disclaimer:** This software is intended only for authorized security testing, network administration, CTFs, laboratories, and educational environments. Do not scan systems or networks without explicit permission.

---

## ✨ Features

* 🚀 Multi-threaded network scanning
* 🎯 IPv4 and `IP:PORT` target support
* 📊 Responsive live terminal dashboard
* 🔍 TCP connectivity testing
* 📡 UDP transmission testing
* 🌐 Reverse DNS lookup
* 🌍 GeoIP information
* 🏢 ISP and ASN information
* 📶 Packet-loss measurement
* 📈 Ping, jitter, stability, and consistency analysis
* 🏆 Quality and network scoring
* 🥇 Real-time result ranking
* 📋 Interactive terminal menu
* 📥 TXT target import
* 💾 Session history
* 📤 JSON export
* 📑 CSV export
* 📝 TXT export
* 🌐 HTML reporting utilities
* 📝 Runtime logging
* ⚙️ Configurable scanner settings
* 🎨 Theme configuration support
* 📦 PyInstaller build support
* 🪟 Prebuilt Windows executable

---

## 🖥️ Responsive Dashboard

The terminal dashboard adapts to the available terminal size.

### Large terminals

The detailed dashboard can display:

* Rank
* Target
* Country
* Ping
* Packet loss
* Jitter
* Stability
* Grade
* TCP latency
* UDP latency
* Provider
* Status

### Smaller terminals

The dashboard automatically switches to a compact layout so the interface remains within the visible terminal area and avoids horizontal overflow.

---

## 🎯 Target Formats

The scanner accepts both plain IPv4 addresses and explicit port targets.

### IP address

```text
1.1.1.1
```

When no port is specified, the scanner uses its default TCP/UDP test ports.

### IP with port

```text
1.1.1.1:443
8.8.8.8:53
192.168.1.10:8080
```

When a port is specified, that port is used for the corresponding TCP/UDP tests.

---

## 📥 TXT Import

Targets can be imported from a `.txt` file.

Example:

```text
1.1.1.1
8.8.8.8
1.1.1.1:443
8.8.8.8:53
192.168.1.10:8080
```

The importer:

* Removes empty lines
* Supports UTF-8 text files
* Accepts `IP` and `IP:PORT`
* Rejects invalid targets
* Removes duplicates
* Displays an import summary

Windows paths containing spaces are supported:

```text
C:\Users\YourName\Desktop\targets.txt
```

---

## 📊 Scan Analysis

Each scan result can contain:

* IP address
* Port
* Hostname
* Country
* City
* ISP
* ASN
* Provider
* Average ping
* Minimum ping
* Maximum ping
* Packet loss
* Jitter
* Stability
* Consistency
* TCP latency
* UDP latency
* Quality score
* Network score
* Response speed
* Network type
* Grade
* Status
* Scan timestamp

---

## ⚙️ Configuration

Application settings are stored in:

```text
config/settings.json
```

Example:

```json
{
    "threads": 300,
    "timeout": 1,
    "ping_count": 3,
    "theme": "default",
    "auto_export": true,
    "auto_save_logs": true,
    "live_dashboard": true,
    "udp_enabled": true,
    "tcp_enabled": true,
    "logging_enabled": true
}
```

### Configuration Options

| Option            | Description                               |
| ----------------- | ----------------------------------------- |
| `threads`         | Maximum number of concurrent scan workers |
| `timeout`         | Network operation timeout in seconds      |
| `ping_count`      | Number of ping requests per target        |
| `theme`           | Selected terminal theme                   |
| `auto_export`     | Automatically export completed scans      |
| `auto_save_logs`  | Store scan session history                |
| `live_dashboard`  | Enable the live terminal dashboard        |
| `udp_enabled`     | Enable UDP testing                        |
| `tcp_enabled`     | Enable TCP testing                        |
| `logging_enabled` | Enable scanner error logging              |

---

# 🐧 Ubuntu / Linux Installation

## Requirements

* Python 3.10+
* Git
* `pip`
* `venv`
* System `ping` utility

On Ubuntu, install the required system packages:

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv iputils-ping
```

## Clone the Repository

```bash
git clone https://github.com/0xLiyo/IPScanner-Professional.git
cd IPScanner-Professional
```

## Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Install Python Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the Application

```bash
python launcher.py
```

`launcher.py` is the recommended entry point because it performs application initialization, configuration setup, directory creation, logging setup, and dependency checks before starting the interface.

The application can also be started directly with:

```bash
python main.py
```

---

# 🪟 Windows Installation

## Run from Source

Install Python 3.10 or newer, then clone the repository:

```powershell
git clone https://github.com/0xLiyo/IPScanner-Professional.git
cd IPScanner-Professional
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run:

```powershell
python launcher.py
```

## Prebuilt Windows Executable

A standalone Windows executable is available through GitHub Releases.

Current release:

**v5.1.0**

Download:

```text
IPScannerProfessional.exe
```

The executable does not require a separate Python installation.

---

# 📦 Building the Executable

PyInstaller is included in `requirements.txt` because it is required for building the standalone executable.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Build:

```bash
python build_exe.py
```

On Windows, the resulting executable is generated at:

```text
dist/
└── IPScannerProfessional.exe
```

The build script creates a standalone console executable and packages the project's configuration resources.

---

# 📤 Export System

Scan results can be exported to:

```text
JSON
CSV
TXT
```

Example generated files:

```text
exports/
├── scan_XXXXXXXXXX.json
├── scan_XXXXXXXXXX.csv
└── scan_XXXXXXXXXX.txt
```

The project also contains an HTML reporting utility under:

```text
core/html_exporter.py
```

which can be used for browser-based reporting integrations.

---

# 🧾 Session History

After a scan is completed, the application generates a session summary containing information such as:

* Total targets
* Online targets
* Offline targets
* Failed scans
* Average ping
* Best target
* Best score
* Scan timestamp

History is stored locally and can be reviewed through the **Scan History** menu.

---

# 📝 Logging

Runtime and scanner errors are logged locally.

Typical runtime files include:

```text
logs/
└── scanner.log
```

Generated logs, exports, and application data are intended to remain local and are excluded from version control.

---

# 🧩 Project Structure

```text
IPScanner-Professional/
│
├── main.py
├── launcher.py
├── build_exe.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
│
├── config/
│   └── themes.json
│
├── core/
│   ├── scanner.py
│   ├── port_scanner.py
│   ├── security.py
│   └── html_exporter.py
│
└── ui/
    ├── dashboard.py
    ├── graphs.py
    └── menu.py
```

### `main.py`

Application controller responsible for:

* Startup
* Scan execution
* Dashboard management
* Session saving
* Result exporting
* Runtime navigation

### `launcher.py`

Application bootstrapper responsible for:

* Python version validation
* Dependency checking
* Runtime directory creation
* Logging setup
* Configuration creation and validation
* System detection
* Terminal initialization

### `core/scanner.py`

Main scanning engine responsible for:

* Target parsing
* IPv4 validation
* IP/port handling
* Ping analysis
* TCP testing
* UDP testing
* Reverse DNS
* GeoIP lookup
* Network scoring
* Ranking
* JSON/CSV/TXT exports

### `core/port_scanner.py`

Reusable TCP port-scanning utilities for multiple ports.

### `core/security.py`

Validation and utility helpers for:

* IPv4 targets
* Ports
* Target parsing
* Filenames
* Numeric configuration values

### `core/html_exporter.py`

HTML report generation utilities.

### `ui/menu.py`

Handles:

* Main menu
* Manual target input
* TXT import
* Settings
* History
* Export center
* About page

### `ui/dashboard.py`

Provides the responsive live terminal dashboard and automatically adapts the layout to the terminal size.

### `ui/graphs.py`

Provides terminal-oriented visualization helpers for scan metrics and summary information.

---

# 🔐 Responsible Use

This tool performs network-related operations.

Only use it against systems and networks you own or are explicitly authorized to test.

Appropriate environments include:

* Your own infrastructure
* Authorized internal networks
* Security laboratories
* Virtual machines
* CTF environments
* Educational environments
* Authorized penetration-testing engagements

Unauthorized scanning may violate laws, organizational policies, or service terms.

The author is not responsible for misuse of this software.

---

# 🛠️ Roadmap

Possible future improvements include:

* Deeper integration of the reusable port scanner
* Additional reporting formats
* More advanced terminal visualizations
* Scan profiles
* Custom port ranges
* Improved cross-platform support
* Automated tests
* CI/CD
* Automated release builds
* Expanded HTML reporting
* More advanced scan result filtering

---

# 📄 License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

# ⭐ Support

If you find the project useful, consider giving the repository a ⭐ on GitHub.

---

**IP Scanner Professional**
*Network analysis and security testing toolkit for authorized environments.*
