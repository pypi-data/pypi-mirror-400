"""
Adlibo SDK for Python
AI Prompt Injection Protection

Example:
    >>> from adlibo import Adlibo
    >>> client = Adlibo("al_live_xxx")
    >>> result = client.analyze("user input")
    >>> if not result.safe:
    ...     print(f"Threat detected: {result.severity}")
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import httpx

__version__ = "1.2.0"
__all__ = [
    "Adlibo",
    "AsyncAdlibo",
    "AdliboError",
    "AnalyzeResult",
    "DetectResult",
    "SanitizeResult",
    "DlpResult",
    "DlpFinding",
    "Severity",
    "Action",
    "Category",
    "DlpDomain",
    "DlpAction",
    "PatternMatch",
]


# ==================== ENUMS ====================


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Action(str, Enum):
    LOG = "LOG"
    WARN = "WARN"
    BLOCK = "BLOCK"
    ALERT = "ALERT"


class Category(str, Enum):
    DIRECT_OVERRIDE = "DIRECT_OVERRIDE"
    ROLE_MANIPULATION = "ROLE_MANIPULATION"
    EXTRACTION = "EXTRACTION"
    FORMAT_TOKENS = "FORMAT_TOKENS"
    FAKE_AUTHORITY = "FAKE_AUTHORITY"
    DAN_JAILBREAK = "DAN_JAILBREAK"
    ROLEPLAY_ATTACK = "ROLEPLAY_ATTACK"
    HYPOTHETICAL = "HYPOTHETICAL"
    EMOTIONAL = "EMOTIONAL"
    GRADUAL_BOUNDARY = "GRADUAL_BOUNDARY"
    CONTEXT_EXPLOIT = "CONTEXT_EXPLOIT"
    ENCODING = "ENCODING"
    TECHNICAL = "TECHNICAL"
    MODEL_INFO = "MODEL_INFO"
    HARMFUL_BEHAVIOR = "HARMFUL_BEHAVIOR"


class DlpDomain(str, Enum):
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    HR = "hr"
    LEGAL = "legal"
    TECH = "tech"
    GOVERNMENT = "government"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    REALESTATE = "realestate"


class DlpAction(str, Enum):
    BLOCKED = "BLOCKED"
    REDACTED = "REDACTED"
    ALLOWED = "ALLOWED"


# ==================== DATA CLASSES ====================


@dataclass
class PatternMatch:
    """A matched pattern in the analysis."""

    category: Category
    match: str
    score: int
    pattern: Optional[str] = None


@dataclass
class AnalyzeMetadata:
    """Metadata from analysis."""

    input_length: int
    processing_time_ms: float
    patterns_checked: int
    encoding_detected: bool


@dataclass
class AnalyzeResult:
    """Result from the analyze endpoint."""

    safe: bool
    risk_score: int
    severity: Severity
    action: Action
    categories: List[Category]
    metadata: AnalyzeMetadata
    patterns: Optional[List[PatternMatch]] = None
    sanitized: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalyzeResult":
        """Create from API response dict."""
        patterns = None
        if "patterns" in data and data["patterns"]:
            patterns = [
                PatternMatch(
                    category=Category(p["category"]),
                    match=p["match"],
                    score=p["score"],
                    pattern=p.get("pattern"),
                )
                for p in data["patterns"]
            ]

        meta = data.get("metadata", {})
        metadata = AnalyzeMetadata(
            input_length=meta.get("inputLength", 0),
            processing_time_ms=meta.get("processingTimeMs", 0),
            patterns_checked=meta.get("patternsChecked", 0),
            encoding_detected=meta.get("encodingDetected", False),
        )

        return cls(
            safe=data["safe"],
            risk_score=data["riskScore"],
            severity=Severity(data["severity"]),
            action=Action(data["action"]),
            categories=[Category(c) for c in data.get("categories", [])],
            patterns=patterns,
            sanitized=data.get("sanitized"),
            metadata=metadata,
        )


@dataclass
class DetectResult:
    """Result from the detect endpoint."""

    detected: bool
    risk_score: int
    category: Optional[Category] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectResult":
        """Create from API response dict."""
        return cls(
            detected=data["detected"],
            risk_score=data["riskScore"],
            category=Category(data["category"]) if data.get("category") else None,
        )


@dataclass
class SanitizeResult:
    """Result from the sanitize endpoint."""

    text: str
    patterns_removed: int
    categories_removed: List[Category]
    original_risk_score: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SanitizeResult":
        """Create from API response dict."""
        return cls(
            text=data["text"],
            patterns_removed=data["patternsRemoved"],
            categories_removed=[Category(c) for c in data.get("categoriesRemoved", [])],
            original_risk_score=data["originalRiskScore"],
        )


@dataclass
class RateLimitInfo:
    """Rate limit information."""

    remaining: int
    limit: int
    reset: int


@dataclass
class DlpFinding:
    """A DLP finding in content."""

    domain: DlpDomain
    type: str
    severity: Severity
    match: str
    position: Dict[str, int]
    redacted: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DlpFinding":
        return cls(
            domain=DlpDomain(data["domain"]),
            type=data["type"],
            severity=Severity(data["severity"]),
            match=data["match"],
            position=data["position"],
            redacted=data.get("redacted"),
        )


@dataclass
class DlpResult:
    """Result from DLP analysis."""

    safe: bool
    findings: List[DlpFinding]
    redacted_content: Optional[str]
    total_findings: int
    action: DlpAction
    processing_time_ms: float

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DlpResult":
        findings = [DlpFinding.from_dict(f) for f in data.get("findings", [])]
        return cls(
            safe=data["safe"],
            findings=findings,
            redacted_content=data.get("redactedContent"),
            total_findings=data["totalFindings"],
            action=DlpAction(data["action"]),
            processing_time_ms=data.get("processingTimeMs", 0),
        )


# ==================== EXCEPTIONS ====================


class AdliboError(Exception):
    """Base exception for Adlibo SDK."""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.status = status
        self.details = details or {}


class RateLimitError(AdliboError):
    """Rate limit exceeded."""

    def __init__(self, message: str, reset_at: int):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)
        self.reset_at = reset_at


class AuthenticationError(AdliboError):
    """Authentication failed."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, "AUTHENTICATION_FAILED", 401)


