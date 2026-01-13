# -*- coding: utf-8 -*-
"""
Librería tratadocu_2 (segunda parte de tratatez) para operaciones específicas en archivos de texto.
"""

from tratatez.metodos_de_apoyo.c_apoyo import Funciones_de_apoyo

#       2° parte
########################################
#                                      #
#   14- modificar carapter             #
#   15- si en final de línea, carapt   # -> conte=caracter. Devuelve True/False
#   16- si este carapter () en linea   # -> conte=caracter. Devuelve True/False
#   17- elim ultimo o ultimos caracts  # -> conte='1' o '2'. Modifica archivo.
#   18- si carpt existe Retorna posic  # -> conte=caracter. Devuelve lista de índices [int] o None.
#   --------------------------     |#| #
#   19- ¿cuantas '    ' hay al Principio de la linea x? # -> Devuelve int.
#   20- poner, quitar tab o resto      # -> punt=0(poner)/1(quitar), conte=0(tab)/1(espacios inicio). Modifica archivo.
#   21- quitar resto de espacio        # -> Quita espacios/tabs al final (rstrip). Modifica archivo.
#   --------------------------     |#| #
#   22- extrae stream de entre margens # -> 
#   23- extrae desde, hasta (stream)   # -> conte=desde_str, punt=hasta_str. Devuelve str.
#                                      #
########################################

# objeto de la clase Funciones_de_apoyo
asistencia = Funciones_de_apoyo()

# -------------------------------------
# Funciones de Operación por Tipo
# -------------------------------------

def _info_del_tipo():
    """Tipo 0: Muestra documentación interna."""
    ayuda = """
=============================================================================
Documentación Rápida de tratadocu-2.py (Segunda parte de tratatez)

Operaciones disponibles (argumento tipe):
  14: Modifica un caracter en una posición específica de una línea.
  15: Verifica si una línea termina con un caracter o cadena.
  16: Verifica si una subcadena está presente en una línea.
  17: Elimina el último o los últimos dos caracteres de una línea.
  18: Devuelve una lista de posiciones donde se encuentra una subcadena.
  19: Cuenta tabs o espacios al principio de una línea.
  20: Pone o quita tabulaciones o espacios al inicio de una línea.
  21: Quita espacios en blanco al final de una o todas las líneas.
  22: Extrae texto entre delimitadores con búsqueda desde los extremos.
  23: Extrae un substring de una línea por índices numéricos.

Argumentos:
  dire (str): Ruta al archivo .txt a procesar.
  tipe (int | str): Código numérico (14-23) que indica la operación.
  conte (str): Contenido a usar en la operación (caracter, palabra, etc.).
               - Tipo 17: '1' o '2' para indicar cuántos caracteres eliminar.
               - Tipo 20: '0' (tab) o '1' (espacios) para indicar qué procesar.
               - Tipo 22: Número de ocurrencias del delimitador a saltar (int, base 0).
               - Tipo 23: Índice de inicio (int) para extracción.
  line (int | str): Índice de la línea a modificar (base 0).
  punt (int | str): Parámetro adicional (posición, opción, etc.).
               - Tipo 14: Posición (base 1) del caracter a modificar.
               - Tipo 19: 0 (contar tabs) o 1 (contar espacios) al inicio.
               - Tipo 20: 0 (poner) o 1 (quitar).
               - Tipo 21: 0 (línea específica) o 1 (todas las líneas).
               - Tipo 22: Tipo de delimitador (int 0-8) para extracción.
                           0:(), 1:[], 2:{}, 3:<>, 4://, 5:¿?, 6:¡!, 7:'', 8:**
               - Tipo 23: Índice de fin (int) para extracción.
=============================================================================
    """
    print(ayuda)
    return None # Termina tras mostrar ayuda

def _modificar_caracter(lineas, num_linea, contenido_str, puntero_arg, ruta_archivo):
    """Tipo 14: Modifica un caracter en una posición específica de una línea."""
    if not isinstance(puntero_arg, int) or puntero_arg <= 0:
        print("Error tipo 14: El puntero debe ser un entero positivo (base 1).")
        return False
    if len(contenido_str) != 1:
        print("Error tipo 14: El contenido debe ser un solo caracter.")
        return False

    linea_actual = lineas[num_linea]
    longitud_linea = len(linea_actual)
    posicion_base_cero = puntero_arg - 1 # Convertir a base 0

    if not (0 <= posicion_base_cero < longitud_linea):
        print(f"Error tipo 14: El puntero {puntero_arg} está fuera del rango de la línea (1-{longitud_linea}).")
        return False

    linea_modificada = linea_actual[:posicion_base_cero] + contenido_str + linea_actual[posicion_base_cero+1:]
    lineas[num_linea] = linea_modificada

    if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
        print(f"Caracter en la posición {puntero_arg} de la línea {num_linea} modificado.")
        return True
    else:
        print(f"Error al guardar los cambios para el tipo 14.")
        return False

def _verificar_final_linea(lineas, num_linea, contenido_str):
    """Tipo 15: Verifica si una línea termina con un caracter o cadena."""
    if not contenido_str:
        print("Error tipo 15: Se requiere un caracter o texto en 'conte'.")
        return None
    return lineas[num_linea].endswith(contenido_str)

