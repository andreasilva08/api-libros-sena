from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResenaIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calificacion: int = Field(ge=1, le=5)
    comentario: str | None = Field(default=None, max_length=2000)

    @field_validator("comentario")
    @classmethod
    def limpiar_comentario(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class ResenaResponse(BaseModel):
    id: int
    libro_id: int
    autor_nombre: str
    calificacion: int
    comentario: str | None
    creado_en: datetime
    actualizado_en: datetime
    es_mia: bool


class ResenasLibroResponse(BaseModel):
    items: list[ResenaResponse]
    promedio: float
    total: int
    mi_resena: ResenaResponse | None
    puede_opinar: bool
