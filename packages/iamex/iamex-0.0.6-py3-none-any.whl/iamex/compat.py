"""
Compatibilidad estilo SDK v1 con nombre IAMEX.

Superficie pública equivalente a OpenAI v1, pero bajo la clase IAMEX:
  - IAMEX.chat.completions.create(...)
  - IAMEX.completions.create(...)
  - IAMEX.models.list()

Las llamadas se enrutan a PromptClient y las respuestas se normalizan
al esquema de chat/text completions (choices, usage, etc.).
"""

import os
import time
import uuid
from typing import Any, Dict, List, Optional, Awaitable, AsyncIterator

from .client import PromptClient
from .async_client import AsyncPromptClient


def _now_unix_seconds() -> int:
    return int(time.time())


def _gen_id(prefix: str) -> str:
    # ID sintético legible y único
    return f"{prefix}_{uuid.uuid4().hex[:24]}"


class _AttrDict(dict):
    """Dict con acceso por atributos: obj.key en lugar de obj["key"].
    Se usa para compat con SDKs que exponen propiedades (e.g., response.output_text).
    """
    def __getattr__(self, key: str) -> Any:
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value


def _to_attr(obj: Any) -> Any:
    if isinstance(obj, dict):
        return _AttrDict({k: _to_attr(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [ _to_attr(v) for v in obj ]
    return obj
class _AwaitableAsyncIterator:
    """Iterador que espera perezosamente a que un awaitable produzca
    el iterador asíncrono real la primera vez que se llama a __anext__.
    """

    def __init__(self, awaitable: Awaitable[AsyncIterator[Any]]):
        self._awaitable = awaitable
        self._iterator: Optional[AsyncIterator[Any]] = None

    async def __anext__(self) -> Any:
        if self._iterator is None:
            self._iterator = await self._awaitable
        return await self._iterator.__anext__()


class _AwaitableAsyncIterable:
    """Envuelve un awaitable que resuelve a AsyncIterator y expone
    un objeto con __aiter__ síncrono para `async for`.
    """

    def __init__(self, awaitable: Awaitable[AsyncIterator[Any]]):
        self._awaitable = awaitable

    def __aiter__(self) -> _AwaitableAsyncIterator:
        return _AwaitableAsyncIterator(self._awaitable)



def _pick_response_container(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Devuelve el contenedor donde está la respuesta principal."""
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, dict) and isinstance(data.get("response"), dict):
            return data["response"]
    return payload


def _normalize_usage(container: Dict[str, Any]) -> Optional[Dict[str, int]]:
    usage = container.get("usage") or container.get("token_usage")
    if isinstance(usage, dict):
        prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
        completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
        total_tokens = usage.get("total_tokens") or (
            (prompt_tokens or 0) + (completion_tokens or 0)
            if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int)
            else None
        )
        result: Dict[str, int] = {}
        if isinstance(prompt_tokens, int):
            result["prompt_tokens"] = prompt_tokens
        if isinstance(completion_tokens, int):
            result["completion_tokens"] = completion_tokens
        if isinstance(total_tokens, int):
            result["total_tokens"] = total_tokens
        return result if result else None
    return None


def _normalize_chat_choices(container: Dict[str, Any]) -> List[Dict[str, Any]]:
    choices = container.get("choices")
    if isinstance(choices, list) and choices:
        normalized: List[Dict[str, Any]] = []
        for index, choice in enumerate(choices):
            if not isinstance(choice, dict):
                continue
            message = choice.get("message")
            role = None
            content = None
            if isinstance(message, dict):
                role = message.get("role")
                content = message.get("content")
                # Fallbacks ampliados: modelos de razonamiento pueden poner texto en reasoning_content
                if not content:
                    content = (
                        message.get("reasoning_content")
                        or message.get("refusal")
                    )
            # Fallbacks
            role = role or "assistant"
            if content is None:
                content = (
                    choice.get("reasoning_content")
                    or choice.get("text")
                    or choice.get("content")
                    or container.get("content")
                )
            normalized.append({
                "index": index,
                "message": {
                    "role": role,
                    "content": content,
                },
                "finish_reason": choice.get("finish_reason") or container.get("finish_reason") or "stop",
            })
        if normalized:
            return normalized
    # Si no hay choices, construir uno a partir de content directo
    content = container.get("content") or container.get("text")
    if content is not None:
        return [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": container.get("finish_reason") or "stop",
        }]
    return []


def _normalize_text_choices(container: Dict[str, Any]) -> List[Dict[str, Any]]:
    choices = container.get("choices")
    if isinstance(choices, list) and choices:
        normalized: List[Dict[str, Any]] = []
        for index, choice in enumerate(choices):
            text_value = None
            if isinstance(choice, dict):
                text_value = choice.get("text")
                if text_value is None and isinstance(choice.get("message"), dict):
                    text_value = choice["message"].get("content")
            normalized.append({
                "index": index,
                "text": text_value,
                "finish_reason": (choice.get("finish_reason") if isinstance(choice, dict) else None) or container.get("finish_reason") or "stop",
            })
        return normalized
    # Fallback a 'content' o 'text'
    text_value = container.get("text") or container.get("content")
    if text_value is not None:
        return [{
            "index": 0,
            "text": text_value,
            "finish_reason": container.get("finish_reason") or "stop",
        }]
    return []


def _extract_content_string(payload: Dict[str, Any]) -> Optional[str]:
    container = _pick_response_container(payload)
    # Prefer chat format
    chat_choices = _normalize_chat_choices(container)
    if chat_choices:
        msg = chat_choices[0].get("message", {})
        return msg.get("content")
    # Fallback to text format
    text_choices = _normalize_text_choices(container)
    if text_choices:
        return text_choices[0].get("text")
    # Last resort
    return container.get("content") or container.get("text")


def _to_chat_completion(payload: Dict[str, Any], model: str) -> Dict[str, Any]:
    container = _pick_response_container(payload)
    result: Dict[str, Any] = {
        "id": payload.get("id") or _gen_id("chatcmpl"),
        "object": "chat.completion",
        "created": payload.get("created") or _now_unix_seconds(),
        "model": payload.get("model") or model,
        "choices": _normalize_chat_choices(container),
    }
    usage = _normalize_usage(container)
    if usage:
        result["usage"] = usage
    return result


def _to_text_completion(payload: Dict[str, Any], model: str) -> Dict[str, Any]:
    container = _pick_response_container(payload)
    result: Dict[str, Any] = {
        "id": payload.get("id") or _gen_id("cmpl"),
        "object": "text_completion",
        "created": payload.get("created") or _now_unix_seconds(),
        "model": payload.get("model") or model,
        "choices": _normalize_text_choices(container),
    }
    usage = _normalize_usage(container)
    if usage:
        result["usage"] = usage
    return result


class _ChatCompletions:
    def __init__(self, prompt_client: PromptClient):
        self._client = prompt_client

    def create(self, *, model: str, messages: List[Dict[str, Any]], **kwargs: Any) -> Dict[str, Any]:
        normalized_messages = _normalize_incoming_messages(messages, instructions=kwargs.pop("instructions", None))
        stream = kwargs.pop("stream", False) is True
        if stream:
            # Devolver iterador de chunks SSE compatibles con OpenAI
            return self._client.send_messages(
                messages=normalized_messages,
                model=model,
                full_response=True,  # no se usa en stream en el Hub, pero no afecta
                openai_compat_endpoint=True,
                stream=True,
                **kwargs,
            )
        full_response = self._client.send_messages(
            messages=normalized_messages,
            model=model,
            full_response=True,
            openai_compat_endpoint=True,
            **kwargs,
        )
        return _to_chat_completion(full_response, model=model)


class _Chat:
    def __init__(self, prompt_client: PromptClient):
        self.completions = _ChatCompletions(prompt_client)


class _Completions:
    def __init__(self, prompt_client: PromptClient):
        self._client = prompt_client

    def create(self, *, model: str, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        stream = kwargs.pop("stream", False) is True
        if stream:
            return self._client.send_prompt(
                prompt=prompt,
                model=model,
                full_response=True,
                openai_compat_endpoint=True,
                stream=True,
                **kwargs,
            )
        full_response = self._client.send_prompt(
            prompt=prompt,
            model=model,
            full_response=True,
            openai_compat_endpoint=True,
            **kwargs,
        )
        return _to_text_completion(full_response, model=model)


class _Models:
    def __init__(self, prompt_client: PromptClient):
        self._client = prompt_client

    def list(self) -> Dict[str, Any]:
        payload = self._client.get_models()

        # Intentar extraer una lista de IDs de modelos de formas comunes
        model_ids: List[str] = []
        if isinstance(payload, dict):
            data = payload.get("data")
            if isinstance(data, list) and data:
                for item in data:
                    if isinstance(item, dict) and isinstance(item.get("id"), str):
                        model_ids.append(item["id"])
            elif isinstance(payload.get("models"), list):
                for item in payload["models"]:
                    if isinstance(item, dict) and isinstance(item.get("id"), str):
                        model_ids.append(item["id"])
                    elif isinstance(item, str):
                        model_ids.append(item)
        elif isinstance(payload, list):
            for item in payload:
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    model_ids.append(item["id"])
                elif isinstance(item, str):
                    model_ids.append(item)

        # Normalizar a esquema tipo OpenAI
        data_items = [{"id": mid, "object": "model"} for mid in model_ids]
        return {"object": "list", "data": data_items}


def _normalize_incoming_messages(messages: List[Dict[str, Any]], instructions: Optional[str] = None) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    if instructions:
        normalized.append({"role": "system", "content": instructions})
    for msg in messages or []:
        if not isinstance(msg, dict):
            continue
        role = msg.get("role")
        content = msg.get("content")
        # Mapear developer -> system
        if role == "developer":
            role = "system"
        normalized.append({"role": role, "content": content})
    return normalized


def _to_responses_payload(payload: Dict[str, Any], *, model: str, role: str = "assistant") -> Dict[str, Any]:
    content_text = _extract_content_string(payload) or ""
    result: Dict[str, Any] = {
        "id": payload.get("id") or _gen_id("resp"),
        "object": "response",
        "created": payload.get("created") or _now_unix_seconds(),
        "model": payload.get("model") or model,
        "output": [
            {
                "index": 0,
                "type": "message",
                "role": role,
                "content": [
                    {"type": "output_text", "text": content_text}
                ],
            }
        ],
        "output_text": content_text,
    }
    usage = _normalize_usage(_pick_response_container(payload))
    if usage:
        result["usage"] = usage
    return result


class _Responses:
    def __init__(self, prompt_client: PromptClient):
        self._client = prompt_client

    def create(
        self,
        *,
        model: str,
        input: Optional[Any] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        instructions: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        # Si vienen messages, tratamos como chat (preferimos /v1/responses si existe)
        if messages is not None:
            normalized_messages = _normalize_incoming_messages(messages, instructions=instructions)
            # Intentar enviar al endpoint /v1/responses
            try:
                # Streaming directo si stream=True
                if kwargs.pop("stream", False) is True:
                    return self._client.send_responses({
                        "model": model,
                        "messages": normalized_messages,
                        **kwargs,
                    })
                full = self._client.send_responses({
                    "model": model,
                    "messages": normalized_messages,
                    **kwargs,
                })
                # Algunos hubs podrían ya devolver object=response
                if isinstance(full, dict) and full.get("object") == "response":
                    return _to_attr(full)
                # Si no, normalizamos igual
                return _to_attr(_to_responses_payload(full, model=model, role="assistant"))
            except Exception:
                # Fallback a /v1/chat/completions
                full = self._client.send_messages(
                    messages=normalized_messages,
                    model=model,
                    full_response=True,
                    openai_compat_endpoint=True,
                    **kwargs,
                )
                return _to_attr(_to_responses_payload(full, model=model, role="assistant"))

        # Sino, tratamos como "input" y preferimos /v1/responses; si falla, fallback a chat.completions
        prompt_text = input if isinstance(input, str) else (" ".join(input) if isinstance(input, list) else "")
        try:
            if kwargs.pop("stream", False) is True:
                return self._client.send_responses({
                    "model": model,
                    "input": prompt_text,
                    **({"instructions": instructions} if instructions else {}),
                    **kwargs,
                })
            full = self._client.send_responses({
                "model": model,
                "input": prompt_text,
                **({"instructions": instructions} if instructions else {}),
                **kwargs,
            })
            if isinstance(full, dict) and full.get("object") == "response":
                return _to_attr(full)
            return _to_attr(_to_responses_payload(full, model=model, role="assistant"))
        except Exception:
            normalized_messages = _normalize_incoming_messages(
                messages=[{"role": "user", "content": prompt_text}],
                instructions=instructions,
            )
            full = self._client.send_messages(
                messages=normalized_messages,
                model=model,
                full_response=True,
                openai_compat_endpoint=True,
                **kwargs,
            )
            return _to_attr(_to_responses_payload(full, model=model, role="assistant"))


class IAMEX:
    """Cliente de alto nivel con interfaz estilo v1.

    Ejemplo de uso:
        from iamex import IAMEX
        client = IAMEX(api_key="...")
        client.chat.completions.create(model="IAM-advanced", messages=[...])
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.getenv("IAMEX_API_KEY")
        # PromptClient ya conoce el endpoint real
        self._prompt_client = PromptClient(api_key=api_key)
        if base_url:
            # Permitir override si se pasa explícitamente
            self._prompt_client.base_url = base_url

        self.chat = _Chat(self._prompt_client)
        self.completions = _Completions(self._prompt_client)
        self.models = _Models(self._prompt_client)
        self.responses = _Responses(self._prompt_client)
        
        # Importar y agregar funcionalidades de imagen y visión
        from .image import _Image
        from .vision import _Vision
        self.image = _Image(self._prompt_client)
        self.vision = _Vision(self._prompt_client)


class AsyncIAMEX:
    """Versión asíncrona de alto nivel, similar a OpenAI Async client.

    Uso:
        async with AsyncIAMEX(api_key="...") as client:
            async for chunk in client.chat.completions.create(..., stream=True):
                ...
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        api_key = api_key or os.getenv("IAMEX_API_KEY")
        self._prompt_client = AsyncPromptClient(api_key=api_key)
        if base_url:
            self._prompt_client.base_url = base_url
            self._prompt_client.base_url_openai = base_url

        # Reutilizamos las mismas fachadas pero invocando métodos async del cliente
        self.chat = _AsyncChat(self._prompt_client)
        self.completions = _AsyncCompletions(self._prompt_client)
        self.responses = _AsyncResponses(self._prompt_client)
        self.models = _AsyncModels(self._prompt_client)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        await self._prompt_client.aclose()


class _AsyncChatCompletions:
    def __init__(self, client: AsyncPromptClient):
        self._client = client

    def create(self, *, model: str, messages: List[Dict[str, Any]], **kwargs: Any):
        normalized_messages = _normalize_incoming_messages(messages, instructions=kwargs.pop("instructions", None))
        stream = kwargs.pop("stream", False) is True
        if stream:
            return _AwaitableAsyncIterable(self._client.send_messages(
                messages=normalized_messages,
                model=model,
                full_response=True,
                openai_compat_endpoint=True,
                stream=True,
                **kwargs,
            ))
        full = self._client.send_messages(
            messages=normalized_messages,
            model=model,
            full_response=True,
            openai_compat_endpoint=True,
            **kwargs,
        )
        return _to_chat_completion(full, model=model)


class _AsyncChat:
    def __init__(self, client: AsyncPromptClient):
        self.completions = _AsyncChatCompletions(client)


class _AsyncCompletions:
    def __init__(self, client: AsyncPromptClient):
        self._client = client

    def create(self, *, model: str, prompt: str, **kwargs: Any):
        stream = kwargs.pop("stream", False) is True
        if stream:
            return _AwaitableAsyncIterable(self._client.send_prompt(
                prompt=prompt,
                model=model,
                full_response=True,
                openai_compat_endpoint=True,
                stream=True,
                **kwargs,
            ))
        full = self._client.send_prompt(
            prompt=prompt,
            model=model,
            full_response=True,
            openai_compat_endpoint=True,
            **kwargs,
        )
        return _to_text_completion(full, model=model)


class _AsyncResponses:
    def __init__(self, client: AsyncPromptClient):
        self._client = client

    def create(
        self,
        *,
        model: str,
        input: Optional[Any] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        instructions: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        if messages is not None:
            normalized_messages = _normalize_incoming_messages(messages, instructions=instructions)
            if kwargs.pop("stream", False) is True:
                return _AwaitableAsyncIterable(self._client.send_responses({
                    "model": model,
                    "messages": normalized_messages,
                    "stream": True,
                    **kwargs,
                }))
            full = self._client.send_responses({
                "model": model,
                "messages": normalized_messages,
                **kwargs,
            })
            if isinstance(full, dict) and full.get("object") == "response":
                return _to_attr(full)
            return _to_attr(_to_responses_payload(full, model=model, role="assistant"))
        prompt_text = input if isinstance(input, str) else (" ".join(input) if isinstance(input, list) else "")
        if kwargs.pop("stream", False) is True:
            return _AwaitableAsyncIterable(self._client.send_responses({
                "model": model,
                "input": prompt_text,
                "stream": True,
                **({"instructions": instructions} if instructions else {}),
                **kwargs,
            }))
        full = self._client.send_responses({
            "model": model,
            "input": prompt_text,
            **({"instructions": instructions} if instructions else {}),
            **kwargs,
        })
        if isinstance(full, dict) and full.get("object") == "response":
            return _to_attr(full)
        return _to_attr(_to_responses_payload(full, model=model, role="assistant"))


class _AsyncModels:
    def __init__(self, client: AsyncPromptClient):
        self._client = client

    async def list(self) -> Dict[str, Any]:
        return await self._client.get_models()


__all__ = ["IAMEX", "AsyncIAMEX"]


