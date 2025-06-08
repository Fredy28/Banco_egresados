# corba_client.py adaptado para múltiples IORs
import json
import os
import sys
import logging

from omniORB import CORBA

# Rutas IDL
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../idl')))
import crudbanco_idl
from crudbanco_idl import _0_CrudApp as CrudApp

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CORBA-Client")

class CORBAConnectionError(Exception):
    pass

class CORBAOperationError(Exception):
    pass

class CORBAClient:
    def __init__(self):
        self.orb = CORBA.ORB_init([], CORBA.ORB_ID)
        self.egresados = self._connect_service('egresados', CrudApp.Egresados)
        self.empresas = self._connect_service('empresas', CrudApp.Empresas)
        self.usuarios = self._connect_service('usuarios', CrudApp.Usuarios)

    def _get_ior(self, name):
        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../server'))
            path = os.path.join(base_dir, f'ior_{name}.txt')
            with open(path, 'r') as f:
                ior = f.read().strip()
            if not ior:
                raise ValueError("IOR vacío")
            logger.info(f"IOR para {name} leído correctamente")
            return ior
        except Exception as e:
            raise CORBAConnectionError(f"IOR {name} error: {e}")

    def _connect_service(self, name, interface):
        try:
            ior = self._get_ior(name)
            obj = self.orb.string_to_object(ior)
            narrowed = obj._narrow(interface)
            if narrowed is None:
                raise CORBAConnectionError(f"Referencia inválida: {name}")
            narrowed._non_existent()  # test
            logger.info(f"Conectado a servicio {name}")
            return narrowed
        except Exception as e:
            raise CORBAConnectionError(f"Error conectando a {name}: {e}")

    def create(self, data):
        return self.egresados.create(json.dumps(data))

    def read(self, id):
        return json.loads(self.egresados.read(id))

    def update(self, id, data):
        return json.loads(self.egresados.update(id, json.dumps(data)))['success']

    def delete(self, id):
        return json.loads(self.egresados.delete(id))['success']

    def list_all(self) -> list:
        try:
            result = self.egresados.list_all()
            return json.loads(result)  # ← esto debe dar una lista de dicts
        except Exception as e:
            raise CORBAOperationError(f"List error: {e}")


if __name__ == '__main__':
    try:
        client = CORBAClient()
        print("Conexiones exitosas")
        print("Egresados:", client.list_all())
    except Exception as e:
        print("Error:", e)
