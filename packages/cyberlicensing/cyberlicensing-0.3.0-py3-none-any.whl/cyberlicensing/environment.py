"""Environment helpers for CyberLicensing SDK."""

from __future__ import annotations

import hashlib
import platform
import socket
import uuid
from typing import Dict, Optional

import requests

PUBLIC_IP_ENDPOINT = "https://api.ipify.org?format=json"


def get_public_ip(timeout: float = 3.0) -> Optional[str]:
    """Return the machine's public IP using a lightweight HTTPS call."""

    try:
        response = requests.get(PUBLIC_IP_ENDPOINT, timeout=timeout)
        response.raise_for_status()
        return response.json().get("ip")
    except Exception:
        return None


def get_machine_fingerprint() -> str:
    """Compute a stable machine fingerprint using MAC + platform info."""

    mac = uuid.getnode()
    platform_bits = platform.platform()
    processor = platform.processor()
    base_string = f"{mac}-{platform_bits}-{processor}"
    digest = hashlib.sha256(base_string.encode("utf-8")).hexdigest()
    return digest


def collect_environment_metadata(include_public_ip: bool = False) -> Dict[str, Optional[str]]:
    """Gather useful metadata (HWID only by default).

    Note: Public IP is captured automatically by the server.
    """

    metadata: Dict[str, Optional[str]] = {
        "hwid": get_machine_fingerprint(),
    }

    # Ces champs ne sont inclus que si explicitement demandé
    # et nécessitent une configuration client_editable côté projet
    if include_public_ip:
        metadata["ip"] = get_public_ip()

    return metadata
