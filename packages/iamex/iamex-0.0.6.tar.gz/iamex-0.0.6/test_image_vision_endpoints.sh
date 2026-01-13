#!/bin/bash

# Script para probar los endpoints de imagen y visión
# Configuración de la URL base para IAMEX

echo "=========================================="
echo "PRUEBA DE ENDPOINTS: IMAGE & VISION"
echo "=========================================="
echo ""

# Opción 1: API en producción (puede estar caída)
# export IAMEX_BASE_URL="https://api.iamex.io/v1"

# Opción 2: HAProxy (con problema de routing):
# export IAMEX_BASE_URL="https://api-sdk.iamexprogramers.site/v1"

# Opción 3: Directo al apihub (saltando HAProxy):
export IAMEX_BASE_URL="http://localhost:30452/v1"

echo "✅ IAMEX_BASE_URL configurado: $IAMEX_BASE_URL"
echo ""

# Ejecutar scripts de prueba
echo "=========================================="
echo "Ejecutando pruebas de endpoints..."
echo "=========================================="
echo ""

# Prueba completa de ambos endpoints
python3 test_endpoints.py

echo ""
echo "=========================================="
echo "✅ Pruebas completadas"
echo "=========================================="

