"""Facilitator client.

This module provides a thin SDK wrapper around the Cronos Facilitator service,
exposing helpers for discovery, payment verification, settlement execution, and
construction of X402-related headers and payment requirement payloads.

The SDK intentionally uses a fixed base URL:
``https://facilitator.cronoslabs.org``

Consumers interact with:
- Network discovery (supported networks and capabilities)
- Payment verification
- Payment settlement
- Local helpers for requirements/header construction
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from ...integrations.facilitator_api import (
    get_supported,
    verify_payment,
    settle_payment,
)
from ...integrations.facilitator_interface import (
    ClientConfig,
    Contract,
    CronosNetwork,
    PaymentRequirements,
    VerifyRequest,
    X402OutputSchema,
    X402SupportedResponse,
    X402VerifyResponse,
    X402SettleResponse,
)
from ...integrations.facilitator_registry import NETWORK_REGISTRY
from ..utils.payment_requirements import generate_payment_requirements
from ..utils.payment_header import generate_cronos_payment_header


FACILITATOR_BASE_URL: str = "https://facilitator.cronoslabs.org"


class Facilitator:
    """
    Client wrapper for interacting with the Cronos Facilitator service.

    The client is configured for a specific Cronos network and exposes:
    - Remote calls for supported-network discovery, payment verification, and settlement
    - Local helpers for generating payment headers and payment requirements
    - A convenience builder for verification/settlement request payloads

    Network-specific defaults (such as the settlement asset and optional RPC URL)
    are derived from the local network registry.

    Attributes:
        network: The Cronos network this client is configured for.
        base_url: Base URL of the Facilitator service.
        default_asset: Default settlement asset for the selected network.
        rpc_url: Optional RPC URL associated with the selected network.
    """

    def __init__(
        self,
        config: Optional[Union[ClientConfig, Dict[str, Any]]] = None,
        *,
        network: Optional[CronosNetwork] = None,
    ):
        """
        Initialize a Facilitator client.

        Configuration may be provided either as a typed ``ClientConfig`` object
        or as a plain dictionary containing a ``network`` key. For convenience,
        the network may also be supplied directly via the ``network`` keyword.

        Args:
            config: Optional client configuration object or dict. Must contain
                a ``network`` entry if provided.
            network: Optional Cronos network identifier. Used if ``config`` is
                not supplied.

        Raises:
            TypeError: If neither ``config`` nor ``network`` is provided.
            ValueError: If the specified network is not supported.
        """
        if config is None:
            if network is None:
                raise TypeError(
                    "Facilitator requires config with 'network' or network=..."
                )
            config = {"network": network}

        cfg_network = config["network"] if isinstance(config, dict) else config.network
        self.network: CronosNetwork = cfg_network

        registry = NETWORK_REGISTRY.get(self.network)
        if registry is None:
            raise ValueError(f"Unsupported network: {self.network}")

        self.base_url: str = FACILITATOR_BASE_URL
        self.default_asset: Contract = registry.asset
        self.rpc_url: Optional[str] = getattr(registry, "rpc_url", None)

    async def get_supported(self) -> X402SupportedResponse:
        """
        Retrieve supported networks and capabilities from the Facilitator.

        Returns:
            A structured response describing supported networks, assets, and
            protocol features.
        """
        return await get_supported(self.base_url)

    async def verify_payment(self, request: VerifyRequest) -> X402VerifyResponse:
        """
        Verify an X402 payment against the Facilitator service.

        Args:
            request: Verification request payload containing payment header and
                payment requirements.

        Returns:
            A verification response indicating whether the payment is valid
            and acceptable.
        """
        return await verify_payment(self.base_url, request)

    async def settle_payment(self, request: VerifyRequest) -> X402SettleResponse:
        """
        Settle an X402 payment through the Facilitator service.

        Args:
            request: Settlement request payload containing payment header and
                payment requirements.

        Returns:
            A settlement response describing the outcome of the payment
            execution.
        """
        return await settle_payment(self.base_url, request)

    async def generate_payment_header(
        self,
        *,
        to: str,
        value: str,
        signer: Any,
        asset: Optional[Contract] = None,
        valid_after: int = 0,
        valid_before: Optional[int] = None,
    ) -> str:
        """
        Generate a Cronos-compatible X402 payment header.

        This helper signs and encodes payment information into the format
        expected by X402-compatible services.

        Args:
            to: Destination address for the payment.
            value: Amount to transfer, expressed as a string.
            signer: Signer object capable of authorizing the payment.
            asset: Optional asset contract to use for settlement. Defaults
                to the network's default asset.
            valid_after: Unix timestamp after which the payment is valid.
            valid_before: Optional Unix timestamp after which the payment
                expires.

        Returns:
            A serialized payment header string suitable for inclusion in
            request headers.
        """
        return generate_cronos_payment_header(
            network=self.network,
            to=to,
            value=value,
            asset=asset or self.default_asset,
            signer=signer,
            valid_after=valid_after,
            valid_before=valid_before,
        )

    def generate_payment_requirements(
        self,
        *,
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
        Construct a ``PaymentRequirements`` object for an X402 request.

        This helper assembles metadata describing how a client should pay for
        access to a protected resource.

        Args:
            pay_to: Address that should receive payment.
            asset: Optional asset contract to use. Defaults to the network's
                default asset.
            description: Human-readable description of the payment request.
            max_amount_required: Maximum amount that may be charged.
            mime_type: Expected MIME type of the protected resource.
            max_timeout_seconds: Maximum time allowed for payment settlement.
            resource: Optional identifier of the protected resource.
            extra: Optional provider-specific metadata.
            output_schema: Optional schema describing the expected response
                payload.

        Returns:
            A populated ``PaymentRequirements`` structure.
        """
        return generate_payment_requirements(
            network=self.network,
            pay_to=pay_to,
            asset=asset or self.default_asset,
            description=description,
            max_amount_required=max_amount_required,
            mime_type=mime_type,
            max_timeout_seconds=max_timeout_seconds,
            resource=resource,
            extra=extra,
            output_schema=output_schema,
        )

    def build_verify_request(
        self,
        payment_header: str,
        payment_requirements: PaymentRequirements,
    ) -> VerifyRequest:
        """
        Build a verification request payload for Facilitator verification/settlement calls.

        Args:
            payment_header: Serialized X402 payment header.
            payment_requirements: Payment requirements associated with the
                protected resource.

        Returns:
            A dictionary conforming to the ``VerifyRequest`` schema.
        """
        return {
            "x402Version": 1,
            "paymentHeader": payment_header,
            "paymentRequirements": payment_requirements,
        }
