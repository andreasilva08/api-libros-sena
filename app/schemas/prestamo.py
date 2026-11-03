from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from app.schemas.libro import LibroResponse
from app.schemas.socio import SocioResponse

class PrestamoBase(BaseModel):
    libro_id: int
    socio_id: int
    fecha_prestamo: Optional[date] = None
    dias: Optional[int] = Field(14, ge=1, le=30)

class PrestamoCreate(PrestamoBase):
    pass

class DevolucionCreate(BaseModel):
    fecha_devolucion: Optional[date] = None

class PrestamoResponse(BaseModel):
    id: int
    libro_id: int
    socio_id: int
    fecha_prestamo: date
    fecha_limite: date
    fecha_devolucion: Optional[date] = None
    multa: float
    libro: Optional[LibroResponse] = None
    socio: Optional[SocioResponse] = None

    class Config:
        from_attributes = True