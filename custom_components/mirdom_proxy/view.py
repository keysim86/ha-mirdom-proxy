import secrets as secrets_mod
from datetime import datetime

from aiohttp import web
from homeassistant.components.http import HomeAssistantView
from homeassistant.helpers.aiohttp_client import async_get_clientsession

COOKIE_NAME = "mirdom_session"
SESSION_TTL = 30 * 24 * 3600  # 30 days


class MirdomProxyView(HomeAssistantView):
    url = "/mirdom/{path:.*}"
    name = "mirdom_proxy"
    requires_auth = False

    def __init__(self, hass, secret: str, agent_url: str) -> None:
        self._hass = hass
        self._secret = secret
        self._agent_url = agent_url.rstrip("/")
        self._sessions: dict[str, float] = {}

    def _authenticated(self, request: web.Request) -> bool:
        token = request.cookies.get(COOKIE_NAME)
        if token and self._sessions.get(token, 0) > datetime.now().timestamp():
            return True
        return secrets_mod.compare_digest(
            request.query.get("secret", ""), self._secret
        )

    def _create_session(self) -> str:
        token = secrets_mod.token_hex(32)
        self._sessions[token] = datetime.now().timestamp() + SESSION_TTL
        return token

    async def get(self, request: web.Request, path: str = "") -> web.Response:
        if not self._authenticated(request):
            return web.Response(status=401, text="Unauthorized")
        if "secret" in request.query:
            token = self._create_session()
            redirect_to = f"/mirdom/{path}" if path else "/mirdom/"
            response = web.HTTPFound(redirect_to)
            response.set_cookie(
                COOKIE_NAME, token,
                httponly=True, samesite="Lax",
                path="/mirdom/", max_age=SESSION_TTL,
            )
            return response
        return await self._forward(request, "GET", path)

    async def post(self, request: web.Request, path: str = "") -> web.Response:
        if not self._authenticated(request):
            return web.Response(status=401, text="Unauthorized")
        return await self._forward(request, "POST", path)

    async def delete(self, request: web.Request, path: str = "") -> web.Response:
        if not self._authenticated(request):
            return web.Response(status=401, text="Unauthorized")
        return await self._forward(request, "DELETE", path)

    async def _forward(self, request: web.Request, method: str, path: str) -> web.Response:
        params = {k: v for k, v in request.query.items() if k != "secret"}
        url = f"{self._agent_url}/{path}"
        body = await request.read()
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() in ("content-type", "accept")
        }
        session = async_get_clientsession(self._hass)
        async with session.request(method, url, params=params, data=body, headers=headers) as resp:
            content = await resp.read()
            ct = resp.headers.get("Content-Type", "application/octet-stream")
            return web.Response(status=resp.status, body=content, headers={"Content-Type": ct})
