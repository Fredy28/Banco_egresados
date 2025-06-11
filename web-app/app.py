# app.py
import sys
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, session, url_for, flash

# Añade la carpeta raíz del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.egresados_routes import buscar_egresado_por_correo 
from routes.egresados_routes import egresados_bp
from routes.empresas_routes import empresas_bp
from routes.usuarios_routes import usuarios_bp

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta' 

@app.after_request
def agregar_headers_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Registrar blueprints
app.register_blueprint(egresados_bp, url_prefix='/egresados')
app.register_blueprint(empresas_bp, url_prefix='/empresas')
app.register_blueprint(usuarios_bp, url_prefix='/usuarios')

@app.route('/')
def home():
    return render_template('Login.html')
    #return redirect(url_for('egresados.index'))

# Decorador para restringir acceso por rol
def login_required(rol=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'rol' not in session:
                flash('Debes iniciar sesión primero.', 'warning')
                return redirect(url_for('login'))
            if rol and session['rol'] != rol:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        contacto = request.form.get('contacto')
        password = request.form.get('password')
        rol = request.form.get('rol')

        if rol == 'admin':
            if contacto == 'admin@egresados.com' and password == 'admin123':
                session['rol'] = 'admin'
                session['usuario'] = 'admin'
                return redirect(url_for('egresados.index'))
            else:
                flash('Credenciales inválidas para administrador.', 'danger')

        elif rol == 'egresado':
            egresado = buscar_egresado_por_correo(contacto)
            print(f"📌 Buscando egresado con correo: {contacto}")
            print(f"🔍 Resultado de búsqueda: {egresado}")

            if egresado and str(egresado.get('password')) == str(password):
                session['rol'] = 'egresado'
                session['usuario'] = str(egresado['_id'])
                return redirect(url_for('egresados.read_egresado', egresado_id=egresado['_id']))
            else:
                flash('Credenciales inválidas para egresado.', 'danger')
        else:
            flash('Selecciona un rol válido.', 'warning')

    return render_template('Login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('login'))

# Ejemplo de ruta protegida para el administrador
@app.route('/admin/dashboard')
@login_required(rol='admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

# Ejemplo de ruta protegida para el egresado
@app.route('/egresado/perfil/<string:egresado_id>')
@login_required(rol='egresado')
def perfil_egresado(egresado_id):
    from routes.egresados_routes import mostrar_perfil_egresado 
    perfil = mostrar_perfil_egresado(egresado_id)
    if not perfil:
        flash('Perfil no encontrado.', 'warning')
        return redirect(url_for('login'))
    return render_template('alumno/perfil.html', egresado=perfil)


# Manejo de errores
@app.errorhandler(404)
def not_found(e):
    return "<h2>Página no encontrada</h2>", 404

@app.errorhandler(500)
def server_error(e):
    return "<h2>Error interno del servidor</h2>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
