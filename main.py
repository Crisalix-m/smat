from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
title="SMAT - Sistema de Monitoreo de Alerta Temprana",
description="""
API robusta para la gestión y monitoreo de desastres naturales.
Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.
**Entidades principales:**
* **Estaciones:** Puntos de monitoreo físico.
* **Lecturas:** Datos capturados por sensores.
* **Riesgos:** Análisis de criticidad basado en umbrales.
""",
version="1.0.0",
terms_of_service="http://unmsm.edu.pe/terms/",
contact={
"name": "Soporte Técnico SMAT - FISI",
"url": "http://fisi.unmsm.edu.pe",
"email": "desarrollo.smat@unmsm.edu.pe",
},
license_info={
"name": "Apache 2.0",
"url": "https://www.apache.org/licenses/LICENSE-2.0.html",
},
)

class EstacionCreate(BaseModel):
    id: int
    nombre: str
    ubicacion: str
class LecturaCreate(BaseModel):
    estacion_id: int
    valor: float

@app.post(
"/estaciones/",
status_code=201,
tags=["Gestión de Infraestructura"],
summary="Registrar una nueva estación de monitoreo",
description="Inserta una estación física (ej. río, volcán, zona sísmica) en la base de datos relacional."
)
def crear_estacion(estacion: EstacionCreate, db: Session = Depends(get_db)):
# ... (lógica implementada en Semanas 2 y 3)
    nueva_estacion = models.EstacionDB(id=estacion.id, nombre=estacion.nombre,
    ubicacion=estacion.ubicacion)
    db.add(nueva_estacion)
    db.commit()
    db.refresh(nueva_estacion)
    return {"msj": "Estacion guardada en DB", "data": nueva_estacion}

@app.post(
"/lecturas/",
status_code=201,
tags=["Telemetría de Sensores"],
summary="Recibir datos de telemetría",
description="""Recibe el valor capturado por un sensor y lo vincula a una estación existente mediante su 
ID."""
)
def registrar_lectura(lectura: LecturaCreate, db: Session = Depends(get_db)):
# ... (lógica implementada)
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == lectura.estacion_id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estacion no existe")

    nueva_lectura = models.LecturaDB(valor=lectura.valor, estacion_id=lectura.estacion_id)
    db.add(nueva_lectura)   
    db.commit()
    return {"status": "Lectura guardada en DB"}

@app.get(
"/estaciones/{id}/riesgo",
tags=["Análisis de Riesgo"],
summary="Evaluar nivel de peligro actual",
description="Analiza la última lectura recibida de una estación y determina si el estado es NORMAL,ALERTA o PELIGRO."
)
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
# ... (lógica implementada)
    return db.query(models.EstacionDB).all()


@app.get(
    "/estaciones/{id}/historial",
    tags=["Reportes Históricos"],
    summary="Obtener historial estadístico de una estación",
    description="""
    Recupera todas las lecturas registradas para una estación específica. 
    
    Realiza los siguientes cálculos:
    - **Conteo:** Cantidad total de registros asociados a la estación.
    - **Promedio:** Media aritmética de los valores de las lecturas.
    """,
    responses={
        200: {"description": "Historial obtenido exitosamente"},
        404: {"description": "Estación no encontrada o sin lecturas"}
    }
)
async def obtener_historial(id: int, db: Session = Depends(get_db)):
    # Nota: Aquí asumo que tu lógica está validando si hay lecturas 
    # para verificar la existencia.
    lecturas_filtro = db.query(models.LecturaDB).filter(models.LecturaDB.estacion_id == id).all()
    
    if not lecturas_filtro:
        raise HTTPException(status_code=404, detail="Estacion no encontrada o sin lecturas")
    
    valores = [l.valor for l in lecturas_filtro]
    
    # Como ya validamos que lecturas_filtro no está vacío, 
    # podemos calcular el promedio directamente:
    promedio = sum(valores) / len(valores)
    
    return {
        "estacion_id": id,
        "lecturas": lecturas_filtro,
        "conteo": len(lecturas_filtro),
        "promedio": promedio
    }

@app.get(
    "/estaciones/stats",
    tags=["Resumen Ejecutivo"],
    summary="Resumen general del sistema SMAT",
    description="""
    Proporciona un resumen ejecutivo del sistema de monitoreo.

    **Incluye:**
    - Total de estaciones registradas.
    - Total de lecturas almacenadas.
    - Promedio global de todas las lecturas.

    Este endpoint permite obtener una visión rápida del estado general
    del sistema y su volumen de datos.
    """,
    responses={
        404: {
            "description": "No hay datos disponibles en el sistema"
        }
    }
)
def obtener_stats(db: Session = Depends(get_db)):
    estaciones = db.query(models.EstacionDB).all()
    lecturas = db.query(models.LecturaDB).all()

    if not estaciones or not lecturas:
        raise HTTPException(status_code=404, detail="No hay datos suficientes")

    valores = [l.valor for l in lecturas]
    promedio_global = sum(valores) / len(valores)

    return {
        "total_estaciones": len(estaciones),
        "total_lecturas": len(lecturas),
        "promedio_global": promedio_global
    }