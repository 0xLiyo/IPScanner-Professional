# ================================
# FILE: core/security.py
# ================================

import ipaddress
import re


class SecurityUtils:

    # ============================================================
    # IP
    # ============================================================

    @staticmethod
    def validate_ipv4(ip):

        try:

            address = ipaddress.ip_address(
                str(ip).strip()
            )

            return (
                address.version == 4
            )

        except ValueError:

            return False

    # ============================================================
    # PORT
    # ============================================================

    @staticmethod
    def validate_port(port):

        try:
            port = int(port)
        except (
            TypeError,
            ValueError,
        ):
            return False

        return 1 <= port <= 65535

    # ============================================================
    # TARGET
    # ============================================================

    @classmethod
    def parse_target(cls, target):

        if target is None:
            return None

        target = str(
            target
        ).strip()

        target = target.strip(
            "\"'[](),"
        )

        if not target:
            return None

        # IP:PORT
        match = re.fullmatch(
            r"^"
            r"(\d{1,3}"
            r"(?:\.\d{1,3}){3})"
            r":"
            r"(\d{1,5})"
            r"$",
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

            if not cls.validate_ipv4(ip):
                return None

            if not cls.validate_port(port):
                return None

            return {
                "ip": ip,
                "port": port,
                "target": f"{ip}:{port}",
            }

        # IP only
        if cls.validate_ipv4(target):

            return {
                "ip": target,
                "port": None,
                "target": target,
            }

        return None

    # ============================================================
    # FILENAME
    # ============================================================

    @staticmethod
    def sanitize_filename(
        filename,
        default="export",
    ):

        if not filename:
            return default

        filename = str(
            filename
        ).strip()

        filename = re.sub(
            r'[<>:"/\\|?*\x00-\x1f]',
            "_",
            filename,
        )

        filename = filename.strip(
            ". "
        )

        return (
            filename
            if filename
            else default
        )

    # ============================================================
    # INTEGER
    # ============================================================

    @staticmethod
    def clamp_int(
        value,
        minimum,
        maximum,
        default=None,
    ):

        try:
            value = int(value)
        except (
            TypeError,
            ValueError,
        ):

            if default is not None:
                return default

            return minimum

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )

    # ============================================================
    # FLOAT
    # ============================================================

    @staticmethod
    def clamp_float(
        value,
        minimum,
        maximum,
        default=None,
    ):

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):

            if default is not None:
                return default

            return minimum

        return max(
            minimum,
            min(
                maximum,
                value,
            ),
        )