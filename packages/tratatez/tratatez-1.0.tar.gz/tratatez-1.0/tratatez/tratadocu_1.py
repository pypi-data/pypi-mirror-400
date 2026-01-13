# -*- coding: utf-8 -*-
"""
Librería tratatez_1 (primera parte de tratatez) para operaciones específicas en archivos de texto.
"""

import os
import shutil
from tratatez.metodos_de_apoyo.c_apoyo import Funciones_de_apoyo

#       1° parte
#####################################
#                                   #
#   0- Muestra documentación interna# -> Imprime ayuda.
#   1- Crea un archivo vacío        # -> Crea/sobrescribe archivo.
#   2- Elimina el archivo           # -> Elimina archivo.
#   3- Copia el archivo             # -> conte=nuevo_nombre, punt=ruta_destino. Copia archivo.
#   4- Mueve el archivo             # -> conte=nuevo_nombre, punt=ruta_destino. Mueve archivo.
#   5- Reemplaza todo el contenido  # -> conte=contenido. Modifica archivo.
#   6- Añade 'contenido' al final   # -> conte=contenido, punt=0(final_linea)/1(nueva_linea_final)/2(inicio_archivo)/3(debajo_linea). Modifica archivo.
#   7- Extrae y devuelve contenido  # -> Devuelve str.
#   8- Devuelve lista con líneas    # -> Devuelve list[str].
#   9- Devuelve línea específica    # -> line=numero_linea. Devuelve str.
#   10- Reemplaza línea específica  # -> conte=contenido, line=numero_linea. Modifica archivo.
#   11- Modifica palabra en línea   # -> conte=contenido, line=numero_linea, punt=indice_palabra. Modifica archivo.
#   12- Añade texto al final línea  # -> conte=contenido, line=numero_linea, punt=añadir_espacio(bool). Modifica archivo.
#   13- Enumera o des-enumera líneas# -> conte=contenido(para opcion 2), punt=0(enumerar)/1(quitar_num)/2(quitar_num_cont)/3(quitar_esp_inicio). Modifica archivo o devuelve str si line="here" (opc 1,2).
#                                   #
#####################################

# objeto de la clase Funciones_de_apoyo
asistencia = Funciones_de_apoyo()

# -------------------------------------
# Funciones de Operación por Tipo
# -------------------------------------

