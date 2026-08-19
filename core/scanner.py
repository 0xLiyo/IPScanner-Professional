# ================================
# FILE: core/scanner.py
# ================================

import os
import re
import csv
import json
import time
import queue
import socket
import random
import logging
import platform
import statistics
import subprocess

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

class ScanResult:

    def __init__(self, ip):

        self.ip = ip

        self.hostname = "-"
        self.country = "Unknown"
        self.city = "Unknown"
        self.isp = "Unknown"
        self.asn = "Unknown"

        self.provider = "Unknown"

        self.pings = []

        self.avg_ping = 9999
        self.min_ping = 9999
        self.max_ping = 9999

        self.packet_loss = 100

        self.jitter = 0
        self.stability = 0
        self.consistency = 0

        self.tcp_latency = 9999
        self.udp_latency = 9999

        self.tcp_open = False
        self.udp_open = False

        self.grade = "F"

        self.network_type = "Unknown"

        self.quality_score = 0
        self.network_score = 0

        self.response_speed = "Unknown"

        self.status = "OFFLINE"

        self.rank = 0

        self.scan_time = time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def to_dict(self):

        return {
            "rank": self.rank,
            "ip": self.ip,
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
            "scan_time": self.scan_time
        }

class ProfessionalScanner:

    def __init__(self, config):

        self.config = config

        self.results = []

        self.best_result = None

        self.total_scanned = 0

        self.failed_scans = 0

        self.max_threads = config["threads"]

        self.timeout = config["timeout"]

        self.ping_count = config["ping_count"]

        self.system = platform.system().lower()

        self.stop_scan = False

    def validate_ip(self, ip):

        pattern = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"

        if not re.match(pattern, ip):
            return False

        parts = ip.split(".")

        for part in parts:

            if int(part) > 255:
                return False

        return True

    def build_ping_command(self, ip):

        if "windows" in self.system:

            return [
                "ping",
                "-n",
                str(self.ping_count),
                "-w",
                str(self.timeout * 1000),
                ip
            ]

        return [
            "ping",
            "-c",
            str(self.ping_count),
            "-W",
            str(self.timeout),
            ip
        ]

    def extract_ping_values(self, output):

        values = []

        matches = re.findall(
            r"time[=<]?\s?(\d+)",
            output.lower()
        )

        for match in matches:

            try:

                values.append(int(match))

            except:
                pass

        return values

    def extract_packet_loss(self, output):

        output = output.lower()

        patterns = [
            r"(\d+)% packet loss",
            r"(\d+)% loss",
            r"lost = \d+ \((\d+)% loss\)"
        ]

        for pattern in patterns:

            match = re.search(pattern, output)

            if match:

                try:
                    return int(match.group(1))
                except:
                    pass

        return 100

    def calculate_jitter(self, pings):

        if len(pings) < 2:
            return 0

        diffs = []

        for i in range(1, len(pings)):

            diffs.append(
                abs(pings[i] - pings[i - 1])
            )

        return round(
            sum(diffs) / len(diffs),
            2
        )

    def calculate_stability(self, pings):

        if len(pings) < 2:
            return 0

        deviation = statistics.stdev(pings)

        stability = max(
            0,
            100 - deviation
        )

        return round(stability, 2)

    def calculate_consistency(self, pings):

        if not pings:
            return 0

        avg = sum(pings) / len(pings)

        stable_hits = 0

        for ping in pings:

            if abs(ping - avg) <= 10:
                stable_hits += 1

        return round(
            (stable_hits / len(pings)) * 100,
            2
        )

    def determine_grade(self, avg_ping, loss):

        if loss >= 100:
            return "F"

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

    def detect_network_type(self, avg_ping):

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
        stability
    ):

        score = 100

        score -= avg_ping * 0.35

        score -= packet_loss * 0.9

        score += stability * 0.2

        score = max(
            0,
            min(100, score)
        )

        return round(score, 2)

    def calculate_network_score(
        self,
        result
    ):

        score = 0

        score += max(
            0,
            50 - result.avg_ping
        )

        score += max(
            0,
            30 - result.packet_loss
        )

        score += result.stability * 0.2

        score += result.quality_score * 0.3

        return round(score, 2)

    def reverse_dns(self, ip):

        try:

            return socket.gethostbyaddr(ip)[0]

        except:

            return "-"

    def detect_provider(self, hostname):

        hostname = hostname.lower()

        providers = {
            "cloudflare": "Cloudflare",
            "akamai": "Akamai",
            "amazon": "AWS",
            "google": "Google",
            "facebook": "Meta",
            "microsoft": "Azure",
            "fastly": "Fastly",
            "cdn": "CDN"
        }

        for key, value in providers.items():

            if key in hostname:
                return value

        return "Unknown"

    def tcp_test(self, ip, port=443):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        sock.settimeout(self.timeout)

        start = time.time()

        try:

            result = sock.connect_ex((ip, port))

            latency = round(
                (time.time() - start) * 1000,
                2
            )

            sock.close()

            if result == 0:
                return True, latency

            return False, latency

        except:

            return False, 9999

    def udp_test(self, ip, port=53):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.settimeout(self.timeout)

        start = time.time()

        try:

            sock.sendto(
                b"test",
                (ip, port)
            )

            latency = round(
                (time.time() - start) * 1000,
                2
            )

            sock.close()

            return True, latency

        except:

            return False, 9999

    def geo_lookup(self, ip):

        try:

            import requests

            response = requests.get(
                f"http://ip-api.com/json/{ip}",
                timeout=5
            )

            data = response.json()

            return {
                "country": data.get(
                    "country",
                    "Unknown"
                ),
                "city": data.get(
                    "city",
                    "Unknown"
                ),
                "isp": data.get(
                    "isp",
                    "Unknown"
                ),
                "asn": data.get(
                    "as",
                    "Unknown"
                )
            }

        except:

            return {
                "country": "Unknown",
                "city": "Unknown",
                "isp": "Unknown",
                "asn": "Unknown"
            }
