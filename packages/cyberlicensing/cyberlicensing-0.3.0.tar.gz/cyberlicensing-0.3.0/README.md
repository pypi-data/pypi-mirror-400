# CyberLicensing Python SDK

> Client and manager helpers for integrating public validation flows and project operations with the CyberLicensing API.

**License client** – validates license keys, collects environment metadata and lets end-users update `client_editable` fields.
**Manager client** – handles authentication plus CRUD operations for projects, metadata schemas and licenses.
**Environment helpers** – gather HWID, local/public IPs and other contextual information in one call.

The SDK targets Python 3.9+ and is published to PyPI as `cyberlicensing`.

## Installation

```bash
pip install cyberlicensing
```



## Quick start

### Validate a license key

```python
from cyberlicensing import LicenseClient

client = LicenseClient(
  base_url="https://licensing.showdown.boo",
  project_id=42,
)

# Automatically collects HWID, LAN/public IP, etc.
result = client.validate_with_environment("CL-XXXX-XXXX")
print(result)
```

To control the payload manually, call `validate_license` and pass `hwid`, `ip`, and `metadata` yourself. The metadata must only contain fields that are marked `client_editable` in your project schema.

### Manage projects and licenses

```python
from cyberlicensing import ManagerClient

manager = ManagerClient(base_url="https://licensing.showdown.boo")
manager.authenticate("automation_bot", api_key="sk_live_XXXXXXXXXXXXXXXX")

# Create project and create license
project = manager.create_project(
  name="My Awesome App",
  description="Tooling pour la communauté",
)
license_data = manager.create_license(
  project_id=project["id"],
  days_valid=30,
  metadata={"plan": "pro"},
)

# Revoke a license
manager.update_license(
    license_id=license_data["id"],
    is_active=False,
    metadata={"plan": "revoked", "notes": "Chargeback"},
)

# Update a license
manager.update_license(
  license_id=license_data["id"],
  metadata={"plan": "enterprise", "notes": "Upgraded"},
)

# Delegate day-to-day operations to another teammate
manager.add_project_manager(project_id=project["id"], username="support_team")
```

More helpers are exposed for listing projects/licenses, extending expirations, resetting HWIDs, or deleting keys entirely.

### Look up a license by key

For efficiency, use `get_license_by_key` when you only need to look up a single license instead of fetching all licenses:

```python
try:
    license_data = manager.get_license_by_key(
        project_id=42,
        license_key="CL-XXXX-XXXX"
    )
    print(f"License ID: {license_data['id']}, Active: {license_data['is_active']}")
except NotFoundError:
    print("License key not found in this project")
except ForbiddenError:
    print("Insufficient permissions for this project")
```

The key is automatically normalized to uppercase to avoid case mismatches. This method is ideal for dashboards and support tools that need to quickly retrieve license details by key.

### API key management

Automations or SDKs can provision scoped API keys and rotate them without touching end-user credentials.

```python
manager = ManagerClient(base_url="https://licensing.showdown.boo")
manager.authenticate("admin", password="password")

# Create a key limited to a project (secret is returned once)
api_key = manager.create_api_key(
  label="CI Runner",
  project_ids=[project["id"]],
  allow_all_projects=False,
)

# Update its scopes or friendly label
manager.update_api_key(
  api_key_id=api_key["id"],
  project_ids=[project["id"], 7],
)

# Dashboard helper: only show keys relevant to a project
manager.list_project_api_keys(project_id=project["id"])

# Cleanup when the automation is retired
manager.delete_api_key(api_key_id=api_key["id"])
```

Use `manager.list_api_keys()` to render an operator-wide view (active + revoked keys).

## Client-editable metadata workflow

Certain metadata fields can be safely mutated by the end-user thanks to the `client_editable` flag defined in the project schema.

1. **Manager** defines the schema:

```python
from cyberlicensing import ManagerClient

manager = ManagerClient(base_url="https://licensing.showdown.boo")
manager.authenticate("admin", "password")

manager.update_metadata_schema(
  project_id=42,
  fields=[
    {"name": "notes", "type": "string", "client_editable": True},
    {"name": "plan", "type": "string", "client_editable": False},
  ],
)
```

2. **Client** updates the editable fields:

```python
from cyberlicensing import LicenseClient

client = LicenseClient(base_url="https://licensing.showdown.boo", project_id=42)

client.update_client_metadata(
  key="CL-XXXX-XXXX",
  metadata={"notes": "Nouvelle machine"},
)
```

`update_client_metadata` validates locally that `project_id` is an `int` and the `metadata` dictionary is non-empty before calling `POST /api/client_metadata`. Server responses bubble up any JSON `msg` errors through `ApiError` for easier debugging (e.g., non editable field, inactive key, etc.).

## Environment helpers

```python
from cyberlicensing import collect_environment_metadata

print(collect_environment_metadata())
```

The helper returns HWID, hostname, LAN IP, optional public IP, and other useful attributes. Use it to enrich `validate_license` calls or to store telemetry on validated machines.

## Error handling

The SDK provides specific exception classes for common HTTP errors:

- `BadRequestError` – raised for HTTP 400 (Bad Request, e.g., missing or invalid parameters)
- `ForbiddenError` – raised for HTTP 403 (Forbidden, e.g., insufficient project scope)
- `NotFoundError` – raised for HTTP 404 (Not Found, e.g., unknown license key)
- `ApiError(status_code, message, payload)` – generic error for other HTTP ≥ 400 responses
- `AuthenticationError` – surfaces authentication/authorization issues in manager flows
- `CyberLicensingError` – base class for all SDK exceptions for easy broad exception handling

All error classes include a `status_code` and `payload` for detailed debugging:

```python
from cyberlicensing import ApiError, BadRequestError, ForbiddenError, NotFoundError

try:
    license_data = manager.get_license_by_key(project_id=42, license_key="CL-XXXX")
except BadRequestError as exc:
    print(f"Invalid request: {exc}")
except ForbiddenError as exc:
    print(f"Access denied to project: {exc}")
except NotFoundError as exc:
    print(f"License not found: {exc}")
except ApiError as exc:
    print(f"API error {exc.status_code}: {exc}")
    print(exc.payload)
```

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m build
```

Additional helpers:

- `list_licenses(project_id)` – list all licenses (keys + live metadata and usage counters) for a project (prefer `get_license_by_key` for single lookups)
- `get_license_by_key(project_id, license_key)` – efficiently retrieve a single license by its key (automatically normalized to uppercase)
- `create_license(project_id, days_valid=None, metadata=None)` – generate a new license key
- `update_license(license_id, is_active=None, expires_at=None, reset_hwid=False, metadata=None)` – ban/disable, move expiration, reset HWID, or overwrite metadata
- `extend_license(project_id, license_id, days)` – convenience method to push expiration forward
- `delete_license(license_id)` – hard-delete a key
- `add_project_manager(project_id, username)` – delegate back-office access to teammates
- `create_api_key(label, project_ids=None, allow_all_projects=False)` – mint scoped API keys from the dashboard
- `update_api_key(api_key_id, ...)`/`delete_api_key(api_key_id)` – rotate or revoke keys instantly
- `list_api_keys()`/`list_project_api_keys(project_id)` – audit keys globally or per project

## Environment helpers

```python
from cyberlicensing import collect_environment_metadata

print(collect_environment_metadata())
```

Returns HWID, hostname, LAN IP, and (if available) public IP.
