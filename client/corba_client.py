# corba-client/client.py
import json
import os
import sys
import logging

from omniORB import CORBA

# Añadir rutas para los módulos generados
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../idl')))
import crudbanco_idl # Importar módulo generado
from crudbanco_idl import _0_CrudApp as CrudApp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CORBA-Client")

class CORBAConnectionError(Exception):
    """Excepción para errores de conexión CORBA"""
    pass

class CORBAOperationError(Exception):
    """Excepción para errores en operaciones CRUD"""
    pass

class CORBAClient:
    def __init__(self):
        self.orb = None
        self.db = None
        self._connect()

    def _get_ior(self):
        """Obtiene el IOR desde el archivo ior.txt"""
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            ior_path = os.path.join(base_dir, 'server', 'ior.txt')
            
            with open(ior_path, 'r') as f:
                ior = f.read().strip()
                
            if not ior:
                raise ValueError("IOR vacío en el archivo")
                
            logger.info("IOR leído correctamente")
            return ior
            
        except FileNotFoundError:
            raise CORBAConnectionError("Archivo ior.txt no encontrado")
        except Exception as e:
            raise CORBAConnectionError(f"Error leyendo IOR: {str(e)}")

    def _connect(self):
        """Establece la conexión CORBA"""
        try:
            ior = self._get_ior()
            self.orb = CORBA.ORB_init([], CORBA.ORB_ID)
            obj = self.orb.string_to_object(ior)
            self.db = obj._narrow(CrudApp.Egresados)

            self.egresados = obj._narrow(CrudApp.Egresados)
            self.empresas = obj._narrow(CrudApp.Empresas)
            self.usuarios = obj._narrow(CrudApp.Usuarios)
            
            if self.db is None:
                raise CORBAConnectionError("Referencia CORBA inválida")
                
            # Test de conexión
            self.db._non_existent()
            logger.info("Conexión CORBA establecida correctamente")
            
        except CORBA.TRANSIENT as e:
            raise CORBAConnectionError(f"Error transitorio: {e}")
        except CORBA.Exception as e:
            raise CORBAConnectionError(f"Error CORBA: {e}")
        except Exception as e:
            raise CORBAConnectionError(f"Error de conexión: {e}")

    def create(self, data: dict) -> str:
        try:
            json_data = json.dumps(data)
            result = self.db.create(json_data)
            return result
        except CORBA.Exception as e:
            raise CORBAOperationError(f"Create error: {e}")

    def read(self, item_id: str) -> dict:
        try:
            result = self.db.read(item_id)
            logger.debug(f"Respuesta cruda de read: {result}")
            
            # Verificar si es un JSON válido
            if not result.startswith("{"):
                raise CORBAOperationError("Respuesta inválida del servidor")
                
            data = json.loads(result)
            
            if 'error' in data:
                raise CORBAOperationError(data['error'])
                
            return data
            
        except CORBA.Exception as e:
            # Obtener detalles del error CORBA de forma segura
            error_details = {
                "name": e._name if hasattr(e, '_name') else 'Unknown',
                "reason": str(e),
                "code": e._major if hasattr(e, '_major') else -1
            }
            logger.error(f"Error CORBA: {json.dumps(error_details)}")
            raise CORBAOperationError(f"Error de comunicación: {error_details['reason']}")
            
        except CORBA.Exception as e:
            error_msg = f"Read error: {e._repr_()}"
            logger.error(error_msg)
            raise CORBAOperationError("Error de comunicación con el servidor")

    def update(self, item_id: str, data: dict) -> bool:
        try:
            json_data = json.dumps(data)
            result = self.db.update(item_id, json_data)
            return json.loads(result)["success"]
        except CORBA.Exception as e:
            raise CORBAOperationError(f"Update error: {e}")

    def delete(self, item_id: str) -> bool:
        try:
            result = self.db.delete(item_id)
            return json.loads(result)["success"]
        except CORBA.Exception as e:
            raise CORBAOperationError(f"Delete error: {e}")

    def list_all(self) -> list:
        try:
            result = self.db.list_all()
            return json.loads(result)
        except CORBA.Exception as e:
            error_msg = f"List error: {e._name}"
            if "BAD_PARAM" in error_msg:
                error_msg += " (Verifique los tipos de datos en la respuesta)"
            raise CORBAOperationError(error_msg)
        except json.JSONDecodeError as e:
            raise CORBAOperationError(f"Error decodificando JSON: {str(e)}")
        except Exception as e:
            raise CORBAOperationError(f"Error inesperado: {str(e)}")

if __name__ == "__main__":
    try:
        client = CORBAClient()
        print("Test de conexión exitoso!")
        print("Frutas:", client.list_all())
    except CORBAConnectionError as e:
        print(f"Error de conexión: {e}")
    except CORBAOperationError as e:
        print(f"Error de operación: {e}")