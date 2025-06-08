# app.py
import sys
import os

from flask import Flask, redirect, url_for, render_template


# Añade la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.egresados_routes import egresados_bp
from routes.empresas_routes import empresas_bp
from routes.usuarios_routes import usuarios_bp

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' 

# Registrar blueprints (uno por módulo funcional)
app.register_blueprint(egresados_bp, url_prefix='/egresados')
app.register_blueprint(empresas_bp, url_prefix='/empresas')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

@app.route('/')
def home():
    return render_template('Login.html')
    #return redirect(url_for('egresados.index'))

# Manejo de errores
@app.errorhandler(404)
def not_found(e):
    return "<h2>Página no encontrada</h2>", 404

@app.errorhandler(500)
def server_error(e):
    return "<h2>Error interno del servidor</h2>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
