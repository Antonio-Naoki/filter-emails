from flask import Flask, flash, request, render_template, send_file, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin
import pandas as pd
import pyrebase
import re
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'
# Comienza el inicio  de sesion:

# Configuración de Firebase
firebase_config = {
    "apiKey": "AIzaSyCP_3xBrnX3vqOwXpFtY1R2u3qXO943Jss",
    "authDomain": "filteremails-1a87f.firebaseapp.com",
    "projectId": "filteremails-1a87f",
    "storageBucket": "filteremails-1a87f.appspot.com",
    "messagingSenderId": "68320069554",
    "appId": "1:668320069554:web:d235ffd7874e8b0a2896ab",
    "measurementId": "G-KXNGC285RZ",
    "databaseURL": ""  # Añade esto, aunque no lo uses
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Clase de Usuario
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# Cargar usuario
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        try:
            # Autenticación con Firebase
            user = auth.sign_in_with_email_and_password(email, password)
            user_id = user['localId']
            user_obj = User(user_id)
            login_user(user_obj)
            return redirect(url_for('sesion'))
        except:
            flash("Credenciales incorrectas. Inténtalo de nuevo.", "error")
    return render_template('login.html')

# Ruta protegida
@app.route('/index')
@login_required
def sesion():
    return render_template('index.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
# Termina el inicio de sesion.
#---------------------------------------------------------------------------------------------------------
# Función para limpiar correos inválidos y conservar los válidos
def limpiar_correos(df):
    # Expresión regular ajustada para incluir dominios específicos
    regex = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@(wix\.com|[a-zA-Z0-9-]+\.(com|co\.uk|org|net|net\.uk|edu|gov|io|info|biz))$'
    
    # Función auxiliar para validar correos en una cadena
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
            return ''
    
    # Detectar las columnas que contienen correos electrónicos
    for columna in df.columns:
        # Suponer que si más del 50% de los valores en la columna coinciden con la expresión regular de correos, es una columna de correos
        muestra = df[columna].dropna().astype(str).head(10)  # Toma una muestra de hasta 10 valores
        if muestra.apply(lambda x: bool(re.match(r'.+@.+\..+', x))).mean() > 0.5:
            # Aplicar la validación a la columna de correos
            df[columna] = df[columna].apply(validar_correos)
    
    return df

# Ruta principal que muestra el formulario
@app.route('/')
def index():
    return render_template('login.html')

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

    # Limpiar los correos inválidos en todas las columnas que contengan correos
    df_limpio = limpiar_correos(df)

    # Guardar el archivo filtrado en un nuevo archivo
    archivo_salida = "/tmp/limpios.xlsx" # Para un servidor como pythonanywhere.com hay que usar esta ruta para los archivos de descarga: /tmp/limpios.xlsx
    df_limpio.to_excel(archivo_salida, index=False)

    # Enviar el archivo filtrado como respuesta para descarga
    return send_file(archivo_salida, as_attachment=True)

if __name__ == '__main__':
    # Asegúrate de tener la carpeta de plantillas en el mismo nivel
    app.run(debug=True)



# Codigo para el script con integracion web pero detectando la columna de correos llamada "company_email":
# from flask import Flask, request, render_template, send_file
# import pandas as pd
# import re
# import os

# app = Flask(__name__)

# # Función para limpiar correos inválidos y conservar los válidos
# def limpiar_correos(df, columna_correo):
#     # Expresión regular ajustada para incluir dominios específicos
#     regex = r'^[a-zA-Z][a-zA-Z0-9._%+-]*@(wix\.com|[a-zA-Z0-9-]+\.(com|co\.uk|org|net|net\.uk|edu|gov|io|info|biz))$'
    
#     # Limpiar la columna de correos
#     def validar_correos(correos):
#         if isinstance(correos, str):
#             # Separar correos por comas y limpiar espacios
#             lista_correos = [correo.strip() for correo in correos.split(',')]
#             # Filtrar correos válidos que no comiencen con números y no contengan "example"
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

# # Ruta principal que muestra el formulario
# @app.route('/')
# def index():
#     return render_template('index.html')

# # Ruta para manejar la carga del archivo y procesamiento
# @app.route('/procesar', methods=['POST'])
# def procesar_archivo():
#     if 'file' not in request.files:
#         return "No se ha subido ningún archivo"
    
#     archivo = request.files['file']

#     if archivo.filename == '':
#         return "No se ha seleccionado ningún archivo"

#     # Leer el archivo Excel
#     df = pd.read_excel(archivo)

#     # Limpiar los correos inválidos
#     columna_correo = "company_email"  # Cambia este nombre según tu archivo Excel
#     df_limpio = limpiar_correos(df, columna_correo)

#     # Guardar el archivo filtrado en un nuevo archivo
#     archivo_salida = "/tmp/limpios.xlsx" # Para un servidor como pythonanywhere.com hay que usar esta ruta para los archivos de descarga
#     df_limpio.to_excel(archivo_salida, index=False)

#     # Enviar el archivo filtrado como respuesta para descarga
#     return send_file(archivo_salida, as_attachment=True)

# if __name__ == '__main__':
#     # Asegúrate de tener la carpeta de plantillas en el mismo nivel
#     app.run(debug=True)



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


# // Import the functions you need from the SDKs you need
# import { initializeApp } from "firebase/app";
# import { getAnalytics } from "firebase/analytics";
# // TODO: Add SDKs for Firebase products that you want to use
# // https://firebase.google.com/docs/web/setup#available-libraries

# // Your web app's Firebase configuration
# // For Firebase JS SDK v7.20.0 and later, measurementId is optional
# const firebaseConfig = {
#   apiKey: "AIzaSyCP_3xBrnX3vqOwXpFtY1R2u3qXO943Jss",
#   authDomain: "filteremails-1a87f.firebaseapp.com",
#   projectId: "filteremails-1a87f",
#   storageBucket: "filteremails-1a87f.appspot.com",
#   messagingSenderId: "668320069554",
#   appId: "1:668320069554:web:d235ffd7874e8b0a2896ab",
#   measurementId: "G-KXNGC285RZ"
# };

# // Initialize Firebase
# const app = initializeApp(firebaseConfig);
# const analytics = getAnalytics(app);