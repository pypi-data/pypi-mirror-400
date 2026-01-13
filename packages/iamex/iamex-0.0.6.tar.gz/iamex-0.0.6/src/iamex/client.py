"""
Cliente principal para consumir la API de modelos de inferencia
"""

import os
import json
import time
import math
import requests
from typing import Dict, Any, Optional, Generator, Iterable

from .errors import (
    AuthenticationError,
    RateLimitError,
    BadRequestError,
    PermissionDeniedError,
    NotFoundError,
    APIStatusError,
    APIConnectionError,
)


class PromptClient:
    """Cliente para enviar prompts a modelos de inferencia"""
    
    def __init__(
        self,
        api_key: str = None,
        *,
        timeout: float = 30.0,
        max_retries: int = 2,
        backoff_factor: float = 0.5,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
        Inicializa el cliente
        
        Args:
            api_key: Clave de API para autenticación (opcional por ahora)
        """
        self.api_key = api_key
        # Nuevo dominio sin legacy: por defecto todo en "/v1".
        # Overridable vía IAMEX_BASE_URL / IAMEX_OPENAI_BASE_URL.
        self.base_url = os.getenv("IAMEX_BASE_URL", "https://api.iamex.io/v1")
        # Compatibilidad estilo OpenAI (idéntico al base_url por defecto).
        self.base_url_openai = os.getenv("IAMEX_OPENAI_BASE_URL", self.base_url)
        self.session = requests.Session()
        
        # Configurar headers básicos
        self.session.headers.update({
            'accept': 'application/json',
            'Content-Type': 'application/json'
        })
        if self.api_key:
            self.session.headers.update({'Authorization': f'Bearer {self.api_key}'})

        # Config básica de red
        self.timeout = timeout
        self.max_retries = max(0, int(max_retries))
        self.backoff_factor = max(0.0, float(backoff_factor))
        if proxies:
            # Ejemplo: {"http": "http://proxy:8080", "https": "http://proxy:8080"}
            self.session.proxies.update(proxies)
    
    def send_prompt(self, prompt: str, model: str = "IAM-advanced", system_prompt: str = None, full_response: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Envía un prompt al modelo especificado
        
        Args:
            prompt: El prompt del usuario a enviar
            model: Modelo a usar (por defecto 'IAM-advanced')
            system_prompt: Prompt del sistema (opcional)
            full_response: Si True retorna respuesta completa, si False solo el content (default: False)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Si full_response=False: Solo el contenido de la respuesta (str)
            Si full_response=True: Respuesta completa de la API (dict)
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_payload(prompt, model, system_prompt, **kwargs)
        
        try:
            # Compatibilidad: si openai_compat_endpoint=True, usar /v1/completions (plural); si no, /api/v1/prompt-model
            openai_compat = kwargs.pop("openai_compat_endpoint", False)
            stream = kwargs.pop("stream", False)
            url_base = self.base_url_openai if openai_compat else self.base_url
            url = f"{url_base}/completions" if openai_compat else f"{url_base}/prompt-model"

            if openai_compat and stream:
                # Devolver un generador SSE que produzca chunks JSON por línea 'data:'
                response = self._post(url, json=payload, stream=True)

                def _iter_sse():
                    try:
                        for raw_line in response.iter_lines(decode_unicode=True):
                            if not raw_line:
                                continue
                            line = raw_line.strip()
                            if not line.startswith("data:"):
                                continue
                            data_str = line[len("data:"):].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                yield json.loads(data_str)
                            except Exception:
                                # Ignorar líneas mal formadas
                                continue
                    finally:
                        response.close()

                return _iter_sse()

            response = self._post(url, json=payload)
            json_response = response.json()
            
            # Si full_response es False, extraer solo el content
            if not full_response:
                return self._extract_content(json_response)
            
            return json_response
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="enviar prompt")
    
    def send_messages(self, messages: list, model: str = "IAM-advanced", full_response: bool = False, **kwargs) -> Dict[str, Any]:
        """
        Envía mensajes al modelo especificado usando formato de conversación
        
        Args:
            messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "mensaje"}]
            model: Modelo a usar (por defecto 'IAM-advanced')
            full_response: Si True retorna respuesta completa, si False solo el content (default: False)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Si full_response=False: Solo el contenido de la respuesta (str)
            Si full_response=True: Respuesta completa de la API (dict)
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        payload = self._prepare_messages_payload(messages, model, **kwargs)
        
        try:
            # Compatibilidad: si openai_compat_endpoint=True, usar /v1/chat/completions; si no, /api/v1/prompt-model
            openai_compat = kwargs.pop("openai_compat_endpoint", False)
            stream = kwargs.pop("stream", False)
            url_base = self.base_url_openai if openai_compat else self.base_url
            url = f"{url_base}/chat/completions" if openai_compat else f"{url_base}/prompt-model"

            if openai_compat and stream:
                # Devolver un generador SSE que produzca chunks JSON por línea 'data:'
                response = self._post(url, json=payload, stream=True)

                def _iter_sse():
                    try:
                        for raw_line in response.iter_lines(decode_unicode=True):
                            if not raw_line:
                                continue
                            line = raw_line.strip()
                            if not line.startswith("data:"):
                                continue
                            data_str = line[len("data:"):].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                yield json.loads(data_str)
                            except Exception:
                                continue
                    finally:
                        response.close()

                return _iter_sse()

            response = self._post(url, json=payload)
            json_response = response.json()
            
            # Si full_response es False, extraer solo el content
            if not full_response:
                return self._extract_content(json_response)
            
            return json_response
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="enviar mensajes")

    def send_responses(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envía payload al endpoint de Responses estilo OpenAI (/v1/responses).

        Si payload contiene stream=True, devuelve un generador que itera chunks SSE
        con líneas que empiezan con 'data:' y final '[DONE]'.
        """
        try:
            url = f"{self.base_url_openai}/responses"
            stream_flag = bool(payload.get("stream"))
            if stream_flag:
                response = self._post(url, json=payload, stream=True)

                def _iter_sse():
                    try:
                        for raw_line in response.iter_lines(decode_unicode=True):
                            if not raw_line:
                                continue
                            line = raw_line.strip()
                            if not line.startswith("data:"):
                                continue
                            data_str = line[len("data:"):].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                yield json.loads(data_str)
                            except Exception:
                                continue
                    finally:
                        response.close()

                return _iter_sse()

            response = self._post(url, json=payload)
            return response.json()
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="/responses")
    
    def _prepare_payload(self, prompt: str, model: str, system_prompt: str = None, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de prompt"""
        # Estructura exacta que espera la API para prompts
        payload = {
            'apikey': self.api_key,
            'model': model,
            'prompt': prompt
        }
        
        # Agregar parámetros adicionales si se proporcionan
        if system_prompt:
            payload['system_prompt'] = system_prompt
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'prompt', 'system_prompt']:
                payload[key] = value
        
        return payload
    
    def _prepare_messages_payload(self, messages: list, model: str, **kwargs) -> Dict[str, Any]:
        """Prepara el payload para la API de iam-hub con formato de mensajes"""
        # Estructura que espera la API con messages
        payload = {
            'apikey': self.api_key,
            'model': model,
            'messages': messages
        }
        
        # Agregar otros parámetros si se proporcionan
        for key, value in kwargs.items():
            if key not in ['apikey', 'model', 'messages']:
                payload[key] = value
        
        return payload
    
    def _extract_content(self, json_response: Dict[str, Any]) -> str:
        """
        Extrae solo el contenido de la respuesta de la API
        
        Args:
            json_response: Respuesta completa de la API
            
        Returns:
            Solo el contenido/texto de la respuesta
        """
        try:
            # Formato de iamex API: data.response.choices[0].message.content
            if 'data' in json_response and 'response' in json_response['data']:
                response_data = json_response['data']['response']
                if 'choices' in response_data and len(response_data['choices']) > 0:
                    choice = response_data['choices'][0]
                    if 'message' in choice and 'content' in choice['message']:
                        return choice['message']['content']
            
            # Formato estándar de respuesta: choices[0].message.content
            if 'choices' in json_response and len(json_response['choices']) > 0:
                choice = json_response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    return choice['message']['content']
            
            # Formato alternativo: directamente en 'content'
            if 'content' in json_response:
                return json_response['content']
            
            # Si no encuentra el formato esperado, devolver la respuesta completa
            return str(json_response)
        except (KeyError, IndexError, TypeError):
            # En caso de error, devolver la respuesta completa como string
            return str(json_response)
    
    def get_models(self) -> Dict[str, Any]:
        """Obtiene la lista de modelos disponibles"""
        try:
            response = self.session.get(
                f"{self.base_url}/models",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="obtener modelos")
    
    def send_image_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera imágenes usando modelos de IA
        
        Args:
            payload: Diccionario con parámetros de generación (prompt, model, size, n, etc.)
            
        Returns:
            Respuesta de la API con URLs de imágenes generadas
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        try:
            url = f"{self.base_url}/images/generate"
            response = self._post(url, json=payload)
            return response.json()
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="generar imagen")
    
    def send_vision_analysis(self, payload: Dict[str, Any], image_file: Any) -> Dict[str, Any]:
        """
        Analiza una imagen usando modelos de visión IA
        
        Args:
            payload: Diccionario con parámetros (prompt, model, max_tokens, temperature, etc.)
            image_file: File-like object con la imagen a analizar
            
        Returns:
            Respuesta de la API con el análisis de la imagen
            
        Raises:
            requests.RequestException: Si hay un error en la petición HTTP
        """
        try:
            url = f"{self.base_url}/vision/analyze"
            
            # Preparar multipart/form-data correctamente
            # La clave es NO convertir los valores numéricos a strings
            # y dejar que requests maneje la serialización
            data = {}
            for key, value in payload.items():
                if value is not None:
                    data[key] = value  # NO convertir a string
            
            files = {
                "image": ("image.jpg", image_file, "image/jpeg")
            }
            
            # Para multipart, necesitamos hacer la petición sin el header Content-Type: application/json
            # requests lo configurará automáticamente con el boundary correcto
            # IMPORTANTE: Usar una sesión nueva o copiar headers sin Content-Type
            headers = {
                'accept': 'application/json',
                # NO incluir 'Content-Type' - requests lo configurará automáticamente para multipart
            }
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Usar retry logic similar a _post pero con multipart
            attempt = 0
            while True:
                try:
                    # Resetear la posición del archivo antes de cada intento
                    # (importante para los reintentos)
                    if hasattr(image_file, 'seek'):
                        image_file.seek(0)
                    
                    # Usar requests.post() directamente en lugar de self.session.post()
                    # porque la sesión tiene 'Content-Type': 'application/json' por defecto
                    # y eso interfiere con multipart/form-data
                    resp = requests.post(
                        url, 
                        data=data,
                        files=files,
                        headers=headers,
                        timeout=self.timeout,
                        proxies=self.session.proxies  # Mantener configuración de proxies
                    )
                    if resp.status_code >= 400:
                        self._raise_for_status(resp)
                    return resp.json()
                except requests.RequestException as exc:
                    if attempt >= self.max_retries:
                        raise
                    status = getattr(exc.response, 'status_code', None) if hasattr(exc, 'response') and exc.response is not None else None
                    should_retry = status in (429, 500, 502, 503, 504) or status is None
                    if not should_retry:
                        raise
                    delay = self._compute_backoff(attempt)
                    time.sleep(delay)
                    attempt += 1
        except requests.RequestException as e:
            self._raise_from_requests_exception(e, context="analizar imagen")

    # ======== Helpers de red con retries/backoff y mapeo de errores ========
    def _post(self, url: str, *, json: Dict[str, Any], stream: bool = False) -> requests.Response:
        attempt = 0
        while True:
            try:
                resp = self.session.post(url, json=json, timeout=self.timeout, stream=stream)
                if resp.status_code >= 400:
                    self._raise_for_status(resp)
                return resp
            except requests.RequestException as exc:
                if attempt >= self.max_retries:
                    raise
                # Retry solo para 429, 5xx o errores de conexión
                status = getattr(exc.response, 'status_code', None) if hasattr(exc, 'response') and exc.response is not None else None
                should_retry = status in (429, 500, 502, 503, 504) or status is None
                if not should_retry:
                    raise
                delay = self._compute_backoff(attempt)
                time.sleep(delay)
                attempt += 1

    def _compute_backoff(self, attempt: int) -> float:
        base = self.backoff_factor * (2 ** attempt)
        # jitter pequeño
        return base + (0.05 * base)

    def _raise_for_status(self, response: requests.Response) -> None:
        status = response.status_code
        try:
            payload = response.json()
            message = payload.get('detail') or payload.get('error', {}).get('message') or response.text
        except ValueError:
            message = response.text

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

    def _raise_from_requests_exception(self, e: requests.RequestException, *, context: str) -> None:
        if hasattr(e, 'response') and e.response is not None:
            self._raise_for_status(e.response)
        # Sin respuesta: error de conexión/DNS/timeout
        raise APIConnectionError(f"Error de conexión al {context}: {str(e)}")
