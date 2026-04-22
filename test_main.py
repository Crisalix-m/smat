from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_crear_estacion():
    response = client.post("/estaciones/", json={
        "id": 1,
        "nombre": "Estación Peru",
        "ubicacion": "Lima"
    })
    assert response.status_code==201
    assert response.json()["data"]["nombre"] == "Estación Peru"

def test_registrar_lectura():
    response = client.post("/lecturas/", json={
        "estacion_id": 1,
        "valor": 12.5
    })
    assert response.status_code == 201
    assert response.json()["status"] == "Lectura guardada en DB"
    
def test_riesgo_peligro():
    client.post("/estaciones/", json={"id": 10, "nombre": "Misti", "ubicacion": "Arequipa"})
    client.post("/lecturas/", json={"estacion_id": 10, "valor": 25.5})
    
    response = client.get("/estaciones/10/riesgo")
    assert response.status_code == 200
    assert response.json()["nivel"] == "PELIGRO"

def test_estacion_no_encontrada():
    response = client.get("/estaciones/999/riesgo")
    assert response.status_code == 404
    assert response.json()["detail"] == "Estacion no encontrada"

def test_historial_y_promedio():
        client.post("/estaciones/", json={"id": 30, "nombre": "Rio HGF", "ubicacion": "La PERO"})
        
        # 2. Registro de 3 lecturas: 10.0, 20.0, 30.0 (Promedio esperado = 20.0)
        client.post("/lecturas/", json={"estacion_id": 30, "valor": 30.0})
        client.post("/lecturas/", json={"estacion_id": 30, "valor": 30.0})
        client.post("/lecturas/", json={"estacion_id": 30, "valor": 30.0})
        
        # 3. Petición al nuevo endpoint
        response = client.get("/estaciones/30/historial")
        assert response.status_code == 200
        assert response.json()["conteo"] == 3
        assert response.json()["promedio"] == 30.0
