""" Este módulo asiste a las librerias """

import os

class Funciones_de_apoyo:
    
    """Clase que contiene funciones de apoyo."""
    
    def __init__(self):
        """Inicializa la instancia con el atributo retornando."""
        self.retornando = None

    def _validar_argumentos(self, ruta, tipo, conte, linea, puntero):
        """
        Valida los argumentos para las funciones tratatez.

        Args:
            ruta (str): Ruta al archivo.
            tipo (int | str): Código numérico de la operación.
            conte (any): Contenido a usar.
            linea (int | str | None): Índice de línea o valor especial ("here").
            puntero (any | None): Parámetro adicional.

        Returns:
            tuple: (bool, str) indicando éxito/fracaso y mensaje, o (True, tuple) con argumentos validados.
        """
        if not isinstance(ruta, str) or ruta.isdigit():
            return (False, "La ruta del archivo debe ser un texto (string) y no solo dígitos.")

        try:
            tipo_int = int(tipo)
            # Validar rango general de tipos
            if not (0 <= tipo_int <= 29 and tipo_int not in [25, 26]):
                 return (False, f"Tipo de operación {tipo_int} fuera del rango válido (0-29, excluyendo 25 y 26).")
        except (ValueError, TypeError):
            return (False, "El tipo de operación debe ser un número entero válido.")

        # Validar línea solo si es necesaria para el tipo específico
        linea_int = None
        linea_especial = None
        # Tipos que siempre necesitan 'line'
        tipos_con_linea = [9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 22, 23]
        tipos_con_linea_opcional = [6, 13, 21, 24, 27, 28] # Depende de 'punt' o tiene opciones especiales

        linea_requerida = tipo_int in tipos_con_linea or \
                          (tipo_int == 6 and puntero == 3) or \
                          (tipo_int == 21 and puntero == 0) or \
                          (tipo_int == 24 and puntero == 2) or \
                          (tipo_int == 27 and puntero == 1) or \
                          (tipo_int == 28 and puntero == 1) # Tipo 27/28 con punt=1 requiere línea

        # Para tipo 13 con punt=3, siempre procesar linea (puede ser None, int, "here" o "out")
        if tipo_int == 13 and puntero == 3:
            if linea is not None:
                try:
                    linea_int = int(linea)
                    if linea_int < 0:
                        return (False, "El número de línea no puede ser negativo.")
                except (ValueError, TypeError):
                    if isinstance(linea, str) and linea in ["here", "out"]:
                        linea_especial = linea # Guardamos el string especial
                    else:
                        return (False, f"El número de línea para el tipo {tipo_int} debe ser un entero no negativo, None, 'here' o 'out'.")
            # Si linea es None, linea_int permanece None (lo cual es válido para quitar espacios de todas las líneas)
        elif linea_requerida or (tipo_int == 13 and linea in ["here", "out"]):
             if linea is None:
                 return (False, f"La operación tipo {tipo_int} requiere un número de línea o 'here'.")
             try:
                 linea_int = int(linea)
                 if linea_int < 0:
                     return (False, "El número de línea no puede ser negativo.")
             except (ValueError, TypeError):
                 if isinstance(linea, str) and linea in ["here", "out"]:
                     linea_especial = linea # Guardamos el string especial
                 else:
                     return (False, f"El número de línea para el tipo {tipo_int} debe ser un entero no negativo, 'here' o 'out'.")
        # Si no se requiere línea, linea_int y linea_especial permanecen None

        # Validar puntero según el tipo
        punt_arg = puntero # Mantenerlo como está inicialmente
        try:
            # Tipos que usan puntero numérico
            tipos_numericos_punt = [6, 11, 12, 13, 14, 19, 20, 21, 22, 23, 24, 27, 28]
            if tipo_int in tipos_numericos_punt:
                # Validar que no sea None antes de intentar convertir a int
                if puntero is None:
                     return (False, f"El argumento 'punt' es requerido para el tipo {tipo_int}.")

                punt_int = int(puntero)

                # Validaciones específicas por tipo
                if tipo_int == 6 and punt_int not in [0, 1, 2, 3]:
                    return (False, f"Para tipo 6, 'punt' debe ser 0, 1, 2 o 3. Valor recibido: {puntero}")
                if tipo_int == 11 and punt_int < 0:
                     return (False, f"Para tipo 11, 'punt' (índice de palabra) debe ser un entero no negativo. Valor recibido: {puntero}")
                # Tipo 12 acepta bool o convertible a bool (int 0/1)
                if tipo_int == 13 and punt_int not in [0, 1, 2, 3]:
                    return (False, f"Para tipo 13, 'punt' debe ser un entero entre 0 y 3. Valor recibido: {puntero}")
                if tipo_int == 14 and punt_int <= 0: # Tipo 14 requiere puntero positivo (base 1)
                     return (False, f"Para tipo 14, 'punt' (posición) debe ser un entero positivo (base 1). Valor recibido: {puntero}")
                if tipo_int == 19 and punt_int not in [0, 1]:
                     return (False, f"Para tipo 19, 'punt' debe ser 0 (tabulaciones) o 1 (espacios). Valor recibido: {puntero}")
                if tipo_int == 20 and punt_int not in [0, 1]:
                     return (False, f"Para tipo 20, 'punt' debe ser 0 (poner) o 1 (quitar). Valor recibido: {puntero}")
                if tipo_int == 21 and punt_int not in [0, 1]:
                     return (False, f"Para tipo 21, 'punt' debe ser 0 (línea específica) o 1 (todas las líneas). Valor recibido: {puntero}")
                if tipo_int == 22 and punt_int not in range(9): # Delimitadores 0-8
                     return (False, f"Para tipo 22, 'punt' (tipo de delimitador) debe ser un entero entre 0 y 8. Valor recibido: {puntero}")
                if tipo_int == 23 and punt_int < 0: # Índice de fin no puede ser negativo
                     return (False, f"Para tipo 23, 'punt' (índice de fin) debe ser un entero no negativo. Valor recibido: {puntero}")
                if tipo_int == 24 and punt_int not in [0, 1, 2]:
                    return (False, "Para tipo 24, 'punt' debe ser 0, 1 o 2.")
                if tipo_int == 27 and punt_int not in [0, 1]:
                    return (False, "Para tipo 27, 'punt' debe ser 0 o 1.")
                if tipo_int == 28 and punt_int not in [0, 1, 2]:
                    return (False, "Para tipo 28, 'punt' debe ser 0, 1 o 2.")

                # Si pasa las validaciones específicas, asignamos el int
                punt_arg = punt_int

            # Tipo 3, 4 usan puntero como string (ruta)
            elif tipo_int in [3, 4]:
                 if not isinstance(puntero, str) or not puntero or puntero.isdigit():
                      return (False, f"Para tipo {tipo_int}, 'punt' debe ser la ruta de destino (string no vacío y no solo dígitos).")
                 punt_arg = puntero # Mantener como string

            # Tipo 0, 1, 2, 5, 7, 8, 9, 10, 29 no usan puntero de forma estricta o su validación es trivial/interna.
            # punt_arg ya tiene el valor original, que es aceptable para estos tipos.

        except (ValueError, TypeError):
            # Si la conversión a int falla para un tipo que lo requiere
            tipos_requieren_int_punt = [6, 11, 13, 14, 19, 20, 21, 22, 23, 24, 27, 28]
            if tipo_int in tipos_requieren_int_punt:
                 return (False, f"El argumento 'punt' debe ser un entero válido para el tipo {tipo_int}. Valor recibido: {puntero}")
            # Tipo 12 es más flexible, solo validar si no es None/vacío y no convertible a int
            elif tipo_int == 12:
                 if puntero is None or str(puntero).strip() == "":
                      punt_arg = False # Default a False si no se proporciona o está vacío
                 elif not isinstance(puntero, bool):
                      return (False, f"Para tipo 12, 'punt' debe ser True/False o convertible a entero (0/1). Valor recibido: {puntero}")
            # Si la conversión a int falla para un tipo que no lo requiere (ej. tipo 29),
            # punt_arg ya tiene el valor original, lo cual es correcto.


        # Validar 'conte' según el tipo
        # Para tipo 28, conte debe ser una lista, no la convertimos a string
        # Para tipo 13 con linea_especial=="out", conte puede ser int o lista
        # Para otros tipos, convertimos a string
        if tipo_int == 28:
            conte_final = conte
        elif tipo_int == 13 and linea_especial == "out":
            conte_final = conte  # Preservar como int o lista
        else:
            conte_final = str(conte)

        return (True, (str(ruta), tipo_int, conte_final, linea_int, linea_especial, punt_arg))

    def _leer_lineas_como_lista(self, ruta_archivo):
        """Lee todas las líneas de un archivo y las devuelve como lista, sin el salto de línea final."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                # rstrip('\n') para quitar solo el salto de línea final, conservando otros espacios
                lineas = [linea.rstrip('\n') for linea in f.readlines()]
            return lineas
        except FileNotFoundError:
            print(f"Error: El archivo '{ruta_archivo}' no existe.")
            return None # Indica que el archivo no existe
        except Exception as e:
            print(f"Error inesperado al leer el archivo {ruta_archivo}: {e}")
            return None

    def _escribir_lineas_archivo(self, ruta_archivo, lineas):
        """Escribe una lista de líneas en un archivo, añadiendo saltos de línea."""
        try:
            directorio = os.path.dirname(ruta_archivo)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.writelines(linea + '\n' for linea in lineas)
            self.retornando = True
            return True
        except Exception as e:
            print(f"Error inesperado al escribir en el archivo {ruta_archivo}: {e}")
            self.retornando = False
            return False

    def _leer_contenido_completo(self, ruta_archivo):
        """Lee y devuelve todo el contenido de un archivo como un solo string."""
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: El archivo '{ruta_archivo}' no existe.")
            return None
        except Exception as e:
            print(f"Error inesperado al leer el archivo {ruta_archivo}: {e}")
            return None

    def _escribir_contenido_completo(self, ruta_archivo, contenido):
        """Escribe un string en un archivo, sobrescribiendo el contenido existente."""
        try:
            directorio = os.path.dirname(ruta_archivo)
            if directorio:
                os.makedirs(directorio, exist_ok=True)
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            self.retornando = True
            return True
        except Exception as e:
            print(f"Error inesperado al escribir en el archivo {ruta_archivo}: {e}")
            self.retornando = False
            return False

    def _anadir_contenido(self, ruta_archivo, contenido_a_anadir):
        """Añade contenido al final de un archivo existente."""
        try:
            # Usamos 'a' (append) para añadir al final. Si el archivo no existe, lo crea.
            # Esto difiere ligeramente del comportamiento original que fallaba si no existía.
            # Consideramos que añadir al final debe crear el archivo si no está.
            directorio = os.path.dirname(ruta_archivo)
            if directorio:
                os.makedirs(directorio, exist_ok=True)

            # Leer el último caracter para decidir si añadir un espacio
            # Esto solo es relevante si el archivo ya existía y no estaba vacío
            contenido_actual = ""
            if os.path.exists(ruta_archivo) and os.path.getsize(ruta_archivo) > 0:
                 try:
                      with open(ruta_archivo, 'rb') as f: # Leer en binario para ir al final
                           f.seek(-1, os.SEEK_END)
                           ultimo_byte = f.read(1)
                           # Intentar decodificar el último byte para ver si es un caracter de espacio/salto
                           try:
                                ultimo_char = ultimo_byte.decode('utf-8')
                                if ultimo_char in (' ', '\n', '\t'):
                                     contenido_actual = "termina_en_espacio" # Indicador
                                else:
                                     contenido_actual = "no_termina_en_espacio" # Indicador
                           except UnicodeDecodeError:
                                # Si no se puede decodificar, asumimos que no termina en un caracter de espacio/salto UTF-8 simple
                                contenido_actual = "no_termina_en_espacio"

                 except Exception:
                      # Si hay algún error al leer el último byte, asumimos que no termina en espacio
                      contenido_actual = "no_termina_en_espacio"
            else:
                 # Archivo no existe o está vacío, no necesitamos añadir espacio inicial
                 contenido_actual = "vacio_o_no_existe"


            separador = ""
            if contenido_actual == "no_termina_en_espacio":
                separador = " "

            with open(ruta_archivo, 'a', encoding='utf-8') as f:
                f.write(separador + contenido_a_anadir)
            return True
        except Exception as e:
            print(f"Error inesperado al añadir contenido al archivo {ruta_archivo}: {e}")
            return False

    def _cifrado_cesar(self, texto, desplazamiento, direccion):
        """Aplica cifrado César a un texto, moviendo letras y números."""
        resultado = []
        # Asegurar que el desplazamiento sea un entero válido
        try:
            desplazamiento = int(desplazamiento)
        except (ValueError, TypeError):
            print("Error Cifrado César: El desplazamiento debe ser un número entero.")
            return None

        # Validar dirección
        if direccion not in [0, 1]:
            print("Error Cifrado César: La dirección debe ser 0 (atrás) o 1 (adelante).")
            return None

        # Ajustar desplazamiento efectivo para letras y números
        desplazamiento_letras = desplazamiento % 26
        desplazamiento_numeros = desplazamiento % 10

        # Invertir desplazamiento si la dirección es hacia atrás
        if direccion == 0: # Hacia atrás
            desplazamiento_letras = -desplazamiento_letras
            desplazamiento_numeros = -desplazamiento_numeros

        for char in texto:
            if 'a' <= char <= 'z':
                nuevo_codigo = ord('a') + (ord(char) - ord('a') + desplazamiento_letras) % 26
                resultado.append(chr(nuevo_codigo))
            elif 'A' <= char <= 'Z':
                nuevo_codigo = ord('A') + (ord(char) - ord('A') + desplazamiento_letras) % 26
                resultado.append(chr(nuevo_codigo))
            elif '0' <= char <= '9':
                nuevo_codigo = ord('0') + (ord(char) - ord('0') + desplazamiento_numeros) % 10
                resultado.append(chr(nuevo_codigo))
            else:
                resultado.append(char) # Mantener otros caracteres
        return "".join(resultado)

    def _xor_cipher(self, text, key):
        """Aplica cifrado/descifrado XOR simple."""
        if not key:
            return None # No se puede cifrar/descifrar sin clave
        key_len = len(key)
        # Usamos encode/decode para manejar correctamente caracteres multibyte
        # Se asume que tanto el texto como la clave son UTF-8 válidos
        try:
            text_bytes = text.encode('utf-8')
            key_bytes = key.encode('utf-8')
            result_bytes = bytearray()
            for i, byte in enumerate(text_bytes):
                result_bytes.append(byte ^ key_bytes[i % key_len])
            # Intentamos decodificar de vuelta a UTF-8. Si falla, podría indicar
            # que el resultado no es texto válido (ej. al descifrar con clave incorrecta)
            # o que el original no era UTF-8. Devolvemos bytes en ese caso.
            try:
                return result_bytes.decode('utf-8')
            except UnicodeDecodeError:
                print("Advertencia: El resultado del XOR no es decodificable como UTF-8. Devolviendo bytes.")
                return bytes(result_bytes) # Devolver bytes crudos si falla la decodificación
        except UnicodeError as e:
            print(f"Error de codificación/decodificación: {e}. Asegúrese que el texto y la clave sean UTF-8 válidos.")
            return None
