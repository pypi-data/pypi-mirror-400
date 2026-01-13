"""x402 helpers for building payment payloads."""

from typing import Any, Dict


def build_payment_payload(
    *,
    payload: Dict[str, Any],
    network: str,
    scheme: str = "exact",
    x402_version: int = 1,
) -> Dict[str, Any]:
    """
    Build a top-level x402 paymentPayload object.

    Args:
        payload: Inner payload object (network-specific fields)
        network: Network identifier (e.g., "base", "solana-devnet")
        scheme: Payment scheme (default: "exact")
        x402_version: Protocol version (default: 1)
    """
    return {
        "x402Version": x402_version,
        "scheme": scheme,
        "network": network,
        "payload": payload,
    }


def build_evm_authorization(
    *,
    from_address: str,
    to_address: str,
    value: str,
    valid_after: str,
    valid_before: str,
    nonce: str,
) -> Dict[str, str]:
    """
    Build an EVM authorization object for EIP-3009-style flows.
    """
    return {
        "from": from_address,
        "to": to_address,
        "value": value,
        "validAfter": valid_after,
        "validBefore": valid_before,
        "nonce": nonce,
    }


def build_evm_payment_payload(
    *,
    signature: str,
    authorization: Dict[str, Any],
    network: str,
    scheme: str = "exact",
    x402_version: int = 1,
) -> Dict[str, Any]:
    """
    Build an x402 paymentPayload for EVM networks.
    """
    payload = {"signature": signature, "authorization": authorization}
    return build_payment_payload(
        payload=payload,
        network=network,
        scheme=scheme,
        x402_version=x402_version,
    )


def build_solana_payment_payload(
    *,
    transaction: str,
    network: str,
    encoding: str = "base64",
    scheme: str = "exact",
    x402_version: int = 1,
) -> Dict[str, Any]:
    """
    Build an x402 paymentPayload for Solana networks.
    """
    payload = {"transaction": transaction, "encoding": encoding}
    return build_payment_payload(
        payload=payload,
        network=network,
        scheme=scheme,
        x402_version=x402_version,
    )
