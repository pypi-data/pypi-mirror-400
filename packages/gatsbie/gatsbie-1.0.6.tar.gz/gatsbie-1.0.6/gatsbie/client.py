"""Gatsbie API client."""

from typing import Any, Dict, Optional, Type, TypeVar

import httpx

from .errors import APIError, RequestError
from .types import (
    AkamaiCookies,
    AkamaiRequest,
    AkamaiSolution,
    CaptchaFoxCookies,
    CaptchaFoxRequest,
    CaptchaFoxSolution,
    CastleRequest,
    CastleSolution,
    CloudflareWAFCookies,
    CloudflareWAFRequest,
    CloudflareWAFSolution,
    DatadomeRequest,
    DatadomeSliderRequest,
    DatadomeSliderSolution,
    DatadomeSolution,
    ForterRequest,
    ForterSolution,
    FuncaptchaRequest,
    FuncaptchaSolution,
    HealthResponse,
    PerimeterXCookies,
    PerimeterXRequest,
    PerimeterXSolution,
    RecaptchaRequest,
    RecaptchaEnterpriseRequest,
    RecaptchaSolution,
    Reese84Request,
    Reese84Solution,
    SBSDRequest,
    SBSDSolution,
    ShapeRequest,
    ShapeSolution,
    ShapeV2Request,
    ShapeV2Solution,
    SolveResponse,
    TurnstileRequest,
    TurnstileSolution,
    VercelRequest,
    VercelSolution,
)

T = TypeVar("T")

DEFAULT_BASE_URL = "https://api2.gatsbie.io"
DEFAULT_TIMEOUT = 120.0


