# ================================
# FILE: core/scanner.py
# ================================

import csv
import json
import logging
import platform
import re
import socket
import statistics
import subprocess
import time

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)
from pathlib import Path


class ScanResult:

    def __init__(self, ip, port=None):

        self.ip = ip
        self.port = port

        self.target = (
            f"{ip}:{port}"
            if port is not None
            else ip
        )

        # --------------------------------------------------------
        # Identification
        # --------------------------------------------------------

        self.hostname = "-"
        self.country = "Unknown"
        self.city = "Unknown"
        self.isp = "Unknown"
        self.asn = "Unknown"
        self.provider = "Unknown"

        # --------------------------------------------------------
        # Ping
        # --------------------------------------------------------

        self.pings = []

        self.avg_ping = 9999
        self.min_ping = 9999
        self.max_ping = 9999

        self.packet_loss = 100

        # --------------------------------------------------------
        # Network quality
        # --------------------------------------------------------

        self.jitter = 0
        self.stability = 0
        self.consistency = 0

        # --------------------------------------------------------
        # TCP / UDP
        # --------------------------------------------------------

        self.tcp_latency = 9999
        self.udp_latency = 9999

        self.tcp_open = False
        self.udp_open = False

        # --------------------------------------------------------
        # Classification
        # --------------------------------------------------------

        self.grade = "F"
        self.network_type = "Unknown"

        self.quality_score = 0
        self.network_score = 0

        self.response_speed = "Unknown"

        # --------------------------------------------------------
        # State
        # --------------------------------------------------------

        self.status = "OFFLINE"

        self.rank = 0

        self.scan_time = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def to_dict(self):

        return {
            "rank": self.rank,
            "ip": self.ip,
            "port": self.port,
            "target": self.target,
            "hostname": self.hostname,
            "country": self.country,
            "city": self.city,
            "isp": self.isp,
            "asn": self.asn,
            "provider": self.provider,
            "avg_ping": self.avg_ping,
            "min_ping": self.min_ping,
            "max_ping": self.max_ping,
            "packet_loss": self.packet_loss,
            "jitter": self.jitter,
            "stability": self.stability,
            "consistency": self.consistency,
            "tcp_latency": self.tcp_latency,
            "udp_latency": self.udp_latency,
            "tcp_open": self.tcp_open,
            "udp_open": self.udp_open,
            "grade": self.grade,
            "network_type": self.network_type,
            "quality_score": self.quality_score,
            "network_score": self.network_score,
            "response_speed": self.response_speed,
            "status": self.status,
            "scan_time": self.scan_time,
        }


