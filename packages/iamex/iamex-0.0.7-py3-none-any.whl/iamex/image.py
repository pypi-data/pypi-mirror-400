"""
Módulo para generación de imágenes usando modelos de IA
"""

from typing import Any, Dict, Optional
from .client import PromptClient


class _ImageGenerate:
    """Clase para manejar la generación de imágenes"""
    
    def __init__(self, client: PromptClient):
        self._client = client
    
    def generate(
        self,
        *,
        prompt: str,
        model: Optional[str] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Genera imágenes basadas en un prompt de texto
        
        Args:
            prompt: Descripción de la imagen a generar (requerido)
            model: Modelo de imagen a usar (opcional)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Respuesta de la API con URLs de las imágenes generadas
            
        Example:
            >>> client = IAMEX(api_key="...")
            >>> response = client.image.generate(
            ...     prompt="Un perro en la playa al atardecer"
            ... )
            >>> print(response['data'][0]['url'])
        """
        payload = {
            "prompt": prompt,
        }
        
        if model:
            payload["model"] = model
        
        # Agregar otros parámetros adicionales
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        return self._client.send_image_generation(payload)


class _Image:
    """Clase contenedora para funcionalidades de imagen"""
    
    def __init__(self, client: PromptClient):
        self.generate = _ImageGenerate(client).generate

