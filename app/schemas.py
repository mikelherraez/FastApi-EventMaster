from pydantic import BaseModel, Field
from datetime import datetime

# RECINTO

class RecintoBase(BaseModel):
    nombre: str
    ciudad: str
    capacidad: int

class RecintoCreate(RecintoBase):
    pass

class RecintoResponse(RecintoBase):
    id: int

    class Config:
        from_attributes = True

# EVENTO

class EventoBase(BaseModel):
    nombre: str
    fecha: datetime
    precio: float = Field(..., ge=0)


class EventoCreate(EventoBase):
    recinto_id: int


class EventoResponse(EventoBase):
    id: int
    tickets_vendidos: int
    recinto_id: int

    class Config:
        from_attributes = True


class CompraRequest(BaseModel):
    cantidad: int
