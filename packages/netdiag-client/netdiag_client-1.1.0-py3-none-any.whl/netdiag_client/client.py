"""NetDiag API client implementation."""

from __future__ import annotations

from urllib.parse import urlparse, urlencode
from typing import overload

import httpx

from .types import (
    Status,
    ErrorCode,
    ErrorInfo,
    CheckRequest,
    CheckResponse,
    LocationResult,
    PingResult,
    DnsResult,
    TlsResult,
    HttpResult,
    HttpEvidence,
    RedirectHop,
    QuorumInfo,
    Observation,
)
from .errors import NetDiagError, NetDiagApiError, NetDiagRateLimitError


DEFAULT_BASE_URL = "https://api.netdiag.dev"
DEFAULT_TIMEOUT = 30.0


class NetDiagClient:
    """
    Official Python client for the NetDiag API.

    Provides network diagnostics (DNS, TLS, HTTP, Ping) from multiple geographic regions.

    Example:
        >>> from netdiag_client import NetDiagClient
        >>>
        >>> client = NetDiagClient()
        >>> result = client.check("example.com")
        >>> print(result.status)  # Status.HEALTHY, Status.WARNING, or Status.UNHEALTHY
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Create a new NetDiagClient instance.

        Args:
            api_key: API key for authenticated requests (increases rate limits).
            base_url: API base URL. Defaults to "https://api.netdiag.dev".
            timeout: Request timeout in seconds. Defaults to 30.
        """
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        headers = {"Accept": "application/json"}
        if api_key:
            headers["x-api-key"] = api_key

        self._client = httpx.Client(timeout=timeout, headers=headers)

    def __enter__(self) -> NetDiagClient:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()

    @overload
    def check(self, host: str) -> CheckResponse: ...

    @overload
    def check(self, host: CheckRequest) -> CheckResponse: ...

    def check(self, host: str | CheckRequest) -> CheckResponse:
        """
        Run network diagnostics against a host.

        Args:
            host: Target hostname, IP address, URL, or CheckRequest object.

        Returns:
            Complete diagnostics response with results from all regions.

        Raises:
            NetDiagApiError: If the API returns an error response.
            NetDiagRateLimitError: If rate limited (HTTP 429).

        Example:
            >>> # Simple usage with hostname
            >>> result = client.check("example.com")
            >>>
            >>> # Full URL is also accepted (host is extracted)
            >>> result = client.check("https://example.com/path")
            >>>
            >>> # With options
            >>> result = client.check(CheckRequest(
            ...     host="example.com",
            ...     port=443,
            ...     regions="us-west,eu-central",
            ... ))
        """
        if isinstance(host, str):
            request = CheckRequest(host=host)
        else:
            request = host

        if not request.host:
            raise NetDiagError("host is required")

        normalized = self._normalize_request(request)
        url = self._build_url(normalized)

        response = self._client.get(url)
        self._handle_response(response)

        return self._parse_response(response.json())

    @overload
    def check_prometheus(self, host: str) -> str: ...

    @overload
    def check_prometheus(self, host: CheckRequest) -> str: ...

    def check_prometheus(self, host: str | CheckRequest) -> str:
        """
        Run network diagnostics and return Prometheus-formatted metrics.

        Args:
            host: Target hostname, IP address, URL, or CheckRequest object.

        Returns:
            Prometheus metrics as a string.

        Raises:
            NetDiagApiError: If the API returns an error response.
            NetDiagRateLimitError: If rate limited (HTTP 429).
        """
        if isinstance(host, str):
            request = CheckRequest(host=host)
        else:
            request = host

        if not request.host:
            raise NetDiagError("host is required")

        normalized = self._normalize_request(request)
        url = self._build_url(normalized, format="prometheus")

        response = self._client.get(url)
        self._handle_response(response)

        return response.text

    def is_healthy(self, host: str) -> bool:
        """
        Check if a host is healthy.

        Args:
            host: Target hostname, IP address, or URL.

        Returns:
            True if the host status is 'Healthy', False otherwise.
        """
        result = self.check(host)
        return result.status == Status.HEALTHY

    def get_status(self, host: str) -> Status:
        """
        Get the health status of a host.

        Args:
            host: Target hostname, IP address, or URL.

        Returns:
            The health status: Status.HEALTHY, Status.WARNING, or Status.UNHEALTHY.
        """
        result = self.check(host)
        return result.status

    def _normalize_host(self, host: str) -> str:
        """Extract hostname from URL if needed."""
        # Try parsing as URL
        if host.startswith(("http://", "https://")):
            parsed = urlparse(host)
            if parsed.hostname:
                return parsed.hostname

        # Remove protocol prefix manually
        if host.startswith("https://"):
            host = host[8:]
        elif host.startswith("http://"):
            host = host[7:]

        # Remove path/query
        slash_idx = host.find("/")
        if slash_idx > 0:
            host = host[:slash_idx]

        return host

    def _normalize_request(self, request: CheckRequest) -> CheckRequest:
        """Create a normalized request with hostname extracted."""
        normalized_host = self._normalize_host(request.host)
        if normalized_host == request.host:
            return request

        return CheckRequest(
            host=normalized_host,
            port=request.port,
            ping_count=request.ping_count,
            ping_timeout=request.ping_timeout,
            dns=request.dns,
            regions=request.regions,
        )

    def _build_url(self, request: CheckRequest, format: str | None = None) -> str:
        """Build API URL with query parameters."""
        params: dict[str, str] = {"host": request.host}

        if request.port is not None:
            params["port"] = str(request.port)
        if request.ping_count is not None:
            params["pingCount"] = str(request.ping_count)
        if request.ping_timeout is not None:
            params["pingTimeout"] = str(request.ping_timeout)
        if request.dns:
            params["dns"] = request.dns
        if request.regions:
            params["regions"] = request.regions
        if format:
            params["format"] = format

        return f"{self._base_url}/v1/checks?{urlencode(params)}"

    def _handle_response(self, response: httpx.Response) -> None:
        """Handle API error responses."""
        if response.is_success:
            return

        body = response.text

        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            retry_seconds = int(retry_after) if retry_after and retry_after.isdigit() else None
            raise NetDiagRateLimitError(retry_seconds, body)

        raise NetDiagApiError(
            response.status_code,
            f"API error: {response.status_code} {response.reason_phrase}",
            body,
        )

    def _parse_response(self, data: dict) -> CheckResponse:
        """Parse JSON response into CheckResponse."""
        quorum_data = data["quorum"]
        quorum = QuorumInfo(
            required=quorum_data["required"],
            total=quorum_data["total"],
            met=quorum_data["met"],
        )

        observations = [
            Observation(
                code=obs["code"],
                severity=obs["severity"],
                message=obs["message"],
                details=obs.get("details"),
            )
            for obs in data.get("observations", [])
        ]

        return CheckResponse(
            run_id=data["runId"],
            host=data["host"],
            status=Status(data["status"]),
            quorum=quorum,
            started_at=data["startedAt"],
            completed_at=data["completedAt"],
            duration_ms=data["durationMs"],
            observations=observations,
            regions=[self._parse_location(loc) for loc in data["regions"]],
        )

    def _parse_location(self, data: dict) -> LocationResult:
        """Parse location result from JSON."""
        return LocationResult(
            region=data["region"],
            status=Status(data["status"]),
            ping=self._parse_ping(data.get("ping")) if data.get("ping") else None,
            dns=self._parse_dns(data.get("dns")) if data.get("dns") else None,
            tls=self._parse_tls(data.get("tls")) if data.get("tls") else None,
            http=self._parse_http(data.get("http")) if data.get("http") else None,
        )

    def _parse_error(self, data: dict | None) -> ErrorInfo | None:
        """Parse error info from JSON."""
        if not data:
            return None
        return ErrorInfo(
            code=ErrorCode(data["code"]),
            message=data["message"],
            retryable=data.get("retryable"),
            details=data.get("details"),
        )

    def _parse_ping(self, data: dict) -> PingResult:
        """Parse ping result from JSON."""
        return PingResult(
            status=Status(data["status"]),
            sent=data.get("sent", 0),
            received=data.get("received", 0),
            avg_rtt_ms=data.get("avgRttMs"),
            min_rtt_ms=data.get("minRttMs"),
            max_rtt_ms=data.get("maxRttMs"),
            packet_loss_percent=data.get("packetLossPercent"),
            tcp_fallback_used=data.get("tcpFallbackUsed", False),
            error=self._parse_error(data.get("error")),
        )

    def _parse_dns(self, data: dict) -> DnsResult:
        """Parse DNS result from JSON."""
        return DnsResult(
            status=Status(data["status"]),
            resolved_addresses=data.get("resolvedAddresses", []),
            query_time_ms=data.get("queryTimeMs"),
            error=self._parse_error(data.get("error")),
        )

    def _parse_tls(self, data: dict) -> TlsResult:
        """Parse TLS result from JSON."""
        return TlsResult(
            status=Status(data["status"]),
            certificate_valid=data.get("certificateValid", False),
            days_until_expiry=data.get("daysUntilExpiry"),
            expires_at=data.get("expiresAt"),
            subject=data.get("subject"),
            issuer=data.get("issuer"),
            protocol=data.get("protocol"),
            error=self._parse_error(data.get("error")),
        )

    def _parse_http(self, data: dict) -> HttpResult:
        """Parse HTTP result from JSON."""
        evidence = None
        if data.get("evidence"):
            evidence = self._parse_evidence(data["evidence"])

        return HttpResult(
            status=Status(data["status"]),
            status_code=data.get("statusCode"),
            total_time_ms=data.get("totalTimeMs"),
            final_host=data.get("finalHost"),
            error=self._parse_error(data.get("error")),
            evidence=evidence,
        )

    def _parse_evidence(self, data: dict) -> HttpEvidence:
        """Parse HTTP evidence from JSON."""
        redirect_chain = [
            RedirectHop(
                status_code=hop["statusCode"],
                location=hop["location"],
            )
            for hop in data.get("redirectChain", [])
        ]

        return HttpEvidence(
            final_url=data["finalUrl"],
            redirect_chain=redirect_chain,
            headers=data.get("headers", {}),
            set_cookie_count=data.get("setCookieCount", 0),
        )
