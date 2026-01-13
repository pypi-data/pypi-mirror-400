"""Storage connectors for reading and writing data.

Connectors provide a uniform interface for accessing data from different
storage backends (local filesystem, S3).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol
from urllib.parse import quote, urlparse

import boto3
import httpx
import jwt
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from .errors import ConnectorError
from .profiles import Profile


class Connector(Protocol):
    """Protocol for storage connectors."""

    async def fetch(self, location: str) -> bytes:
        """Fetch data from a location.

        Args:
            location: Path or URL to fetch from

        Returns:
            Raw bytes of the file content

        Raises:
            ConnectorError: If the fetch fails
        """
        ...

    async def put(self, location: str, data: bytes) -> None:
        """Write data to a location.

        Args:
            location: Path or URL to write to
            data: Raw bytes to write

        Raises:
            ConnectorError: If the write fails
        """
        ...


class LocalConnector:
    """Connector for local filesystem access."""

    async def fetch(self, location: str) -> bytes:
        """Fetch data from a local file.

        Args:
            location: Path to the file

        Returns:
            Raw bytes of the file content

        Raises:
            ConnectorError: If the file cannot be read
        """
        try:
            path = Path(location)
            return path.read_bytes()
        except FileNotFoundError:
            raise ConnectorError(f"File not found: {location}", "local")
        except OSError as e:
            raise ConnectorError(f"Error reading file: {e}", "local")

    async def put(self, location: str, data: bytes) -> None:
        """Write data to a local file.

        Args:
            location: Path to write to
            data: Raw bytes to write

        Raises:
            ConnectorError: If the file cannot be written
        """
        try:
            path = Path(location)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        except OSError as e:
            raise ConnectorError(f"Error writing file: {e}", "local")


class S3Connector:
    """Connector for Amazon S3 access.

    Supports custom endpoints (for MinIO, LocalStack, etc.) and
    both virtual-hosted and path-style addressing.

    Attributes:
        client: boto3 S3 client
        bucket: Default bucket name extracted from the initial URL
    """

    def __init__(self, client: boto3.client, bucket: str) -> None:
        self.client = client
        self.bucket = bucket

    @classmethod
    def from_profile_and_url(cls, profile: Profile, url: str) -> S3Connector:
        """Build an S3Connector from a profile and URL.

        Args:
            profile: Profile containing credentials and configuration
            url: S3 URL (s3://bucket/key)

        Returns:
            Configured S3Connector instance

        Raises:
            ConnectorError: If the URL is invalid or client cannot be created
        """
        parsed = urlparse(url)
        if parsed.scheme != "s3":
            raise ConnectorError(f"Invalid S3 URL scheme: {parsed.scheme}", "s3")

        bucket = parsed.netloc
        if not bucket:
            raise ConnectorError("Invalid S3 URL: missing bucket name", "s3")

        region = profile.region or "us-east-1"

        # Build boto3 client configuration
        client_kwargs: dict = {
            "service_name": "s3",
            "region_name": region,
        }

        # Custom endpoint (for MinIO, LocalStack, etc.)
        if profile.endpoint:
            client_kwargs["endpoint_url"] = profile.endpoint

        # Explicit credentials from profile
        if profile.access_key and profile.secret_key:
            client_kwargs["aws_access_key_id"] = profile.access_key
            client_kwargs["aws_secret_access_key"] = profile.secret_key

        # Path-style addressing configuration
        if profile.path_style:
            client_kwargs["config"] = BotoConfig(s3={"addressing_style": "path"})

        try:
            client = boto3.client(**client_kwargs)
        except Exception as e:
            raise ConnectorError(f"Failed to create S3 client: {e}", "s3")

        return cls(client=client, bucket=bucket)

    def _parse_s3_path(self, location: str) -> tuple[str, str]:
        """Parse an S3 location into bucket and key.

        Args:
            location: Either a full s3://bucket/key URL or just a key

        Returns:
            Tuple of (bucket, key)
        """
        if location.startswith("s3://"):
            parsed = urlparse(location)
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            return bucket, key
        else:
            # Assume it's just a key using the default bucket
            return self.bucket, location

    async def fetch(self, location: str) -> bytes:
        """Fetch data from S3.

        Args:
            location: S3 URL (s3://bucket/key) or key within default bucket

        Returns:
            Raw bytes of the object content

        Raises:
            ConnectorError: If the fetch fails
        """
        bucket, key = self._parse_s3_path(location)

        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "NoSuchKey":
                raise ConnectorError(f"Object not found: s3://{bucket}/{key}", "s3")
            raise ConnectorError(f"S3 error: {e}", "s3")
        except BotoCoreError as e:
            raise ConnectorError(f"S3 connection error: {e}", "s3")

    async def put(self, location: str, data: bytes) -> None:
        """Write data to S3.

        Args:
            location: S3 URL (s3://bucket/key) or key within default bucket
            data: Raw bytes to write

        Raises:
            ConnectorError: If the write fails
        """
        bucket, key = self._parse_s3_path(location)

        try:
            self.client.put_object(Bucket=bucket, Key=key, Body=data)
        except ClientError as e:
            raise ConnectorError(f"S3 upload error: {e}", "s3")
        except BotoCoreError as e:
            raise ConnectorError(f"S3 connection error: {e}", "s3")

    async def list_objects(self, prefix: str = "") -> list[str]:
        """List objects in the bucket with an optional prefix.

        Args:
            prefix: Optional prefix to filter objects

        Returns:
            List of object keys

        Raises:
            ConnectorError: If the list operation fails
        """
        try:
            paginator = self.client.get_paginator("list_objects_v2")
            keys = []

            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                for obj in page.get("Contents", []):
                    keys.append(obj["Key"])

            return keys
        except ClientError as e:
            raise ConnectorError(f"S3 list error: {e}", "s3")
        except BotoCoreError as e:
            raise ConnectorError(f"S3 connection error: {e}", "s3")


class GCSConnector:
    """Connector for Google Cloud Storage access.

    Uses service account JSON credentials with JWT bearer flow for OAuth2 tokens.
    Communicates with GCS via the REST API.

    Attributes:
        client_email: Service account email from credentials
        private_key: RSA private key for signing JWTs
        client: httpx AsyncClient for HTTP requests
    """

    def __init__(self, client_email: str, private_key: str) -> None:
        self.client_email = client_email
        self.private_key = private_key
        self.client = httpx.AsyncClient()

    @classmethod
    def from_profile_and_url(cls, profile: Profile, url: str) -> GCSConnector:
        """Build a GCSConnector from a profile and URL.

        Args:
            profile: Profile containing service_account_json
            url: GCS URL (gs://bucket/key)

        Returns:
            Configured GCSConnector instance

        Raises:
            ConnectorError: If credentials are missing or invalid
        """
        if not profile.service_account_json:
            raise ConnectorError("GCS profile missing service_account_json", "gcs")

        try:
            creds = json.loads(profile.service_account_json)
        except json.JSONDecodeError as e:
            raise ConnectorError(f"Invalid service account JSON: {e}", "gcs")

        client_email = creds.get("client_email")
        private_key = creds.get("private_key")

        if not client_email:
            raise ConnectorError("Missing client_email in service account JSON", "gcs")
        if not private_key:
            raise ConnectorError("Missing private_key in service account JSON", "gcs")

        return cls(client_email=client_email, private_key=private_key)

    async def _generate_access_token(self) -> str:
        """Generate an OAuth2 access token using JWT bearer flow.

        Returns:
            Access token string

        Raises:
            ConnectorError: If token generation fails
        """
        now = int(time.time())
        claims = {
            "iss": self.client_email,
            "scope": "https://www.googleapis.com/auth/cloud-platform",
            "aud": "https://oauth2.googleapis.com/token",
            "exp": now + 3600,
            "iat": now,
        }

        try:
            token = jwt.encode(claims, self.private_key, algorithm="RS256")
        except Exception as e:
            raise ConnectorError(f"Failed to sign JWT: {e}", "gcs")

        try:
            response = await self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                    "assertion": token,
                },
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"Token exchange failed: {e}", "gcs")

        token_data = response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ConnectorError("access_token not found in response", "gcs")

        return access_token

    def _parse_gcs_url(self, location: str) -> tuple[str, str]:
        """Parse a GCS URL into bucket and object path.

        Args:
            location: GCS URL (gs://bucket/path/to/object)

        Returns:
            Tuple of (bucket, object_path)

        Raises:
            ConnectorError: If URL format is invalid
        """
        parsed = urlparse(location)
        if parsed.scheme != "gs":
            raise ConnectorError(f"Invalid GCS URL scheme: {parsed.scheme}", "gcs")

        bucket = parsed.netloc
        if not bucket:
            raise ConnectorError("Invalid GCS URL: missing bucket name", "gcs")

        object_path = parsed.path.lstrip("/")
        if not object_path:
            raise ConnectorError("Invalid GCS URL: missing object path", "gcs")

        return bucket, object_path

    def _build_api_url(self, bucket: str, object_path: str, for_upload: bool = False) -> str:
        """Build the GCS REST API URL.

        Args:
            bucket: Bucket name
            object_path: Object path within bucket
            for_upload: If True, build upload URL; otherwise download URL

        Returns:
            REST API URL string
        """
        encoded_path = quote(object_path, safe="")
        if for_upload:
            return f"https://storage.googleapis.com/upload/storage/v1/b/{bucket}/o?uploadType=media&name={encoded_path}"
        return f"https://storage.googleapis.com/storage/v1/b/{bucket}/o/{encoded_path}?alt=media"

    async def fetch(self, location: str) -> bytes:
        """Fetch data from GCS.

        Args:
            location: GCS URL (gs://bucket/key)

        Returns:
            Raw bytes of the object content

        Raises:
            ConnectorError: If the fetch fails
        """
        bucket, object_path = self._parse_gcs_url(location)
        access_token = await self._generate_access_token()
        api_url = self._build_api_url(bucket, object_path)

        try:
            response = await self.client.get(
                api_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if response.status_code == 404:
                raise ConnectorError(f"Object not found: {location}", "gcs")
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            raise ConnectorError(f"GCS fetch error: {e}", "gcs")

    async def put(self, location: str, data: bytes) -> None:
        """Write data to GCS.

        Args:
            location: GCS URL (gs://bucket/key)
            data: Raw bytes to write

        Raises:
            ConnectorError: If the write fails
        """
        bucket, object_path = self._parse_gcs_url(location)
        access_token = await self._generate_access_token()
        api_url = self._build_api_url(bucket, object_path, for_upload=True)

        try:
            response = await self.client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/octet-stream",
                },
                content=data,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"GCS upload error: {e}", "gcs")


class AzureConnector:
    """Connector for Azure Blob Storage access.

    Uses SharedKey authentication with HMAC-SHA256 signatures.
    Communicates with Azure Blob Storage via the REST API.

    Attributes:
        account_name: Azure storage account name
        account_key: Azure storage account key
        client: httpx AsyncClient for HTTP requests
    """

    def __init__(self, account_name: str, account_key: str) -> None:
        self.account_name = account_name
        self.account_key = account_key
        self.client = httpx.AsyncClient()

    @classmethod
    def from_profile_and_url(cls, profile: Profile, url: str) -> AzureConnector:
        """Build an AzureConnector from a profile and URL.

        Args:
            profile: Profile containing connection_string
            url: Azure Blob URL

        Returns:
            Configured AzureConnector instance

        Raises:
            ConnectorError: If credentials are missing or invalid
        """
        if not profile.connection_string:
            raise ConnectorError("Azure profile missing connection_string", "azure")

        account_name = None
        account_key = None

        for part in profile.connection_string.split(";"):
            if part.startswith("AccountName="):
                account_name = part[len("AccountName="):]
            elif part.startswith("AccountKey="):
                account_key = part[len("AccountKey="):]

        if not account_name:
            raise ConnectorError("Missing AccountName in connection string", "azure")
        if not account_key:
            raise ConnectorError("Missing AccountKey in connection string", "azure")

        return cls(account_name=account_name, account_key=account_key)

    def _create_auth_header(
        self, method: str, url: str, content_length: int = 0
    ) -> tuple[str, str]:
        """Create SharedKey authorization header for Azure Blob Storage.

        Args:
            method: HTTP method (GET, PUT)
            url: Full URL to the blob
            content_length: Content length for PUT requests

        Returns:
            Tuple of (authorization_header, date_header)

        Raises:
            ConnectorError: If signature generation fails
        """
        parsed = urlparse(url)
        date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
        resource = f"/{self.account_name}{parsed.path}"

        # Build canonical string to sign
        if method == "GET":
            string_to_sign = (
                f"{method}\n"  # HTTP verb
                f"\n"  # Content-Encoding
                f"\n"  # Content-Language
                f"\n"  # Content-Length
                f"\n"  # Content-MD5
                f"\n"  # Content-Type
                f"\n"  # Date
                f"\n"  # If-Modified-Since
                f"\n"  # If-Match
                f"\n"  # If-None-Match
                f"\n"  # If-Unmodified-Since
                f"\n"  # Range
                f"x-ms-date:{date}\n"
                f"x-ms-version:2020-04-08\n"
                f"{resource}"
            )
        else:
            string_to_sign = (
                f"{method}\n"
                f"\n"  # Content-Encoding
                f"\n"  # Content-Language
                f"{content_length}\n"
                f"\n"  # Content-MD5
                f"\n"  # Content-Type
                f"\n"  # Date
                f"\n"  # If-Modified-Since
                f"\n"  # If-Match
                f"\n"  # If-None-Match
                f"\n"  # If-Unmodified-Since
                f"\n"  # Range
                f"x-ms-date:{date}\n"
                f"x-ms-version:2020-04-08\n"
                f"{resource}"
            )

        try:
            key_bytes = base64.b64decode(self.account_key)
            signature = hmac.new(
                key_bytes, string_to_sign.encode("utf-8"), hashlib.sha256
            ).digest()
            signature_b64 = base64.b64encode(signature).decode("utf-8")
        except Exception as e:
            raise ConnectorError(f"Failed to create signature: {e}", "azure")

        auth_header = f"SharedKey {self.account_name}:{signature_b64}"
        return auth_header, date

    async def fetch(self, location: str) -> bytes:
        """Fetch data from Azure Blob Storage.

        Args:
            location: Full Azure Blob URL

        Returns:
            Raw bytes of the blob content

        Raises:
            ConnectorError: If the fetch fails
        """
        auth_header, date = self._create_auth_header("GET", location)

        try:
            response = await self.client.get(
                location,
                headers={
                    "Authorization": auth_header,
                    "x-ms-date": date,
                    "x-ms-version": "2020-04-08",
                },
            )
            if response.status_code == 404:
                raise ConnectorError(f"Blob not found: {location}", "azure")
            response.raise_for_status()
            return response.content
        except httpx.HTTPError as e:
            raise ConnectorError(f"Azure fetch error: {e}", "azure")

    async def put(self, location: str, data: bytes) -> None:
        """Write data to Azure Blob Storage.

        Args:
            location: Full Azure Blob URL
            data: Raw bytes to write

        Raises:
            ConnectorError: If the write fails
        """
        auth_header, date = self._create_auth_header("PUT", location, len(data))

        try:
            response = await self.client.put(
                location,
                headers={
                    "Authorization": auth_header,
                    "x-ms-date": date,
                    "x-ms-version": "2020-04-08",
                    "x-ms-blob-type": "BlockBlob",
                    "Content-Type": "application/octet-stream",
                },
                content=data,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise ConnectorError(f"Azure upload error: {e}", "azure")


def get_connector(connector_type: str, profile: Profile | None, location: str) -> Connector:
    """Get the appropriate connector for a type and location.

    Args:
        connector_type: Type of connector ("local", "s3", "gcs", "azure")
        profile: Optional profile for credentials
        location: Location to connect to

    Returns:
        Configured connector instance

    Raises:
        ConnectorError: If the connector type is unknown
    """
    match connector_type.lower():
        case "local":
            return LocalConnector()
        case "s3":
            if profile is None:
                raise ConnectorError("S3 connector requires a profile", "s3")
            return S3Connector.from_profile_and_url(profile, location)
        case "gcs":
            if profile is None:
                raise ConnectorError("GCS connector requires a profile", "gcs")
            return GCSConnector.from_profile_and_url(profile, location)
        case "azure":
            if profile is None:
                raise ConnectorError("Azure connector requires a profile", "azure")
            return AzureConnector.from_profile_and_url(profile, location)
        case _:
            raise ConnectorError(f"Unknown connector type: {connector_type}")
