# web-app/app.py
import os
import sys
import json
from flask import Blueprint, request, render_template, redirect, url_for, flash, Flask
# Añadir rutas para los módulos generados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../client')))
from client.corba_client import CORBAClient, CORBAConnectionError, CORBAOperationError

# Configurar rutas
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(BASE_DIR, '..'))

egresados_bp = Blueprint('egresados', __name__)

# Configurar cliente CORBA
try:
    client = CORBAClient()
    print("✅ CORBA Client connected successfully")
except CORBAConnectionError as e:
    print(f"❌ Critical CORBA error: {str(e)}")
    exit(1)

@egresados_bp.route('/')
def index():
    print("🟢 Entrando a la vista index() de egresados")
    try:
        egresados = client.list_all()
        print("📋 Egresados:", egresados)
        empresas = client.empresas.list_all()
        print("🏢 Empresas:", empresas)
        return render_template('admin/dashboard.html', egresados=egresados, empresas=empresas)
    except CORBAOperationError as e:
        print(f"❌ Error CORBA: {e}")
        flash(f'Error al obtener registros: {str(e)}', 'danger')
        return render_template('admin/dashboard.html', egresados=[], empresas=[])



    
@egresados_bp.route('/editar_perfil/<string:egresado_id>')
def editar_perfil(egresado_id):
    egresado = client.read(egresado_id) 
    return render_template('alumno/editar_perfil.html', egresado=egresado)

@egresados_bp.route('/nuevo_perfil', methods=['GET'])
def nuevo_perfil():
    return render_template('alumno/añadir_perfil.html')

@egresados_bp.route('/editar/<string:egresado_id>')
def editar_egresado(egresado_id):
    egresado = client.read(egresado_id)
    return render_template('alumno/editar_perfil.html', egresado=egresado)


@egresados_bp.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        try:
            egresado_data = {
                "nombre": request.form.get("nombre"),
                "sexo": request.form.get("sexo"),
                "foto": request.form.get("foto"),
                "nacimiento": request.form.get("nacimiento"),
                "licenciatura": request.form.get("licenciatura"),
                "maestria": request.form.get("maestria"),
                "titulo": request.form.get("titulo"),
                "certificados": request.form.get("certificados"),
                "nivel_ingles": request.form.get("nivel_ingles"),
                "descripcion": request.form.get("descripcion"),
                "contacto": request.form.get("contacto"),
                "password": request.form.get("password"),
            }

            print("📥 Datos recibidos:", egresado_data)
            new_egresadoid = client.create(egresado_data)
            print("✅ ID creado:", new_egresadoid)
            flash(f'egresado creado con ID: {new_egresadoid}', 'success')
        except KeyError as e:
            print(f"⚠️ Campo faltante: {e}")
            flash(f'Campo faltante: {e}', 'warning')
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            flash(f'Error inesperado: {e}', 'danger')
    return redirect(url_for('egresados.index'))


@egresados_bp.route('/egresado/<string:egresado_id>')
def read_egresado(egresado_id):
    try:
        egresado = client.read(egresado_id)
        return render_template('/alumno/perfil.html', egresado=egresado)
    except CORBAOperationError as e:
        flash(f'Error al obtener el egresado: {str(e)}', 'danger')
        return redirect(url_for('egresados.index'))

@egresados_bp.route('/egresado/update/<string:egresado_id>', methods=['POST'])
def update_egresado(egresado_id):
    if request.method == 'POST':
        try:
            egresado_actual = client.read(egresado_id) 
            if not egresado_actual:
                flash('Error: El egresado no existe en la base de datos.', 'danger')
                return redirect(url_for('egresados.index'))

            print(f"📌 egresado encontrado: {egresado_actual}")

            update_data = {
                "nombre": request.form.get("nombre"),
                "sexo": request.form.get("sexo"),
                "foto": request.form.get("foto"),
                "nacimiento": request.form.get("nacimiento"),
                "licenciatura": request.form.get("licenciatura"),
                "maestria": request.form.get("maestria"),
                "titulo": request.form.get("titulo"),
                "certificados": request.form.get("certificados"),
                "nivel_ingles": request.form.get("nivel_ingles"),
                "descripcion": request.form.get("descripcion"),
                "contacto": request.form.get("contacto"),
                "password": request.form.get("password"),
            }

            success = client.update(egresado_id, update_data)

            if success:
                flash('¡Actualización exitosa!', 'success')
            else:
                flash('Sin cambios', 'warning')

        except CORBAOperationError as e:
            flash(f'Error de actualización: {str(e)}', 'danger')

    return redirect(url_for('egresados.read_egresado', egresado_id=egresado_id))


@egresados_bp.route('/delete/<egresado_id>', methods=['POST'])
def delete(egresado_id):
    try:
        success = client.delete(egresado_id)
        if success:
            flash('egresado deleted successfully!', 'success')
        else:
            flash('Delete failed: egresado not found', 'warning')
    except CORBAOperationError as e:
        flash(f'Delete error: {str(e)}', 'danger')
    return redirect(url_for('egresados.index'))

@egresados_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@egresados_bp.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    egresados_bp.run(host='0.0.0.0', port=5000, debug=True)