"""HTTP integration for the Cronos X402 Facilitator API.

This module provides low-level HTTP helpers for interacting with the
Cronos X402 Facilitator service. It exposes functions for querying
supported networks and capabilities, verifying X402 payment requests,
and settling verified payments on-chain.
"""

from __future__ import annotations

from typing import Any, Dict

import requests

from .facilitator_interface import (
    VerifyRequest,
    X402SupportedResponse,
    X402VerifyResponse,
    X402SettleResponse,
)


#: Default HTTP headers used for all requests sent to the Cronos X402 Facilitator API.
#:
#: Includes:
#: - ``Content-Type: application/json``
#: - ``X402-Version: 1``
HEADERS: Dict[str, str] = {
    "Content-Type": "application/json",
    "X402-Version": "1",
}


def get_supported(*, base_url: str) -> X402SupportedResponse:
    """
    Fetch supported networks, schemes, and capabilities from the Facilitator.

    Args:
        base_url: Base URL of the Facilitator service.

    Returns:
        A structured response describing supported networks, assets, and
        protocol features.

    Raises:
        RuntimeError: If the request fails or the Facilitator returns
            a non-success status code.
    """
    url = f"{base_url}/v2/x402/supported"
    res = requests.get(url, headers=HEADERS, timeout=30)
    try:
        json = res.json()
    except Exception:
        json = {"error": res.text}
    if not res.ok:
        raise RuntimeError(f"Supported failed: {res.status_code} – {json}")
    return json


def verify_payment(*, base_url: str, body: VerifyRequest) -> X402VerifyResponse:
    """
    Verify an X402 payment request with the Facilitator.

    This endpoint validates the provided Base64-encoded payment header
    together with its associated payment requirements.

    Args:
        base_url: Base URL of the Facilitator service.
        body: Verification request payload containing the payment header
            and payment requirements.

    Returns:
        A verification response indicating whether the payment is valid
        and acceptable.

    Raises:
        RuntimeError: If the request fails or the Facilitator returns
            a non-success status code.
    """
    url = f"{base_url}/v2/x402/verify"
    res = requests.post(url, headers=HEADERS, json=body, timeout=30)
    try:
        json = res.json()
    except Exception:
        json = {"error": res.text}
    if not res.ok:
        raise RuntimeError(f"Verify failed: {res.status_code} – {json}")
    return json


def settle_payment(*, base_url: str, body: VerifyRequest) -> X402SettleResponse:
    """
    Settle a previously verified X402 payment.

    Settlement is the final step in the X402 flow and submits the authorized
    EIP-3009 transfer on-chain.

    Args:
        base_url: Base URL of the Facilitator service.
        body: Settlement request payload containing the payment header
            and payment requirements.

    Returns:
        A settlement response describing the outcome of the on-chain
        execution.

    Raises:
        RuntimeError: If the request fails or the Facilitator returns
            a non-success status code.
    """
    url = f"{base_url}/v2/x402/settle"
    res = requests.post(url, headers=HEADERS, json=body, timeout=60)
    try:
        json = res.json()
    except Exception:
        json = {"error": res.text}
    if not res.ok:
        raise RuntimeError(f"Settle failed: {res.status_code} – {json}")
    return json
