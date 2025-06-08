import os
import sys

from omniORB import CORBA
from database import MongoDBEgresados
from database import MongoDBEmpresas
from database import MongoDBUsuarios
#sys.path.append(os.path.abspath("./idl/crud_idl"))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../idl')))
#sys.path.append(os.path.join(os.path.dirname(__file__), 'idl'))

import crudbanco_idl
from crudbanco_idl import _0_CrudApp as CrudApp
from crudbanco_idl import _0_CrudApp__POA as CrudApp__POA


class EgresadosServant(CrudApp__POA.Egresados):
    def __init__(self):
        self.db = MongoDBEgresados()

    def create(self, data): return self.db.create(data)
    def read(self, id): return self.db.read(id)
    def update(self, id, data): return self.db.update(id, data)
    def delete(self, id): return self.db.delete(id)
    def list_all(self): return self.db.list_all()

class EmpresasServant(CrudApp__POA.Empresas):
    def __init__(self):
        self.db = MongoDBEmpresas()

    def create(self, data): return self.db.create(data)
    def read(self, id): return self.db.read(id)
    def update(self, id, data): return self.db.update(id, data)
    def delete(self, id): return self.db.delete(id)
    def list_all(self): return self.db.list_all()

class UsuariosServant(CrudApp__POA.Usuarios):
    def __init__(self):
        self.db = MongoDBUsuarios()

    def register(self, data): return self.db.register(data)
    def login(self, email, password): return self.db.login(email, password)
    def get_user_by_id(self, id): return self.db.get_user_by_id(id)
        
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
poa = orb.resolve_initial_references("RootPOA")
poaManager = poa._get_the_POAManager()
poaManager.activate()

# Crear servants
egresados_servant = EgresadosServant()
empresas_servant = EmpresasServant()
usuarios_servant = UsuariosServant()

# Activar objetos CORBA
egresados_obj = egresados_servant._this()
empresas_obj = empresas_servant._this()
usuarios_obj = usuarios_servant._this()

with open("ior_egresados.txt", "w") as f:
    f.write(orb.object_to_string(egresados_obj))

with open("ior_empresas.txt", "w") as f:
    f.write(orb.object_to_string(empresas_obj))

with open("ior_usuarios.txt", "w") as f:
    f.write(orb.object_to_string(usuarios_obj))


print("Servidor CORBA listo con interfaces: Egresados, Empresas y Usuarios")
orb.run()