# ==================== SYNC CLIENT ====================


class Adlibo:
    """
    Adlibo SDK client for Python.

    Args:
        api_key: Your Adlibo API key (starts with al_live_ or al_test_)
        base_url: API base URL (default: https://www.adlibo.com/api/v1)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Max retry attempts for failed requests (default: 3)

    Example:
        >>> client = Adlibo("al_live_xxx")
        >>> result = client.analyze("user input")
        >>> print(result.safe, result.risk_score)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.adlibo.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        if not api_key:
            raise AdliboError("API key is required", "MISSING_API_KEY")
        if not api_key.startswith("al_"):
            raise AdliboError("Invalid API key format", "INVALID_API_KEY")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"adlibo-sdk-python/{__version__}",
            },
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Get the last rate limit info."""
        return self._rate_limit

    def analyze(
        self,
        text: str,
        *,
        include_details: bool = True,
        sanitize: bool = False,
        threshold: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AnalyzeResult:
        """
        Analyze text for prompt injection attacks.

        Args:
            text: The text to analyze
            include_details: Include pattern details in response
            sanitize: Also sanitize the text
            threshold: Custom threshold (0-100)
            metadata: Custom metadata to log

        Returns:
            AnalyzeResult with risk score and detected patterns
        """
        data = self._request(
            "/analyze",
            {
                "text": text,
                "options": {
                    "includeDetails": include_details,
                    "sanitize": sanitize,
                    "threshold": threshold,
                    "metadata": metadata,
                },
            },
        )
        return AnalyzeResult.from_dict(data)

    def detect(self, text: str) -> DetectResult:
        """
        Quick detection check (faster than analyze).

        Args:
            text: The text to check

        Returns:
            DetectResult with detection status
        """
        data = self._request("/detect", {"text": text})
        return DetectResult.from_dict(data)

    def sanitize(self, text: str) -> SanitizeResult:
        """
        Sanitize text by removing detected patterns.

        Args:
            text: The text to sanitize

        Returns:
            SanitizeResult with cleaned text
        """
        data = self._request("/sanitize", {"text": text})
        return SanitizeResult.from_dict(data)

    def is_safe(self, text: str) -> bool:
        """
        Convenience method to check if text is safe.

        Args:
            text: The text to check

        Returns:
            True if safe, False if threat detected
        """
        result = self.detect(text)
        return not result.detected

    def feedback(
        self,
        text: str,
        *,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
        expected_categories: Optional[List[Category]] = None,
        context: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        Submit feedback for false positives/negatives.

        Args:
            text: The text that was analyzed
            is_false_positive: Was this a false positive
            is_false_negative: Was this a false negative
            expected_categories: Expected categories
            context: Additional context

        Returns:
            Confirmation dict
        """
        return self._request(
            "/feedback",
            {
                "text": text,
                "isFalsePositive": is_false_positive,
                "isFalseNegative": is_false_negative,
                "expectedCategories": (
                    [c.value for c in expected_categories] if expected_categories else None
                ),
                "context": context,
            },
        )

    def _request(
        self, endpoint: str, body: Dict[str, Any], attempt: int = 1
    ) -> Dict[str, Any]:
        """Make an HTTP request with retries."""
        try:
            response = self._client.post(endpoint, json=body)
            self._update_rate_limit(response)

            if response.status_code == 429:
                reset = int(response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitError("Rate limit exceeded", reset)

            if response.status_code == 401:
                raise AuthenticationError()

            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise AdliboError(
                    error_data.get("message", f"Request failed: {response.status_code}"),
                    error_data.get("code", "API_ERROR"),
                    response.status_code,
                    error_data,
                )

            return response.json()

        except httpx.TimeoutException:
            if attempt < self.max_retries:
                time.sleep(2**attempt)
                return self._request(endpoint, body, attempt + 1)
            raise AdliboError("Request timeout", "TIMEOUT")

        except httpx.RequestError as e:
            if attempt < self.max_retries:
                time.sleep(2**attempt)
                return self._request(endpoint, body, attempt + 1)
            raise AdliboError(str(e), "NETWORK_ERROR")

    def _update_rate_limit(self, response: httpx.Response):
        """Update rate limit info from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        limit = response.headers.get("X-RateLimit-Limit")
        reset = response.headers.get("X-RateLimit-Reset")

        if remaining and limit and reset:
            self._rate_limit = RateLimitInfo(
                remaining=int(remaining),
                limit=int(limit),
                reset=int(reset),
            )

    # ==================== DLP METHODS ====================

    @property
    def dlp(self) -> "DlpClient":
        """Get the DLP client for data loss prevention."""
        if not hasattr(self, "_dlp_client"):
            self._dlp_client = DlpClient(self)
        return self._dlp_client


class DlpClient:
    """DLP (Data Loss Prevention) client."""

    def __init__(self, client: Adlibo):
        self._client = client

    def analyze(
        self,
        content: str,
        *,
        domains: Optional[List[DlpDomain]] = None,
        action: DlpAction = DlpAction.REDACTED,
        custom_patterns: Optional[List[Dict[str, Any]]] = None,
    ) -> DlpResult:
        """
        Analyze content for sensitive data.

        Args:
            content: Content to analyze
            domains: Domains to check (default: all)
            action: Action to take (default: REDACTED)
            custom_patterns: Custom regex patterns to check

        Returns:
            DlpResult with findings
        """
        data = self._client._request(
            "/dlp/analyze",
            {
                "content": content,
                "domains": [d.value for d in domains] if domains else None,
                "action": action.value,
                "customPatterns": custom_patterns,
            },
        )
        return DlpResult.from_dict(data)

    def has_sensitive_data(
        self,
        content: str,
        domains: Optional[List[DlpDomain]] = None,
    ) -> bool:
        """Check if content contains sensitive data."""
        result = self.analyze(content, domains=domains, action=DlpAction.ALLOWED)
        return not result.safe

    def redact(
        self,
        content: str,
        domains: Optional[List[DlpDomain]] = None,
    ) -> str:
        """Redact sensitive data from content."""
        result = self.analyze(content, domains=domains, action=DlpAction.REDACTED)
        return result.redacted_content or content


# ==================== ASYNC CLIENT ====================


class AsyncAdlibo:
    """
    Async Adlibo SDK client for Python.

    Args:
        api_key: Your Adlibo API key
        base_url: API base URL
        timeout: Request timeout in seconds
        max_retries: Max retry attempts

    Example:
        >>> async with AsyncAdlibo("al_live_xxx") as client:
        ...     result = await client.analyze("user input")
        ...     print(result.safe)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://www.adlibo.com/api/v1",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        if not api_key:
            raise AdliboError("API key is required", "MISSING_API_KEY")
        if not api_key.startswith("al_"):
            raise AdliboError("Invalid API key format", "INVALID_API_KEY")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self._rate_limit: Optional[RateLimitInfo] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"adlibo-sdk-python/{__version__}",
            },
        )
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    @property
    def rate_limit(self) -> Optional[RateLimitInfo]:
        """Get the last rate limit info."""
        return self._rate_limit

    async def analyze(
        self,
        text: str,
        *,
        include_details: bool = True,
        sanitize: bool = False,
        threshold: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AnalyzeResult:
        """Analyze text for prompt injection attacks."""
        data = await self._request(
            "/analyze",
            {
                "text": text,
                "options": {
                    "includeDetails": include_details,
                    "sanitize": sanitize,
                    "threshold": threshold,
                    "metadata": metadata,
                },
            },
        )
        return AnalyzeResult.from_dict(data)

    async def detect(self, text: str) -> DetectResult:
        """Quick detection check."""
        data = await self._request("/detect", {"text": text})
        return DetectResult.from_dict(data)

    async def sanitize(self, text: str) -> SanitizeResult:
        """Sanitize text by removing detected patterns."""
        data = await self._request("/sanitize", {"text": text})
        return SanitizeResult.from_dict(data)

    async def is_safe(self, text: str) -> bool:
        """Check if text is safe."""
        result = await self.detect(text)
        return not result.detected

    async def feedback(
        self,
        text: str,
        *,
        is_false_positive: bool = False,
        is_false_negative: bool = False,
        expected_categories: Optional[List[Category]] = None,
        context: Optional[str] = None,
    ) -> Dict[str, bool]:
        """Submit feedback for false positives/negatives."""
        return await self._request(
            "/feedback",
            {
                "text": text,
                "isFalsePositive": is_false_positive,
                "isFalseNegative": is_false_negative,
                "expectedCategories": (
                    [c.value for c in expected_categories] if expected_categories else None
                ),
                "context": context,
            },
        )

    async def _request(
        self, endpoint: str, body: Dict[str, Any], attempt: int = 1
    ) -> Dict[str, Any]:
        """Make an async HTTP request with retries."""
        if not self._client:
            raise AdliboError("Client not initialized. Use async with.", "NOT_INITIALIZED")

        try:
            response = await self._client.post(endpoint, json=body)
            self._update_rate_limit(response)

            if response.status_code == 429:
                reset = int(response.headers.get("X-RateLimit-Reset", 0))
                raise RateLimitError("Rate limit exceeded", reset)

            if response.status_code == 401:
                raise AuthenticationError()

            if response.status_code >= 400:
                error_data = response.json() if response.content else {}
                raise AdliboError(
                    error_data.get("message", f"Request failed: {response.status_code}"),
                    error_data.get("code", "API_ERROR"),
                    response.status_code,
                    error_data,
                )

            return response.json()

        except httpx.TimeoutException:
            if attempt < self.max_retries:
                import asyncio
                await asyncio.sleep(2**attempt)
                return await self._request(endpoint, body, attempt + 1)
            raise AdliboError("Request timeout", "TIMEOUT")

        except httpx.RequestError as e:
            if attempt < self.max_retries:
                import asyncio
                await asyncio.sleep(2**attempt)
                return await self._request(endpoint, body, attempt + 1)
            raise AdliboError(str(e), "NETWORK_ERROR")

    def _update_rate_limit(self, response: httpx.Response):
        """Update rate limit info from response headers."""
        remaining = response.headers.get("X-RateLimit-Remaining")
        limit = response.headers.get("X-RateLimit-Limit")
        reset = response.headers.get("X-RateLimit-Reset")

        if remaining and limit and reset:
            self._rate_limit = RateLimitInfo(
                remaining=int(remaining),
                limit=int(limit),
                reset=int(reset),
            )