def _procesar_tipo_0():
    """Tipo 0: Muestra documentación interna."""
    ayuda = """
=============================================================================
Documentación Rápida de tratatez.py

Operaciones disponibles (argumento tipo_operacion):
  0: Muestra documentación interna.
  1: Crear archivo (sobrescribe si existe).
  2: Eliminar archivo.
  3: Copiar archivo (parametro_extra=ruta_destino, contenido=nuevo_nombre).
  4: Mover archivo (parametro_extra=ruta_destino, contenido=nuevo_nombre).
  5: Reemplazar contenido total del archivo con 'contenido'.
  6: Añadir 'contenido' al archivo. El comportamiento exacto depende de 'parametro_extra' (punt):
     punt=0: Añadir al final de la última línea (con espacio si es necesario). (Archivo debe existir)
     punt=1: Añadir 'contenido' en una nueva línea al final del archivo. (Crea archivo si no existe)
     punt=2: Añadir 'contenido' al inicio del archivo, contenido original debajo. (Crea archivo si no existe)
     punt=3: Añadir 'contenido' en una nueva línea debajo de 'numero_linea'. (Archivo y línea deben existir)
  7: Leer y devolver todo el contenido del archivo.
  8: Leer y devolver todas las líneas como una lista.
  9: Devolver la línea específica 'numero_linea'.
 10: Reemplazar la línea 'numero_linea' con 'contenido'.
 11: Cambiar palabra en 'numero_linea' (índice en 'parametro_extra') por 'contenido'.
 12: Añadir 'contenido' al final de 'numero_linea' (espacio si 'parametro_extra' es True).
 13: Enumerar/des-enumerar líneas:
     parametro_extra=0: Enumerar ("idx-contenido linea").
     parametro_extra=1: Quitar enumeración ("idx-").
     parametro_extra=2: Quitar enumeración y contenido ("idx-contenido"). (Requiere 'contenido')
     parametro_extra=3: Operaciones con espacios y líneas:
       - Si numero_linea=None: Quita espacios iniciales de todas las líneas.
       - Si numero_linea=<int>: Quita espacios iniciales solo de esa línea.
       - Si numero_linea="here": Devuelve lista con números de líneas vacías.
       - Si numero_linea="out": Elimina las líneas especificadas en 'contenido' (int o list[int]).
     Si 'numero_linea' esta en "here" mientras ejecutas parametro_extra en 1 o 2, entonces,
     se devuelve el resultado (sin modificar el archivo).

-----------------------------------------------------------------------------
OPERACIONES ADICIONALES (Módulo tratadocu_2.py - Segunda parte)
-----------------------------------------------------------------------------

 14: Modifica un caracter en una posición específica de una línea.
     - conte: El nuevo caracter (solo 1 caracter).
     - line: Índice de línea (base 0).
     - punt: Posición del caracter en la línea (base 1).

 15: Verifica si una línea termina con un caracter o cadena.
     - conte: Caracter o cadena a verificar.
     - line: Índice de línea (base 0).
     - Devuelve: True o False.

 16: Verifica si una subcadena está presente en una línea.
     - conte: Subcadena a buscar.
     - line: Índice de línea (base 0).
     - Devuelve: True o False.

 17: Elimina el último o los últimos dos caracteres de una línea.
     - conte: '1' (eliminar 1 caracter) o '2' (eliminar 2 caracteres).
     - line: Índice de línea (base 0).

 18: Devuelve una lista de posiciones donde se encuentra una subcadena.
     - conte: Subcadena a buscar.
     - line: Índice de línea (base 0).
     - Devuelve: Lista de índices [int] o None si no se encuentra.

 19: Cuenta tabs o espacios al principio de una línea.
     - line: Índice de línea (base 0).
     - punt: 0 (contar tabs) o 1 (contar espacios).
     - Devuelve: Cantidad de tabs o espacios (int).

 20: Pone o quita tabulaciones o espacios al inicio de una línea.
     - conte: '0' (trabajar con tabs) o '1' (trabajar con espacios).
     - line: Índice de línea (base 0).
     - punt: 0 (poner) o 1 (quitar).

 21: Quita espacios en blanco al final de una o todas las líneas.
     - line: Índice de línea (base 0) - solo si punt=0.
     - punt: 0 (línea específica) o 1 (todas las líneas).

 22: Extrae texto entre delimitadores con búsqueda desde los extremos.
     - conte: Número de ocurrencias del delimitador a saltar (int, base 0).
     - line: Índice de línea (base 0).
     - punt: Tipo de delimitador (int 0-8):
             0:(), 1:[], 2:{}, 3:<>, 4://, 5:¿?, 6:¡!, 7:'', 8:**
     - Devuelve: Texto extraído (str).

 23: Extrae un substring de una línea por índices numéricos.
     - conte: Índice de inicio (int).
     - line: Índice de línea (base 0).
     - punt: Índice de fin (int).
     - Devuelve: Substring extraído (str).

-----------------------------------------------------------------------------
OPERACIONES ADICIONALES (Módulo tratadocu_3.py - Tercera parte)
-----------------------------------------------------------------------------

 24: Encriptar/Desencriptar archivo (XOR o César).
     - conte: Para XOR (punt=0,1): Clave de cifrado (str).
              Para César (punt=2): Dirección 1 (adelante) o 0 (atrás).
     - line: Para César (punt=2): Desplazamiento (int).
     - punt: 0 (desencriptar XOR), 1 (encriptar XOR), 2 (encriptar César).

 27: Separar contenido por ';' en una lista.
     - line: Índice de línea (base 0) - solo si punt=1.
     - punt: 0 (todo el archivo) o 1 (línea específica).
     - Devuelve: Lista de elementos (list[str]).

 28: Unir lista con ';' y escribir en archivo.
     - conte: Lista de Python a unir (list).
     - line: Índice de línea (base 0) - solo si punt=1.
     - punt: 0 (añadir al inicio), 1 (reemplazar línea), 2 (añadir al final).

 29: Crear archivo .csv a partir de .txt (delimitado por comas).
     - El archivo .txt debe tener datos separados por comas.
     - Crea un archivo .csv con el mismo nombre en la misma ubicación.

=============================================================================

Argumentos generales:
  ruta_archivo (str): Ruta del archivo a tratar.
  tipo_operacion (int): Número de la operación a realizar (0-29).
  contenido (any): Texto/datos para operaciones de escritura/modificación.
  numero_linea (int | str, optional): Índice de línea (base 0) o comando especial.
  parametro_extra (any, optional): Parámetro adicional según tipo_operacion.
=============================================================================
    """
    print(ayuda)
    return None # Termina tras mostrar ayuda