def _verificar_subcadena_en_linea(lineas, num_linea, contenido_str):
    """Tipo 16: Verifica si una subcadena está presente en una línea."""
    if not contenido_str:
        print("Error tipo 16: Se requiere un caracter o texto en 'conte'.")
        return None
    return contenido_str in lineas[num_linea]

def _eliminar_caracteres_final(lineas, num_linea, contenido_str, ruta_archivo):
    """Tipo 17: Elimina el último o los últimos dos caracteres de una línea."""
    if contenido_str not in ['1', '2']:
        print("Error tipo 17: 'conte' debe ser '1' o '2'.")
        return False
    cantidad_a_eliminar = int(contenido_str)

    linea_actual = lineas[num_linea]
    if len(linea_actual) < cantidad_a_eliminar:
        print(f"Error tipo 17: La línea no tiene suficientes caracteres para eliminar {cantidad_a_eliminar}.")
        return False

    lineas[num_linea] = linea_actual[:-cantidad_a_eliminar]

    if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
        print(f"{cantidad_a_eliminar} caracter(es) eliminado(s) del final de la línea {num_linea}.")
        return True
    else:
        print(f"Error al guardar los cambios para el tipo 17.")
        return False

def _buscar_posiciones_subcadena(lineas, num_linea, contenido_str):
    """Tipo 18: Devuelve una lista de posiciones donde se encuentra una subcadena."""
    if not contenido_str:
        print("Error tipo 18: Se requiere un caracter o texto en 'conte'.")
        return None
    linea_actual = lineas[num_linea]
    posiciones = [i for i in range(len(linea_actual)) if linea_actual.startswith(contenido_str, i)]
    return posiciones if posiciones else None

def _contar_espacios_inicio(lineas, num_linea, puntero_arg):
    """Tipo 19: Cuenta tabs o espacios al principio de una línea."""
    if not isinstance(puntero_arg, int) or puntero_arg not in [0, 1]:
        print("Error tipo 19: 'punt' debe ser 0 (tabulaciones) o 1 (espacios).")
        return -1

    linea_actual = lineas[num_linea]
    char_a_contar = '\t' if puntero_arg == 0 else ' '
    
    count = 0
    for char in linea_actual:
        if char == char_a_contar:
            count += 1
        else:
            break
    return count

def _modificar_espacios_inicio(lineas, num_linea, contenido_str, puntero_arg, ruta_archivo):
    """Tipo 20: Pone o quita tabulaciones o espacios al inicio de una línea."""
    if contenido_str not in ["0", "1"]:
        print("Error tipo 20: 'conte' debe ser '0' (tab) o '1' (espacios).")
        return False
    if not isinstance(puntero_arg, int) or puntero_arg not in [0, 1]:
        print("Error tipo 20: 'punt' debe ser 0 (poner) o 1 (quitar).")
        return False

    opcion_char = int(contenido_str)
    opcion_accion = puntero_arg
    char_a_procesar = '\t' if opcion_char == 0 else ' '
    desc_char = 'Tabulador' if opcion_char == 0 else 'Espacio(s)'
    linea_actual = lineas[num_linea]

    if opcion_accion == 0:  # Poner
        lineas[num_linea] = char_a_procesar + linea_actual
        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
            print(f"{desc_char} añadido al inicio de la línea {num_linea}.")
            return True
        else:
            print(f"Error al guardar los cambios para el tipo 20.")
            return False
    else:  # Quitar
        if linea_actual.startswith(char_a_procesar):
            lineas[num_linea] = linea_actual.lstrip(char_a_procesar)
            if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
                print(f"{desc_char} quitado(s) del inicio de la línea {num_linea}.")
                return True
            else:
                print(f"Error al guardar los cambios para el tipo 20.")
                return False
        else:
            print(f"Tipo 20: La línea {num_linea} no comienza con {desc_char.lower()}.")
            return True

def _quitar_espacios_final(lineas, num_linea, puntero_arg, ruta_archivo):
    """Tipo 21: Quita espacios en blanco al final de una o todas las líneas."""
    if not isinstance(puntero_arg, int) or puntero_arg not in [0, 1]:
        print("Error tipo 21: 'punt' debe ser 0 (línea específica) o 1 (todas las líneas).")
        return False

    if puntero_arg == 0:  # Línea específica
        linea_actual = lineas[num_linea]
        linea_modificada = linea_actual.rstrip()

        if linea_actual == linea_modificada:
            print(f"Tipo 21: No había espacios al final de la línea {num_linea}.")
            return True

        lineas[num_linea] = linea_modificada
        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
            print(f"Espacios eliminados del final de la línea {num_linea}.")
            return True
        else:
            print(f"Error al guardar los cambios para el tipo 21.")
            return False

    else:  # Todas las líneas
        lineas_modificadas = [linea.rstrip() for linea in lineas]
        
        if lineas == lineas_modificadas:
            print(f"Tipo 21: No se encontraron espacios al final de ninguna línea.")
            return True

        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas_modificadas):
            print(f"Espacios eliminados del final de todas las líneas.")
            return True
        else:
            print(f"Error al guardar los cambios para el tipo 21.")
            return False

