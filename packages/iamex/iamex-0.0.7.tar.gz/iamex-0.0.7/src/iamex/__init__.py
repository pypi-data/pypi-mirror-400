"""
iamex - Acceso unificado a múltiples modelos de inferencia AI
"""

from .compat import IAMEX, AsyncIAMEX
from .client import PromptClient

__version__ = "0.0.7"
__author__ = "Inteligencia Artificial México"
__email__ = "hostmaster@iamex.io"

def send_prompt(prompt: str, api_key: str, model: str, full_response: bool = False, max_tokens: int = None, **kwargs):
    """
    Función simple para enviar un prompt usando la API de iamex
    
    Args:
        prompt: El prompt del usuario a enviar
        api_key: Clave de API para autenticación
        model: Modelo a usar (ej: "IAM-advanced", "IAM-advance-Mexico")
        full_response: Si True retorna respuesta completa, si False solo el content (default: False)
        max_tokens: Número máximo de tokens en la respuesta (opcional)
        **kwargs: Parámetros adicionales (system_prompt, temperature, etc.)
        
    Returns:
        Si full_response=False: Solo el contenido de la respuesta (str)
        Si full_response=True: Respuesta completa de la API (dict)
        
    Example:
        >>> from iamex import send_prompt
        >>> # Solo contenido
        >>> response = send_prompt("Hola, ¿cómo estás?", "tu_api_key_aqui", "IAM-advanced")
        >>> print(response)  # "Hola! Estoy bien, gracias por preguntar..."
        >>> 
        >>> # Respuesta completa
        >>> response = send_prompt("Hola", "tu_api_key_aqui", "IAM-advanced", full_response=True)
        >>> print(response)  # {"choices": [{"message": {"content": "..."}}], ...}
    """
    client = PromptClient(api_key=api_key)
    
    # Preparar kwargs con max_tokens si se proporciona
    if max_tokens is not None:
        kwargs['max_tokens'] = max_tokens
    
    return client.send_prompt(prompt, model=model, full_response=full_response, **kwargs)


def send_messages(messages: list, api_key: str, model: str, full_response: bool = False, max_tokens: int = None, **kwargs):
    """
    Función para enviar mensajes usando la API de iamex con formato de conversación
    
    Args:
        messages: Lista de mensajes con formato [{"role": "system/user/assistant", "content": "mensaje"}]
        api_key: Clave de API para autenticación
        model: Modelo a usar (ej: "IAM-advanced", "IAM-advance-Mexico")
        full_response: Si True retorna respuesta completa, si False solo el content (default: False)
        max_tokens: Número máximo de tokens en la respuesta (opcional)
        **kwargs: Parámetros adicionales (temperature, etc.)
        
    Returns:
        Si full_response=False: Solo el contenido de la respuesta (str)
        Si full_response=True: Respuesta completa de la API (dict)
        
    Example:
        >>> from iamex import send_messages
        >>> messages = [
        ...     {"role": "system", "content": "You are a helpful assistant."},
        ...     {"role": "user", "content": "What are some fun things to do in New York?"}
        ... ]
        >>> # Solo contenido
        >>> response = send_messages(messages, "tu_api_key_aqui", "IAM-advanced")
        >>> print(response)  # "There are many fun activities in New York..."
        >>> 
        >>> # Respuesta completa
        >>> response = send_messages(messages, "tu_api_key_aqui", "IAM-advanced", full_response=True)
        >>> print(response)  # {"choices": [{"message": {"content": "..."}}], ...}
    """
    client = PromptClient(api_key=api_key)
    
    # Preparar kwargs con max_tokens si se proporciona
    if max_tokens is not None:
        kwargs['max_tokens'] = max_tokens
    
    return client.send_messages(messages, model=model, full_response=full_response, **kwargs)

__all__ = ["IAMEX", "AsyncIAMEX", "PromptClient", "send_prompt", "send_messages"]
