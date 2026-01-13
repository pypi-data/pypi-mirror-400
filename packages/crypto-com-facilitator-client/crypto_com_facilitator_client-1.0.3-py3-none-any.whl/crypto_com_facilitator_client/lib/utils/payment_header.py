"""Payment header utilities (EIP-3009 -> X402).

This module contains helpers for constructing X402-compatible payment headers
backed by EIP-3009 authorization payloads.

It includes:
- Secure nonce generation for EIP-3009 authorization messages
- Construction of an EIP-3009/X402 header object for a given Cronos network
- Encoding/decoding helpers for Base64 transport of header JSON
- JSON-RPC chainId lookup (``eth_chainId``)
- EIP-712 signing to produce an EIP-3009 authorization signature
"""

from __future__ import annotations

import base64
import json
import os
import time
from typing import Any, Dict, Optional, Union
from eth_account import Account
from eth_account.messages import encode_typed_data

import requests

from ...integrations.facilitator_interface import (
    Contract,
    CronosNetwork,
    Eip3009PaymentHeader,
    Eip3009Payload,
    Scheme,
    _serialize_payload,
)


def random_nonce_hex32() -> str:
    """
    Generate a cryptographically secure 32-byte nonce as a ``0x``-prefixed hex string.

    Returns:
        A 32-byte nonce encoded as hex with a ``0x`` prefix.
    """
    return "0x" + os.urandom(32).hex()


def build_eip3009_header(
    payload: Eip3009Payload, network: CronosNetwork
) -> Eip3009PaymentHeader:
    """
    Build an X402-compatible payment header for a given Cronos network.

    Args:
        payload: EIP-3009 authorization payload, including signature and
            authorization parameters.
        network: Cronos network identifier to attach to the header.

    Returns:
        A payment header object conforming to ``Eip3009PaymentHeader``.
    """
    return {
        "x402Version": 1,
        "scheme": Scheme.Exact,
        "network": network,
        "payload": payload,
    }


def encode_payment_header(header: Eip3009PaymentHeader) -> str:
    """
    Serialize and Base64-encode an EIP-3009 payment header.

    The header's payload is first normalized via ``_serialize_payload`` and the
    full header is then serialized as compact JSON (no whitespace) before being
    Base64-encoded.

    Args:
        header: Payment header to serialize and encode.

    Returns:
        A Base64-encoded string representation of the header JSON.
    """
    payload = _serialize_payload(header["payload"])
    header_json = dict(header)
    header_json["payload"] = payload
    raw = json.dumps(header_json, separators=(",", ":"), ensure_ascii=False).encode(
        "utf-8"
    )
    return base64.b64encode(raw).decode("ascii")


def decode_payment_header(base64_string: str) -> str:
    """
    Decode a Base64-encoded header JSON string.

    Args:
        base64_string: Base64-encoded header JSON.

    Returns:
        The decoded UTF-8 JSON string.
    """
    return base64.b64decode(base64_string).decode("utf-8")


def _jsonrpc_chain_id(rpc_url: str) -> int:
    """
    Fetch the chain ID from an EVM JSON-RPC endpoint via ``eth_chainId``.

    Args:
        rpc_url: JSON-RPC HTTP endpoint URL.

    Returns:
        The chain ID as an integer.

    Raises:
        requests.HTTPError: If the JSON-RPC request fails at the HTTP layer.
        RuntimeError: If the JSON-RPC response does not contain a ``result`` field.
        ValueError: If the returned chain ID cannot be parsed as hex.
    """
    res = requests.post(
        rpc_url,
        json={"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []},
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()
    if "result" not in data:
        raise RuntimeError(f"Invalid JSON-RPC response: {data}")
    return int(data["result"], 16)


def generate_cronos_payment_header(
    *,
    signer: Union[str, Any],
    network: CronosNetwork,
    to: str,
    value: str,
    asset: Optional[Contract] = None,
    valid_after: Optional[int] = None,
    valid_before: Optional[int] = None,
) -> str:
    """
    Generate a signed, X402-compatible payment header for a Cronos network.

    This function:
    - Resolves network configuration from the local registry
    - Fetches the network chain ID from the configured JSON-RPC endpoint
    - Builds an EIP-712 typed data message for EIP-3009 TransferWithAuthorization
    - Signs the typed data using the provided signer
    - Packages the signed authorization into an ``Eip3009Payload``
    - Wraps the payload into an X402 payment header and Base64-encodes it

    The signer may be:
    - A private key hex string, or
    - An object exposing a private key via ``.key`` or ``.privateKey``

    Args:
        signer: Private key material used for EIP-712 signing.
        network: Cronos network identifier used to select registry config and
            embed into the header.
        to: Recipient address for the authorization.
        value: Amount to authorize, expressed as a stringified integer.
        asset: Optional token contract address. Defaults to the network's
            configured asset.
        valid_after: Optional Unix timestamp after which the authorization is
            valid. Defaults to ``0``.
        valid_before: Optional Unix timestamp after which the authorization is
            invalid. Defaults to ``now + 3600``.

    Returns:
        A Base64-encoded payment header JSON string.

    Raises:
        ImportError: If required signing dependencies are not installed when
            called.
        ValueError: If the network is not supported by the local registry.
        TypeError: If ``signer`` is not a supported type.
    """

    from ...integrations.facilitator_registry import NETWORK_REGISTRY

    config = NETWORK_REGISTRY.get(network)
    if config is None:
        raise ValueError(f"Unsupported network: {network}")

    chain_id = _jsonrpc_chain_id(config.rpc_url)
    token_address: Contract = asset or config.asset

    now = int(time.time())
    computed_valid_after = 0 if valid_after is None else int(valid_after)
    computed_valid_before = (now + 3600) if valid_before is None else int(valid_before)
    nonce = random_nonce_hex32()

    if isinstance(signer, str):
        acct = Account.from_key(signer)
    else:
        if hasattr(signer, "key"):
            acct = Account.from_key(getattr(signer, "key"))
        elif hasattr(signer, "privateKey"):
            acct = Account.from_key(getattr(signer, "privateKey"))
        else:
            raise TypeError(
                "Unsupported signer type; pass a private key hex string or LocalAccount."
            )

    from_addr = acct.address

    domain = {
        "name": "Bridged USDC (Stargate)",
        "version": "1",
        "chainId": chain_id,
        "verifyingContract": token_address,
    }

    message_types = {
        "TransferWithAuthorization": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "validAfter", "type": "uint256"},
            {"name": "validBefore", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }

    message = {
        "from": from_addr,
        "to": to,
        "value": int(value),
        "validAfter": computed_valid_after,
        "validBefore": computed_valid_before,
        "nonce": nonce,
    }

    signable = encode_typed_data(domain, message_types, message)
    signed = acct.sign_message(signable)
    signature = "0x" + signed.signature.hex()

    payload: Eip3009Payload = {
        "from_": from_addr,
        "to": to,
        "value": str(int(value)),
        "validAfter": computed_valid_after,
        "validBefore": computed_valid_before,
        "nonce": nonce,
        "signature": signature,
        "asset": token_address,
    }

    header = build_eip3009_header(payload, network)
    return encode_payment_header(header)