def _extraer_entre_delimitadores(lineas, num_linea, contenido_str, puntero_arg):
    """Tipo 22: Extrae texto entre delimitadores con búsqueda desde los extremos."""
    delimitadores = [
        ('(', ')'), ('[', ']'), ('{', '}'), ('<', '>'),
        ('//', '//'), ('¿', '?'), ('¡', '!'), ("'", "'"),
        ('**', '**')
    ]

    try:
        tipo_delimitador = int(puntero_arg)
        skip_count = int(contenido_str)
    except ValueError:
        print("Error tipo 22: 'punt' y 'conte' deben ser números enteros.")
        return None

    if not (0 <= tipo_delimitador < len(delimitadores)):
        print(f"Error tipo 22: 'punt' debe estar entre 0 y {len(delimitadores)-1}.")
        return None
    if skip_count < 0:
        print("Error tipo 22: 'conte' (número de saltos) no puede ser negativo.")
        return None

    del_abrir, del_cerrar = delimitadores[tipo_delimitador]
    linea_actual = lineas[num_linea]

    # Buscar delimitador de apertura desde el inicio
    start_index = -1
    search_from = 0
    for _ in range(skip_count + 1):
        idx = linea_actual.find(del_abrir, search_from)
        if idx == -1:
            return None
        start_index = idx
        search_from = start_index + len(del_abrir)

    # Buscar delimitador de cierre desde el final
    end_index = -1
    search_to = len(linea_actual)
    for _ in range(skip_count + 1):
        idx = linea_actual.rfind(del_cerrar, 0, search_to)
        if idx == -1:
            return None
        end_index = idx
        search_to = end_index

    if end_index <= start_index + len(del_abrir) - 1:
        return None

    return linea_actual[start_index + len(del_abrir):end_index]

def _extraer_substring_por_indices(lineas, num_linea, contenido_str, puntero_arg):
    """Tipo 23: Extrae un substring de una línea por índices numéricos."""
    try:
        inicio_idx = int(contenido_str)
        fin_idx = int(puntero_arg)
    except ValueError:
        print("Error tipo 23: 'conte' (inicio) y 'punt' (fin) deben ser números enteros.")
        return None

    if inicio_idx < 0 or fin_idx < 0:
        print("Error tipo 23: Los índices no pueden ser negativos.")
        return None

    return lineas[num_linea][inicio_idx:fin_idx]

# -------------------------------------
# Función Principal - Segunda Parte
# -------------------------------------

def tratatez(dire, tipe, conte, line, punt):
    """
    Realiza operaciones específicas (tipos 14-23) sobre un archivo de texto.

    Args:
        dire (str): Ruta al archivo .txt a procesar.
        tipe (int | str): Código numérico (14-23) que indica la operación.
        conte (str): Contenido a usar en la operación.
        line (int | str): Índice de la línea a modificar (base 0).
        punt (int | str): Parámetro adicional.

    Returns:
        any: Depende de la operación.
    """
    # Validación Inicial
    valido, args = asistencia._validar_argumentos(dire, tipe, conte, line, punt)
    if not valido:
        print(args)
        return None
    ruta_archivo, tipo, contenido_str, num_linea, linea_especial, puntero_arg = args

    # Leer el archivo
    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        return None
    
    # Validar número de línea (solo para tipos que lo requieren)
    if num_linea is not None and not (0 <= num_linea < len(lineas)):
        print(f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}).")
        return None

    # Despachador de Operaciones
    if tipo == 0:
        _info_del_tipo()
        return None
    elif tipo == 14:
        return _modificar_caracter(lineas, num_linea, contenido_str, puntero_arg, ruta_archivo)
    elif tipo == 15:
        return _verificar_final_linea(lineas, num_linea, contenido_str)
    elif tipo == 16:
        return _verificar_subcadena_en_linea(lineas, num_linea, contenido_str)
    elif tipo == 17:
        return _eliminar_caracteres_final(lineas, num_linea, contenido_str, ruta_archivo)
    elif tipo == 18:
        return _buscar_posiciones_subcadena(lineas, num_linea, contenido_str)
    elif tipo == 19:
        return _contar_espacios_inicio(lineas, num_linea, puntero_arg)
    elif tipo == 20:
        return _modificar_espacios_inicio(lineas, num_linea, contenido_str, puntero_arg, ruta_archivo)
    elif tipo == 21:
        return _quitar_espacios_final(lineas, num_linea, puntero_arg, ruta_archivo)
    elif tipo == 22:
        return _extraer_entre_delimitadores(lineas, num_linea, contenido_str, puntero_arg)
    elif tipo == 23:
        return _extraer_substring_por_indices(lineas, num_linea, contenido_str, puntero_arg)
    else:
        print(f"Error: Tipo de operación '{tipo}' no reconocido o inválido.")
        return None

# -------------------------------------
# Ejemplo de uso
# -------------------------------------

if __name__ == "__main__":
    print("Módulo tratadocu-2 cargado. Llama a la función tratatez() para usarlo.")
    pass
