# routes/usuarios_routes.py

from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from client import corba_client

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        try:
            respuesta = corba_client.usuarios.login(correo, password)
            if respuesta != "error":
                session['usuario_id'] = respuesta
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for('home'))
            else:
                flash("Correo o contraseña incorrectos", "danger")
        except Exception as e:
            flash(f"Error en login: {str(e)}", "danger")
    return render_template('usuarios/login.html')

@usuarios_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        datos = request.form.to_dict()
        try:
            corba_client.usuarios.register(datos)
            flash("Usuario registrado", "success")
            return redirect(url_for('usuarios.login'))
        except Exception as e:
            flash(f"Error al registrar: {str(e)}", "danger")
    return render_template('usuarios/registrar.html')

@usuarios_bp.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash("Sesión cerrada", "info")
    return redirect(url_for('usuarios.login'))
