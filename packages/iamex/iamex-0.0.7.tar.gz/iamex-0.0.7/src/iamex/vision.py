"""
Módulo para análisis de imágenes usando modelos de visión IA
"""

from typing import Any, Dict, Optional, Union, BinaryIO
import os
from .client import PromptClient


class _VisionAnalisis:
    """Clase para manejar el análisis de imágenes"""
    
    def __init__(self, client: PromptClient):
        self._client = client
    
    def analisis(
        self,
        *,
        prompt: str,
        image: Union[str, BinaryIO],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Analiza una imagen usando modelos de visión IA
        
        Args:
            prompt: Pregunta o instrucción sobre la imagen (requerido)
            image: Ruta del archivo de imagen o file-like object (requerido)
            model: Modelo de visión a usar (opcional)
            max_tokens: Límite de tokens en la respuesta
            temperature: Temperatura del modelo (0.0 a 1.0)
            **kwargs: Parámetros adicionales para la API
            
        Returns:
            Respuesta de la API con el análisis de la imagen
            
        Example:
            >>> client = IAMEX(api_key="...")
            >>> response = client.vision.analisis(
            ...     prompt="Describe esta imagen",
            ...     image="/ruta/imagen.jpg",
            ...     max_tokens=200,
            ...     temperature=0.7
            ... )
            >>> print(response['choices'][0]['message']['content'])
        """
        payload = {
            "prompt": prompt,
        }
        
        if model:
            payload["model"] = model
        
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        
        if temperature is not None:
            payload["temperature"] = temperature
        
        # Agregar otros parámetros adicionales
        for key, value in kwargs.items():
            if key not in payload and key != "image":
                payload[key] = value
        
        # Manejar el archivo de imagen
        if isinstance(image, str):
            # Es una ruta de archivo, abrirlo
            if not os.path.exists(image):
                raise FileNotFoundError(f"No se encontró el archivo de imagen: {image}")
            
            with open(image, "rb") as img_file:
                return self._client.send_vision_analysis(payload, img_file)
        else:
            # Es un file-like object
            return self._client.send_vision_analysis(payload, image)


class _Vision:
    """Clase contenedora para funcionalidades de visión"""
    
    def __init__(self, client: PromptClient):
        self.analisis = _VisionAnalisis(client).analisis

