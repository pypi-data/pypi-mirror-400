"""
Kyvern Shield Python SDK.

Protect your AI agent transactions from prompt injection attacks,
wallet drains, and unauthorized transactions.

Example:
    ```python
    from kyvern_shield import KyvernShield

    shield = KyvernShield(api_key="sk_live_kyvern_xxxxx")

    result = shield.analyze(
        intent="Transfer 10 SOL to partner wallet",
        to="TargetWalletAddressHere",
        amount=10.0,
        reasoning="Payment for services rendered"
    )

    if result.is_blocked:
        print(f"BLOCKED: {result.explanation}")
    else:
        # Safe to proceed
        execute_transaction()
    ```
"""

from kyvern_shield.client import (
    # Main clients
    KyvernShield,
    AsyncKyvernShield,
    # Result models
    AnalysisResult,
    HeuristicResult,
    LLMAnalysisResult,
    SourceDetectionResult,
    TransactionIntent,
    # Exceptions
    KyvernShieldError,
    AuthenticationError,
    ValidationError,
    APIError,
    NetworkError,
)

__version__ = "0.1.0"
__all__ = [
    # Clients
    "KyvernShield",
    "AsyncKyvernShield",
    # Models
    "AnalysisResult",
    "HeuristicResult",
    "LLMAnalysisResult",
    "SourceDetectionResult",
    "TransactionIntent",
    # Exceptions
    "KyvernShieldError",
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "NetworkError",
]
