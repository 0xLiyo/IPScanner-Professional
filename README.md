# IP Scanner Professional

A Python-based network scanning toolkit with a professional terminal interface, live monitoring, configurable scan options, session history, and multi-format result exporting.

Built with a modular architecture that separates the scanning engine, user interface, configuration, and application startup.

> ⚠️ **Disclaimer:** This project is intended for authorized security testing, network administration, CTFs, labs, and educational purposes only. Do not scan systems or networks without permission.

---

## ✨ Features

* 🚀 Multi-threaded network scanning
* 📊 Live terminal dashboard
* 🔍 TCP scanning
* 📡 UDP scanning
* ⚙️ Configurable scan settings
* 📋 Interactive terminal menu
* 📂 Import targets from TXT files
* 💾 Session history
* 📤 JSON export
* 📑 CSV export
* 📝 TXT export
* 🖥️ System information detection
* 📝 Automatic logging
* 🎨 Configurable terminal themes
* 📦 PyInstaller executable build support

---

## 🖥️ Interface

The application provides an interactive terminal-based interface with:

* Startup animation
* Main navigation menu
* Live scan monitoring
* Scan statistics
* Result screens
* Export notifications
* Configuration management
* Session history

---

## 📁 Project Structure

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

### Core

The `core/` package contains the main scanning and processing components.

### UI

The `ui/` package contains the terminal interface, dashboard, menus, and visualization components.

### Config

The `config/` directory contains application configuration and theme resources.

---

## ⚙️ Requirements

* Python 3.10+
* pip

Python dependencies:

```text
rich
requests
colorama
psutil
pyinstaller
```

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

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Running

Start the application through the launcher:

```bash
python launcher.py
```

The launcher performs the initial application setup before starting the main program.

It handles:

1. Python version checking
2. Dependency checking
3. Directory creation
4. Logging initialization
5. Configuration creation
6. System information detection
7. Application startup

You can also run the main application directly:

```bash
python main.py
```

Using `launcher.py` is recommended.

---

## ⚙️ Configuration

Application settings are stored inside the `config/` directory.

The scanner supports configurable options such as:

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
    "tcp_enabled": true
}
```

### Configuration Options

| Option           | Description                       |
| ---------------- | --------------------------------- |
| `threads`        | Number of scanning threads        |
| `timeout`        | Network operation timeout         |
| `ping_count`     | Number of ping attempts           |
| `theme`          | Terminal interface theme          |
| `auto_export`    | Automatically export scan results |
| `auto_save_logs` | Enable application logging        |
| `live_dashboard` | Enable live monitoring            |
| `udp_enabled`    | Enable UDP scanning               |
| `tcp_enabled`    | Enable TCP scanning               |

---

## 📥 Target Input

Targets can be provided in two ways:

### Manual Input

Enter targets directly through the interactive menu.

### TXT Import

Import targets from a `.txt` file through the application's import option.

---

## 📤 Export System

Scan results can be exported in multiple formats:

```text
JSON
CSV
TXT
```

When automatic export is enabled, result files are generated after a scan is completed.

Example:

```text
exports/
├── scan_XXXXXXXXXX.json
├── scan_XXXXXXXXXX.csv
└── scan_XXXXXXXXXX.txt
```

---

## 🧾 Session History

After a scan is completed, the application generates a summary and stores the session through the history system.

This allows previous scan sessions to be reviewed from the application interface.

---

## 🏗️ Building an Executable

The project includes a PyInstaller build script.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Then run:

```bash
python build_exe.py
```

The build process creates a standalone executable named:

```text
IPScannerProfessional
```

The generated files are normally placed in:

```text
dist/
```

---

## 📝 Logging

The launcher initializes application logging and stores runtime logs inside:

```text
logs/
```

Generated logs and other runtime files should not be committed to the repository.

---

## 🔐 Responsible Use

This tool performs network-related operations.

Only use it against systems and networks where you have explicit authorization.

Recommended environments include:

* Your own systems
* Authorized infrastructure
* CTF competitions
* Security laboratories
* Virtual machines
* Educational environments
* Internal network administration

Unauthorized scanning may violate laws, policies, or terms of service.

The author is not responsible for misuse of this software.

---

## 🛠️ Roadmap

Potential future improvements:

* Improved scan visualization
* More detailed result analysis
* Additional export formats
* Custom port configuration
* Scan profiles
* Improved cross-platform support
* Automated testing
* CI/CD integration
* Release automation

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
