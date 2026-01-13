"""
Errores específicos estilo OpenAI para el SDK de Python.

Estos errores permiten a los usuarios capturar situaciones comunes con clases
concretas en lugar de analizar códigos HTTP manualmente.
"""

from typing import Optional


class IAMEXError(Exception):
    """Error base para el SDK de iamex."""

    def __init__(self, message: str, *, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class AuthenticationError(IAMEXError):
    """401 - API key inválida o ausente."""


class RateLimitError(IAMEXError):
    """429 - Se excedió el límite de peticiones."""


class BadRequestError(IAMEXError):
    """400 - Parámetros inválidos o solicitud mal formada."""


class PermissionDeniedError(IAMEXError):
    """403 - Permisos insuficientes."""


class NotFoundError(IAMEXError):
    """404 - Recurso no encontrado."""


class APIStatusError(IAMEXError):
    """5xx - Errores del servidor o estados no manejados explícitamente."""


class APIConnectionError(IAMEXError):
    """Errores de red, DNS o conexión interrumpida (sin respuesta HTTP)."""







