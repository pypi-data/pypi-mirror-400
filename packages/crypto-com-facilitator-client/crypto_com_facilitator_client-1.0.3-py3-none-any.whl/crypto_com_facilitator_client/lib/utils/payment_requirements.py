"""Payment requirements builder.

This module provides helpers for constructing structured X402
``PaymentRequirements`` objects used to describe how a client should pay for
access to a protected resource.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from ...integrations.facilitator_interface import (
    Contract,
    CronosNetwork,
    PaymentRequirements,
    Scheme,
    X402OutputSchema,
)
from ...integrations.facilitator_registry import NETWORK_REGISTRY


def generate_payment_requirements(
    *,
    network: CronosNetwork,
    pay_to: str,
    asset: Optional[Contract] = None,
    description: str = "X402 payment request",
    max_amount_required: str = "1000",
    mime_type: str = "application/json",
    max_timeout_seconds: int = 300,
    resource: str = "",
    extra: Optional[Dict[str, Any]] = None,
    output_schema: Optional[X402OutputSchema] = None,
) -> PaymentRequirements:
    """
    Generate a structured X402 ``PaymentRequirements`` object.

    The returned object describes the payment scheme, network, recipient, asset,
    and additional metadata required for a client to complete payment and access
    a protected resource.

    Args:
        network: Cronos network identifier to embed in the requirements and to
            resolve a default asset from the registry.
        pay_to: Address that should receive payment.
        asset: Optional token contract address. Defaults to the network's
            configured asset.
        description: Human-readable description of the payment request.
        max_amount_required: Maximum amount that may be charged, expressed as a
            stringified integer.
        mime_type: Expected MIME type of the protected resource.
        max_timeout_seconds: Maximum time allowed for payment settlement.
        resource: Optional identifier of the protected resource.
        extra: Optional provider-specific metadata. Defaults to an empty dict.
        output_schema: Optional schema describing the expected response payload.

    Returns:
        A populated ``PaymentRequirements`` structure.

    Raises:
        ValueError: If the network is not supported by the local registry.
    """

    config = NETWORK_REGISTRY.get(network)
    if config is None:
        raise ValueError(f"Unsupported network: {network}")

    req: PaymentRequirements = {
        "scheme": Scheme.Exact,
        "network": network,
        "payTo": pay_to,
        "asset": asset or config.asset,
        "description": description,
        "mimeType": mime_type,
        "maxAmountRequired": max_amount_required,
        "maxTimeoutSeconds": max_timeout_seconds,
        "resource": resource,
        "extra": extra or {},
    }

    if output_schema is not None:
        req["outputSchema"] = output_schema
    return req
