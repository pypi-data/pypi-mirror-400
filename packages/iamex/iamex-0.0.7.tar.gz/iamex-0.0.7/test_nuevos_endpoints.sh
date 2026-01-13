#!/bin/bash

# Script para probar individualmente los nuevos endpoints
# Permite seleccionar qué prueba ejecutar

echo "=========================================="
echo "PRUEBA DE NUEVOS ENDPOINTS - IAMEX SDK"
echo "=========================================="
echo ""

# Configuración de URL base
# Descomentar la opción que necesites:

# Opción 1: API en producción
# export IAMEX_BASE_URL="https://api.iamex.io/v1"

# Opción 2: HAProxy
# export IAMEX_BASE_URL="https://api-sdk.iamexprogramers.site/v1"

# Opción 3: Localhost (desarrollo)
export IAMEX_BASE_URL="http://localhost:30666/v1"

echo "📍 Base URL: $IAMEX_BASE_URL"
echo ""

# Verificar qué script ejecutar
if [ "$1" == "imagen" ] || [ "$1" == "image" ]; then
    echo "🎨 Ejecutando prueba de GENERACIÓN DE IMÁGENES..."
    python3 test_image_generation.py
    
elif [ "$1" == "vision" ]; then
    echo "👁️  Ejecutando prueba de ANÁLISIS DE VISIÓN..."
    python3 test_vision_analysis.py
    
elif [ "$1" == "ejemplos" ]; then
    echo "📚 Ejecutando EJEMPLOS completos..."
    python3 ejemplo_nuevas_funcionalidades.py
    
elif [ "$1" == "todos" ] || [ "$1" == "all" ]; then
    echo "🚀 Ejecutando TODAS las pruebas..."
    python3 test_endpoints.py
    
else
    echo "Uso: $0 [opcion]"
    echo ""
    echo "Opciones disponibles:"
    echo "  imagen     - Prueba de generación de imágenes"
    echo "  vision     - Prueba de análisis de visión"
    echo "  ejemplos   - Ejecuta todos los ejemplos"
    echo "  todos      - Ejecuta todas las pruebas"
    echo ""
    echo "Ejemplo:"
    echo "  $0 imagen"
    echo "  $0 vision"
    echo "  $0 todos"
    echo ""
    echo "Ejecutando prueba completa por defecto..."
    python3 test_endpoints.py
fi

echo ""
echo "=========================================="
echo "✅ Prueba completada"
echo "=========================================="

