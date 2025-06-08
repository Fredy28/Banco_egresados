from pymongo import MongoClient
from pymongo.errors import PyMongoError
from bson import ObjectId, json_util
import json
import os
import logging
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MongoDB")


class MongoDB:
    def __init__(self, collection_name):
        self.user = os.getenv('MONGO_USER', 'fredi')
        self.password = os.getenv('MONGO_PASSWORD', 'fredi1234')
        self.host = os.getenv('MONGO_HOST', '189.129.50.181')
        self.port = os.getenv('MONGO_PORT', '27017')
        self.auth_db = os.getenv('MONGO_AUTH_DB', 'admin')
        self.db_name = os.getenv('MONGO_DB_NAME', 'banco_egresados')
        self.collection_name = collection_name
        
        self.uri = (
            f"mongodb://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/"
            f"?authSource={self.auth_db}"
            "&authMechanism=SCRAM-SHA-256"
        )
        
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
            )
            
            self.client.fredi.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(f"Conectado exitosamente a la colección: {self.collection_name}")
        except PyMongoError as e:
            logger.error(f"Error de conexión a MongoDB: {str(e)}")
            raise

    def create(self, data):
        try:
            # SOLO deserializa si es string
            if isinstance(data, str):
                item = json.loads(data)
            else:
                item = data
            logger.info(f"Datos convertidos a dict: {item} ({type(item)})")
            result = self.collection.insert_one(item)
            logger.info(f"Insertado con ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error en create: {str(e)}")
            raise

    def read(self, id):
        try:
            obj_id = ObjectId(id)
            item = self.collection.find_one({"_id": obj_id})
            if item is None:
                return json.dumps({"error": "No encontrado"})
            item['_id'] = str(item['_id'])
            return json_util.dumps(item)
        except Exception as e:
            logger.error(f"Error completo en read: {traceback.format_exc()}")
            return json.dumps({"error": "Error interno del servidor"})

    def update(self, id, data):
        try:
            obj_id = ObjectId(id)
            update_data = json.loads(data)
            result = self.collection.update_one({"_id": obj_id}, {"$set": update_data})
            return json.dumps({
                "success": result.modified_count > 0,
                "matched": result.matched_count,
                "modified": result.modified_count
            })
        except Exception as e:
            logger.error(f"Error general en update: {str(e)}")
            raise

    def delete(self, id):
        try:
            obj_id = ObjectId(id)
            result = self.collection.delete_one({"_id": obj_id})
            return json.dumps({
                "success": result.deleted_count > 0,
                "deleted": result.deleted_count
            })
        except Exception as e:
            logger.error(f"Error en delete: {str(e)}")
            raise

    def list_all(self):
        try:
            items = list(self.collection.find({}))
            for item in items:
                item['_id'] = str(item['_id'])
            return json.dumps(items)
        except Exception as e:
            logger.error(f"Error en list_all: {str(e)}")
            return json.dumps([])


# Clases específicas para cada colección
class MongoDBEgresados(MongoDB):
    def __init__(self):
        super().__init__('egresados')


class MongoDBEmpresas(MongoDB):
    def __init__(self):
        super().__init__('empresas')
           
    def delete_vacante(self, empresa_id, vacante_id):
        result = self.collection.update_one(
            {"_id": ObjectId(empresa_id)},
            {"$pull": {"vacantes": {"id": int(vacante_id)}}}
        )
        return result.modified_count > 0


class MongoDBUsuarios(MongoDB):
    def __init__(self):
        super().__init__("usuarios")

    def register(self, data):
        usuario = {
            "correo": data.get("correo"),
            "password": data.get("password"), 
            "rol": data.get("rol")
        }
        result = self.collection.insert_one(usuario)
        return str(result.inserted_id)

    def login(self, email, password):
        try:
            user = self.collection.find_one({"email": email, "password": password})
            if user:
                user["_id"] = str(user["_id"])
                return json.dumps(user)
            return json.dumps({"error": "Credenciales inválidas"})
        except Exception as e:
            return json.dumps({"error": str(e)})

    def get_user_by_id(self, id):
        return self.read(id)
