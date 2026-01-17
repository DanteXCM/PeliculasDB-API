from flask import Flask, render_template, request, redirect, url_for
import json, os, requests

# CORRECCIÓN: Usar __name__ (doble guion bajo)
app = Flask(__name__)

# NOTA IMPORTANTE: Coloca tu propia clave de API de OMDb aquí.
API_KEY = "b4641759" 

# Obtenemos la ruta absoluta del directorio del script para guardar el archivo JSON de forma segura
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PELICULAS_FILE = os.path.join(BASE_DIR, 'peliculas.json')


# --- Funciones auxiliares ---

def cargar_peliculas():
    """Carga la lista de películas desde el archivo JSON."""
    if os.path.exists(PELICULAS_FILE):
        with open(PELICULAS_FILE, "r", encoding="utf-8") as f:
            try:
                contenido = f.read()
                if contenido:
                    return json.loads(contenido)
                else:
                    return []
            except json.JSONDecodeError:
                return []
    return []

def guardar_peliculas(peliculas):
    """Guarda la lista de películas en el archivo JSON."""
    with open(PELICULAS_FILE, "w", encoding="utf-8") as f:
        json.dump(peliculas, f, ensure_ascii=False, indent=4)

# Lista de películas cargada al iniciar
peliculas = cargar_peliculas()


# --- Rutas ---

@app.route('/')
def index():
    """Ruta principal: Muestra la lista de películas."""
    return render_template('index.html', peliculas=peliculas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    """Permite buscar y agregar una película a la colección."""
    if request.method == 'POST':
        nombre = request.form.get('nombre')

        if nombre:
            # Llamar a la API OMDb para buscar por título (t)
            url = f"http://www.omdbapi.com/?t={nombre}&apikey={API_KEY}"
            
            respuesta = requests.get(url)
            datos = respuesta.json()

            if datos.get("Response") == "True":
                # Construir el objeto película con datos de la API
                pelicula = {
                    "titulo": datos.get("Title"),
                    "anio": datos.get("Year"),
                    "poster": datos.get("Poster"),
                    "actores": datos.get("Actors"),
                    "sinopsis": datos.get("Plot")
                }
            else:
                # Si la API no encuentra la película
                pelicula = {
                    "titulo": nombre,
                    "anio": "Desconocido",
                    "poster": "",
                    "actores": "No disponible",
                    "sinopsis": "No se encontró información."
                }
            
            peliculas.append(pelicula)
            guardar_peliculas(peliculas)

            return redirect(url_for('index'))
            
    return render_template('agregar.html')

@app.route('/editar/<int:indice>', methods=['GET', 'POST'])
def editar(indice):
    """Muestra y maneja el formulario de edición de una película."""
    
    # Validar índice
    if not (0 <= indice < len(peliculas)):
        return redirect(url_for('index'))
        
    pelicula = peliculas[indice]

    if request.method == 'POST':
        nuevo_titulo = request.form.get('titulo')

        # Actualizar llamando de nuevo a la API para obtener nuevos datos
        url = f"http://www.omdbapi.com/?t={nuevo_titulo}&apikey={API_KEY}"
        respuesta = requests.get(url)
        datos = respuesta.json()

        if datos.get("Response") == "True":
            # Actualizar todos los campos de la película con los datos nuevos
            pelicula["titulo"] = datos.get("Title")
            pelicula["anio"] = datos.get("Year")
            pelicula["poster"] = datos.get("Poster")
            pelicula["actores"] = datos.get("Actors")
            pelicula["sinopsis"] = datos.get("Plot")
        else:
            # Si la API falla o no encuentra el nuevo título
            pelicula["titulo"] = nuevo_titulo
            pelicula["anio"] = "Desconocido"
            pelicula["poster"] = ""
            pelicula["actores"] = "No disponible"
            pelicula["sinopsis"] = "No se encontró información."
        
        guardar_peliculas(peliculas)
        return redirect(url_for('index'))

    return render_template('editar.html', pelicula=pelicula, indice=indice)

@app.route('/eliminar/<int:indice>')
def eliminar(indice):
    """Elimina una película de la colección."""
    
    # Validar índice
    if 0 <= indice < len(peliculas):
        peliculas.pop(indice)
        guardar_peliculas(peliculas)
        
    return redirect(url_for('index'))

# CORRECCIÓN: Usar __name__ (doble guion bajo)
if __name__ == '__main__':
    app.run(debug=True)