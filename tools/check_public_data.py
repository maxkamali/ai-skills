#!/usr/bin/env python3
"""Fail when repository text contains obvious non-public operational data."""

from __future__ import annotations

import argparse
import ipaddress
import re
from pathlib import Path

TEXT_SUFFIXES = {
    ".md", ".txt", ".py", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".conf", ".sh", ".xml", ".csv", ".tsv",
}
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "dist"}
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
IPV4_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6_TOKEN_RE = re.compile(r"(?<![\w:])(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:]{0,4}(?![\w:])")

ALLOWED_V4 = [
    ipaddress.ip_network("192.0.2.0/24"),
    ipaddress.ip_network("198.51.100.0/24"),
    ipaddress.ip_network("203.0.113.0/24"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("0.0.0.0/32"),
]
ALLOWED_V6 = [
    ipaddress.ip_network("2001:db8::/32"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("::/128"),
]


def allowed_ip(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return True
    networks = ALLOWED_V4 if address.version == 4 else ALLOWED_V6
    return any(address in network for network in networks)


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    findings: list[str] = []
    for number, line in enumerate(text.splitlines(), 1):
        if EMAIL_RE.search(line):
            findings.append(f"{path}:{number}: email address")
        for match in IPV4_RE.finditer(line):
            value = match.group(0)
            if not allowed_ip(value):
                findings.append(f"{path}:{number}: non-documentation IPv4 {value}")
        for match in IPV6_TOKEN_RE.finditer(line):
            value = match.group(0)
            try:
                parsed = str(ipaddress.ip_address(value))
            except ValueError:
                continue
            if not allowed_ip(parsed):
                findings.append(f"{path}:{number}: non-documentation IPv6 {value}")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "LICENSE" or path.suffix.lower() in TEXT_SUFFIXES:
            findings.extend(scan_file(path))
    if findings:
        print("Public-data scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Public-data scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
