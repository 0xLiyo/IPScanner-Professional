# IP Scanner Professional

A Python-based network analysis and scanning toolkit with a responsive terminal dashboard, configurable scanning engine, IP/port target support, session history, and multi-format reporting.

The project uses a modular architecture that separates the scanner engine, terminal UI, configuration, reporting, and application bootstrap.

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
* 🌐 HTML report generation
* 📝 Runtime logging
* ⚙️ Configurable scanner settings
* 🎨 Theme configuration support
* 📦 PyInstaller executable build support
* 🪟 Standalone Windows executable release

---

## 🖥️ Dashboard

The terminal dashboard automatically adapts to the available terminal width.

### Large terminals

Displays detailed scan information including:

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

The interface automatically switches to a compact layout so the dashboard remains inside the visible terminal area instead of overflowing horizontally.

---

## 🎯 Target Formats

The scanner supports both plain IPv4 addresses and explicit port targets.

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

When a port is specified, that port is used for the TCP/UDP tests.

---

## 📥 TXT Import

Targets can be loaded from a text file.

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
* Handles UTF-8 text files
* Accepts `IP` and `IP:PORT`
* Rejects invalid targets
* Removes duplicates
* Shows an import summary

A Windows path containing spaces can also be provided:

```text
C:\Users\YourName\Desktop\targets.txt
```

---

## 📊 Scan Analysis

Each target can include information such as:

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

## 📤 Export System

Completed scan results can be exported to:

```text
JSON
CSV
TXT
HTML
```

Example generated files:

```text
exports/
├── scan_XXXXXXXXXX.json
├── scan_XXXXXXXXXX.csv
├── scan_XXXXXXXXXX.txt
└── scan_XXXXXXXXXX.html
```

The generated HTML report is designed for viewing in a normal web browser.

---

## 🧾 Session History

After a scan is completed, the application generates a summary containing information such as:

* Total targets
* Online targets
* Offline targets
* Failed scans
* Average ping
* Best target
* Best score
* Scan timestamp

History is stored locally and can be viewed through the application's **Scan History** menu.

---

## 📝 Logging

Runtime and scanner errors are logged locally.

Typical runtime files include:

```text
logs/
└── scanner.log
```

Generated logs, exports, and application data are intended to remain local and are excluded from version control.

---

## 🧩 Project Structure

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

Provides reusable TCP port-scanning functionality for multiple ports.

### `core/security.py`

Provides validation and utility functions for targets, ports, filenames, and numeric configuration values.

### `core/html_exporter.py`

Generates browser-based HTML scan reports.

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

Provides the responsive live terminal interface and adapts its layout according to terminal size.

### `ui/graphs.py`

Provides terminal-oriented visualization components for scan metrics and summaries.

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/0xLiyo/IPScanner-Professional.git
```

Enter the project directory:

```bash
cd IPScanner-Professional
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

---

## ▶️ Running from Source

Start the application with:

```bash
python launcher.py
```

Using `launcher.py` is recommended because it performs the application initialization before starting the main interface.

The application can also be started directly with:

```bash
python main.py
```

---

## 📦 Building the Executable

The repository includes a dedicated PyInstaller build script.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Build the application:

```bash
python build_exe.py
```

The Windows executable is generated at:

```text
dist/
└── IPScannerProfessional.exe
```

The build script packages the application as a standalone executable.

---

## 🪟 Windows Release

Prebuilt Windows executables are available through the GitHub Releases page.

Current release:

**v5.1.0**

The release includes:

```text
IPScannerProfessional.exe
```

---

## 🔐 Responsible Use

This tool performs network-related operations and should only be used against systems you own or are explicitly authorized to test.

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

## 🛠️ Roadmap

Planned or possible improvements include:

* Deeper port-scanning integration
* Additional reporting formats
* More advanced terminal visualizations
* Scan profiles
* Custom port ranges
* Improved cross-platform support
* Automated tests
* CI/CD
* Automated release builds
* Expanded HTML reporting

---

## 📄 License

This project is licensed under the MIT License.

See [`LICENSE`](LICENSE) for details.

---

## ⭐ Support

If you find the project useful, consider giving the repository a ⭐ on GitHub.

---

**IP Scanner Professional**
*Network analysis and security testing toolkit for authorized environments.*
