#!/bin/bash

# Configuración de la URL base para IAMEX
# HAProxy (con problema de routing):
# export IAMEX_BASE_URL="https://api-sdk.iamexprogramers.site/v1"

# Directo al apihub (saltando HAProxy):
export IAMEX_BASE_URL="http://localhost:30452/v1"

# Ejecutar scripts de prueba
# python prueba_sdk.py
python prueba_sdk_vision.py

