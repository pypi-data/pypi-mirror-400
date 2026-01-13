# Publicar iamex v0.0.7 en PyPI

Este documento contiene las instrucciones actualizadas para publicar el paquete `iamex` v0.0.7 en PyPI.

## ✨ Novedades de v0.0.7

- **Documentación corregida**: README completo con todas las funciones publicado en PyPI

## ✨ Novedades de v0.0.6

- **Nueva función `image.generate()`**: Generación de imágenes basadas en texto usando modelos de IA
- **Nueva función `vision.analisis()`**: Análisis de imágenes usando modelos de visión IA
- **Nuevos endpoints**: `/v1/images/generate` y `/v1/vision/analyze`
- **Soporte multipart/form-data**: Para envío de imágenes en análisis de visión
- **Compatibilidad hacia atrás**: Todas las aplicaciones existentes siguen funcionando

## Prerrequisitos

1. **Cuenta en PyPI**: Crear una cuenta en [PyPI](https://pypi.org/account/register/)
2. **Cuenta en TestPyPI**: Crear una cuenta en [TestPyPI](https://test.pypi.org/account/register/)
3. **Herramientas de empaquetado**: Instalar las herramientas necesarias

```bash
pip install --upgrade setuptools wheel twine
```

## Preparación del Paquete

### 1. Verificar la Estructura

Asegúrate de que tu proyecto tenga la siguiente estructura:

```
iamex/
├── src/
│   └── iamex/
│       ├── __init__.py
│       ├── client.py
│       ├── compat.py
│       ├── async_client.py
│       ├── image.py        # NUEVO: Generación de imágenes
│       ├── vision.py       # NUEVO: Análisis de imágenes
│       └── errors.py
├── tests/
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── requirements.txt
└── .gitignore
```

### 2. Verificar Archivos de Configuración

- **`setup.py`**: Debe tener el nombre correcto `"iamex"`
- **`pyproject.toml`**: Debe tener la configuración correcta
- **`README.md`**: Debe estar en formato Markdown
- **`LICENSE`**: Debe ser un archivo de texto válido

## Construir el Paquete

### 1. Limpiar Construcciones Anteriores

```bash
# Eliminar directorios de construcción anteriores
rm -rf build/ dist/ *.egg-info/
```

### 2. Construir Distribuciones

```bash
# Construir el paquete
python setup.py sdist bdist_wheel
```

O usando herramientas modernas:

```bash
# Construir usando build
python -m build
```

## Probar en TestPyPI

### 1. Subir a TestPyPI

```bash
# Subir a TestPyPI para pruebas
twine upload --repository testpypi dist/*
```

### 2. Probar la Instalación

```bash
# Instalar desde TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ iamex
```

### 3. Verificar Funcionamiento

```python
from iamex import IAMEX
print("¡Instalación exitosa!")
```

## Publicar en PyPI

### 1. Subir a PyPI

```bash
# Subir a PyPI oficial
twine upload dist/*
```

### 2. Verificar la Publicación

- Visita [PyPI](https://pypi.org/project/iamex/)
- Verifica que la información del paquete sea correcta
- Prueba la instalación: `pip install iamex`

## Configuración de Variables de Entorno

Para mayor seguridad, configura las credenciales como variables de entorno:

```bash
# Configurar credenciales de PyPI
export TWINE_USERNAME="tu_usuario_pypi"
export TWINE_PASSWORD="tu_password_pypi"

# O usar archivo .pypirc
```

## Archivo .pypirc (Opcional)

Crear `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = tu_usuario_pypi
password = tu_password_pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = tu_usuario_testpypi
password = tu_password_testpypi
```

## Verificación Post-Publicación

### Verificación Básica
1. **Instalación**: `pip install iamex`
2. **Versión**: `python -c "import iamex; print(iamex.__version__)"`  # Debe mostrar 0.0.7
3. **Importaciones**: `python -c "from iamex import IAMEX; print('OK')"`

### Verificación de Nuevas Funcionalidades v0.0.6

```python
from iamex import IAMEX

client = IAMEX(api_key="tu_api_key")

# Probar generación de imágenes
try:
    response = client.image.generate(
        prompt="Un gato astronauta en el espacio"
    )
    print(f"Imagen generada: {response['data'][0]['url']}")
except Exception as e:
    print(f"Error esperado sin API key válida: {e}")

# Probar análisis de imágenes (vision)
try:
    response = client.vision.analisis(
        prompt="Describe esta imagen en detalle",
        image="/ruta/a/tu/imagen.jpg",
        max_tokens=200,
        temperature=0.7
    )
    print(f"Análisis: {response['choices'][0]['message']['content']}")
except FileNotFoundError:
    print("Error esperado: archivo de imagen no encontrado")
except Exception as e:
    print(f"Error esperado sin API key válida: {e}")
```

## Actualizaciones Futuras

Para actualizar el paquete:

1. Incrementar la versión en `setup.py` y `pyproject.toml`
2. Actualizar `CHANGELOG.md` o `README.md`
3. Reconstruir: `python -m build`
4. Subir: `twine upload dist/*`

## Solución de Problemas

### Error de Autenticación

```bash
# Verificar credenciales
twine check dist/*
```

### Error de Validación

```bash
# Verificar el paquete antes de subir
twine check dist/*
```

### Error de Duplicado

- Verificar que la versión sea única
- Eliminar archivos de distribución anteriores

## Recursos Adicionales

- [Guía de PyPI](https://packaging.python.org/tutorials/packaging-projects/)
- [Documentación de setuptools](https://setuptools.readthedocs.io/)
- [Documentación de twine](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)

## Notas Importantes

- **Nunca subas credenciales** en el código fuente
- **Siempre prueba** en TestPyPI antes de PyPI oficial
- **Verifica** que el paquete funcione después de la instalación
- **Mantén** las versiones sincronizadas en todos los archivos de configuración
