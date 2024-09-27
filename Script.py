from flask import Flask, request, render_template, send_file
import pandas as pd
import re
import os

app = Flask(__name__)

# Función para limpiar correos inválidos y conservar los válidos
def limpiar_correos(df, columna_correo):
    # Expresión regular ajustada para incluir dominios específicos
    regex = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@(wix\.com|[a-zA-Z0-9-]+\.(com|co\.uk|org|net|net\.uk|edu|gov|io|info|biz))$'
    
    # Limpiar la columna de correos
    def validar_correos(correos):
        if isinstance(correos, str):
            # Separar correos por comas y limpiar espacios
            lista_correos = [correo.strip() for correo in correos.split(',')]
            # Filtrar correos válidos que no comiencen con números y no contengan "example"
            correos_validos = [
                correo for correo in lista_correos 
                if re.match(regex, correo) and not correo[0].isdigit() and 'example' not in correo.lower()
            ]
            # Unir correos válidos de nuevo en una cadena separada por comas
            return ', '.join(correos_validos)
        else:
            # Si no es una cadena, retornar un string vacío
            return ''

    # Aplicar la validación a la columna de correos
    df[columna_correo] = df[columna_correo].apply(validar_correos)
    
    return df

# Ruta principal que muestra el formulario
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para manejar la carga del archivo y procesamiento
@app.route('/procesar', methods=['POST'])
def procesar_archivo():
    if 'file' not in request.files:
        return "No se ha subido ningún archivo"
    
    archivo = request.files['file']

    if archivo.filename == '':
        return "No se ha seleccionado ningún archivo"

    # Leer el archivo Excel
    df = pd.read_excel(archivo)

    # Limpiar los correos inválidos
    columna_correo = "company_email"  # Cambia este nombre según tu archivo Excel
    df_limpio = limpiar_correos(df, columna_correo)

    # Guardar el archivo filtrado en un nuevo archivo
    archivo_salida = "limpios.xlsx"
    df_limpio.to_excel(archivo_salida, index=False)

    # Enviar el archivo filtrado como respuesta para descarga
    return send_file(archivo_salida, as_attachment=True)

if __name__ == '__main__':
    # Asegúrate de tener la carpeta de plantillas en el mismo nivel
    app.run(debug=True)



#Codigo para el script sin integracion web:
# import pandas as pd
# import re

# # Función para limpiar correos inválidos y conservar los válidos
# def limpiar_correos(df, columna_correo):
#     # Expresión regular mejorada para validar correos electrónicos
#     # regex = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9-]+\.(com|co\.uk|org|net|net\.uk|edu|gov|io|info|biz)$'
#     regex = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@(wix\.com|[a-zA-Z0-9-]+\.(com|co\.uk|org|net|net\.uk|edu|gov|io|info|biz))$'
    
#     # Limpiar la columna de correos
#     def validar_correos(correos):
#         if isinstance(correos, str):
#             # Separar correos por comas y limpiar espacios
#             lista_correos = [correo.strip() for correo in correos.split(',')]
#             # Filtrar correos válidos que no comiencen números y no contengan "example"
#             correos_validos = [
#                 correo for correo in lista_correos 
#                 if re.match(regex, correo) and not correo[0].isdigit() and 'example' not in correo.lower()
#             ]
#             # Unir correos válidos de nuevo en una cadena separada por comas
#             return ', '.join(correos_validos)
#         else:
#             # Si no es una cadena, retornar un string vacío
#             return ''

#     # Aplicar la validación a la columna de correos
#     df[columna_correo] = df[columna_correo].apply(validar_correos)
    
#     return df

# # Leer la lista de correos desde un archivo Excel
# def leer_excel(archivo_excel):
#     # Cargar el archivo Excel
#     df = pd.read_excel(archivo_excel)
#     return df

# # Guardar la lista de correos limpios y la información adicional en un nuevo archivo Excel
# def guardar_correos_limpios(df_limpios, nombre_salida):
#     df_limpios.to_excel(nombre_salida, index=False)

# # Configurar los nombres de los archivos
# archivo_entrada = "correos.xlsx"  # Nombre de tu archivo Excel de entrada
# archivo_salida = "limpios.xlsx"   # Nombre del archivo donde guardar los correos limpios
# columna_correo = "company_email"  # Nombre de la columna que contiene los correos. company_email

# # Leer el archivo Excel original
# df = leer_excel(archivo_entrada)

# # Limpiar los correos inválidos y eliminar los que contienen "example"
# df_limpio = limpiar_correos(df, columna_correo)

# # Guardar los correos válidos junto con la información restante en un nuevo archivo
# guardar_correos_limpios(df_limpio, archivo_salida)

# print(f"Proceso completado. Correos válidos guardados en '{archivo_salida}'.")