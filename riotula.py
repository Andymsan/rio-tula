from flask import Flask, send_from_directory
import os

# Carpeta donde vive riotula.py
BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(BASE, 'index.html')

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(os.path.join(BASE, 'css'), filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory(os.path.join(BASE, 'js'), filename)

@app.route('/data/<path:filename>')
def data(filename):
    return send_from_directory(os.path.join(BASE, 'data'), filename)

@app.route('/videos/<path:filename>')
def videos(filename):
    return send_from_directory(os.path.join(BASE, 'videos'), filename)

@app.route('/mapabase/<path:filename>')
def mapabase(filename):
    return send_from_directory(
        os.path.join(BASE, 'data', 'mapa base'), filename
    )

if __name__ == '__main__':
    print(f"✓ Proyecto en: {BASE}")
    print("✓ Abre en el navegador: http://localhost:5500")
    app.run(debug=True, port=5500)

