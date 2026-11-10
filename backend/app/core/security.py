"""
URL validation and SSRF protection for OmniSight.

Any URL submitted by users (e.g. the target_url of a task) is validated here
before the automation engine is allowed to open it.  Private / loopback addresses
are blocked so that the automation engine cannot be weaponised to probe internal
infrastructure.
"""

import ipaddress
import socket
from urllib.parse import urlparse

from app.core.exceptions import SecurityException

# ── Private / reserved ranges that must never be reached ─────────────────────
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),   # link-local
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("100.64.0.0/10"),    # shared address space
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 unique-local
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
]

_BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal", "169.254.169.254"}


def is_private_ip(ip: str) -> bool:
    """Return True if the IP address falls within a private/reserved range."""
    try:
        addr = ipaddress.ip_address(ip)
        return any(addr in network for network in _PRIVATE_NETWORKS)
    except ValueError:
        # Malformed IP — treat as unsafe
        return True


def validate_url(url: str) -> bool:
    """
    Validate that *url* is a safe, publicly-reachable HTTP/HTTPS URL.

    Checks performed:
    1. Scheme must be http or https.
    2. Hostname must not be in the blocked-hostname list.
    3. All resolved IPs must be public (not private/loopback/link-local).

    Raises SecurityException with a descriptive message on any violation.
    Returns True when the URL passes all checks.
    """
    if not url:
        raise SecurityException("URL must not be empty.")

    parsed = urlparse(url)

    # 1. Scheme check
    if parsed.scheme not in ("http", "https"):
        raise SecurityException(
            f"URL scheme '{parsed.scheme}' is not allowed. Only http and https are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise SecurityException("URL does not contain a valid hostname.")

    # 2. Blocked hostname check (case-insensitive)
    if hostname.lower() in _BLOCKED_HOSTNAMES:
        raise SecurityException(
            f"Access to '{hostname}' is not permitted (blocked hostname)."
        )

    # 3. DNS resolution + IP range check
    try:
        addr_infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise SecurityException(
            f"Could not resolve hostname '{hostname}': {exc}"
        ) from exc

    if not addr_infos:
        raise SecurityException(f"Hostname '{hostname}' resolved to no addresses.")

    for addr_info in addr_infos:
        # addr_info = (family, type, proto, canonname, sockaddr)
        # sockaddr is (ip, port) for IPv4 or (ip, port, flow, scope) for IPv6
        ip = addr_info[4][0]
        if is_private_ip(ip):
            raise SecurityException(
                f"URL '{url}' resolves to a private/reserved IP address ({ip}), "
                "which is not permitted (SSRF protection)."
            )

    return True
