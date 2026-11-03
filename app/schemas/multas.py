from pydantic import BaseModel

from app.schemas.prestamo import PrestamoResponse


class SocioMultasResponse(BaseModel):
    items: list[PrestamoResponse]
    total_adeudado: float
    skip: int
    limit: int
