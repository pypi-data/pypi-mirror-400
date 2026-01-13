"""Network registry for the Facilitator SDK.

This module defines a centralized registry that maps each supported Cronos
network to its associated configuration, including:

- The default ERC-20 asset used for X402 payments
- The JSON-RPC endpoint used for chain metadata resolution and signing
- The payment header generator function used to build X402-compliant headers

The registry is used throughout the SDK to ensure network-specific behavior
(such as asset selection and EIP-712 domain construction) is applied
consistently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict

from .facilitator_interface import Contract, CronosNetwork, Eip3009PaymentHeader


@dataclass(frozen=True)
class NetworkConfig:
    """
    Configuration entry for a supported Cronos network.

    Each entry defines the network-specific defaults and helpers required
    to construct and validate X402 payment headers.

    Attributes:
        asset: Default ERC-20 token contract used for payments on this network.
        rpc_url: JSON-RPC endpoint for resolving chain metadata (e.g., chainId).
        header_generator: Callable used to generate X402 payment headers for
            this network.
    """

    asset: Contract
    rpc_url: str
    header_generator: Callable[..., str]


# Import here to avoid circular imports at module load time.
from ..lib.utils.payment_header import generate_cronos_payment_header


NETWORK_REGISTRY: Dict[CronosNetwork, NetworkConfig] = {
    CronosNetwork.CronosMainnet: NetworkConfig(
        asset=Contract.USDCe,
        rpc_url="https://evm.cronos.org",
        header_generator=generate_cronos_payment_header,
    ),
    CronosNetwork.CronosTestnet: NetworkConfig(
        asset=Contract.DevUSDCe,
        rpc_url="https://evm-t3.cronos.org",
        header_generator=generate_cronos_payment_header,
    ),
}
