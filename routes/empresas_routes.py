# /empresas_routes.py
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

empresas_bp = Blueprint('empresas', __name__)

# Configurar cliente CORBA
try:
    client = CORBAClient()
    print("✅ CORBA Client connected successfully")
except CORBAConnectionError as e:
    print(f"❌ Critical CORBA error: {str(e)}")
    exit(1)

@empresas_bp.route('/')
def index():
    try:
        empresas = client.list_all_empresas()
        egresados = client.egresados.list_all()
        # Si quieres mostrar ambos en dashboard, pásalos juntos:
        return render_template('admin/dashboard.html', empresas=empresas, egresados=egresados)
    except CORBAOperationError as e:
        flash(f'Error retrieving empresa: {str(e)}', 'danger')
        return render_template('admin/dashboard.html', empresas=[], egresados=[])
    
@empresas_bp.route('/editar_empresa/<string:empresa_id>')
def editar_empresa(empresa_id):
    empresa = client.read_empresa(empresa_id) 
    return render_template('empresa/editar_empresa.html', empresa=empresa)

@empresas_bp.route('/nueva_empresa', methods=['GET'])
def nueva_empresa():
    return render_template('empresa/añadir_empresa.html')

@empresas_bp.route('/create', methods=['POST'])
def create():
    if request.method == 'POST':
        try:
            empresa_data = {
                "nombre": request.form.get('nombre'),
                "vacantes_disponibles": int(request.form.get('vacantes_disponibles')),
                "ubicacion": request.form.get('ubicacion'),
                "sector": request.form.get('sector'),
                "descripcion": request.form.get('descripcion'),
                "especialidades": request.form.get('especialidades'),
                "contacto": request.form.get('contacto'),
                "vacantes": []
            }

            vacantes_json = request.form.get('vacantes_json')
            if vacantes_json:
                vacantes = json.loads(vacantes_json)
                empresa_data["vacantes"] = vacantes
            else:
                empresa_data["vacantes"] = []

            new_empresaid = client.create_empresa(empresa_data)
            flash(f'Empresa creada correctamente con ID: {new_empresaid}', 'success')
        except CORBAOperationError as e:
            flash(f'Error en creación: {str(e)}', 'danger')
        except KeyError as e:
            flash(f'Campo faltante: {str(e)}', 'warning')
    return redirect(url_for('empresas.index'))



@empresas_bp.route('/empresa/<string:empresa_id>')
def read_empresa(empresa_id):
    try:
        empresa = client.read_empresa(empresa_id)
        return render_template('/empresa/empresa.html', empresa=empresa)
    except CORBAOperationError as e:
        flash(f'Error al obtener el empresa: {str(e)}', 'danger')
        return redirect(url_for('empresas.index'))

@empresas_bp.route('/empresa/update/<string:empresa_id>', methods=['POST'])
def update_empresa(empresa_id):
    if request.method == 'POST':
        try:
            empresa_actual = client.read_empresa(empresa_id)
            if not empresa_actual:
                flash('Error: La empresa no existe en la base de vacante.', 'danger')
                return redirect(url_for('empresas.index'))

            update_data = {
                "nombre": request.form.get('nombre'),
                "vacantes_disponibles": int(request.form.get('vacantes_disponibles')),
                "ubicacion": request.form.get('ubicacion'),
                "sector": request.form.get('sector'),
                "descripcion": request.form.get('descripcion'),
                "especialidades": request.form.get('especialidades'),
                "contacto": request.form.get('contacto'),
                "vacantes": []
            }

            # Vacantes actualizadas
            vacantes_json = request.form.get('vacantes_json')
            if vacantes_json:
                vacantes = json.loads(vacantes_json)
                update_data["vacantes"] = vacantes

            success = client.update_empresa(empresa_id, update_data)
            if success:
                flash('¡Actualización exitosa!', 'success')
            else:
                flash('Sin cambios', 'warning')

        except CORBAOperationError as e:
            flash(f'Error en actualización: {str(e)}', 'danger')

    return redirect(url_for('empresas.read_empresa', empresa_id=empresa_id))


@empresas_bp.route('/delete/<empresa_id>', methods=['POST'])
def delete(empresa_id):
    try:
        success = client.delete_empresa(empresa_id)
        if success:
            flash('empresa deleted successfully!', 'success')
        else:
            flash('Delete failed: empresa not found', 'warning')
    except CORBAOperationError as e:
        flash(f'Delete error: {str(e)}', 'danger')
    return redirect(url_for('egresados.index'))

# Listar vacantes de una empresa
@empresas_bp.route('/<empresa_id>/vacantes')
def listar_vacantes(empresa_id):
    vacantes = corba_client.vacantes.list_by_empresa(empresa_id)
    return render_template('alumnos/vacantes.html', vacantes=vacantes, empresa_id=empresa_id)

# Crear vacante
@empresas_bp.route('/<empresa_id>/vacantes/crear', methods=['GET', 'POST'])
def crear_vacante(empresa_id):
    if request.method == 'POST':
        vacante = request.form.to_dict()
        vacante['empresa_id'] = empresa_id  # asegurar que la vacante se asocia a la empresa
        try:
            corba_client.vacantes.create(json.dumps(vacante))
            flash("Vacante creada exitosamente", "success")
            return redirect(url_for('empresas.listar_vacantes', empresa_id=empresa_id))
        except Exception as e:
            flash(f"Error al crear la vacante: {str(e)}", "danger")
    return render_template('empresa/añadir_vacante.html', empresa_id=empresa_id)

# Editar vacante
@empresas_bp.route('/<empresa_id>/vacantes/editar/<vacante_id>', methods=['GET', 'POST'])
def editar_vacante(empresa_id, vacante_id):
    if request.method == 'POST':
        vacante = request.form.to_dict()
        try:
            corba_client.vacantes.update(vacante_id, json.dumps(vacante))
            flash("Vacante actualizada exitosamente", "success")
            return redirect(url_for('empresas.listar_vacantes', empresa_id=empresa_id))
        except Exception as e:
            flash(f"Error al actualizar la vacante: {str(e)}", "danger")
    else:
        vacante = corba_client.vacantes.read(vacante_id)
        return render_template('empresa/editar_vacante.html', vacante=vacante, empresa_id=empresa_id)

# Eliminar vacante
@empresas_bp.route('/<empresa_id>/vacantes/eliminar/<vacante_id>', methods=['POST'])
def eliminar_vacante(empresa_id, vacante_id):
    try:
        corba_client.vacantes.delete(vacante_id)
        flash("Vacante eliminada exitosamente", "success")
    except Exception as e:
        flash(f"Error al eliminar la vacante: {str(e)}", "danger")
    return redirect(url_for('empresas.listar_vacantes', empresa_id=empresa_id))


@empresas_bp.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@empresas_bp.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500