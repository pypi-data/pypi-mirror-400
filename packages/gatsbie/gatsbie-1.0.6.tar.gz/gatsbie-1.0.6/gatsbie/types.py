"""Type definitions for the Gatsbie SDK."""

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, TypeVar

T = TypeVar("T")


# ============================================================================
# Response Types
# ============================================================================


@dataclass
class HealthResponse:
    """Response from the health check endpoint."""

    status: str


@dataclass
class SolveResponse(Generic[T]):
    """Generic response for successful captcha solves."""

    success: bool
    task_id: str
    service: str
    solution: T
    cost: float
    solve_time: float


# ============================================================================
# Solution Types
# ============================================================================


@dataclass
class DatadomeSolution:
    """Solution for Datadome challenges."""

    datadome: str
    user_agent: str


@dataclass
class RecaptchaSolution:
    """Solution for reCAPTCHA challenges."""

    token: str


@dataclass
class AkamaiCookies:
    """Cookies returned by Akamai."""

    abck: str
    bm_sz: str
    country: Optional[str] = None
    usr_locale: Optional[str] = None


@dataclass
class AkamaiSolution:
    """Solution for Akamai challenges."""

    cookies: AkamaiCookies
    user_agent: str


@dataclass
class VercelSolution:
    """Solution for Vercel challenges."""

    vcrcs: str
    user_agent: str


@dataclass
class ShapeSolution:
    """Solution for Shape challenges.

    Shape uses dynamic header names that vary by site.
    Access the headers dict to get all solution headers.
    """

    headers: Dict[str, str]
    user_agent: str


@dataclass
class ShapeV2Solution:
    """Solution for Shape v2 challenges.

    Returns headers and extra data from the TLS fingerprinting solver.
    """

    headers: Dict[str, str]
    extra: Optional[Dict[str, Any]] = None


@dataclass
class TurnstileSolution:
    """Solution for Cloudflare Turnstile challenges."""

    token: str
    user_agent: str


@dataclass
class PerimeterXCookies:
    """PerimeterX cookies needed for requests."""

    px3: str
    pxde: str
    pxvid: str
    pxcts: str


@dataclass
class PerimeterXSolution:
    """Solution for PerimeterX challenges."""

    cookies: PerimeterXCookies
    user_agent: str


@dataclass
class CloudflareWAFCookies:
    """Cookies returned by Cloudflare WAF."""

    cf_clearance: str


@dataclass
class CloudflareWAFSolution:
    """Solution for Cloudflare WAF challenges."""

    cookies: CloudflareWAFCookies
    user_agent: str


@dataclass
class DatadomeSliderSolution:
    """Solution for Datadome Slider challenges."""

    datadome: str
    user_agent: str


@dataclass
class CaptchaFoxCookies:
    """Cookies returned by CaptchaFox."""

    bm_s: str
    bm_sc: str


@dataclass
class CaptchaFoxSolution:
    """Solution for CaptchaFox challenges."""

    cookie: CaptchaFoxCookies
    user_agent: str


@dataclass
class CastleSolution:
    """Solution for Castle challenges."""

    token: str
    user_agent: str


@dataclass
class Reese84Solution:
    """Solution for Incapsula Reese84 challenges."""

    reese84: str
    user_agent: str


@dataclass
class ForterSolution:
    """Solution for Forter challenges."""

    token: str
    user_agent: str


@dataclass
class FuncaptchaSolution:
    """Solution for Funcaptcha challenges."""

    token: str
    user_agent: str


@dataclass
class SBSDSolution:
    """Solution for Akamai SBSD challenges."""

    bm_s: str
    bm_sc: str
    user_agent: str


# ============================================================================
# Request Types
# ============================================================================


@dataclass
class DatadomeRequest:
    """Request for solving Datadome device check challenges."""

    proxy: str
    target_url: str
    target_method: str = "GET"


@dataclass
class RecaptchaRequest:
    """Request for solving reCAPTCHA v2/v3 (Universal) challenges."""

    proxy: str
    target_url: str
    site_key: str
    size: str
    title: str
    action: Optional[str] = None
    ubd: bool = False


@dataclass
class RecaptchaEnterpriseRequest:
    """Request for solving reCAPTCHA Enterprise challenges."""

    proxy: str
    target_url: str
    site_key: str
    size: str
    title: str
    action: Optional[str] = None
    ubd: bool = False
    sa: Optional[str] = None


@dataclass
class AkamaiRequest:
    """Request for solving Akamai challenges."""

    proxy: str
    target_url: str
    akamai_js_url: str
    page_fp: Optional[str] = None


@dataclass
class VercelRequest:
    """Request for solving Vercel challenges."""

    proxy: str
    target_url: str


@dataclass
class ShapeRequest:
    """Request for solving Shape challenges."""

    proxy: str
    target_url: str
    target_api: str
    shape_js_url: str
    title: str
    method: str


@dataclass
class ShapeV2Request:
    """Request for solving Shape v2 challenges with TLS fingerprinting."""

    url: str
    """Target page URL."""

    proxy: str
    """Proxy URL (required)."""

    pkey: Optional[str] = None
    """Site public key (optional)."""

    script_url: Optional[str] = None
    """Shape script URL (optional)."""

    request: Optional[Dict[str, str]] = None
    """Request parameters (optional)."""

    country: Optional[str] = None
    """Country code for geo-location (optional)."""

    timeout: Optional[int] = None
    """Timeout in seconds (optional)."""


@dataclass
class TurnstileRequest:
    """Request for solving Cloudflare Turnstile challenges."""

    proxy: str
    target_url: str
    site_key: str


@dataclass
class PerimeterXRequest:
    """Request for solving PerimeterX challenges."""

    proxy: str
    target_url: str
    perimeterx_js_url: str
    px_app_id: str


@dataclass
class CloudflareWAFRequest:
    """Request for solving Cloudflare WAF challenges."""

    proxy: str
    target_url: str
    target_method: str = "GET"


@dataclass
class DatadomeSliderRequest:
    """Request for solving Datadome Slider challenges."""

    proxy: str
    target_url: str
    target_method: str = "GET"


@dataclass
class CaptchaFoxRequest:
    """Request for solving CaptchaFox challenges."""

    proxy: str
    target_url: str
    site_key: str


@dataclass
class CastleConfigJSON:
    """Castle configuration parameters."""

    pk: str
    w_url: str
    sw_url: str
    avoid_cookies: bool = False


@dataclass
class CastleRequest:
    """Request for solving Castle challenges."""

    proxy: str
    target_url: str
    config_json: CastleConfigJSON


@dataclass
class Reese84Request:
    """Request for solving Incapsula Reese84 challenges."""

    proxy: str
    reese84_js_url: str


@dataclass
class ForterRequest:
    """Request for solving Forter challenges."""

    proxy: str
    target_url: str
    forter_js_url: str
    site_id: str


@dataclass
class FuncaptchaRequest:
    """Request for solving Funcaptcha challenges."""

    proxy: str
    target_url: str
    custom_api_host: str
    public_key: str


@dataclass
class SBSDRequest:
    """Request for solving Akamai SBSD challenges."""

    proxy: str
    target_url: str
    target_method: str
