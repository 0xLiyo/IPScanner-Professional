# ================================
# FILE: core/port_scanner.py
# ================================

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


class PortScanner:

    def __init__(
        self,
        timeout=1,
        max_threads=100,
    ):
        self.timeout = max(
            0.1,
            float(timeout),
        )

        self.max_threads = max(
            1,
            min(
                int(max_threads),
                500,
            ),
        )

    # ============================================================
    # SINGLE PORT
    # ============================================================

    def scan_port(self, ip, port):

        try:
            port = int(port)

            if not 1 <= port <= 65535:
                return {
                    "ip": ip,
                    "port": port,
                    "open": False,
                    "latency": 9999,
                    "error": "Invalid port",
                }

            sock = socket.socket(
                socket.AF_INET,
                socket.SOCK_STREAM,
            )

            sock.settimeout(
                self.timeout
            )

            start = socket.getdefaulttimeout()

            try:
                import time

                start_time = time.perf_counter()

                result = sock.connect_ex(
                    (
                        ip,
                        port,
                    )
                )

                latency = round(
                    (
                        time.perf_counter()
                        - start_time
                    ) * 1000,
                    2,
                )

            finally:
                sock.close()

            return {
                "ip": ip,
                "port": port,
                "open": result == 0,
                "latency": latency,
                "error": None,
            }

        except Exception as error:

            return {
                "ip": ip,
                "port": port,
                "open": False,
                "latency": 9999,
                "error": str(error),
            }

    # ============================================================
    # MULTIPLE PORTS
    # ============================================================

    def scan_ports(
        self,
        ip,
        ports,
    ):

        unique_ports = []

        seen = set()

        for port in ports:

            try:
                port = int(port)
            except (
                TypeError,
                ValueError,
            ):
                continue

            if not 1 <= port <= 65535:
                continue

            if port in seen:
                continue

            seen.add(port)
            unique_ports.append(port)

        if not unique_ports:
            return []

        results = []

        with ThreadPoolExecutor(
            max_workers=min(
                self.max_threads,
                len(unique_ports),
            )
        ) as executor:

            futures = {
                executor.submit(
                    self.scan_port,
                    ip,
                    port,
                ): port
                for port in unique_ports
            }

            for future in as_completed(
                futures
            ):

                try:
                    results.append(
                        future.result()
                    )

                except Exception:
                    pass

        results.sort(
            key=lambda item: item["port"]
        )

        return results

    # ============================================================
    # OPEN PORTS ONLY
    # ============================================================

    def scan_open_ports(
        self,
        ip,
        ports,
    ):

        results = self.scan_ports(
            ip,
            ports,
        )

        return [
            result
            for result in results
            if result["open"]
        ]