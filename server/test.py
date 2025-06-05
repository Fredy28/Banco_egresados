from pymongo import MongoClient

client = MongoClient("mongodb://fredi:fredi1234@189.129.50.181:27017/?authSource=admin&authMechanism=SCRAM-SHA-256", tlsInsecure=True)
db = client['banco_egresados']
collection = db['egresados']

# Inserta un egresado de prueba
egresado = {
    "nombre": "Juan Pérez",
    "contacto": "Ingeniería",
    "titulo": "No"
}

result = collection.insert_one(egresado)
print("ID insertado:", result.inserted_id)

# Verifica que se haya insertado
for doc in collection.find():
    print(doc)