def _procesar_tipo_1(ruta_archivo):
    """Tipo 1: Crea un archivo vacío o sobrescribe si existe."""
    if asistencia._escribir_contenido_completo(ruta_archivo, ""):
         print(f"Archivo '{ruta_archivo}' creado/sobrescrito.")
    else:
         print(f"Error al crear/sobrescribir '{ruta_archivo}'.")
    return None

def _procesar_tipo_2(ruta_archivo):
    """Tipo 2: Elimina el archivo especificado."""
    try:
        os.remove(ruta_archivo)
        print(f"Archivo '{ruta_archivo}' eliminado.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}' para eliminar.")
    except OSError as e:
        print(f"Error al eliminar '{ruta_archivo}': {e}")
    return None

def _procesar_tipo_3_o_4(ruta_archivo, tipo_op, contenido_str, puntero_arg):
    """Tipo 3 (Copiar) o Tipo 4 (Mover) archivo."""
    if not isinstance(puntero_arg, str) or puntero_arg.isdigit():
        return "Para copiar/mover, 'parametro_extra' debe ser la ruta de destino (string)."
    if not isinstance(contenido_str, str) or not contenido_str:
         return "Para copiar/mover, 'contenido' debe ser el nuevo nombre del archivo (string no vacío)."

    ruta_destino_base = puntero_arg
    nuevo_nombre = contenido_str
    ruta_destino_completa = os.path.join(ruta_destino_base, nuevo_nombre)

    # Crear directorio destino si no existe
    try:
        os.makedirs(ruta_destino_base, exist_ok=True)
    except OSError as e:
        print(f"Error al crear directorio destino '{ruta_destino_base}': {e}")
        return None

    operacion_str = "copiar" if tipo_op == 3 else "mover"
    accion_func = shutil.copy2 if tipo_op == 3 else shutil.move # copy2 preserva metadatos

    try:
        accion_func(ruta_archivo, ruta_destino_completa)
        print(f"Archivo '{ruta_archivo}' {operacion_str} a '{ruta_destino_completa}'.")
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo origen '{ruta_archivo}'.")
    except Exception as e:
        print(f"Error al {operacion_str} '{ruta_archivo}' a '{ruta_destino_completa}': {e}")
    return None

def _procesar_tipo_5(ruta_archivo, contenido_str):
    """Tipo 5: Reemplaza todo el contenido del archivo con el 'contenido' proporcionado."""
    if asistencia._escribir_contenido_completo(ruta_archivo, contenido_str):
        print(f"Contenido de '{ruta_archivo}' reemplazado.")
    else:
        print(f"Error al reemplazar contenido de '{ruta_archivo}'.")
    return None