class ProfessionalScanner:

    def __init__(self, config):

        self.config = config or {}

        self.results = []
        self.best_result = None

        self.total_scanned = 0
        self.failed_scans = 0

        # Used by the live dashboard to know exactly
        # how many targets are expected.
        self.expected_total = 0

        self.max_threads = self._safe_int(
            self.config.get("threads", 20),
            20,
            minimum=1,
            maximum=500,
        )

        self.timeout = self._safe_float(
            self.config.get("timeout", 2),
            2,
            minimum=0.2,
            maximum=60,
        )

        self.ping_count = self._safe_int(
            self.config.get("ping_count", 4),
            4,
            minimum=1,
            maximum=20,
        )

        self.tcp_enabled = bool(
            self.config.get(
                "tcp_enabled",
                True,
            )
        )

        self.udp_enabled = bool(
            self.config.get(
                "udp_enabled",
                True,
            )
        )

        self.system = platform.system().lower()

        self.stop_scan = False

        self.log_enabled = bool(
            self.config.get(
                "logging_enabled",
                True,
            )
        )

        self._configure_logging()

    # ============================================================
    # BASIC HELPERS
    # ============================================================

    @staticmethod
    def _safe_int(
        value,
        default,
        minimum=None,
        maximum=None,
    ):

        try:
            value = int(value)
        except (TypeError, ValueError):
            value = default

        if minimum is not None:
            value = max(
                minimum,
                value,
            )

        if maximum is not None:
            value = min(
                maximum,
                value,
            )

        return value

    @staticmethod
    def _safe_float(
        value,
        default,
        minimum=None,
        maximum=None,
    ):

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = default

        if minimum is not None:
            value = max(
                minimum,
                value,
            )

        if maximum is not None:
            value = min(
                maximum,
                value,
            )

        return value

    def _configure_logging(self):

        if not self.log_enabled:
            return

        try:

            logging.basicConfig(
                filename="scanner.log",
                level=logging.ERROR,
                format=(
                    "%(asctime)s | "
                    "%(levelname)s | "
                    "%(message)s"
                ),
            )

        except Exception:
            pass

    # ============================================================
    # TARGET PARSING
    # ============================================================

    def parse_target(self, target):

        if target is None:
            return None

        target = str(target).strip()

        if not target:
            return None

        target = target.strip(
            "\"'[](),"
        )

        # --------------------------------------------------------
        # IPv4:PORT
        # --------------------------------------------------------

        match = re.fullmatch(
            r"^(\d{1,3}(?:\.\d{1,3}){3}):(\d{1,5})$",
            target,
        )

        if match:

            ip = match.group(1)

            try:
                port = int(
                    match.group(2)
                )
            except ValueError:
                return None

            if not self.validate_ip(ip):
                return None

            if not self.validate_port(port):
                return None

            return {
                "ip": ip,
                "port": port,
                "target": f"{ip}:{port}",
            }

        # --------------------------------------------------------
        # Plain IPv4
        # --------------------------------------------------------

        if self.validate_ip(target):

            return {
                "ip": target,
                "port": None,
                "target": target,
            }

        return None

    def validate_ip(self, ip):

        if not isinstance(ip, str):
            return False

        pattern = (
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        )

        if not re.fullmatch(
            pattern,
            ip,
        ):
            return False

        parts = ip.split(".")

        if len(parts) != 4:
            return False

        for part in parts:

            try:
                value = int(part)
            except (TypeError, ValueError):
                return False

            if value < 0 or value > 255:
                return False

        return True

    def validate_port(self, port):

        try:
            port = int(port)
        except (
            TypeError,
            ValueError,
        ):
            return False

        return 1 <= port <= 65535

    def normalize_targets(self, targets):

        clean_targets = []
        seen = set()

        if not targets:
            return clean_targets

        for raw_target in targets:

            parsed = self.parse_target(
                raw_target
            )

            if not parsed:
                continue

            key = (
                parsed["ip"],
                parsed["port"],
            )

            if key in seen:
                continue

            seen.add(key)
            clean_targets.append(parsed)

        return clean_targets

    # ============================================================
    # PING
    # ============================================================

    def build_ping_command(self, ip):

        if "windows" in self.system:

            return [
                "ping",
                "-n",
                str(self.ping_count),
                "-w",
                str(
                    int(
                        self.timeout * 1000
                    )
                ),
                ip,
            ]

        return [
            "ping",
            "-c",
            str(self.ping_count),
            "-W",
            str(
                max(
                    1,
                    int(self.timeout),
                )
            ),
            ip,
        ]

    def extract_ping_values(self, output):

        if not output:
            return []

        values = []

        patterns = [
            r"time[=<]\s*([\d.]+)\s*ms",
            r"time[=<]\s*([\d.]+)",
        ]

        for pattern in patterns:

            matches = re.findall(
                pattern,
                output.lower(),
            )

            if not matches:
                continue

            for match in matches:

                try:

                    value = float(match)

                    if value >= 0:
                        values.append(value)

                except (
                    TypeError,
                    ValueError,
                ):
                    continue

            if values:
                break

        return values

    def extract_packet_loss(self, output):

        if not output:
            return 100

        output = output.lower()

        # Windows:
        # Lost = 0 (0% loss)

        windows_pattern = (
            r"lost\s*=\s*\d+\s*"
            r"\((\d+(?:\.\d+)?)%\s*loss\)"
        )

        match = re.search(
            windows_pattern,
            output,
        )

        if match:

            try:

                return int(
                    float(
                        match.group(1)
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                pass

        # Linux / macOS:
        # 0% packet loss

        unix_pattern = (
            r"(\d+(?:\.\d+)?)%\s*"
            r"(?:packet\s+loss|loss)"
        )

        match = re.search(
            unix_pattern,
            output,
        )

        if match:

            try:

                return int(
                    float(
                        match.group(1)
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                pass

        # Generic fallback

        generic_pattern = (
            r"(\d+(?:\.\d+)?)%\s*"
            r"(?:packet\s+)?loss"
        )

        match = re.search(
            generic_pattern,
            output,
        )

        if match:

            try:

                return int(
                    float(
                        match.group(1)
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                pass

        return 100

    # ============================================================
    # METRICS
    # ============================================================

    def calculate_jitter(self, pings):

        if len(pings) < 2:
            return 0

        diffs = []

        for index in range(
            1,
            len(pings),
        ):

            diffs.append(
                abs(
                    pings[index]
                    - pings[index - 1]
                )
            )

        if not diffs:
            return 0

        return round(
            sum(diffs) / len(diffs),
            2,
        )

    def calculate_stability(self, pings):

        if not pings:
            return 0

        if len(pings) == 1:
            return 100

        try:

            deviation = statistics.stdev(
                pings
            )

        except statistics.StatisticsError:

            return 100

        stability = 100 - (
            deviation * 2
        )

        return round(
            max(
                0,
                min(
                    100,
                    stability,
                ),
            ),
            2,
        )

    def calculate_consistency(self, pings):

        if not pings:
            return 0

        if len(pings) == 1:
            return 100

        average = (
            sum(pings)
            / len(pings)
        )

        tolerance = max(
            5,
            average * 0.10,
        )

        stable_hits = sum(
            1
            for ping in pings
            if abs(
                ping - average
            ) <= tolerance
        )

        return round(
            (
                stable_hits
                / len(pings)
            ) * 100,
            2,
        )

    def determine_grade(
        self,
        avg_ping,
        loss,
    ):

        if loss >= 100:
            return "F"

        if loss >= 20:
            return "D"

        if avg_ping <= 20:
            return "A+"

        if avg_ping <= 40:
            return "A"

        if avg_ping <= 70:
            return "B"

        if avg_ping <= 120:
            return "C"

        return "D"

    def detect_speed(self, avg_ping):

        if avg_ping <= 20:
            return "EXTREME"

        if avg_ping <= 40:
            return "ULTRA"

        if avg_ping <= 70:
            return "FAST"

        if avg_ping <= 120:
            return "NORMAL"

        if avg_ping <= 180:
            return "SLOW"

        return "VERY SLOW"

    def detect_network_type(
        self,
        avg_ping,
    ):

        if avg_ping <= 15:
            return "FIBER"

        if avg_ping <= 40:
            return "HIGH SPEED"

        if avg_ping <= 80:
            return "BROADBAND"

        if avg_ping <= 150:
            return "MOBILE"

        return "WEAK"

    def calculate_quality_score(
        self,
        avg_ping,
        packet_loss,
        stability,
    ):

        score = 100.0

        score -= min(
            50,
            avg_ping * 0.35,
        )

        score -= (
            packet_loss * 0.9
        )

        score += (
            stability * 0.2
        )

        return round(
            max(
                0,
                min(
                    100,
                    score,
                ),
            ),
            2,
        )

    def calculate_network_score(
        self,
        result,
    ):

        score = 0.0

        score += max(
            0,
            50 - result.avg_ping,
        )

        score += max(
            0,
            30 - result.packet_loss,
        )

        score += (
            result.stability * 0.2
        )

        score += (
            result.quality_score * 0.3
        )

        if result.tcp_open:
            score += 5

        if result.udp_open:
            score += 5

        return round(
            score,
            2,
        )

    # ============================================================
    # DNS / PROVIDER
    # ============================================================

    def reverse_dns(self, ip):

        try:

            hostname = socket.gethostbyaddr(
                ip
            )[0]

            if hostname:
                return hostname

        except (
            socket.herror,
            socket.gaierror,
            OSError,
        ):
            pass

        except Exception:
            pass

        return "-"

    def detect_provider(self, hostname):

        if not hostname:
            return "Unknown"

        hostname = hostname.lower()

        providers = {
            "cloudflare": "Cloudflare",
            "akamai": "Akamai",
            "amazonaws": "AWS",
            "amazon": "AWS",
            "google": "Google",
            "facebook": "Meta",
            "meta": "Meta",
            "microsoft": "Azure",
            "azure": "Azure",
            "fastly": "Fastly",
            "digitalocean": "DigitalOcean",
            "oracle": "Oracle",
            "ovh": "OVH",
            "hetzner": "Hetzner",
            "linode": "Linode",
            "vultr": "Vultr",
            "cdn": "CDN",
        }

        for key, value in providers.items():

            if key in hostname:
                return value

        return "Unknown"

    # ============================================================
    # TCP
    # ============================================================

    def tcp_test(
        self,
        ip,
        port=443,
    ):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        sock.settimeout(
            self.timeout
        )

        start = time.perf_counter()

        try:

            result = sock.connect_ex(
                (
                    ip,
                    int(port),
                )
            )

            latency = round(
                (
                    time.perf_counter()
                    - start
                ) * 1000,
                2,
            )

            if result == 0:

                return (
                    True,
                    latency,
                )

            return (
                False,
                latency,
            )

        except Exception:

            return (
                False,
                9999,
            )

        finally:

            try:
                sock.close()
            except Exception:
                pass

    # ============================================================
    # UDP
    # ============================================================

    def udp_test(
        self,
        ip,
        port=53,
    ):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        sock.settimeout(
            self.timeout
        )

        start = time.perf_counter()

        try:

            sock.sendto(
                b"",
                (
                    ip,
                    int(port),
                ),
            )

            latency = round(
                (
                    time.perf_counter()
                    - start
                ) * 1000,
                2,
            )

            # A successful UDP send does not prove
            # that the remote UDP port is open.
            # This value represents successful transmission.

            return (
                True,
                latency,
            )

        except Exception:

            return (
                False,
                9999,
            )

        finally:

            try:
                sock.close()
            except Exception:
                pass

    # ============================================================
    # GEO IP
    # ============================================================

    def geo_lookup(self, ip):

        try:

            import requests

            response = requests.get(
                f"http://ip-api.com/json/{ip}",
                params={
                    "fields": (
                        "status,"
                        "message,"
                        "country,"
                        "city,"
                        "isp,"
                        "as"
                    )
                },
                timeout=5,
            )

            if response.status_code != 200:
                return self._empty_geo()

            data = response.json()

            if data.get("status") != "success":
                return self._empty_geo()

            return {
                "country": data.get(
                    "country",
                    "Unknown",
                ),
                "city": data.get(
                    "city",
                    "Unknown",
                ),
                "isp": data.get(
                    "isp",
                    "Unknown",
                ),
                "asn": data.get(
                    "as",
                    "Unknown",
                ),
            }

        except Exception:

            return self._empty_geo()

    @staticmethod
    def _empty_geo():

        return {
            "country": "Unknown",
            "city": "Unknown",
            "isp": "Unknown",
            "asn": "Unknown",
        }

    # ============================================================
    # SINGLE TARGET SCAN
    # ============================================================

    def perform_scan(
        self,
        target,
    ):

        if isinstance(
            target,
            dict,
        ):

            ip = target.get("ip")
            port = target.get("port")

            if not self.validate_ip(ip):
                return None

            if port is not None:

                if not self.validate_port(
                    port
                ):
                    return None

                port = int(port)

        else:

            parsed = self.parse_target(
                target
            )

            if not parsed:
                return None

            ip = parsed["ip"]
            port = parsed["port"]

        result = ScanResult(
            ip,
            port,
        )

        try:

            # ----------------------------------------------------
            # Reverse DNS
            # ----------------------------------------------------

            hostname = self.reverse_dns(
                ip
            )

            result.hostname = hostname

            result.provider = (
                self.detect_provider(
                    hostname
                )
            )

            # ----------------------------------------------------
            # GeoIP
            # ----------------------------------------------------

            geo = self.geo_lookup(
                ip
            )

            result.country = geo.get(
                "country",
                "Unknown",
            )

            result.city = geo.get(
                "city",
                "Unknown",
            )

            result.isp = geo.get(
                "isp",
                "Unknown",
            )

            result.asn = geo.get(
                "asn",
                "Unknown",
            )

            # ----------------------------------------------------
            # Ping
            # ----------------------------------------------------

            command = (
                self.build_ping_command(
                    ip
                )
            )

            process_timeout = (
                (
                    self.timeout
                    * self.ping_count
                )
                + 5
            )

            creationflags = 0

            if "windows" in self.system:

                creationflags = getattr(
                    subprocess,
                    "CREATE_NO_WINDOW",
                    0,
                )

            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=process_timeout,
                creationflags=creationflags,
            )

            output = (
                process.stdout
                + "\n"
                + process.stderr
            )

            pings = (
                self.extract_ping_values(
                    output
                )
            )

            packet_loss = (
                self.extract_packet_loss(
                    output
                )
            )

            result.pings = pings

            result.packet_loss = max(
                0,
                min(
                    100,
                    packet_loss,
                ),
            )

            # ----------------------------------------------------
            # Ping metrics
            # ----------------------------------------------------

            if pings:

                result.avg_ping = round(
                    sum(pings)
                    / len(pings),
                    2,
                )

                result.min_ping = min(
                    pings
                )

                result.max_ping = max(
                    pings
                )

                result.jitter = (
                    self.calculate_jitter(
                        pings
                    )
                )

                result.stability = (
                    self.calculate_stability(
                        pings
                    )
                )

                result.consistency = (
                    self.calculate_consistency(
                        pings
                    )
                )

                result.grade = (
                    self.determine_grade(
                        result.avg_ping,
                        result.packet_loss,
                    )
                )

                result.response_speed = (
                    self.detect_speed(
                        result.avg_ping
                    )
                )

                result.network_type = (
                    self.detect_network_type(
                        result.avg_ping
                    )
                )

                result.quality_score = (
                    self.calculate_quality_score(
                        result.avg_ping,
                        result.packet_loss,
                        result.stability,
                    )
                )

                result.status = "ONLINE"

            else:

                result.avg_ping = 9999
                result.min_ping = 9999
                result.max_ping = 9999

                result.grade = "F"
                result.network_type = "Unknown"
                result.response_speed = "Unknown"

                result.quality_score = 0

                result.status = "OFFLINE"

            # ----------------------------------------------------
            # TCP
            # ----------------------------------------------------

            if self.tcp_enabled:

                tcp_port = (
                    port
                    if port is not None
                    else 443
                )

                tcp_ok, tcp_latency = (
                    self.tcp_test(
                        ip,
                        tcp_port,
                    )
                )

                result.tcp_open = tcp_ok

                result.tcp_latency = (
                    tcp_latency
                )

            else:

                result.tcp_open = False
                result.tcp_latency = 0

            # ----------------------------------------------------
            # UDP
            # ----------------------------------------------------

            if self.udp_enabled:

                udp_port = (
                    port
                    if port is not None
                    else 53
                )

                udp_ok, udp_latency = (
                    self.udp_test(
                        ip,
                        udp_port,
                    )
                )

                result.udp_open = udp_ok

                result.udp_latency = (
                    udp_latency
                )

            else:

                result.udp_open = False
                result.udp_latency = 0

            # ----------------------------------------------------
            # Final score
            # ----------------------------------------------------

            result.network_score = (
                self.calculate_network_score(
                    result
                )
            )

            return result

        except subprocess.TimeoutExpired:

            result.status = "TIMEOUT"

            result.quality_score = 0
            result.network_score = 0

            logging.error(
                "Scan timeout: %s",
                result.target,
            )

            return result

        except Exception as error:

            result.status = "ERROR"

            result.quality_score = 0
            result.network_score = 0

            logging.error(
                "Scan error %s: %s",
                result.target,
                error,
            )

            return result

    # ============================================================
    # SORTING / RANKING
    # ============================================================

    def sort_results(self):

        self.results.sort(
            key=lambda result: (
                result.status != "ONLINE",
                result.packet_loss,
                result.avg_ping,
                -result.stability,
                -result.consistency,
                -result.network_score,
                -result.quality_score,
            )
        )

        for rank, result in enumerate(
            self.results,
            start=1,
        ):

            result.rank = rank

        if self.results:

            self.best_result = (
                self.results[0]
            )

        else:

            self.best_result = None

    # ============================================================
    # MULTI TARGET SCAN
    # ============================================================

    def scan_ips(self, ips):

        self.results = []
        self.best_result = None

        self.total_scanned = 0
        self.failed_scans = 0

        self.stop_scan = False

        targets = self.normalize_targets(
            ips
        )

        # IMPORTANT:
        # Dashboard uses this value to know
        # exactly when scanning is finished.

        self.expected_total = len(
            targets
        )

        if not targets:

            return []

        with ThreadPoolExecutor(
            max_workers=min(
                self.max_threads,
                len(targets),
            )
        ) as executor:

            futures = {
                executor.submit(
                    self.perform_scan,
                    target,
                ): target
                for target in targets
            }

            for future in as_completed(
                futures
            ):

                if self.stop_scan:

                    for pending_future in futures:

                        if not pending_future.done():
                            pending_future.cancel()

                    break

                target = futures[
                    future
                ]

                try:

                    result = future.result()

                    if result is None:

                        self.failed_scans += 1

                        continue

                    self.results.append(
                        result
                    )

                    self.total_scanned += 1

                    self.sort_results()

                except Exception as error:

                    self.failed_scans += 1

                    target_name = (
                        target.get(
                            "target",
                            str(target),
                        )
                        if isinstance(
                            target,
                            dict,
                        )
                        else str(target)
                    )

                    logging.error(
                        "Future error %s: %s",
                        target_name,
                        error,
                    )

        self.sort_results()

        return self.results

    def stop(self):

        self.stop_scan = True

    # ============================================================
    # EXPORT - JSON
    # ============================================================

    def export_json(
        self,
        path,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        data = [
            result.to_dict()
            for result in self.results
        ]

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ============================================================
    # EXPORT - CSV
    # ============================================================

    def export_csv(
        self,
        path,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.writer(
                file
            )

            writer.writerow([
                "Rank",
                "IP",
                "Port",
                "Target",
                "Hostname",
                "Country",
                "City",
                "ISP",
                "ASN",
                "Provider",
                "Avg Ping",
                "Min Ping",
                "Max Ping",
                "Packet Loss",
                "Jitter",
                "Stability",
                "Consistency",
                "TCP Latency",
                "UDP Latency",
                "TCP Open",
                "UDP Response",
                "Grade",
                "Network Type",
                "Quality Score",
                "Network Score",
                "Speed",
                "Status",
                "Scan Time",
            ])

            for result in self.results:

                writer.writerow([

                    result.rank,
                    result.ip,
                    result.port,
                    result.target,
                    result.hostname,
                    result.country,
                    result.city,
                    result.isp,
                    result.asn,
                    result.provider,
                    result.avg_ping,
                    result.min_ping,
                    result.max_ping,
                    result.packet_loss,
                    result.jitter,
                    result.stability,
                    result.consistency,
                    result.tcp_latency,
                    result.udp_latency,
                    result.tcp_open,
                    result.udp_open,
                    result.grade,
                    result.network_type,
                    result.quality_score,
                    result.network_score,
                    result.response_speed,
                    result.status,
                    result.scan_time,

                ])

    # ============================================================
    # EXPORT - TXT
    # ============================================================

    def export_txt(
        self,
        path,
    ):

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as file:

            for result in self.results:

                port_value = (
                    result.port
                    if result.port is not None
                    else "N/A"
                )

                file.write(
                    f"""
====================================================
RANK: {result.rank}
====================================================

TARGET:
{result.target}

IP ADDRESS:
{result.ip}

PORT:
{port_value}

HOSTNAME:
{result.hostname}

LOCATION:
{result.country} / {result.city}

ISP:
{result.isp}

ASN:
{result.asn}

PROVIDER:
{result.provider}

AVERAGE PING:
{result.avg_ping} ms

MINIMUM PING:
{result.min_ping} ms

MAXIMUM PING:
{result.max_ping} ms

PACKET LOSS:
{result.packet_loss}%

JITTER:
{result.jitter} ms

STABILITY:
{result.stability}

CONSISTENCY:
{result.consistency}

TCP LATENCY:
{result.tcp_latency} ms

UDP LATENCY:
{result.udp_latency} ms

TCP OPEN:
{result.tcp_open}

UDP RESPONSE:
{result.udp_open}

GRADE:
{result.grade}

NETWORK TYPE:
{result.network_type}

QUALITY SCORE:
{result.quality_score}

NETWORK SCORE:
{result.network_score}

RESPONSE SPEED:
{result.response_speed}

STATUS:
{result.status}

SCAN TIME:
{result.scan_time}

====================================================

"""
                )

    # ============================================================
    # SUMMARY
    # ============================================================

    def generate_summary(self):

        online = [
            result
            for result in self.results
            if result.status == "ONLINE"
        ]

        offline = [
            result
            for result in self.results
            if result.status != "ONLINE"
        ]

        average_ping = 0

        if online:

            valid_pings = [
                result.avg_ping
                for result in online
                if result.avg_ping < 9999
            ]

            if valid_pings:

                average_ping = round(
                    sum(valid_pings)
                    / len(valid_pings),
                    2,
                )

        return {

            "total": len(
                self.results
            ),

            "online": len(
                online
            ),

            "offline": len(
                offline
            ),

            "failed": self.failed_scans,

            "average_ping": (
                average_ping
            ),

            "best_ip": (
                self.best_result.target
                if self.best_result
                else "N/A"
            ),

            "best_score": (
                self.best_result.network_score
                if self.best_result
                else 0
            ),

            "time": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }