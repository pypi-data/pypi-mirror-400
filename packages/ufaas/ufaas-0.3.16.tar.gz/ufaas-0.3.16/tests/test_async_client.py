"""Test UFaaS client."""

import logging
import os

import pytest

from src.ufaas.client import AsyncUFaaS


@pytest.mark.asyncio
async def test_ufaas_client_api_key() -> None:
    """Test Async UFaaS client."""
    client = AsyncUFaaS(
        ufaas_base_url=os.getenv("UFAAS_URL"),
        usso_base_url=os.getenv("USSO_URL"),
        api_key=os.getenv("UFAAS_API_KEY"),
    )
    scopes = await client._get_scopes()
    logging.info(scopes)
    resp = await client.get(
        f"{client.ufaas_base_url}/api/accounting/v1/wallets"
    )
    resp.raise_for_status()
    logging.info(resp.json())


@pytest.mark.asyncio
async def test_ufaas_client_agent() -> None:
    """Test Async UFaaS client."""
    client = AsyncUFaaS(
        ufaas_base_url=os.getenv("UFAAS_URL"),
        usso_base_url=os.getenv("USSO_URL"),
        api_key=None,
        agent_id=os.getenv("AGENT_ID"),
        agent_private_key=os.getenv("AGENT_PRIVATE_KEY"),
    )
    scopes = await client._get_scopes()
    logging.info(scopes)
    await client._get_token(scopes=scopes, aud="accounting")
    resp = await client.get(
        f"{client.ufaas_base_url}/api/accounting/v1/wallets"
    )
    resp.raise_for_status()
    logging.info(resp.json())
