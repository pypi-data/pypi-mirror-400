# -*- coding: utf-8 -*-
"""
Paquete tratatez - Librería para operaciones en archivos de texto.

Este paquete proporciona funciones para manipular archivos de texto .txt de diversas formas:
- Operaciones básicas (crear, eliminar, copiar, mover archivos)
- Lectura y escritura de contenido
- Manipulación de líneas específicas
- Enumeración y formato de líneas
- Modificación de caracteres
- Extracción de texto entre delimitadores
- Cifrado/descifrado
- Conversión a CSV

Módulos:
    - tratadocu_1: Operaciones tipos 0-13 (operaciones básicas y manejo de líneas)
    - tratadocu_2: Operaciones tipos 14-23 (modificación de caracteres y extracción)
    - tratadocu_3: Operaciones tipos 24, 27-29 (cifrado y conversión)
"""

__version__ = '1.0.0'
__author__ = 'El Señor es el único eterno. Que la ciencia lo honre a Él.'

# Importar funciones principales de cada módulo
# Nota: Los nombres de archivo con guiones necesitan importación especial
import importlib

# Importar los módulos dinámicamente debido a los guiones en los nombres
tratadocu_1 = importlib.import_module('.tratadocu_1', package='tratatez')
tratadocu_2 = importlib.import_module('.tratadocu_2', package='tratatez')
tratadocu_3 = importlib.import_module('.tratadocu_3', package='tratatez')

# Exponer las funciones principales
from .metodos_de_apoyo.c_apoyo import Funciones_de_apoyo

__all__ = [
    'tratatez',
    'Funciones_de_apoyo',
    'tratadocu_1',
    'tratadocu_2',
    'tratadocu_3'
]

def tratatez(dire, tipe, conte="", line=None, punt=None):
    """
    Función unificada para acceder a todas las operaciones de tratatez.
    
    Redirige a la función apropiada según el tipo de operación.
    
    Args:
        dire (str): Ruta al archivo .txt a procesar.
        tipe (int | str): Código numérico (0-29) que indica la operación.
        conte (any): Contenido a usar en la operación.
        line (int | str, optional): Índice de línea o valor especial.
        punt (any, optional): Parámetro adicional según la operación.
    
    Returns:
        any: Depende del tipo de operación.
    """
    try:
        tipo_int = int(tipe)
    except (ValueError, TypeError):
        print("Error: El tipo de operación debe ser un número válido.")
        return None
    
    # Redirigir según el rango del tipo
    if 0 <= tipo_int <= 13:
        return tratadocu_1.tratatez(dire, tipe, conte, line, punt)
    elif 14 <= tipo_int <= 23:
        return tratadocu_2.tratatez(dire, tipe, conte, line, punt)
    elif tipo_int in [24, 27, 28, 29]:
        return tratadocu_3.tratatez(dire, tipe, conte, line, punt)
    else:
        print(f"Error: Tipo de operación {tipo_int} no reconocido.")
        return None
