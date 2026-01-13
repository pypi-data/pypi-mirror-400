# -*- coding: utf-8 -*-
"""
Librería tratatez_3 (tercera parte de tratatez) para operaciones específicas en archivos de texto.
"""

import os
import csv
from tratatez.metodos_de_apoyo.c_apoyo import Funciones_de_apoyo

#       3° parte
#####################################
#                                   #
#   24- encript contenido de arch   # -> XOR/Cesar, conte=clave/direccion, line=desplazamiento, punt=0(decXOR)/1(encXOR)/2(encCesar). Modifica archivo.
#   27- separ por cada ; en lista   # -> punt=0(todo)/1(linea). Devuelve list[str].
#   28- list a stream unidas por ;  # -> conte=list, punt=0(inicio)/1(reemplazar linea)/2(final). Modifica archivo.
#   29- crear .csv a partir de .txt # -> Delimitador ',' en TXT. Crea archivo .csv.
#                                   #
#####################################

# objeto de la clase Funciones_de_apoyo
asistencia = Funciones_de_apoyo()

# -------------------------------------
# Funciones de Operación por Tipo
# -------------------------------------

def _info_del_tipo():
    """Tipo 0: Muestra documentación interna."""
    ayuda = """
=============================================================================
Documentación Rápida de tratadocu-3.py (Tercera parte de tratatez)

Operaciones disponibles (argumento tipe):
  24: Encriptar/Desencriptar archivo (XOR o César).
  27: Separar contenido por ';' en una lista.
  28: Unir lista con ';' y escribir en archivo.
  29: Crear archivo .csv a partir de .txt (delimitado por comas).

Argumentos:
  dire (str): Ruta al archivo .txt a procesar.
  tipe (int | str): Código numérico (24, 27, 28, 29).
  conte (any): Contenido a usar, depende del tipo:
               - Tipo 24 (punt=0, 1): Clave de cifrado/descifrado XOR (str).
               - Tipo 24 (punt=2): Dirección del cifrado César: 1 (adelante), 0 (atrás).
               - Tipo 28: Lista de Python a unir (list).
               - Otros tipos: No usado directamente o validado internamente.
  line (int | str, optional): Depende del tipo:
               - Tipo 24 (punt=2): Desplazamiento para cifrado César (int).
               - Tipo 27, 28: Índice de la línea (base 0).
               Defaults to None.
  punt (int | str, optional): Parámetro adicional, depende del tipo:
               - Tipo 24: 0 (desencriptar XOR), 1 (encriptar XOR), 2 (encriptar César).
               - Tipo 27: 0 (todo el archivo) o 1 (línea específica).
               - Tipo 28: 0 (añadir al inicio), 1 (reemplazar línea), 2 (añadir al final).
               - Tipo 29: No usado.
               Defaults to None.
=============================================================================
    """
    print(ayuda)
    return None