def _procesar_tipo_6(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 6: Añade 'contenido' al archivo (modificado según parametro_extra 'punt')."""
    try:
        punt_val = int(puntero_arg)
    except (ValueError, TypeError):
        return f"Para la operación tipo 6, 'parametro_extra' (punt) debe ser un número entero. Valor recibido: {puntero_arg}"

    if punt_val not in [0, 1, 2, 3]:
        return f"Para la operación tipo 6, 'parametro_extra' (punt) debe ser 0, 1, 2 o 3. Valor recibido: {puntero_arg}"

    if punt_val == 0:
        # Comportamiento original: añadir al final con un espacio si es necesario.
        # _anadir_contenido falla si el archivo no existe.
        if asistencia._anadir_contenido(ruta_archivo, contenido_str):
            print(f"Contenido añadido a '{ruta_archivo}' (punt=0).")
        # _anadir_contenido ya maneja la impresión de errores.
        return None

    elif punt_val == 1:
        # Crear una nueva línea debajo del texto existente y alojar el contenido_str.
        # Crea el archivo si no existe.
        try:
            # Leer primero para determinar si se necesita un \n inicial.
            contenido_previo = ""
            if os.path.exists(ruta_archivo): # Solo leer si existe
                contenido_previo = asistencia._leer_contenido_completo(ruta_archivo)
                if contenido_previo is None: # Error de lectura, tratar como si no existiera o vacío
                    contenido_previo = "" # Para que la lógica de endswith no falle

            with open(ruta_archivo, 'a', encoding='utf-8') as f:
                if contenido_previo and not contenido_previo.endswith('\n'):
                    f.write('\n')
                f.write(contenido_str + '\n')
            print(f"Contenido añadido en una nueva línea al final de '{ruta_archivo}' (punt=1).")
        except Exception as e:
            print(f"Error al añadir contenido (punt=1) a '{ruta_archivo}': {e}")
        return None

    elif punt_val == 2:
        # Alojar contenido_str arriba, el contenido existente debajo en una nueva línea.
        # Crea el archivo si no existe.
        if not contenido_str: # Si el contenido a insertar es una cadena vacía
            if not os.path.exists(ruta_archivo):
                asistencia._escribir_contenido_completo(ruta_archivo, "")
                print(f"Archivo '{ruta_archivo}' creado vacío (punt=2, contenido a insertar vacío).")
            else:
                print(f"Contenido a insertar vacío, no se realizaron cambios en '{ruta_archivo}' (punt=2).")
            return None

        contenido_original = asistencia._leer_contenido_completo(ruta_archivo)
        if contenido_original is None: # Archivo no existe o error al leer
            contenido_original = ""

        nuevo_contenido_total = contenido_str
        if contenido_original: # Solo añadir \n y original si hay contenido original
            if not contenido_str.endswith('\n'):
                nuevo_contenido_total += '\n'
            nuevo_contenido_total += contenido_original
        # Si contenido_original era "", nuevo_contenido_total es solo contenido_str.

        if asistencia._escribir_contenido_completo(ruta_archivo, nuevo_contenido_total):
            print(f"Contenido insertado al inicio de '{ruta_archivo}' (punt=2).")
        else:
            print(f"Error al escribir contenido al inicio de '{ruta_archivo}' (punt=2).")
        return None

    elif punt_val == 3:
        # Alojar contenido_str debajo de la línea 'numero_linea'.
        # Archivo y línea deben existir.
        if num_linea is None:
            return "Para la operación tipo 6 con punt=3, se requiere un 'numero_linea' válido."

        lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
        if lineas is None:
            print(f"Error: El archivo '{ruta_archivo}' no existe o no se pudo leer para la operación (punt=3).")
            return None

        if not (0 <= num_linea < len(lineas)):
            return f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}) para '{ruta_archivo}' (punt=3)."

        lineas.insert(num_linea + 1, contenido_str)

        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
            print(f"Contenido insertado debajo de la línea {num_linea} en '{ruta_archivo}' (punt=3).")
        else:
            print(f"Error al escribir los cambios en '{ruta_archivo}' (punt=3).")
        return None

def _procesar_tipo_7(ruta_archivo):
    """Tipo 7: Extrae y devuelve todo el contenido del archivo."""
    contenido_leido = asistencia._leer_contenido_completo(ruta_archivo)
    if contenido_leido is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None
    return contenido_leido

def _procesar_tipo_8(ruta_archivo):
    """Tipo 8: Devuelve una lista con todas las líneas del archivo."""
    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None
    return lineas

def _procesar_tipo_9(ruta_archivo, num_linea):
    """Tipo 9: Devuelve la línea específica indicada por 'numero_linea'."""
    if num_linea is None:
        return "Se requiere un 'numero_linea' válido para esta operación."
    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None
    if 0 <= num_linea < len(lineas):
        return lineas[num_linea]
    else:
        print(f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}).")
        return None

def _procesar_tipo_10(ruta_archivo, contenido_str, num_linea):
    """Tipo 10: Reemplaza la línea 'numero_linea' con el 'contenido'."""
    if num_linea is None:
        return "Se requiere un 'numero_linea' válido para esta operación."
    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None
    if 0 <= num_linea < len(lineas):
        lineas[num_linea] = contenido_str
        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
            print(f"Línea {num_linea} de '{ruta_archivo}' reemplazada.")
        else:
             print(f"Error al escribir los cambios en '{ruta_archivo}'.")
    else:
        print(f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}).")
    return None

def _procesar_tipo_11(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 11: Modifica una palabra específica (indicada por 'parametro_extra' como índice) en la línea 'numero_linea' con el 'contenido'."""
    if num_linea is None:
        return "Se requiere un 'numero_linea' válido para esta operación."
    try:
        indice_palabra = int(puntero_arg)
    except (ValueError, TypeError):
        return f"Para la operación tipo 11, 'parametro_extra' debe ser un número entero (índice de palabra). Valor recibido: {puntero_arg}"

    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None

    if 0 <= num_linea < len(lineas):
        palabras = lineas[num_linea].split(" ")
        if 0 <= indice_palabra < len(palabras):
            palabras[indice_palabra] = contenido_str
            lineas[num_linea] = " ".join(palabras)
            if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
                print(f"Palabra {indice_palabra} en línea {num_linea} de '{ruta_archivo}' modificada.")
            else:
                print(f"Error al escribir los cambios en '{ruta_archivo}'.")
        else:
            print(f"Error: El índice de palabra {indice_palabra} está fuera del rango (0-{len(palabras)-1}) para la línea {num_linea}.")
    else:
        print(f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}).")
    return None

