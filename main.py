from flask import Flask, request, redirect, jsonify
import string, random
import os
app = Flask(__name__)
urlClo = os.environ.get("URL")
# Base de datos en memoria (puedes cambiar por SQLite o MongoDB)
url_map = {}

# Función para generar códigos aleatorios
def generar_codigo(longitud=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))

# Ruta para acortar una URL
@app.route('/shorten', methods=['POST'])
def acortar_url():
    datos = request.json
    url_larga = datos.get('url')
    alias = datos.get('alias')

    if not url_larga:
        return jsonify({'error': 'Se requiere una URL'}), 400

    if alias:
        if alias in url_map:
            return jsonify({'error': 'Alias ya en uso'}), 409
        codigo = alias
    else:
        codigo = generar_codigo()
        while codigo in url_map:
            codigo = generar_codigo()

    url_map[codigo] = url_larga
    return jsonify({
        'short_url': f'http://{urlClo}/{codigo}',
        'original_url': url_larga
    })

# Ruta para redirigir desde el alias
@app.route('/<codigo>')
def redirigir(codigo):
    if codigo in url_map:
        return redirect(url_map[codigo])
    return 'Alias no encontrado', 404

if __name__ == '__main__':
    app.run(debug=True, port=5007)
