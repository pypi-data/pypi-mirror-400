"""Client-facing helpers for validating CyberLicensing keys."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .environment import collect_environment_metadata, get_machine_fingerprint, get_public_ip
from .exceptions import ApiError


class LicenseClient:
    """Simple wrapper for the public validation endpoint.

    Parameters
    ----------
    base_url:
        Base URL of the CyberLicensing API (e.g. ``"https://licensing.example.com"``).
    project_id:
        Owning project id, required by ``POST /api/validate_license`` to scope
        licenses per product.
    timeout:
        Optional HTTP timeout in seconds.
    """

    def __init__(self, base_url: str, project_id: int, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.project_id = project_id
        self.timeout = timeout

    def _handle_response(self, response: requests.Response) -> Dict:
        if response.status_code >= 400:
            payload: Optional[Dict[str, Any]] = None
            if response.content:
                try:
                    payload = response.json()
                except ValueError:
                    payload = None
            message = (
                payload.get("msg")
                if isinstance(payload, dict) and payload.get("msg")
                else response.text
            )
            raise ApiError(response.status_code, message, payload)
        if response.content:
            try:
                return response.json()
            except ValueError as exc:
                raise ApiError(response.status_code, f"Invalid JSON response: {exc}", None)
        return {}

    def validate_license(
        self,
        key: str,
        hwid: Optional[str] = None,
        ip: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        """Validate a license key against the public endpoint.

        The request payload matches the backend contract::

            {
                "project_id": 1,
                "key": "XXXX-XXXX-XXXX-XXXX",
                "hwid": "unique-hardware-id"
            }

        ``metadata`` can be supplied to share additional key-value pairs, but it
        must only contain fields flagged as ``client_editable`` in the project
        metadata schema configured by the project manager.
        """

        payload: Dict[str, Any] = {
            "project_id": self.project_id,
            "key": key,
        }
        if hwid:
            payload["hwid"] = hwid
        if ip:
            payload["ip"] = ip
        if metadata:
            payload["metadata"] = metadata

        response = requests.post(
            f"{self.base_url}/api/validate_license",
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    def validate_with_environment(self, key: str, extra_metadata: Optional[Dict[str, Any]] = None) -> Dict:
        """Validate a key while auto-populating the machine fingerprint as HWID.

        The public IP is captured automatically server-side, no need to send it.
        Only extra_metadata with client_editable fields can be provided.
        """

        hwid = get_machine_fingerprint()

        return self.validate_license(
            key=key,
            hwid=hwid,
            metadata=extra_metadata if extra_metadata else None,
        )

    def update_client_metadata(self, key: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Update client-editable metadata fields for a specific key.

        Parameters
        ----------
        key:
            License key to mutate.
        metadata:
            Non-empty dictionary of ``client_editable`` fields to update.
        """

        if not isinstance(self.project_id, int):
            raise ValueError("project_id must be an integer")
        if not isinstance(metadata, dict) or not metadata:
            raise ValueError("metadata must be a non-empty dictionary")

        payload = {
            "project_id": self.project_id,
            "key": key,
            "metadata": metadata,
        }
        response = requests.post(
            f"{self.base_url}/api/client_metadata",
            json=payload,
            timeout=self.timeout,
        )
        return self._handle_response(response)

    @staticmethod
    def get_default_hwid() -> str:
        return get_machine_fingerprint()

    @staticmethod
    def get_default_ip() -> Optional[str]:
        return get_public_ip()