def _procesar_tipo_12(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 12: Añade 'contenido' al final de la línea 'numero_linea' (espacio si 'parametro_extra' es True)."""
    if num_linea is None:
        return "Se requiere un 'numero_linea' válido para esta operación."

    anadir_espacio = False
    try:
        # Intenta convertir parametro_extra a booleano (0=False, otro=True)
        anadir_espacio = bool(int(puntero_arg)) if puntero_arg is not None else False
    except (ValueError, TypeError):
         # Si no es convertible a int, considera True si no es una cadena vacía/None
         anadir_espacio = bool(puntero_arg)

    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None

    if 0 <= num_linea < len(lineas):
        linea_original = lineas[num_linea].rstrip() # Quita espacios/saltos al final
        separador = " " if anadir_espacio and linea_original else ""
        lineas[num_linea] = linea_original + separador + contenido_str
        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
            print(f"Texto añadido a la línea {num_linea} de '{ruta_archivo}'.")
        else:
            print(f"Error al escribir los cambios en '{ruta_archivo}'.")
    else:
        print(f"Error: El número de línea {num_linea} está fuera del rango (0-{len(lineas)-1}).")
    return None

def _procesar_tipo_13(ruta_archivo, contenido_str, num_linea_int, linea_especial, puntero_arg):
    """Tipo 13: Enumera o des-enumera líneas."""
    try:
        opcion_enum = int(puntero_arg)
    except (ValueError, TypeError):
        return "Para enumerar/des-enumerar (tipo 13), 'parametro_extra' debe ser un entero entre 0 y 3."

    if opcion_enum not in [0, 1, 2, 3]:
        return "Para enumerar/des-enumerar (tipo 13), 'parametro_extra' debe ser un entero entre 0 y 3."

    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        print(f"No se pudo leer el archivo '{ruta_archivo}'.")
        return None

    # Manejo especial para opcion_enum == 3
    if opcion_enum == 3:
        # Caso especial 1: linea_especial == "here" -> Devolver lista con números de líneas vacías
        if linea_especial == "here":
            lineas_vacias = []
            for idx, linea in enumerate(lineas):
                if not linea.strip(): # Línea vacía o solo espacios
                    lineas_vacias.append(idx)
            return lineas_vacias
        
        # Caso especial 2: linea_especial == "out" -> Eliminar líneas especificadas en contenido_str
        elif linea_especial == "out":
            # Convertir contenido_str a lista de índices
            indices_a_eliminar = []
            if isinstance(contenido_str, list):
                indices_a_eliminar = [int(x) for x in contenido_str if isinstance(x, (int, str)) and str(x).isdigit()]
            elif isinstance(contenido_str, int):
                indices_a_eliminar = [contenido_str]
            elif isinstance(contenido_str, str) and contenido_str.isdigit():
                indices_a_eliminar = [int(contenido_str)]
            else:
                print(f"Error: Para eliminar líneas (punt=3, line='out'), 'contenido' debe ser un número o lista de números.")
                return None
            
            # Eliminar líneas (de mayor a menor índice para no afectar los índices)
            indices_a_eliminar_ordenados = sorted(set(indices_a_eliminar), reverse=True)
            for idx in indices_a_eliminar_ordenados:
                if 0 <= idx < len(lineas):
                    del lineas[idx]
                else:
                    print(f"Advertencia: Índice {idx} fuera de rango, se omite.")
            
            if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
                print(f"Líneas eliminadas de '{ruta_archivo}'.")
            else:
                print(f"Error al escribir los cambios en '{ruta_archivo}'.")
            return None
        
        # Caso normal 1: num_linea_int == None -> Quitar espacios iniciales de todas las líneas
        elif num_linea_int is None:
            lineas_modificadas = [linea.lstrip() for linea in lineas]
            if asistencia._escribir_lineas_archivo(ruta_archivo, lineas_modificadas):
                print(f"Espacios iniciales quitados de todas las líneas en '{ruta_archivo}'.")
            else:
                print(f"Error al escribir los cambios en '{ruta_archivo}'.")
            return None
        
        # Caso normal 2: num_linea_int es un entero -> Quitar espacios solo de esa línea
        elif isinstance(num_linea_int, int):
            if 0 <= num_linea_int < len(lineas):
                lineas[num_linea_int] = lineas[num_linea_int].lstrip()
                if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
                    print(f"Espacios iniciales quitados de la línea {num_linea_int} en '{ruta_archivo}'.")
                else:
                    print(f"Error al escribir los cambios en '{ruta_archivo}'.")
                return None
            else:
                print(f"Error: El número de línea {num_linea_int} está fuera del rango (0-{len(lineas)-1}).")
                return None
        else:
            print(f"Error: Valor inesperado para 'numero_linea': {num_linea_int}")
            return None

    # Lógica para opciones 0, 1, 2
    lineas_modificadas = []
    devolver_resultado = (linea_especial == "here" and opcion_enum in [1, 2])

    for idx, linea in enumerate(lineas):
        nueva_linea = linea
        if opcion_enum == 0: # Añadir enumeración
            nueva_linea = f"{idx}-{contenido_str}{linea}"
        elif opcion_enum == 1: # Quitar enumeración simple ("numero-")
            partes = linea.split('-', 1)
            if len(partes) == 2 and partes[0].isdigit():
                nueva_linea = partes[1] # Resto de la línea
            # else: la línea no tenía el formato, se deja como está
        elif opcion_enum == 2: # Quitar enumeración y contenido ("numero-contenido")
             # Esta opción es más compleja si el contenido puede variar o tener guiones.
             # Asumimos que buscamos "numero-CONTENIDO_FIJO" al inicio.
             prefijo_buscado = f"{idx}-{contenido_str}"
             if linea.startswith(prefijo_buscado):
                 nueva_linea = linea[len(prefijo_buscado):]
             else:
                 # Intenta quitar solo "numero-" si el prefijo completo no coincide
                 partes = linea.split('-', 1)
                 if len(partes) == 2 and partes[0].isdigit():
                     nueva_linea = partes[1]

        lineas_modificadas.append(nueva_linea)

    if devolver_resultado:
        return "\n".join(lineas_modificadas) # Devuelve como string multilínea
    else:
        if asistencia._escribir_lineas_archivo(ruta_archivo, lineas_modificadas):
            print(f"Operación de enumeración (opción {opcion_enum}) completada en '{ruta_archivo}'.")
        else:
            print(f"Error al escribir los cambios de enumeración en '{ruta_archivo}'.")
        return None

# -------------------------------------
# Función Principal - Primera Parte
# -------------------------------------

def tratatez(dire, tipe, conte="", line=None, punt=None):
    """
    Realiza diversas operaciones (tipos 0-13) sobre archivos de texto.

    Args:
        dire (str): Ruta al archivo .txt a procesar.
        tipe (int | str): Código numérico que indica la operación a realizar (ver tabla al inicio).
        conte (str, optional): Texto a escribir, añadir, reemplazar, etc., según la operación. Defaults to "".
                               En tipos 3 y 4, es el nuevo nombre del archivo en destino.
                               En tipo 13 (opcion 2), es el contenido a quitar después del número.
        line (int | str, optional): Índice de la línea a modificar (base 0) o valor especial ("here").
                                   Requerido por tipo 6 (con punt=3), 9, 10, 11, 12. Defaults to None.
                                   En tipo 13 (opciones 1, 2), si es "here", devuelve el resultado en lugar de modificar.
        punt (any, optional): Parámetro adicional con distintos usos según la operación:
                                - Tipos 3, 4: Ruta de destino (str).
                                - Tipo 6: Opción 'punt' (int 0-3) para modo de inserción.
                                - Tipo 11: Índice de la palabra a modificar (int).
                                - Tipo 12: Indicador para añadir espacio (bool o convertible).
                                - Tipo 13: Opción de enumeración (int 0-3).
                                Defaults to None.

    Returns:
        any: Depende de la operación:
             - Tipos 7, 8, 9: Contenido extraído (str o list).
             - Tipo 13 (con "here"): Contenido modificado (str).
             - Tipo 0: None (imprime documentación).
             - Otros tipos: None (realizan operaciones en archivo).
             - En caso de error de validación: Mensaje de error (str).
    """

    # --- Validación Inicial ---
    valido, args = asistencia._validar_argumentos(dire, tipe, conte, line, punt)
    if not valido:
        print(args) # Imprime el mensaje de error
        return None
    ruta_archivo, tipo, contenido_str, num_linea_int, linea_especial, puntero_arg = args

    # --- Ejecución de Operaciones ---

    if tipo == 0:
        return _procesar_tipo_0()
    elif tipo == 1:
        return _procesar_tipo_1(ruta_archivo)
    elif tipo == 2:
        return _procesar_tipo_2(ruta_archivo)
    elif tipo in [3, 4]:
        return _procesar_tipo_3_o_4(ruta_archivo, tipo, contenido_str, puntero_arg)
    elif tipo == 5:
        return _procesar_tipo_5(ruta_archivo, contenido_str)
    elif tipo == 6:
        return _procesar_tipo_6(ruta_archivo, contenido_str, num_linea_int, puntero_arg)
    elif tipo == 7:
        return _procesar_tipo_7(ruta_archivo)
    elif tipo == 8:
        return _procesar_tipo_8(ruta_archivo)
    elif tipo == 9:
        return _procesar_tipo_9(ruta_archivo, num_linea_int)
    elif tipo == 10:
        return _procesar_tipo_10(ruta_archivo, contenido_str, num_linea_int)
    elif tipo == 11:
        return _procesar_tipo_11(ruta_archivo, contenido_str, num_linea_int, puntero_arg)
    elif tipo == 12:
        return _procesar_tipo_12(ruta_archivo, contenido_str, num_linea_int, puntero_arg)
    elif tipo == 13:
        return _procesar_tipo_13(ruta_archivo, contenido_str, num_linea_int, linea_especial, puntero_arg)
    else:
        # Este caso no debería ocurrir si _validar_argumentos_base funciona bien
        print(f"Error: Tipo de operación \'{tipo}\' no reconocido o inválido.")
        return None

# -------------------------------------
# Ejemplo de uso (opcional, si se ejecuta el script directamente)
# -------------------------------------

if __name__ == "__main__":
    # Puedes añadir aquí ejemplos de cómo llamar a la función tratatez
    # Ejemplo: Crear un archivo de prueba
    # print(f"--- Probando Módulo tratatez_1 con '{ruta_prueba}' ---")
    ruta_prueba = "prueba_tratatez1.txt"
    otra_ruta = "C:\\Users\\User\\Desktop\\proyecto_alfha\\tratatez\\otros"
    print("Módulo tratatez cargado. Llama a la función tratatez() para usarlo.")

    # # Probar tipo 1: Crear archivo
    # print("\nProbando tipo 1 (Crear archivo):")
    # tratatez(ruta_prueba, 1)

    # # Probar tipo 2: Eliminar archivo (limpieza)
    # print("\nProbando tipo 2 (Eliminar archivo):")
    # tratatez(ruta_prueba, 2)
    
    # tratatez(ruta_prueba, 3, "prueba_tratatez1.txt", None, otra_ruta)

    # # Probar tipo 5: Reemplazar contenido
    # print("\nProbando tipo 5 (Reemplazar contenido):")
    # contenido_inicial = "Linea 0: Hola mundo\nLinea 1: con areas y espacios\nLinea 2: final."
    # tratatez(ruta_prueba, 5, contenido_inicial)
    # print("Contenido después tipo 5:")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 6 (punt=1): Añadir nueva línea al final
    # print("\nProbando tipo 6 (punt=1, Añadir nueva línea):")
    # tratatez(ruta_prueba, 6, "Nueva linea al final", punt=1)
    # print("Contenido después tipo 6 (punt=1):")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 6 (punt=3): Añadir debajo de línea específica
    # print("\nProbando tipo 6 (punt=3, Añadir debajo de línea 1):")
    # tratatez(ruta_prueba, 6, "Linea insertada debajo de linea 1", line=1, punt=3)
    # print("Contenido después tipo 6 (punt=3):")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 8: Devuelve lista con líneas
    # print("\nProbando tipo 8")
    # list_lineal = tratatez(ruta_prueba, 8)
    # print(f"List:\n '{list_lineal}'")

    # # Probar tipo 9: Sacar línea específica
    # print("\nProbando tipo 9 (Sacar línea 2):")
    # linea_extraida = tratatez(ruta_prueba, 9, line=2)
    # print(f"Línea 2: '{linea_extraida}'")

    # # Probar tipo 10: Reemplazar línea específica
    # print("\nProbando tipo 10 (Reemplazar línea 0):")
    # tratatez(ruta_prueba, 10, "Linea 0 reemplazada", line=0)
    # print("Contenido después tipo 10:")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 12: Añadir texto al final de línea
    # print("\nProbando tipo 12 (Añadir texto al final línea 1 con espacio):")
    # tratatez(ruta_prueba, 12, " - texto añadido", line=1, punt=1) # punt=1 para añadir espacio
    # print("Contenido después tipo 12:")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 13 (opcion 0): Enumerar líneas
    # print("\nProbando tipo 13 (opcion 0, Enumerar):")
    # tratatez(ruta_prueba, 13, "ITEM_", punt=0) # conte="ITEM_" como prefijo
    # print("Contenido después tipo 13 (opcion 0):")
    # print(tratatez(ruta_prueba, 7))

    # # Probar tipo 13 (opcion 1): Quitar enumeración simple
    # print("\nProbando tipo 13 (opcion 1, Quitar enumeración):")
    # tratatez(ruta_prueba, 13, punt=1)
    # print("Contenido después tipo 13 (opcion 1):")
    # print(tratatez(ruta_prueba, 7))

    pass
