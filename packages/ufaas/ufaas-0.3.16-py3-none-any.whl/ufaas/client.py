"""Main UFaaS client implementation."""

import os
from urllib.parse import urlparse

from usso.client import AsyncUssoClient, UssoClient


def _get_usso_url(ufaas_base_url: str) -> str:
    """Get the USSO URL from the UFaaS base URL."""

    # calculate sso_url using ufaas_base_url
    # for example: media.pixiee.io/v1/f -> https://sso.pixiee.io
    # for example: media.ufaas.io/v1/f -> https://sso.ufaas.io
    # for example: media.pixy.ir/api/v1/f -> https://sso.pixy.ir
    # for example: storage.pixy.ir/api/v1/f -> https://sso.pixy.ir

    if not ufaas_base_url:
        raise ValueError(
            "BASE_URLs (UFAAS_BASE_URL and USSO_BASE_URL) are required"
        )

    parsed_url = urlparse(ufaas_base_url)
    netloc = parsed_url.netloc
    netloc_parts = netloc.split(".")
    if len(netloc_parts) > 2:
        netloc_parts[0] = "sso"
    else:
        netloc_parts = ["sso", netloc]
    netloc = ".".join(netloc_parts)
    return f"https://{netloc}"


class UFaaS(UssoClient):
    """Synchronous UFaaS main client."""

    def __init__(
        self,
        *,
        ufaas_base_url: str = os.getenv("UFAAS_BASE_URL"),
        usso_base_url: str | None = os.getenv("USSO_BASE_URL"),
        api_key: str | None = os.getenv("UFAAS_API_KEY"),
        refresh_token: str | None = os.getenv("USSO_REFRESH_TOKEN"),
        agent_id: str | None = os.getenv("AGENT_ID"),
        agent_private_key: str | None = os.getenv("AGENT_PRIVATE_KEY"),
        client: UssoClient | None = None,
    ) -> None:
        """
        Initialize the UFaaS client.

        Args:
            ufaas_base_url: Base URL for UFaaS API
            usso_base_url: Base URL for USSO service
            api_key: API key for authentication
            refresh_token: Refresh token for authentication
            agent_id: Agent ID for authentication
            agent_private_key: Agent private key for authentication
            client: Existing USSO client to reuse
        """
        usso_base_url = (
            usso_base_url
            or getattr(client, "usso_base_url", None)
            or _get_usso_url(ufaas_base_url)
        ).rstrip("/")

        super().__init__(
            usso_base_url=usso_base_url,
            api_key=api_key,
            refresh_token=refresh_token,
            agent_id=agent_id,
            agent_private_key=agent_private_key,
            client=client,
        )
        ufaas_base_url = (
            ufaas_base_url
            or getattr(self, "ufaas_base_url", None)
            or os.getenv("UFAAS_BASE_URL")
        ).rstrip("/")
        if not ufaas_base_url:
            raise ValueError("UFAAS_BASE_URL is required")
        self.ufaas_base_url = ufaas_base_url
        # self.headers.update({"accept-encoding": "identity"})


class AsyncUFaaS(AsyncUssoClient):
    """Asynchronous UFaaS main client."""

    def __init__(
        self,
        *,
        ufaas_base_url: str = os.getenv("UFAAS_BASE_URL"),
        usso_base_url: str | None = os.getenv("USSO_BASE_URL"),
        api_key: str | None = os.getenv("UFAAS_API_KEY"),
        refresh_token: str | None = os.getenv("USSO_REFRESH_TOKEN"),
        agent_id: str | None = os.getenv("AGENT_ID"),
        agent_private_key: str | None = os.getenv("AGENT_PRIVATE_KEY"),
        client: AsyncUssoClient | None = None,
    ) -> None:
        """
        Initialize the AsyncUFaaS client.

        Args:
            ufaas_base_url: Base URL for UFaaS API
            usso_base_url: Base URL for USSO service
            api_key: API key for authentication
            agent_id: Agent ID for authentication
            agent_private_key: Agent private key for authentication
            refresh_token: Refresh token for authentication
            client: Existing USSO client to reuse
        """
        usso_base_url = (
            usso_base_url
            or getattr(client, "usso_base_url", None)
            or _get_usso_url(ufaas_base_url)
        ).rstrip("/")

        super().__init__(
            usso_base_url=usso_base_url,
            api_key=api_key,
            refresh_token=refresh_token,
            agent_id=agent_id,
            agent_private_key=agent_private_key,
            client=client,
        )
        ufaas_base_url = (
            ufaas_base_url
            or getattr(self, "ufaas_base_url", None)
            or os.getenv("UFAAS_BASE_URL")
        ).rstrip("/")
        if not ufaas_base_url:
            raise ValueError("UFAAS_BASE_URL is required")
        self.ufaas_base_url = ufaas_base_url
        # self.headers.update({"accept-encoding": "identity"})
