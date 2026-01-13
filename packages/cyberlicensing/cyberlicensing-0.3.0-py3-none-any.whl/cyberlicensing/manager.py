"""Manager-side client for CyberLicensing operations."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

from .exceptions import ApiError, AuthenticationError, BadRequestError, ForbiddenError, NotFoundError


class ManagerClient:
    def __init__(self, base_url: str, token: Optional[str] = None, timeout: float = 5.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.token = token

    # --- Auth helpers ---
    def authenticate(
        self,
        username: str,
        *,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> str:
        if not username:
            raise AuthenticationError("username is required")
        if (password is None and api_key is None) or (password is not None and api_key is not None):
            raise AuthenticationError("Provide exactly one of password or api_key")

        payload: Dict[str, Any] = {"username": username}
        if password is not None:
            payload["password"] = password
        else:
            payload["api_key"] = api_key

        response = requests.post(
            f"{self.base_url}/api/login",
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            message = "Invalid credentials"
            try:
                data = response.json()
            except ValueError:
                data = None
            if isinstance(data, dict) and data.get("msg"):
                message = data["msg"]
            raise AuthenticationError(message)
        token = response.json().get("access_token")
        if not token:
            raise AuthenticationError("Unable to retrieve access token")
        self.token = token
        return token

    def _headers(self) -> Dict[str, str]:
        if not self.token:
            raise AuthenticationError("JWT token missing. Call authenticate() first or set token.")
        return {"Authorization": f"Bearer {self.token}"}

    def _request(self, method: str, path: str, require_auth: bool = True, **kwargs):
        headers = kwargs.pop('headers', {})
        if require_auth:
            headers.update(self._headers())
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        if response.status_code >= 400:
            payload = None
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
            # Raise specific exceptions for common error codes
            if response.status_code == 400:
                raise BadRequestError(message, payload)
            elif response.status_code == 403:
                raise ForbiddenError(message, payload)
            elif response.status_code == 404:
                raise NotFoundError(message, payload)
            else:
                raise ApiError(response.status_code, message, payload)
        if response.content:
            return response.json()
        return None

    # --- Project helpers ---
    def list_projects(self) -> List[Dict]:
        return self._request('GET', '/api/projects')

    def create_project(self, name: str, description: Optional[str] = None) -> Dict:
        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        return self._request('POST', '/api/projects', json=payload)

    def add_project_manager(self, project_id: int, username: str) -> Dict:
        payload = {"username": username}
        return self._request('POST', f'/api/projects/{project_id}/add_manager', json=payload)

    def update_metadata_schema(self, project_id: int, fields: List[Dict[str, Any]]) -> Dict:
        return self._request('PUT', f'/api/projects/{project_id}/metadata_fields', json={"fields": fields})

    def list_licenses(self, project_id: int) -> List[Dict]:
        return self._request('GET', f'/api/projects/{project_id}/licenses')

    def get_license_by_key(self, project_id: int, license_key: str) -> Dict:
        """Retrieve a single license by its key.

        This is more efficient than fetching all licenses when you only need
        to look up one license by its key. The key is automatically converted
        to uppercase to avoid case mismatches.

        Parameters
        ----------
        project_id:
            The project ID that owns the license.
        license_key:
            The license key to look up (e.g., "CL-XXXX-XXXX").

        Returns
        -------
        Dict containing the license data.

        Raises
        ------
        BadRequestError:
            If the key parameter is missing or invalid (HTTP 400).
        ForbiddenError:
            If the token doesn't have access to this project (HTTP 403).
        NotFoundError:
            If the license key doesn't exist in the project (HTTP 404).
        """
        # Convert key to uppercase to avoid case mismatches
        normalized_key = license_key.upper()
        return self._request('GET', f'/api/projects/{project_id}/licenses/by_key?key={normalized_key}')

    def create_license(
        self,
        project_id: int,
        days_valid: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        payload: Dict[str, object] = {}
        if days_valid is not None:
            payload['days_valid'] = days_valid
        if metadata is not None:
            payload['metadata'] = metadata
        return self._request('POST', f'/api/projects/{project_id}/licenses', json=payload)

    def update_license(
        self,
        license_id: int,
        *,
        is_active: Optional[bool] = None,
        expires_at: Optional[str] = None,
        reset_hwid: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict:
        payload: Dict[str, object] = {}
        if is_active is not None:
            payload['is_active'] = is_active
        if expires_at is not None:
            payload['expires_at'] = expires_at
        if reset_hwid:
            payload['reset_hwid'] = True
        if metadata is not None:
            payload['metadata'] = metadata
        return self._request('PUT', f'/api/licenses/{license_id}', json=payload)

    def extend_license(self, project_id: int, license_id: int, days: int) -> Dict:
        """Convenience helper to push expiration forward by *days*."""

        licenses = self.list_licenses(project_id)
        license_data = next((lic for lic in licenses if lic['id'] == license_id), None)
        if not license_data:
            raise ApiError(404, f"License {license_id} not found in project {project_id}", {})

        expires_at = license_data.get('expires_at')
        if not expires_at:
            raise ApiError(400, "License is lifetime; set an explicit expiration first", {})

        try:
            current_exp = datetime.fromisoformat(expires_at)
        except ValueError as exc:
            raise ApiError(500, f"Invalid expiration format: {expires_at}", {"error": str(exc)})

        new_expiration = (current_exp + timedelta(days=days)).date().isoformat()
        return self.update_license(license_id, expires_at=new_expiration)

    def delete_license(self, license_id: int) -> Dict:
        return self._request('DELETE', f'/api/licenses/{license_id}')

    # --- API key helpers ---
    def list_api_keys(self) -> List[Dict[str, Any]]:
        return self._request('GET', '/api/api_keys')

    def create_api_key(
        self,
        label: str,
        *,
        project_ids: Optional[List[int]] = None,
        allow_all_projects: bool = False,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "label": label,
            "allow_all_projects": allow_all_projects,
        }
        if project_ids is not None:
            payload["project_ids"] = project_ids
        return self._request('POST', '/api/api_keys', json=payload)

    def update_api_key(
        self,
        api_key_id: int,
        *,
        label: Optional[str] = None,
        project_ids: Optional[List[int]] = None,
        allow_all_projects: Optional[bool] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if label is not None:
            payload["label"] = label
        if project_ids is not None:
            payload["project_ids"] = project_ids
        if allow_all_projects is not None:
            payload["allow_all_projects"] = allow_all_projects
        if not payload:
            raise ValueError("At least one field must be provided to update an API key")
        return self._request('PUT', f'/api/api_keys/{api_key_id}', json=payload)

    def delete_api_key(self, api_key_id: int) -> Dict[str, Any]:
        return self._request('DELETE', f'/api/api_keys/{api_key_id}')

    def list_project_api_keys(self, project_id: int) -> List[Dict[str, Any]]:
        return self._request('GET', f'/api/projects/{project_id}/api_keys')
