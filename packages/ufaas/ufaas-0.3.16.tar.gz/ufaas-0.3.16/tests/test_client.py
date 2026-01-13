"""Test UFaaS client."""

import logging
import os

from src.ufaas.client import UFaaS


def test_ufaas_client() -> None:
    """Test UFaaS client."""
    client = UFaaS(
        ufaas_base_url=os.getenv("UFAAS_URL"),
        usso_base_url=os.getenv("USSO_URL"),
        api_key=os.getenv("UFAAS_API_KEY"),
    )
    scopes = client._get_scopes()
    logging.info(scopes)
    resp = client.get(f"{client.ufaas_base_url}/api/accounting/v1/wallets")
    resp.raise_for_status()
    logging.info(resp.json())


def test_ufaas_client_agent() -> None:
    """Test Async UFaaS client."""
    client = UFaaS(
        ufaas_base_url=os.getenv("UFAAS_URL"),
        usso_base_url=os.getenv("USSO_URL"),
        api_key=None,
        agent_id=os.getenv("AGENT_ID"),
        agent_private_key=os.getenv("AGENT_PRIVATE_KEY"),
    )
    scopes = client._get_scopes()
    client._get_token(scopes=scopes, aud="accounting")
    logging.info(scopes)
    resp = client.get(f"{client.ufaas_base_url}/api/accounting/v1/wallets")
    resp.raise_for_status()
    logging.info(resp.json())
