"""Type definitions for the Cronos X402 Facilitator SDK (Python).

This module defines the public enums and TypedDict schemas used by the SDK to
model X402 payment flows, including:

- Supported payment schemes and networks
- Payment requirement payloads describing how to pay for a resource
- Verification/settlement request and response shapes
- EIP-3009 payload and header structures used for signed authorizations
- Optional schema hints for applications that want typed input/output contracts

The helpers at the bottom of the module convert between the Python-friendly
``from_`` field name and the JSON wire format key ``from``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict, Literal


class Scheme(str, Enum):
    """X402 payment scheme type.

    Schemes describe how payment amount matching is evaluated. The current SDK
    models an "exact" scheme where the payment must match the required amount.
    """

    Exact = "exact"


class CronosNetwork(str, Enum):
    """Supported Cronos EVM networks."""

    #: Cronos EVM Mainnet
    CronosMainnet = "cronos-mainnet"

    #: Cronos EVM Testnet
    CronosTestnet = "cronos-testnet"


class X402EventType(str, Enum):
    """Event types surfaced by verification/settlement results."""

    Verified = "verified"
    Settled = "settled"
    Failed = "failed"


class Contract(str, Enum):
    """Supported token contracts for X402 payments.

    These contracts are expected to support EIP-3009 authorization-based
    transfers and may be validated by the facilitator during verification
    and settlement.
    """

    #: USDCe contract address on Cronos mainnet.
    USDCe = "0xf951eC28187D9E5Ca673Da8FE6757E6f0Be5F77C"

    #: USDCe contract address on Cronos testnet.
    DevUSDCe = "0xc01efAaF7C5C61bEbFAeb358E1161b537b8bC0e0"


@dataclass(frozen=True)
class ClientConfig:
    """Client configuration container.

    The SDK uses a fixed facilitator base URL. This configuration type exists
    to carry other client options and to provide a stable, typed entry point.
    """

    #: Optional base URL value (not used by the Cronos SDK runtime).
    base_url: Optional[str] = None


class PaymentRequirements(TypedDict, total=False):
    """Payment requirements for an X402-protected resource.

    This structure describes what a payer must provide in order to access a
    protected resource or service, and is submitted alongside a Base64-encoded
    X402 payment header to the facilitator verification and settlement endpoints.

    Fields are intentionally JSON-friendly and can include provider-specific
    metadata via ``extra``.
    """

    scheme: Literal[Scheme.Exact]
    network: CronosNetwork
    payTo: str
    asset: Contract
    description: str
    mimeType: str
    maxAmountRequired: str
    maxTimeoutSeconds: int
    resource: str
    extra: Dict[str, Any]
    outputSchema: "X402OutputSchema"


class VerifyRequest(TypedDict):
    """Request body for facilitator verification and settlement calls.

    Combines a Base64-encoded payment header with the corresponding payment
    requirements that describe the expected payment and target resource.
    """

    x402Version: int
    paymentHeader: str
    paymentRequirements: PaymentRequirements


class Eip3009Payload(TypedDict):
    """EIP-3009 authorization payload used inside an X402 payment header.

    This payload represents the signed parameters for an authorization-based
    transfer (e.g., TransferWithAuthorization). Numeric values are represented
    as strings when appropriate to remain JSON-compatible.

    Note:
        ``from`` is a Python keyword, so the payer address is stored as ``from_``
        and converted to/from the JSON wire key ``from`` by helper functions.
    """

    from_: str  # "from" is a keyword in Python; serialized as "from"
    to: str
    value: str
    validAfter: int
    validBefore: int
    nonce: str
    signature: str
    asset: Contract


class Eip3009PaymentHeader(TypedDict):
    """X402 payment header wrapper containing an EIP-3009 payload.

    This structure is typically serialized to compact JSON and Base64-encoded
    for transport as a single header value.
    """

    x402Version: int
    scheme: Literal[Scheme.Exact]
    network: CronosNetwork
    payload: Eip3009Payload


class FieldDef(TypedDict, total=False):
    """Single field definition used by ``X402OutputSchema``."""

    name: str
    type: str
    required: bool
    description: str


class X402OutputSchema(TypedDict, total=False):
    """Optional schema hint describing structured outputs.

    This schema is intended for client applications that want a strongly typed
    contract for outputs or artifacts. It is treated as advisory metadata and
    is not necessarily enforced by the facilitator.
    """

    kind: str
    fields: List[FieldDef]


class X402PaymentRequirements(TypedDict, total=False):
    """Wrapper payload shape containing ``paymentRequirements``."""

    paymentRequirements: PaymentRequirements


class X402DiscoverResponse(TypedDict, total=False):
    """Response shape for discovery-style endpoints.

    Contains:
    - kind: Identifier for the discovered resource/workflow kind
    - requirements: Payment requirements accepted for the kind
    - outputSchema: Optional advisory output schema for typed clients
    """

    kind: str
    requirements: PaymentRequirements
    outputSchema: X402OutputSchema


class X402SupportedResponse(TypedDict, total=False):
    """Response shape describing facilitator support and capabilities."""

    networks: List[str]
    schemes: List[str]
    assets: List[str]
    capabilities: Dict[str, Any]


class X402VerifyResponse(TypedDict, total=False):
    """Verification result returned by facilitator verification calls."""

    isValid: bool
    invalidReason: Optional[str]


class X402SettleResponse(TypedDict, total=False):
    """Settlement result returned by facilitator settlement calls.

    Common fields include:
    - txHash: Transaction hash for the submitted on-chain action
    - event: Event type indicating settlement outcome
    - from_/to/value: Transfer details
    - blockNumber/network/timestamp: Execution metadata
    - error: Error message (if any)
    """

    x402Version: int
    event: str
    txHash: str
    from_: str
    to: str
    value: str
    blockNumber: int
    network: str
    timestamp: str
    error: str


def _serialize_payload(payload: Eip3009Payload) -> Dict[str, Any]:
    """Convert an ``Eip3009Payload`` to a JSON-serializable dict.

    This converts the Python-friendly ``from_`` key into the JSON wire-format
    key ``from``.

    Args:
        payload: Payload using ``from_`` as the payer address field.

    Returns:
        A dict suitable for JSON serialization using ``from`` as the payer key.
    """
    d = dict(payload)
    if "from_" in d:
        d["from"] = d.pop("from_")
    return d


def _deserialize_payload(payload: Dict[str, Any]) -> Eip3009Payload:
    """Convert a JSON payload dict into an ``Eip3009Payload``.

    This converts the JSON wire-format key ``from`` into the Python-friendly
    ``from_`` key.

    Args:
        payload: JSON payload dict using ``from`` as the payer address field.

    Returns:
        A payload dict using ``from_`` as the payer address field.
    """
    d = dict(payload)
    if "from" in d:
        d["from_"] = d.pop("from")
    return d


def _serialize_payload(payload: Eip3009Payload) -> Dict[str, Any]:
    """Convert an ``Eip3009Payload`` to a JSON-serializable dict.

    This is a convenience serializer that always rewrites ``from_`` to ``from``.

    Args:
        payload: Payload using ``from_`` as the payer address field.

    Returns:
        A dict suitable for JSON serialization using ``from`` as the payer key.
    """
    d = dict(payload)
    d["from"] = d.pop("from_")
    return d
