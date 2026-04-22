from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SMAT Persistente")

class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str
class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float

@app.post("/estaciones/", status_code=201)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre,
    ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msj": "Estacion guardada en DB", "data": nueva_estacion}

@app.post("/lecturas/", status_code=201)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estacion no existe")

    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)   
    db.commit()
    return {"status": "Lectura guardada en DB"}

@app.get("/estaciones/")
def listar_estaciones(db: Session = Depends(get_db)):
    return db.query(models.EstacionDB).all()


@app.get("/estaciones/{id}/historial")
async def obtener_historial(id: int, db: Session = Depends(get_db)):
    estacion_real = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).first()
    if not estacion_real:
        raise HTTPException(status_code=404, detail="Estacion no encontrada")
    
    lecturas_filtro = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()
    
    valores = [l.valor for l in lecturas_filtro]
    
    if len(valores) > 0:
        promedio = sum(valores)/len(valores)
    else:
        promedio = 0.0
    
    return {
        "estacion_id": id,
        "lecturas": lecturas_filtro,
        "conteo": len(lecturas_filtro),
        "promedio": promedio
    }  