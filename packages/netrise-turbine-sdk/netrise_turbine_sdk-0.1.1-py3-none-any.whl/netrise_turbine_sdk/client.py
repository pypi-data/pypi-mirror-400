from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

# The generated client will live in this module after `ariadne-codegen` runs.
# It is intentionally a separate top-level package so it won't overwrite
# handwritten wrapper code.
from netrise_turbine_sdk_graphql import Client as GeneratedClient


@dataclass(frozen=True)
class TurbineClientConfig:
    endpoint: str

    # Auth0 client-credentials
    auth0_domain: Optional[str] = None
    auth0_client_id: Optional[str] = None
    auth0_client_secret: Optional[str] = None
    auth0_audience: Optional[str] = None
    auth0_organization_id: Optional[str] = None
    auth0_organization_name: Optional[str] = None  # kept for parity with TS tool

    # Manual token override
    turbine_api_token: Optional[str] = None

    @staticmethod
    def from_env(load_env_file: bool = True) -> "TurbineClientConfig":
        """Load config from environment variables.

        If `load_env_file` is True, attempts to load a `.env` file from:
        - turbine/sdk-tools/.env (project-root relative)
        - current working directory .env

        This mirrors the behavior of the TypeScript snapshot tool.
        """
        if load_env_file:
            # Try loading repo-local .env first (same convention as snapshot tool).
            load_dotenv("turbine/sdk-tools/.env", override=False)
            load_dotenv(override=False)

        endpoint = (os.getenv("TURBINE_GRAPHQL_ENDPOINT") or "").strip()
        if not endpoint:
            raise ValueError(
                "TURBINE_GRAPHQL_ENDPOINT is required (e.g. https://apollo.turbine.netrise.io/graphql/v3)"
            )

        return TurbineClientConfig(
            endpoint=endpoint,
            auth0_domain=_strip_or_none(os.getenv("AUTH0_DOMAIN")),
            auth0_client_id=_strip_or_none(os.getenv("AUTH0_CLIENT_ID")),
            auth0_client_secret=_strip_or_none(os.getenv("AUTH0_CLIENT_SECRET")),
            auth0_audience=_strip_or_none(os.getenv("AUTH0_AUDIENCE")),
            auth0_organization_id=_strip_or_none(os.getenv("AUTH0_ORGANIZATION_ID")),
            auth0_organization_name=_strip_or_none(
                os.getenv("AUTH0_ORGANIZATION_NAME")
            ),
            turbine_api_token=_strip_or_none(os.getenv("TURBINE_API_TOKEN")),
        )


class TurbineClient:
    """Sync-first Turbine GraphQL client.

    - Uses `TURBINE_API_TOKEN` if provided.
    - Otherwise uses Auth0 client credentials to fetch a token.

    The underlying request execution is provided by the generated client from
    `ariadne-codegen`.
    """

    def __init__(
        self,
        config: TurbineClientConfig,
        *,
        timeout: float = 30.0,
        httpx_client: Optional[httpx.Client] = None,
    ) -> None:
        self._config = config
        self._timeout = timeout
        self._httpx_client = httpx_client

        self._cached_token: Optional[str] = None
        self._cached_token_expires_at: float = 0.0

    @property
    def config(self) -> TurbineClientConfig:
        return self._config

    def _get_auth_header(self) -> Dict[str, str]:
        token = self._get_token()
        if not token.startswith("Bearer "):
            token = f"Bearer {token}"
        return {"Authorization": token}

    def _get_token(self) -> str:
        # 1) Manual token override
        if self._config.turbine_api_token:
            return self._config.turbine_api_token

        # 2) Cached Auth0 token
        now = time.time()
        if self._cached_token and now < self._cached_token_expires_at:
            return self._cached_token

        # 3) Fetch via Auth0 client credentials
        token, expires_in = _fetch_auth0_token(
            domain=self._config.auth0_domain,
            client_id=self._config.auth0_client_id,
            client_secret=self._config.auth0_client_secret,
            audience=self._config.auth0_audience,
            organization_id=self._config.auth0_organization_id,
            organization_name=self._config.auth0_organization_name,
            timeout=self._timeout,
        )

        # Cache with a small safety buffer.
        self._cached_token = token
        self._cached_token_expires_at = time.time() + max(0, expires_in - 30)
        return token

    def graphql(self) -> GeneratedClient:
        """Return a generated client instance (sync)."""
        headers = self._get_auth_header()

        # Prefer reusing caller-provided httpx client.
        if self._httpx_client is not None:
            self._httpx_client.headers.update(headers)
            return GeneratedClient(
                url=self._config.endpoint,
                http_client=self._httpx_client,
            )

        http_client = httpx.Client(timeout=self._timeout, headers=headers)
        return GeneratedClient(
            url=self._config.endpoint,
            http_client=http_client,
        )


def _strip_or_none(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip()
    return v or None


def _fetch_auth0_token(
    *,
    domain: Optional[str],
    client_id: Optional[str],
    client_secret: Optional[str],
    audience: Optional[str],
    organization_id: Optional[str],
    organization_name: Optional[str],
    timeout: float,
) -> tuple[str, int]:
    if not domain:
        raise ValueError("AUTH0_DOMAIN is required when TURBINE_API_TOKEN is not set")
    if not client_id or not client_secret:
        raise ValueError(
            "AUTH0_CLIENT_ID and AUTH0_CLIENT_SECRET are required when TURBINE_API_TOKEN is not set"
        )
    if not audience:
        raise ValueError("AUTH0_AUDIENCE is required when TURBINE_API_TOKEN is not set")

    domain = domain.rstrip("/")
    token_url = f"{domain}/oauth/token"

    payload: Dict[str, Any] = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
    }

    # Organizations support depends on the Auth0 client grant settings.
    if organization_id:
        payload["organization"] = organization_id
    # Kept for parity with the existing TS tool; Auth0 may ignore it.
    if organization_name:
        payload["organization_name"] = organization_name

    with httpx.Client(timeout=timeout) as c:
        r = c.post(token_url, json=payload)
        r.raise_for_status()
        data = r.json()

    token = data.get("access_token")
    expires_in = int(data.get("expires_in", 3600))

    if not token:
        raise RuntimeError(f"Auth0 token response missing access_token: {data}")

    return token if token.startswith("Bearer ") else f"Bearer {token}", expires_in
