"""
Kyvern Shield Python SDK Client.

This module provides the main client class for interacting with the
Kyvern Shield API to protect AI agent transactions.
"""

from __future__ import annotations

import os
from typing import Any, Literal, Optional
from uuid import uuid4

import httpx
from pydantic import BaseModel, Field, field_validator


# =============================================================================
# MODELS
# =============================================================================


class HeuristicResult(BaseModel):
    """Result from heuristic analysis layer."""

    passed: bool
    blacklisted: bool
    amount_exceeded: bool
    details: list[str] = Field(default_factory=list)


class SourceDetectionResult(BaseModel):
    """Result from source detection layer (indirect injection defense)."""

    risk_score: int
    flags: list[str] = Field(default_factory=list)
    urls_found: list[str] = Field(default_factory=list)
    untrusted_domains: list[str] = Field(default_factory=list)
    sandbox_mode: bool = False
    details: list[str] = Field(default_factory=list)


class LLMAnalysisResult(BaseModel):
    """Result from LLM analysis layer."""

    risk_score: int
    consistency_check: bool
    prompt_injection_detected: bool
    explanation: str
    raw_response: Optional[str] = None


class AnalysisResult(BaseModel):
    """
    Complete analysis result from Kyvern Shield.

    This is the main response object returned by the `analyze()` method.
    """

    request_id: str
    decision: Literal["allow", "block"]
    risk_score: int = Field(ge=0, le=100)
    explanation: str
    heuristic_result: Optional[HeuristicResult] = None
    source_detection_result: Optional[SourceDetectionResult] = None
    llm_result: Optional[LLMAnalysisResult] = None
    analysis_time_ms: float

    @property
    def is_blocked(self) -> bool:
        """Check if the transaction was blocked."""
        return self.decision == "block"

    @property
    def is_allowed(self) -> bool:
        """Check if the transaction was allowed."""
        return self.decision == "allow"

    @property
    def is_high_risk(self) -> bool:
        """Check if the transaction has high risk (score >= 70)."""
        return self.risk_score >= 70

    @property
    def is_low_risk(self) -> bool:
        """Check if the transaction has low risk (score < 30)."""
        return self.risk_score < 30


