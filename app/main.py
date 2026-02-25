from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from . import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Venta de Entradas")

# DEPENDENCIA DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ROOT
@app.get("/")
def root():
    return {"mensaje": "API de venta de entradas funcionando correctamente"}


# RECINTOS 
@app.post("/recintos/", response_model=schemas.RecintoResponse)
def crear_recinto(recinto: schemas.RecintoCreate, db: Session = Depends(get_db)):
    nuevo = models.Recinto(**recinto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/recintos/", response_model=list[schemas.RecintoResponse])
def listar_recintos(db: Session = Depends(get_db)):
    return db.query(models.Recinto).all()


@app.put("/recintos/{id}", response_model=schemas.RecintoResponse)
def actualizar_recinto(id: int, recinto: schemas.RecintoCreate, db: Session = Depends(get_db)):
    db_recinto = db.query(models.Recinto).get(id)

    if not db_recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    for key, value in recinto.model_dump().items():
        setattr(db_recinto, key, value)

    db.commit()
    db.refresh(db_recinto)
    return db_recinto


@app.delete("/recintos/{id}")
def eliminar_recinto(id: int, db: Session = Depends(get_db)):
    recinto = db.query(models.Recinto).get(id)

    if not recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    db.delete(recinto)
    db.commit()
    return {"mensaje": "Recinto eliminado correctamente"}


# EVENTOS

@app.post("/eventos/", response_model=schemas.EventoResponse)
def crear_evento(evento: schemas.EventoCreate, db: Session = Depends(get_db)):

    if evento.precio < 0:
        raise HTTPException(status_code=400, detail="El precio no puede ser negativo")

    recinto = db.query(models.Recinto).get(evento.recinto_id)
    if not recinto:
        raise HTTPException(status_code=404, detail="Recinto no encontrado")

    nuevo = models.Evento(**evento.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/eventos/", response_model=list[schemas.EventoResponse])
def listar_eventos(ciudad: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Evento).join(models.Recinto)
    if ciudad:
        query = query.filter(models.Recinto.ciudad.ilike(f"%{ciudad}%"))
    return query.all()

@app.patch("/eventos/{id}/comprar")
def comprar_tickets(id: int, compra: schemas.CompraRequest, db: Session = Depends(get_db)):

    evento = db.query(models.Evento).get(id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")

    recinto = evento.recinto
    if evento.tickets_vendidos + compra.cantidad > recinto.capacidad:
        raise HTTPException(status_code=400,detail="Aforo insuficiente en el recinto")

    evento.tickets_vendidos += compra.cantidad
    db.commit()
    return {"mensaje": "Compra realizada correctamente"}