def _procesar_tipo_24(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 24: Encriptar/Desencriptar archivo."""
    accion = puntero_arg # 0: XOR decrypt, 1: XOR encrypt, 2: Cesar encrypt

    contenido_original = asistencia._leer_contenido_completo(ruta_archivo)
    if contenido_original is None:
        return None

    contenido_procesado = None
    success = False
    accion_str = ""

    if accion in [0, 1]: # Operaciones XOR
        clave = str(contenido_str)
        if not clave:
            print("Error tipo 24 (XOR): Se requiere una clave en 'conte'.")
            return None

        if accion == 1: # Encriptar XOR con validación ASCII
            if not all(c.isalnum() or c.isspace() for c in contenido_original):
                 print("Error tipo 24 (Encriptar XOR): El contenido debe contener solo letras, números y espacios.")
                 return None
            accion_str = "encriptado (XOR)"
        else:
            accion_str = "desencriptado (XOR)"

        contenido_procesado = asistencia._xor_cipher(contenido_original, clave)
        if contenido_procesado is None:
             print(f"Error tipo 24: Falló la operación XOR.")
             return None

    elif accion == 2: # Encriptar César
        try:
            direccion = int(contenido_str)
            desplazamiento = int(num_linea)
        except (ValueError, TypeError):
             print("Error tipo 24 (César): 'conte' (dirección) y 'line' (desplazamiento) deben ser números enteros.")
             return None

        contenido_procesado = asistencia._cifrado_cesar(contenido_original, desplazamiento, direccion)
        if contenido_procesado is None:
             return None
        accion_str = f"encriptado (César, desp={desplazamiento}, dir={'adelante' if direccion==1 else 'atrás'})"

    # Escritura del resultado
    if contenido_procesado is not None:
        if isinstance(contenido_procesado, bytes):
             print("Escribiendo resultado como bytes crudos.")
             try:
                 directorio = os.path.dirname(ruta_archivo)
                 if directorio:
                     os.makedirs(directorio, exist_ok=True)
                 with open(ruta_archivo, 'wb') as f:
                     f.write(contenido_procesado)
                 success = True
             except Exception as e:
                 print(f"Error al escribir bytes: {e}")
                 success = False
        else:
             success = asistencia._escribir_contenido_completo(ruta_archivo, contenido_procesado)

    if success:
        print(f"Archivo '{ruta_archivo}' {accion_str} con éxito.")
    else:
        if contenido_procesado is not None:
             print(f"Error al guardar el archivo procesado para el tipo 24.")
    return None

def _procesar_tipo_27(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 27: Separar por ';' en lista."""
    modo_operacion = puntero_arg # 0 para todo, 1 para línea

    if modo_operacion == 0: # Todo el archivo
        lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
        if lineas is None:
            return None
        resultado_final = []
        for linea in lineas:
            elementos = linea.split(';')
            resultado_final.extend(elementos)
        return resultado_final
    elif modo_operacion == 1: # Línea específica
        if num_linea is None:
             print("Error tipo 27 (modo 1): Se requiere un número de línea válido.")
             return None
        lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
        if lineas is None:
            return None
        if not (0 <= num_linea < len(lineas)):
             print(f"Error tipo 27 (modo 1): El número de línea {num_linea} está fuera del rango.")
             return None
        return lineas[num_linea].split(';')
    else:
        print(f"Error interno tipo 27: modo de operación '{modo_operacion}' inválido.")
        return None

def _procesar_tipo_28(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 28: Unir lista (conte) con ';' y escribir en archivo."""
    if not isinstance(contenido_str, list):
        print("Error tipo 28: El argumento 'conte' debe ser una lista de Python.")
        return None
    
    try:
        elementos_str = [str(elemento) for elemento in contenido_str]
        resultado_str = ";".join(elementos_str)
    except Exception as e:
         print(f"Error tipo 28: No se pudo convertir la lista a string. ({e})")
         return None

    modo_escritura = puntero_arg # 0 inicio, 1 reemplazar, 2 final

    lineas = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas is None:
        if modo_escritura in [0, 2]:
             lineas = []
        else:
             return None

    if modo_escritura == 0: # Añadir al inicio
        lineas.insert(0, resultado_str)
        accion_desc = "añadida al inicio"
    elif modo_escritura == 1: # Reemplazar línea
        if num_linea is None:
             print("Error tipo 28 (modo 1): Se requiere un número de línea válido para reemplazar.")
             return None
        if not (0 <= num_linea < len(lineas)):
             print(f"Error tipo 28 (modo 1): El número de línea {num_linea} está fuera del rango.")
             return None
        lineas[num_linea] = resultado_str
        accion_desc = f"reemplazada en la línea {num_linea}"
    elif modo_escritura == 2: # Añadir al final
        lineas.append(resultado_str)
        accion_desc = "añadida al final"
    else:
         print(f"Error interno tipo 28: modo de escritura '{modo_escritura}' inválido.")
         return None

    if asistencia._escribir_lineas_archivo(ruta_archivo, lineas):
        print(f"Lista convertida a string y {accion_desc} del archivo.")
    else:
        print(f"Error al guardar los cambios para el tipo 28.")
    return None

def _procesar_tipo_29(ruta_archivo, contenido_str, num_linea, puntero_arg):
    """Tipo 29: Crear .csv a partir de .txt (delimitado por comas)."""
    lineas_txt = asistencia._leer_lineas_como_lista(ruta_archivo)
    if lineas_txt is None:
        return None

    ruta_base, _ = os.path.splitext(ruta_archivo)
    ruta_csv = ruta_base + ".csv"

    try:
        with open(ruta_csv, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            print(f"Creando archivo CSV: '{ruta_csv}'")
            for linea in lineas_txt:
                columnas = linea.split(',')
                columnas_limpias = [col.strip() for col in columnas]
                csv_writer.writerow(columnas_limpias)
        print(f"Archivo '{ruta_csv}' creado con éxito.")
    except csv.Error as e:
        print(f"Error de CSV: {e}")
    except IOError as e:
        print(f"Error de E/S: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    return None

# -------------------------------------
# Función Principal - Tercera Parte
# -------------------------------------

def tratatez(dire, tipe, conte, line=None, punt=None):
    """
    Realiza operaciones específicas (tipos 24, 27-29) sobre archivos de texto.

    Args:
        dire (str): Ruta al archivo .txt a procesar.
        tipe (int | str): Código numérico (24, 27, 28, 29).
        conte (any): Contenido a usar.
        line (int | str, optional): Depende del tipo.
        punt (int | str, optional): Parámetro adicional.

    Returns:
        any: Depende de la operación.
    """
    # Validación Inicial
    valido, args = asistencia._validar_argumentos(dire, tipe, conte, line, punt)
    if not valido:
        print(args)
        return None
    ruta_archivo, tipo, contenido_str, num_linea, linea_especial, puntero_arg = args

    # Despachador de Operaciones
    if tipo == 0:
        return _info_del_tipo()
    if tipo == 24:
        return _procesar_tipo_24(ruta_archivo, contenido_str, num_linea, puntero_arg)
    elif tipo == 27:
        return _procesar_tipo_27(ruta_archivo, contenido_str, num_linea, puntero_arg)
    elif tipo == 28:
        return _procesar_tipo_28(ruta_archivo, contenido_str, num_linea, puntero_arg)
    elif tipo == 29:
        return _procesar_tipo_29(ruta_archivo, contenido_str, num_linea, puntero_arg)
    else:
        print(f"Error: Tipo de operación '{tipo}' no reconocido o inválido.")
        return None

# -------------------------------------
# Ejemplo de uso
# -------------------------------------

if __name__ == "__main__":
    print("Módulo tratadocu-3 cargado. Llama a la función tratatez() para usarlo.")
    pass
