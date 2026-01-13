"""
Ejemplos de uso con el cliente IAMEX (compat v1)
"""

from iamex import IAMEX

def ejemplo_basico():
    """Ejemplo básico de uso"""
    print("=== Ejemplo Básico ===")
    
    # Inicializar cliente (coloca tu API key si aplica)
    client = IAMEX(api_key="tu_api_key_aqui")
    
    # Enviar prompt simple
    try:
        response = client.completions.create(
            model="IAM-advanced",
            prompt="Explica qué es la inteligencia artificial en una frase",
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_con_parametros():
    """Ejemplo con parámetros adicionales"""
    print("\n=== Ejemplo con Parámetros ===")
    
    client = IAMEX(api_key="tu_api_key_aqui")
    
    try:
        response = client.completions.create(
            model="IAM-advanced",
            prompt="¿Cuáles son las ventajas de usar Python?",
            temperature=0.7,
            max_tokens=200,
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_obtener_modelos():
    """Ejemplo para obtener modelos disponibles"""
    print("\n=== Obtener Modelos ===")
    
    client = IAMEX(api_key="tu_api_key_aqui")
    
    try:
        models = client.models.list()
        print("Modelos disponibles:", models)
    except Exception as e:
        print(f"Error: {e}")

def ejemplo_manejo_errores():
    """Ejemplo de manejo de errores"""
    print("\n=== Manejo de Errores ===")
    
    client = IAMEX(api_key="tu_api_key_aqui")
    
    try:
        response = client.completions.create(
            model="IAM-advanced",
            prompt="Este prompt fallará",
        )
        print("Respuesta:", response)
    except Exception as e:
        print(f"Error capturado correctamente: {e}")

if __name__ == "__main__":
    print("Ejemplos de uso de iamex")
    print("=" * 40)
    
    # Ejecutar ejemplos
    ejemplo_basico()
    ejemplo_con_parametros()
    ejemplo_obtener_modelos()
    ejemplo_manejo_errores()
    
    print("\n" + "=" * 40)
    print("Ejemplos completados")
