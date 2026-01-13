"""Official CyberLicensing helper library.

This package exposes two primary interfaces:

- :class:`cyberlicensing.client.LicenseClient` for end-users validating licenses
- :class:`cyberlicensing.manager.ManagerClient` for operators managing projects

Utility helpers live in :mod:`cyberlicensing.environment` for gathering HWID/IP metadata.
"""

from .client import LicenseClient
from .manager import ManagerClient
from .environment import (
    get_machine_fingerprint,
    get_public_ip,
    collect_environment_metadata,
)
from .exceptions import (
    CyberLicensingError,
    AuthenticationError,
    ApiError,
    BadRequestError,
    ForbiddenError,
    NotFoundError,
)

__all__ = [
    "LicenseClient",
    "ManagerClient",
    "get_machine_fingerprint",
    "get_public_ip",
    "collect_environment_metadata",
    "CyberLicensingError",
    "AuthenticationError",
    "ApiError",
    "BadRequestError",
    "ForbiddenError",
    "NotFoundError",
]
