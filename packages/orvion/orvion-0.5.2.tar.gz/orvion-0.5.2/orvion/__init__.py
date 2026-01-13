"""Orvion SDK for x402 payment-protected APIs"""

from orvion.client import OrvionClient
from orvion.exceptions import (
    OrvionError,
    OrvionAPIError,
    OrvionAuthError,
    OrvionConfigError,
    OrvionTimeoutError,
)
from orvion.models import (
    Charge,
    ChargeState,
    CheckoutSession,
    ConfirmResult,
    HealthInfo,
    PaymentInfo,
    PaymentMethodInfo,
    RouteConfig,
    VerifyResult,
    WalletPaymentInfo,
)
from orvion.telemetry import TelemetryConfig, TelemetryManager, get_telemetry, init_telemetry
from orvion.x402 import (
    build_evm_authorization,
    build_evm_payment_payload,
    build_payment_payload,
    build_solana_payment_payload,
)

__version__ = "0.5.2"

__all__ = [
    # Client
    "OrvionClient",
    # Exceptions
    "OrvionError",
    "OrvionAPIError",
    "OrvionAuthError",
    "OrvionConfigError",
    "OrvionTimeoutError",
    # Core Models
    "Charge",
    "PaymentInfo",
    "RouteConfig",
    "VerifyResult",
    # New Models (v0.2.0)
    "CheckoutSession",
    "ConfirmResult",
    "ChargeState",
    "HealthInfo",
    "WalletPaymentInfo",
    "PaymentMethodInfo",
    # Telemetry
    "TelemetryConfig",
    "TelemetryManager",
    "init_telemetry",
    "get_telemetry",
    # x402 helpers
    "build_payment_payload",
    "build_evm_authorization",
    "build_evm_payment_payload",
    "build_solana_payment_payload",
]