class TransactionIntent(BaseModel):
    """
    Transaction intent to be analyzed.

    This represents the action your AI agent wants to perform.
    """

    agent_id: str = Field(description="Unique identifier for your agent")
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    target_address: str = Field(description="Destination wallet address")
    amount_sol: float = Field(ge=0, description="Amount in SOL")
    function_signature: str = Field(default="transfer", description="Transaction type")
    reasoning: str = Field(description="Your agent's reasoning for this transaction")

    @field_validator("target_address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate the target address format."""
        if not v or len(v) < 32:
            raise ValueError("Invalid wallet address: must be at least 32 characters")
        return v

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Ensure reasoning is provided."""
        if not v or len(v.strip()) < 10:
            raise ValueError("Reasoning must be at least 10 characters")
        return v


# =============================================================================
# EXCEPTIONS
# =============================================================================


class KyvernShieldError(Exception):
    """Base exception for Kyvern Shield SDK."""

    pass


class AuthenticationError(KyvernShieldError):
    """Raised when API key is invalid or missing."""

    pass


class ValidationError(KyvernShieldError):
    """Raised when request validation fails."""

    pass


class APIError(KyvernShieldError):
    """Raised when the API returns an error."""

    def __init__(self, message: str, status_code: int, response_body: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class NetworkError(KyvernShieldError):
    """Raised when a network error occurs."""

    pass


# =============================================================================
# CLIENT
# =============================================================================


class KyvernShield:
    """
    Kyvern Shield SDK Client.

    Protects your AI agent transactions from prompt injection attacks,
    wallet drains, and unauthorized transactions.

    Example:
        ```python
        from kyvern_shield import KyvernShield

        shield = KyvernShield(api_key="sk_live_kyvern_xxxxx")

        # Before executing any transaction
        result = shield.analyze(
            intent="Transfer 10 SOL to partner wallet",
            to="TargetWalletAddressHere",
            amount=10.0,
            reasoning="Payment for services rendered per contract #123"
        )

        if result.is_blocked:
            print(f"BLOCKED: {result.explanation}")
        else:
            print(f"APPROVED (risk: {result.risk_score})")
            # Proceed with transaction
        ```
    """

    DEFAULT_BASE_URL = "https://api.kyvernlabs.com"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        agent_id: Optional[str] = None,
    ):
        """
        Initialize the Kyvern Shield client.

        Args:
            api_key: Your Kyvern Shield API key (sk_live_kyvern_xxxxx).
                     If not provided, reads from KYVERN_API_KEY env var.
            base_url: API base URL. Defaults to https://api.kyvernlabs.com.
                      For local development, use http://localhost:8000.
            timeout: Request timeout in seconds. Default: 30.0
            agent_id: Default agent ID to use for all requests.
                      Can be overridden per-request.

        Raises:
            AuthenticationError: If no API key is provided.
        """
        self.api_key = api_key or os.environ.get("KYVERN_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key parameter or set KYVERN_API_KEY environment variable."
            )

        if not self.api_key.startswith("sk_live_kyvern_"):
            raise AuthenticationError(
                "Invalid API key format. Keys must start with 'sk_live_kyvern_'"
            )

        self.base_url = (base_url or os.environ.get("KYVERN_API_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.default_agent_id = agent_id or os.environ.get("KYVERN_AGENT_ID") or "default-agent"

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "kyvern-shield-python/0.1.0",
            },
        )

    def __enter__(self) -> "KyvernShield":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def analyze(
        self,
        intent: str,
        to: str,
        amount: float,
        reasoning: str,
        *,
        agent_id: Optional[str] = None,
        function_signature: str = "transfer",
    ) -> AnalysisResult:
        """
        Analyze a transaction intent for security risks.

        Call this BEFORE your agent executes any transaction.
        The Shield will analyze the intent and return a decision.

        Args:
            intent: What the agent intends to do (e.g., "Transfer 10 SOL").
            to: Target wallet address.
            amount: Amount in SOL.
            reasoning: Your agent's reasoning for this transaction.
                       This is critical for detecting manipulation.
            agent_id: Unique identifier for your agent. Uses default if not provided.
            function_signature: Transaction type (default: "transfer").

        Returns:
            AnalysisResult with decision, risk score, and explanation.

        Raises:
            ValidationError: If input validation fails.
            AuthenticationError: If API key is invalid.
            APIError: If the API returns an error.
            NetworkError: If a network error occurs.

        Example:
            ```python
            result = shield.analyze(
                intent="Swap 5 SOL for USDC",
                to="JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
                amount=5.0,
                reasoning="User requested swap via chat interface"
            )

            if result.decision == "block":
                raise SecurityError(result.explanation)
            ```
        """
        # Build the transaction intent
        try:
            transaction = TransactionIntent(
                agent_id=agent_id or self.default_agent_id,
                target_address=to,
                amount_sol=amount,
                function_signature=function_signature,
                reasoning=f"{intent}\n\nReasoning: {reasoning}",
            )
        except Exception as e:
            raise ValidationError(f"Invalid transaction data: {e}") from e

        # Make the API request
        try:
            response = self._client.post(
                "/api/v1/analysis/intent",
                json=transaction.model_dump(),
            )
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out after {self.timeout}s") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}") from e

        # Handle response
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 422:
            raise ValidationError(f"Validation error: {response.text}")
        elif response.status_code >= 400:
            raise APIError(
                f"API error: {response.text}",
                status_code=response.status_code,
                response_body=response.text,
            )

        # Parse and return result
        try:
            data = response.json()
            return AnalysisResult(**data)
        except Exception as e:
            raise APIError(
                f"Failed to parse response: {e}",
                status_code=response.status_code,
                response_body=response.text,
            ) from e

    def health_check(self) -> dict[str, Any]:
        """
        Check if the API is healthy and reachable.

        Returns:
            API health status including version.

        Raises:
            NetworkError: If the API is unreachable.
        """
        try:
            response = self._client.get("/")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to reach API: {e}") from e


# =============================================================================
# ASYNC CLIENT
# =============================================================================


class AsyncKyvernShield:
    """
    Async version of the Kyvern Shield SDK Client.

    Use this for async/await workflows.

    Example:
        ```python
        import asyncio
        from kyvern_shield import AsyncKyvernShield

        async def main():
            async with AsyncKyvernShield(api_key="sk_live_kyvern_xxxxx") as shield:
                result = await shield.analyze(
                    intent="Transfer 10 SOL",
                    to="TargetWalletAddress",
                    amount=10.0,
                    reasoning="Payment for services"
                )
                print(result.decision)

        asyncio.run(main())
        ```
    """

    DEFAULT_BASE_URL = "https://api.kyvernlabs.com"
    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        agent_id: Optional[str] = None,
    ):
        """Initialize the async client. See KyvernShield for parameter docs."""
        self.api_key = api_key or os.environ.get("KYVERN_API_KEY")
        if not self.api_key:
            raise AuthenticationError(
                "API key required. Pass api_key parameter or set KYVERN_API_KEY environment variable."
            )

        if not self.api_key.startswith("sk_live_kyvern_"):
            raise AuthenticationError(
                "Invalid API key format. Keys must start with 'sk_live_kyvern_'"
            )

        self.base_url = (base_url or os.environ.get("KYVERN_API_URL") or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.default_agent_id = agent_id or os.environ.get("KYVERN_AGENT_ID") or "default-agent"

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "kyvern-shield-python/0.1.0",
            },
        )

    async def __aenter__(self) -> "AsyncKyvernShield":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    async def analyze(
        self,
        intent: str,
        to: str,
        amount: float,
        reasoning: str,
        *,
        agent_id: Optional[str] = None,
        function_signature: str = "transfer",
    ) -> AnalysisResult:
        """
        Analyze a transaction intent for security risks (async version).

        See KyvernShield.analyze() for full documentation.
        """
        # Build the transaction intent
        try:
            transaction = TransactionIntent(
                agent_id=agent_id or self.default_agent_id,
                target_address=to,
                amount_sol=amount,
                function_signature=function_signature,
                reasoning=f"{intent}\n\nReasoning: {reasoning}",
            )
        except Exception as e:
            raise ValidationError(f"Invalid transaction data: {e}") from e

        # Make the API request
        try:
            response = await self._client.post(
                "/api/v1/analysis/intent",
                json=transaction.model_dump(),
            )
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timed out after {self.timeout}s") from e
        except httpx.RequestError as e:
            raise NetworkError(f"Network error: {e}") from e

        # Handle response
        if response.status_code == 401:
            raise AuthenticationError("Invalid API key")
        elif response.status_code == 422:
            raise ValidationError(f"Validation error: {response.text}")
        elif response.status_code >= 400:
            raise APIError(
                f"API error: {response.text}",
                status_code=response.status_code,
                response_body=response.text,
            )

        # Parse and return result
        try:
            data = response.json()
            return AnalysisResult(**data)
        except Exception as e:
            raise APIError(
                f"Failed to parse response: {e}",
                status_code=response.status_code,
                response_body=response.text,
            ) from e

    async def health_check(self) -> dict[str, Any]:
        """Check if the API is healthy (async version)."""
        try:
            response = await self._client.get("/")
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise NetworkError(f"Failed to reach API: {e}") from e
