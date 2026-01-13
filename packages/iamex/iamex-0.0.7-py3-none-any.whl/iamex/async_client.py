"""
Cliente asíncrono basado en httpx, con soporte de timeouts, retries con backoff
exponencial, proxies y streaming SSE compatible con OpenAI.
"""

import os
import json
import asyncio
from typing import Any, AsyncGenerator, Dict, Optional

import httpx

from .errors import (
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    PermissionDeniedError,
    NotFoundError,
    APIStatusError,
    APIConnectionError,
)


class AsyncPromptClient:
    """Cliente asíncrono de bajo nivel para el Hub IAMEX."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        timeout: float = 30.0,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
        proxies: Optional[Dict[str, str]] = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = os.getenv("IAMEX_BASE_URL", "https://api.iamex.io/v1")
        self.base_url_openai = os.getenv("IAMEX_OPENAI_BASE_URL", self.base_url)

        headers: Dict[str, str] = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.timeout = timeout
        self.max_retries = max(0, int(max_retries))
        self.backoff_factor = max(0.0, float(backoff_factor))
        # httpx>=0.28 ya no acepta 'proxies' en el constructor. Si necesitas
        # proxy, configura variables de entorno HTTP_PROXY/HTTPS_PROXY o usa
        # un transporte personalizado. Aquí evitamos romper compat pasando
        # solo headers/timeout.
        self._client = httpx.AsyncClient(headers=headers, timeout=timeout)

    async def aclose(self) -> None:
        await self._client.aclose()

    # ============== Public API ==============
    async def send_prompt(
        self,
        prompt: str,
        *,
        model: str = "IAM-advanced",
        system_prompt: Optional[str] = None,
        full_response: bool = False,
        **kwargs: Any,
    ) -> Any:
        payload = self._prepare_payload(prompt, model, system_prompt, **kwargs)
        openai_compat = kwargs.pop("openai_compat_endpoint", False)
        stream = kwargs.pop("stream", False)
        url_base = self.base_url_openai if openai_compat else self.base_url
        url = f"{url_base}/completions" if openai_compat else f"{url_base}/prompt-model"

        if openai_compat and stream:
            return self._stream_post(url, json=payload)

        resp = await self._post(url, json=payload)
        data = resp.json()
        return data if full_response else self._extract_content(data)

    async def send_messages(
        self,
        messages: list,
        *,
        model: str = "IAM-advanced",
        full_response: bool = False,
        **kwargs: Any,
    ) -> Any:
        payload = self._prepare_messages_payload(messages, model, **kwargs)
        openai_compat = kwargs.pop("openai_compat_endpoint", False)
        stream = kwargs.pop("stream", False)
        url_base = self.base_url_openai if openai_compat else self.base_url
        url = f"{url_base}/chat/completions" if openai_compat else f"{url_base}/prompt-model"

        if openai_compat and stream:
            return self._stream_post(url, json=payload)

        resp = await self._post(url, json=payload)
        data = resp.json()
        return data if full_response else self._extract_content(data)

    async def send_responses(self, payload: Dict[str, Any]) -> Any:
        url = f"{self.base_url_openai}/responses"
        if bool(payload.get("stream")):
            return self._stream_post(url, json=payload)
        resp = await self._post(url, json=payload)
        return resp.json()

    async def get_models(self) -> Dict[str, Any]:
        try:
            res = await self._client.get(f"{self.base_url}/models")
            if res.status_code >= 400:
                self._raise_for_status(res)
            return res.json()
        except httpx.RequestError as e:
            raise APIConnectionError(f"Error de conexión al obtener modelos: {str(e)}")

    # ============== Internos ==============
    async def _post(self, url: str, *, json: Dict[str, Any]) -> httpx.Response:
        attempt = 0
        while True:
            try:
                res = await self._client.post(url, json=json)
                if res.status_code >= 400:
                    self._raise_for_status(res)
                return res
            except httpx.RequestError as e:
                if attempt >= self.max_retries:
                    raise APIConnectionError(f"Error de conexión al enviar POST: {str(e)}")
                # Retry en 429/5xx cuando hay respuesta; o siempre si no hay respuesta
                status = e.response.status_code if getattr(e, "response", None) is not None else None
                should_retry = status in (429, 500, 502, 503, 504) or status is None
                if not should_retry:
                    self._raise_for_status(e.response)  # type: ignore[arg-type]
                await asyncio.sleep(self._compute_backoff(attempt))
                attempt += 1

    async def _stream_post(self, url: str, *, json: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        attempt = 0
        while True:
            try:
                async with self._client.stream("POST", url, json=json) as res:
                    if res.status_code >= 400:
                        self._raise_for_status(res)
                    async for line in res.aiter_lines():
                        if not line:
                            continue
                        line = line.strip()
                        if not line.startswith("data:"):
                            continue
                        data_str = line[len("data:"):].strip()
                        if data_str == "[DONE]":
                            return
                        try:
                            yield json_loads(data_str)
                        except Exception:
                            # ignorar líneas mal formadas
                            continue
                return
            except httpx.RequestError as e:
                if attempt >= self.max_retries:
                    raise APIConnectionError(f"Error de conexión en stream: {str(e)}")
                status = e.response.status_code if getattr(e, "response", None) is not None else None
                should_retry = status in (429, 500, 502, 503, 504) or status is None
                if not should_retry:
                    self._raise_for_status(e.response)  # type: ignore[arg-type]
                await asyncio.sleep(self._compute_backoff(attempt))
                attempt += 1

    def _compute_backoff(self, attempt: int) -> float:
        base = self.backoff_factor * (2 ** attempt)
        return base + (0.05 * base)

    def _raise_for_status(self, res: httpx.Response) -> None:
        status = res.status_code
        try:
            payload = res.json()
            message = payload.get("detail") or (payload.get("error") or {}).get("message")  # type: ignore[assignment]
            if not isinstance(message, str) or not message:
                message = res.text
        except ValueError:
            message = res.text

        if status == 400:
            raise BadRequestError(message or "Bad request", status_code=status)
        if status == 401:
            raise AuthenticationError(message or "Invalid API key", status_code=status)
        if status == 403:
            raise PermissionDeniedError(message or "Permission denied", status_code=status)
        if status == 404:
            raise NotFoundError(message or "Not found", status_code=status)
        if status == 429:
            raise RateLimitError(message or "Rate limit exceeded", status_code=status)
        if 500 <= status <= 599:
            raise APIStatusError(message or "Server error", status_code=status)
        raise APIStatusError(message or f"HTTP {status}", status_code=status)

    # ===== helpers payload y extracción =====
    def _prepare_payload(self, prompt: str, model: str, system_prompt: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"apikey": self.api_key, "model": model, "prompt": prompt}
        if system_prompt:
            payload["system_prompt"] = system_prompt
        for key, value in kwargs.items():
            if key not in ["apikey", "model", "prompt", "system_prompt"]:
                payload[key] = value
        return payload

    def _prepare_messages_payload(self, messages: list, model: str, **kwargs: Any) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"apikey": self.api_key, "model": model, "messages": messages}
        for key, value in kwargs.items():
            if key not in ["apikey", "model", "messages"]:
                payload[key] = value
        return payload

    def _extract_content(self, json_response: Dict[str, Any]) -> str:
        try:
            if "data" in json_response and "response" in json_response["data"]:
                response_data = json_response["data"]["response"]
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    choice = response_data["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        return choice["message"]["content"]
            if "choices" in json_response and len(json_response["choices"]) > 0:
                choice2 = json_response["choices"][0]
                if "message" in choice2 and "content" in choice2["message"]:
                    return choice2["message"]["content"]
            if "content" in json_response:
                return json_response["content"]
            return str(json_response)
        except (KeyError, IndexError, TypeError):
            return str(json_response)


def json_loads(data: str) -> Dict[str, Any]:
    # separada para tests/mocks
    return json.loads(data)


