from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.testclient import TestClient
from typing import List, Any
import json

app = FastAPI()

def load_data_from_json(file_path: str) -> List[dict]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []
    
file_path = "data_collected.json"
data = load_data_from_json(file_path)

#  Authorization and authentication system
security = HTTPBasic()

# Function to verify credentials
def verificar_credenciales(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "user"
    correct_password = "password"
    if credentials.username != correct_username or credentials.password != correct_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True

# Endpoint to get all data
@app.get("/data", response_model=List[Any])
async def obtener_datos(credentials: bool = Depends(verificar_credenciales)):
    return data

# Endpoint to get data by ID_process
@app.get("/data/{id_process}", response_model=Any)
async def obtener_dato(id_process: int, credentials: bool = Depends(verificar_credenciales)):
    for d in data:
        if d["Número de proceso"] == str(id_process):
            return d
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dato no encontrado")

#Endpoint to get data by Actor/Ofendido document or Demandado/Procesado document
@app.get("/data/document/{document}", response_model=List[Any])
async def obtener_dato(document: str, credentials: bool = Depends(verificar_credenciales)):
    all_data = []
    for d in data:
        actor_ofendido = d.get("Cédula/RUC/Pasaporte del Actor/Ofendido", None)
        demandado_procesado = d.get("Cédula/RUC/Pasaporte del Demandado/Procesado", None)
        if actor_ofendido == document or demandado_procesado == document:
            all_data.append(d)
    return all_data


# Test
client = TestClient(app)

def test_obtener_datos():
    response = client.get("/data")
    assert response.status_code == 200

def test_obtener_dato():
    response = client.get("/data/13284202406765")
    assert response.status_code == 200