class Client:
    """Gatsbie API client.

    Args:
        api_key: Your Gatsbie API key (should start with 'gats_').
        base_url: Custom base URL for the API (optional).
        timeout: Request timeout in seconds (default: 120).
        http_client: Custom httpx.Client instance (optional).

    Example:
        >>> client = Client("gats_your_api_key")
        >>> response = client.solve_turnstile(TurnstileRequest(
        ...     proxy="http://user:pass@proxy:8080",
        ...     target_url="https://example.com",
        ...     site_key="0x4AAAAAAABS7TtLxsNa7Z2e"
        ... ))
        >>> print(response.solution.token)
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self._client = http_client or httpx.Client(timeout=timeout)
        self._owns_client = http_client is None

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            self._client.close()

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        try:
            response = self._client.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                json=body,
            )
        except httpx.RequestError as e:
            raise RequestError(f"Request failed: {e}") from e

        data = response.json()

        if response.status_code >= 400:
            error = data.get("error", {})
            raise APIError(
                code=error.get("code", "UNKNOWN"),
                message=error.get("message", "Unknown error"),
                details=error.get("details"),
                timestamp=error.get("timestamp"),
                http_status=response.status_code,
            )

        return data

    def _get(self, path: str) -> Dict[str, Any]:
        """Make a GET request."""
        return self._request("GET", path)

    def _post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Make a POST request."""
        return self._request("POST", path, body)

    # ========================================================================
    # API Methods
    # ========================================================================

    def health(self) -> HealthResponse:
        """Check the API server health status.

        Returns:
            HealthResponse with the server status.
        """
        data = self._get("/health")
        return HealthResponse(status=data["status"])

    def solve_datadome(
        self, request: DatadomeRequest
    ) -> SolveResponse[DatadomeSolution]:
        """Solve a Datadome device check challenge.

        Args:
            request: The Datadome request parameters.

        Returns:
            SolveResponse containing the Datadome solution.
        """
        body = {
            "task_type": "datadome-device-check",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "target_method": request.target_method,
        }
        data = self._post("/v1/solve/datadome-device-check", body)
        solution = DatadomeSolution(
            datadome=data["solution"]["datadome"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_recaptcha(
        self, request: RecaptchaRequest
    ) -> SolveResponse[RecaptchaSolution]:
        """Solve a reCAPTCHA v2/v3 (Universal) challenge.

        Args:
            request: The reCAPTCHA request parameters.

        Returns:
            SolveResponse containing the reCAPTCHA solution.
        """
        body: Dict[str, Any] = {
            "task_type": "recaptcha",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "site_key": request.site_key,
            "size": request.size,
            "title": request.title,
        }
        if request.action:
            body["action"] = request.action
        if request.ubd:
            body["ubd"] = request.ubd

        data = self._post("/v1/solve/recaptcha", body)
        solution = RecaptchaSolution(
            token=data["solution"]["token"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_recaptcha_enterprise(
        self, request: RecaptchaEnterpriseRequest
    ) -> SolveResponse[RecaptchaSolution]:
        """Solve a reCAPTCHA Enterprise challenge.

        Args:
            request: The reCAPTCHA Enterprise request parameters.

        Returns:
            SolveResponse containing the reCAPTCHA solution.
        """
        body: Dict[str, Any] = {
            "task_type": "recaptcha_enterprise",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "site_key": request.site_key,
            "size": request.size,
            "title": request.title,
        }
        if request.action:
            body["action"] = request.action
        if request.ubd:
            body["ubd"] = request.ubd
        if request.sa:
            body["sa"] = request.sa

        data = self._post("/v1/solve/recaptcha-enterprise", body)
        solution = RecaptchaSolution(
            token=data["solution"]["token"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_akamai(self, request: AkamaiRequest) -> SolveResponse[AkamaiSolution]:
        """Solve an Akamai bot management challenge.

        Args:
            request: The Akamai request parameters.

        Returns:
            SolveResponse containing the Akamai solution.
        """
        body = {
            "task_type": "akamai",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "akamai_js_url": request.akamai_js_url,
        }
        if request.page_fp:
            body["page_fp"] = request.page_fp

        data = self._post("/v1/solve/akamai", body)
        sol = data["solution"]
        cookies_dict = sol["cookies_dict"]
        cookies = AkamaiCookies(
            abck=cookies_dict["_abck"],
            bm_sz=cookies_dict["bm_sz"],
            country=cookies_dict.get("Country"),
            usr_locale=cookies_dict.get("UsrLocale"),
        )
        solution = AkamaiSolution(
            cookies=cookies,
            user_agent=sol["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_vercel(self, request: VercelRequest) -> SolveResponse[VercelSolution]:
        """Solve a Vercel bot protection challenge.

        Args:
            request: The Vercel request parameters.

        Returns:
            SolveResponse containing the Vercel solution.
        """
        body = {
            "task_type": "vercel",
            "proxy": request.proxy,
            "target_url": request.target_url,
        }
        data = self._post("/v1/solve/vercel", body)
        solution = VercelSolution(
            vcrcs=data["solution"]["_vcrcs"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_shape(self, request: ShapeRequest) -> SolveResponse[ShapeSolution]:
        """Solve a Shape antibot challenge (v1).

        Args:
            request: The Shape request parameters.

        Returns:
            SolveResponse containing the Shape solution with dynamic headers.
        """
        body = {
            "task_type": "shape",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "target_api": request.target_api,
            "shape_js_url": request.shape_js_url,
            "title": request.title,
            "method": request.method,
        }
        data = self._post("/v1/solve/shape", body)
        sol = data["solution"].copy()
        # Shape returns dynamic headers, extract User-Agent separately
        user_agent = sol.pop("User-Agent", "")
        solution = ShapeSolution(
            headers=sol,
            user_agent=user_agent,
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_shape_v2(self, request: ShapeV2Request) -> SolveResponse[ShapeV2Solution]:
        """Solve a Shape antibot challenge using the v2 API with TLS fingerprinting.

        Args:
            request: The Shape v2 request parameters.

        Returns:
            SolveResponse containing the Shape v2 solution with headers and extra data.
        """
        metadata: Dict[str, Any] = {
            "proxy": request.proxy,
        }
        if request.pkey:
            metadata["pkey"] = request.pkey
        if request.script_url:
            metadata["script_url"] = request.script_url
        if request.request:
            metadata["request"] = request.request
        if request.country:
            metadata["country"] = request.country
        if request.timeout:
            metadata["timeout"] = request.timeout

        body = {
            "url": request.url,
            "metadata": metadata,
        }
        data = self._post("/v1/solve/shape-v2", body)
        sol = data["solution"]
        headers = sol.get("headers", {})
        extra = {k: v for k, v in sol.items() if k != "headers"}
        solution = ShapeV2Solution(
            headers=headers,
            extra=extra if extra else None,
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_turnstile(
        self, request: TurnstileRequest
    ) -> SolveResponse[TurnstileSolution]:
        """Solve a Cloudflare Turnstile challenge.

        Args:
            request: The Turnstile request parameters.

        Returns:
            SolveResponse containing the Turnstile solution.
        """
        body = {
            "task_type": "turnstile",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "site_key": request.site_key,
        }
        data = self._post("/v1/solve/turnstile", body)
        solution = TurnstileSolution(
            token=data["solution"]["token"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_perimeterx(
        self, request: PerimeterXRequest
    ) -> SolveResponse[PerimeterXSolution]:
        """Solve a PerimeterX Invisible challenge.

        Args:
            request: The PerimeterX request parameters.

        Returns:
            SolveResponse containing the PerimeterX solution.
        """
        body = {
            "task_type": "perimeterx_invisible",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "perimeterx_js_url": request.perimeterx_js_url,
            "pxAppId": request.px_app_id,
        }
        data = self._post("/v1/solve/perimeterx-invisible", body)
        cookies_data = data["solution"]["perimeterx_cookies"]
        cookies = PerimeterXCookies(
            px3=cookies_data["_px3"],
            pxde=cookies_data["_pxde"],
            pxvid=cookies_data["_pxvid"],
            pxcts=cookies_data["pxcts"],
        )
        solution = PerimeterXSolution(
            cookies=cookies,
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_cloudflare_waf(
        self, request: CloudflareWAFRequest
    ) -> SolveResponse[CloudflareWAFSolution]:
        """Solve a Cloudflare WAF challenge.

        Args:
            request: The Cloudflare WAF request parameters.

        Returns:
            SolveResponse containing the Cloudflare WAF solution.
        """
        body = {
            "task_type": "cloudflare_waf",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "target_method": request.target_method,
        }
        data = self._post("/v1/solve/cloudflare-waf", body)
        cookies_data = data["solution"]["cookies"]
        cookies = CloudflareWAFCookies(
            cf_clearance=cookies_data["cf_clearance"],
        )
        solution = CloudflareWAFSolution(
            cookies=cookies,
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_datadome_slider(
        self, request: DatadomeSliderRequest
    ) -> SolveResponse[DatadomeSliderSolution]:
        """Solve a Datadome Slider CAPTCHA challenge.

        Args:
            request: The Datadome Slider request parameters.

        Returns:
            SolveResponse containing the Datadome Slider solution.
        """
        body = {
            "task_type": "datadome-slider",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "target_method": request.target_method,
        }
        data = self._post("/v1/solve/datadome-slider", body)
        solution = DatadomeSliderSolution(
            datadome=data["solution"]["datadome"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_captchafox(
        self, request: CaptchaFoxRequest
    ) -> SolveResponse[CaptchaFoxSolution]:
        """Solve a CaptchaFox challenge.

        Args:
            request: The CaptchaFox request parameters.

        Returns:
            SolveResponse containing the CaptchaFox solution.
        """
        body = {
            "task_type": "captchafox",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "site_key": request.site_key,
        }
        data = self._post("/v1/solve/captchafox", body)
        cookie_data = data["solution"]["cookie"]
        cookie = CaptchaFoxCookies(
            bm_s=cookie_data["bm_s"],
            bm_sc=cookie_data["bm_sc"],
        )
        solution = CaptchaFoxSolution(
            cookie=cookie,
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_castle(self, request: CastleRequest) -> SolveResponse[CastleSolution]:
        """Solve a Castle challenge.

        Args:
            request: The Castle request parameters.

        Returns:
            SolveResponse containing the Castle solution.
        """
        body = {
            "task_type": "castle",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "config_json": {
                "avoidCookies": request.config_json.avoid_cookies,
                "pk": request.config_json.pk,
                "wUrl": request.config_json.w_url,
                "swUrl": request.config_json.sw_url,
            },
        }
        data = self._post("/v1/solve/castle", body)
        solution = CastleSolution(
            token=data["solution"]["token"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_reese84(self, request: Reese84Request) -> SolveResponse[Reese84Solution]:
        """Solve an Incapsula Reese84 challenge.

        Args:
            request: The Reese84 request parameters.

        Returns:
            SolveResponse containing the Reese84 solution.
        """
        body = {
            "task_type": "reese84",
            "proxy": request.proxy,
            "reese84_js_url": request.reese84_js_url,
        }
        data = self._post("/v1/solve/reese84", body)
        solution = Reese84Solution(
            reese84=data["solution"]["reese84"],
            user_agent=data["solution"]["user_agent"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_forter(self, request: ForterRequest) -> SolveResponse[ForterSolution]:
        """Solve a Forter challenge.

        Args:
            request: The Forter request parameters.

        Returns:
            SolveResponse containing the Forter solution.
        """
        body = {
            "task_type": "forter",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "forter_js_url": request.forter_js_url,
            "site_id": request.site_id,
        }
        data = self._post("/v1/solve/forter", body)
        solution = ForterSolution(
            token=data["solution"]["token"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_funcaptcha(
        self, request: FuncaptchaRequest
    ) -> SolveResponse[FuncaptchaSolution]:
        """Solve a Funcaptcha (Arkose Labs) challenge.

        Args:
            request: The Funcaptcha request parameters.

        Returns:
            SolveResponse containing the Funcaptcha solution.
        """
        body = {
            "task_type": "funcaptcha",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "custom_api_host": request.custom_api_host,
            "public_key": request.public_key,
        }
        data = self._post("/v1/solve/funcaptcha", body)
        solution = FuncaptchaSolution(
            token=data["solution"]["token"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )

    def solve_sbsd(self, request: SBSDRequest) -> SolveResponse[SBSDSolution]:
        """Solve an Akamai SBSD challenge.

        Args:
            request: The SBSD request parameters.

        Returns:
            SolveResponse containing the SBSD solution.
        """
        body = {
            "task_type": "sbsd",
            "proxy": request.proxy,
            "target_url": request.target_url,
            "target_method": request.target_method,
        }
        data = self._post("/v1/solve/sbsd", body)
        solution = SBSDSolution(
            bm_s=data["solution"]["bm_s"],
            bm_sc=data["solution"]["bm_sc"],
            user_agent=data["solution"]["ua"],
        )
        return SolveResponse(
            success=data["success"],
            task_id=data["taskId"],
            service=data["service"],
            solution=solution,
            cost=data["cost"],
            solve_time=data["solveTime"],
        )