# ================================
# CONTINUE: core/scanner.py
# ================================

    def perform_scan(self, ip):

        result = ScanResult(ip)

        try:

            hostname = self.reverse_dns(ip)

            result.hostname = hostname

            result.provider = self.detect_provider(
                hostname
            )

            geo = self.geo_lookup(ip)

            result.country = geo["country"]
            result.city = geo["city"]
            result.isp = geo["isp"]
            result.asn = geo["asn"]

            command = self.build_ping_command(ip)

            process = subprocess.run(
                command,
                capture_output=True,
                text=True
            )

            output = process.stdout

            pings = self.extract_ping_values(
                output
            )

            packet_loss = self.extract_packet_loss(
                output
            )

            result.pings = pings

            result.packet_loss = packet_loss

            if pings:

                result.avg_ping = round(
                    sum(pings) / len(pings),
                    2
                )

                result.min_ping = min(pings)

                result.max_ping = max(pings)

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
                        packet_loss
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
                        packet_loss,
                        result.stability
                    )
                )

                result.network_score = (
                    self.calculate_network_score(
                        result
                    )
                )

                result.status = "ONLINE"

            tcp_ok, tcp_latency = self.tcp_test(
                ip
            )

            result.tcp_open = tcp_ok

            result.tcp_latency = tcp_latency

            udp_ok, udp_latency = self.udp_test(
                ip
            )

            result.udp_open = udp_ok

            result.udp_latency = udp_latency

        except Exception as error:

            logging.error(
                f"Scan Error {ip}: {error}"
            )

            result.status = "ERROR"

        return result

    def sort_results(self):

        self.results.sort(
            key=lambda x: (
                x.packet_loss,
                x.avg_ping,
                -x.stability,
                -x.consistency,
                -x.network_score,
                -x.quality_score
            )
        )

        rank = 1

        for result in self.results:

            result.rank = rank

            rank += 1

        if self.results:

            self.best_result = self.results[0]

    def scan_ips(self, ips):

        clean_ips = []

        for ip in ips:

            ip = ip.strip()

            if self.validate_ip(ip):

                if ip not in clean_ips:

                    clean_ips.append(ip)

        with ThreadPoolExecutor(
            max_workers=self.max_threads
        ) as executor:

            futures = {

                executor.submit(
                    self.perform_scan,
                    ip
                ): ip

                for ip in clean_ips

            }

            for future in as_completed(futures):

                if self.stop_scan:
                    break

                try:

                    result = future.result()

                    self.results.append(result)

                    self.total_scanned += 1

                    self.sort_results()

                except Exception as error:

                    logging.error(
                        f"Future Error: {error}"
                    )

                    self.failed_scans += 1

        self.sort_results()

        return self.results

    def stop(self):

        self.stop_scan = True

    def export_json(self, path):

        data = [
            result.to_dict()
            for result in self.results
        ]

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4
            )

    def export_csv(self, path):

        with open(
            path,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "Rank",
                "IP",
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
                "UDP Open",
                "Grade",
                "Network Type",
                "Quality Score",
                "Network Score",
                "Speed",
                "Status",
                "Scan Time"
            ])

            for result in self.results:

                writer.writerow([

                    result.rank,
                    result.ip,
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
                    result.scan_time

                ])

    def export_txt(self, path):

        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:

            for result in self.results:

                file.write(f"""

====================================================
RANK: {result.rank}
====================================================

IP ADDRESS:
{result.ip}

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
{result.jitter}

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

UDP OPEN:
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

""")

    def generate_summary(self):

        online = [
            x for x in self.results
            if x.status == "ONLINE"
        ]

        offline = [
            x for x in self.results
            if x.status != "ONLINE"
        ]

        avg_ping = 0

        if online:

            avg_ping = round(

                sum(
                    x.avg_ping
                    for x in online
                ) / len(online),

                2

            )

        return {

            "total": len(self.results),

            "online": len(online),

            "offline": len(offline),

            "average_ping": avg_ping,

            "best_ip": (
                self.best_result.ip
                if self.best_result
                else "N/A"
            )

        }        