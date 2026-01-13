# Changelog

Todos los cambios importantes de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.4] - 2025-01-17

### Agregado
- **Nuevo parámetro `full_response`**: Control completo sobre el tipo de respuesta
  - `full_response=False` (default): Devuelve solo el contenido/texto
  - `full_response=True`: Devuelve el JSON completo con metadatos
- **Nueva función `send_messages`**: Soporte para conversaciones con formato de mensajes
  - Formato estándar: `[{"role": "system/user/assistant", "content": "..."}]`
  - Soporte para conversaciones multi-turno
  - Compatible con aplicaciones de chat avanzadas
- **Extracción inteligente de contenido**: Maneja automáticamente la estructura de respuesta de la API iamex
- **Ejemplos prácticos**: Documentación completa con casos de uso reales

### Mejorado
- **Compatibilidad hacia atrás**: Todas las aplicaciones existentes siguen funcionando sin cambios
- **Documentación**: README completamente renovado con guías paso a paso
- **Manejo de errores**: Mensajes más claros y útiles para desarrolladores
- **Estructura del paquete**: Mejor organización del código fuente

### Técnico
- Método `_extract_content` para parseo inteligente de respuestas
- Soporte para estructura de respuesta `data.response.choices[0].message.content`
- Validación mejorada de parámetros de entrada
- Tests actualizados para nueva funcionalidad

## [0.0.3] - 2024-12-15

### Agregado
- **Parámetro `max_tokens`**: Control de longitud de respuestas
- **Endpoint real**: Conexión directa a `iam-hub.iamexprogramers.site`
- **Estructura de payload optimizada**: Compatible con API de producción

### Mejorado
- Control granular sobre la longitud de respuestas del modelo
- Ejemplos actualizados con nueva funcionalidad
- Documentación técnica mejorada

### Corregido
- Estructura de payload exacta que espera la API
- Manejo de parámetros opcionales

## [0.0.2] - 2024-11-20

### Agregado
- **Función `send_prompt`**: Interfaz simple para uso rápido
  - Sintaxis: `send_prompt(prompt, api_key, model)`
  - Ideal para scripts y aplicaciones simples
- **Autenticación completa**: Soporte para API keys
- **Conexión directa**: Endpoint real de iam-hub

### Mejorado
- Estructura de payload exacta que espera la API
- Documentación con ejemplos prácticos
- Mejor manejo de errores de autenticación

### Técnico
- Implementación de autenticación por API key
- Validación de parámetros de entrada
- Headers HTTP optimizados

## [0.0.1] - 2024-10-15

### Agregado
- **Cliente inicial**: Clase `PromptClient` para uso avanzado
- **Soporte multi-modelo**: Compatible con múltiples modelos de inferencia
- **Modelo por defecto**: `IAM-advanced` como opción recomendada
- **Parámetros optimizados**: Configuración inicial para la API

### Características Iniciales
- Envío básico de prompts
- Endpoint fijo para el modelo actual
- Estructura base del paquete Python
- Licencia MIT
- Documentación inicial

---

## Información de Versiones

- **[0.0.5]**: Versión actual con compatibilidad estilo OpenAI (Responses y Completions)
- **[0.0.4]**: Soporte completo para conversaciones y control de respuestas
- **[0.0.3]**: Versión estable con control de tokens
- **[0.0.2]**: Primera versión con función simple `send_prompt`
- **[0.0.1]**: Versión inicial con cliente básico

## Roadmap Futuro

## [0.0.5] - 2025-09-26

### Agregado
- Compatibilidad con el estilo del SDK de OpenAI v1
  - `client.responses.create(...)`
  - `client.chat.completions.create(...)`
  - `client.completions.create(...)`
  - `client.models.list()`
- Normalización de respuestas a esquemas equivalentes (choices, usage, output_text)

### Mejorado
- Documentación: guía de migración en una línea y ejemplos prácticos
- Interoperabilidad: uso en proyectos existentes que esperan OpenAI

### Nota
- No es necesario publicar ni cambiar endpoints en los ejemplos de uso

### v0.1.0 (Mayor)
- [ ] API asíncrona completa
- [ ] Soporte para fine-tuning
- [ ] Dashboard de métricas
- [ ] Integración con frameworks populares

---

**Nota**: Este proyecto sigue [Semantic Versioning](https://semver.org/). Las versiones PATCH (0.0.x) incluyen correcciones y mejoras menores, MINOR (0.x.0) agregan funcionalidad compatible, y MAJOR (x.0.0) incluyen cambios incompatibles.





