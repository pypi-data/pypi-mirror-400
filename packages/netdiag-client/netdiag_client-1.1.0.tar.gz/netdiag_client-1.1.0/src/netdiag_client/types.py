"""Type definitions for NetDiag API responses."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class Status(str, Enum):
    """Health status using traffic light model."""

    HEALTHY = "Healthy"
    WARNING = "Warning"
    UNHEALTHY = "Unhealthy"


class ErrorCode(str, Enum):
    """Error codes for programmatic handling of diagnostic failures."""

    # General (100s)
    NONE = "None"
    UNKNOWN_ERROR = "UnknownError"
    TIMEOUT = "Timeout"

    # Ping (200s)
    PING_NO_RESPONSE = "PingNoResponse"
    PING_ICMP_BLOCKED = "PingIcmpBlocked"
    PING_HOST_UNREACHABLE = "PingHostUnreachable"

    # DNS (300s)
    DNS_NXDOMAIN = "DnsNxDomain"
    DNS_TIMEOUT = "DnsTimeout"
    DNS_SERVER_FAILURE = "DnsServerFailure"
    DNS_NO_RECORDS = "DnsNoRecords"

    # TLS (400s)
    TLS_CONNECTION_FAILED = "TlsConnectionFailed"
    TLS_CERTIFICATE_EXPIRED = "TlsCertificateExpired"
    TLS_HANDSHAKE_FAILED = "TlsHandshakeFailed"

    # HTTP (500s)
    HTTP_CONNECTION_FAILED = "HttpConnectionFailed"
    HTTP_TIMEOUT = "HttpTimeout"
    HTTP_CONNECTION_REFUSED = "HttpConnectionRefused"


@dataclass
class ErrorInfo:
    """Structured error information with code and message."""

    code: ErrorCode
    message: str
    retryable: bool | None = None
    details: str | None = None


@dataclass
class CheckRequest:
    """Request parameters for multi-region network diagnostics."""

    host: str
    """Target hostname to diagnose."""

    port: int | None = None
    """Optional TCP port number for TLS/HTTP checks (80, 443, 8080, 8443)."""

    ping_count: int | None = None
    """Number of ICMP ping packets to send (1-100). Defaults to 4."""

    ping_timeout: int | None = None
    """Timeout in seconds for each ping attempt (1-30). Defaults to 5."""

    dns: str | None = None
    """Optional custom DNS server to use for resolution."""

    regions: str | None = None
    """Comma-separated list of region codes to run checks from."""

    http_evidence: Literal["0", "1", "auto"] = "0"
    """HTTP evidence collection mode: "0" (none), "1" (always), "auto" (on issues)."""

    max_redirects: int | None = None
    """Maximum number of HTTP redirects to follow (0-10). Only applies when http_evidence is enabled."""


@dataclass
class PingResult:
    """ICMP ping result containing latency and reachability information."""

    status: Status
    sent: int
    received: int
    avg_rtt_ms: float | None
    min_rtt_ms: float | None
    max_rtt_ms: float | None
    packet_loss_percent: float | None
    tcp_fallback_used: bool = False
    error: ErrorInfo | None = None


@dataclass
class DnsResult:
    """DNS resolution result containing resolved IP addresses."""

    status: Status
    resolved_addresses: list[str]
    query_time_ms: int | None
    error: ErrorInfo | None = None


@dataclass
class TlsResult:
    """TLS/SSL certificate validation result."""

    status: Status
    certificate_valid: bool
    days_until_expiry: int | None
    expires_at: str | None
    subject: str | None
    issuer: str | None
    protocol: str | None
    error: ErrorInfo | None = None


@dataclass
class RedirectHop:
    """A single redirect hop in the HTTP redirect chain."""

    status_code: int
    """HTTP status code of the redirect response (e.g., 301, 302, 307)."""

    location: str
    """The Location header value - the URL being redirected to."""


@dataclass
class HttpEvidence:
    """HTTP evidence containing redirect chain and selected response headers."""

    final_url: str
    """The final URL after following all redirects."""

    redirect_chain: list["RedirectHop"]
    """Array of redirect hops, empty if no redirects occurred."""

    headers: dict[str, list[str]]
    """Selected response headers (allowlisted for CDN/WAF detection)."""

    set_cookie_count: int
    """Number of Set-Cookie headers in the response (values not stored for privacy)."""


@dataclass
class HttpResult:
    """HTTP/HTTPS request result containing response status and performance metrics."""

    status: Status
    status_code: int | None
    total_time_ms: int | None
    final_host: str | None
    error: ErrorInfo | None = None
    evidence: HttpEvidence | None = None
    """HTTP evidence containing redirect chain and headers. None if evidence collection was not enabled."""


@dataclass
class LocationResult:
    """Diagnostics results from a specific geographic location/region."""

    region: str
    status: Status
    ping: PingResult | None
    dns: DnsResult | None
    tls: TlsResult | None
    http: HttpResult | None


@dataclass
class QuorumInfo:
    """Quorum information for multi-region health checks."""

    required: int
    """Number of healthy regions required for quorum."""

    total: int
    """Total number of regions checked."""

    met: bool
    """Whether the required quorum was met."""


@dataclass
class Observation:
    """An observation about the diagnostic results (cross-region analysis)."""

    code: str
    """Observation code (e.g., DNS_ANSWERS_MISMATCH, CERT_EXPIRING_SOON)."""

    severity: Literal["info", "warning", "error"]
    """Severity level: info, warning, or error."""

    message: str
    """Human-readable description of the observation."""

    details: dict[str, Any] | None = None
    """Machine-readable details for programmatic handling."""


@dataclass
class CheckResponse:
    """Complete diagnostics response containing results from all network checks."""

    run_id: str
    host: str
    status: Status
    quorum: QuorumInfo
    started_at: str
    completed_at: str
    duration_ms: int
    observations: list[Observation]
    regions: list[LocationResult]
