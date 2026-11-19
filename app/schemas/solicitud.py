from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.schemas.usuario import validar_password


class SolicitudCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=3, max_length=100)
    email: EmailStr = Field(max_length=100)
    telefono: str | None = Field(
        default=None,
        max_length=20,
        pattern=r"^[0-9\s+]{7,15}$",
    )
    password: str = Field(min_length=8, max_length=64)
    confirm_password: str = Field(min_length=8, max_length=64)

    @field_validator("email", mode="after")
    @classmethod
    def normalizar_email(cls, email: EmailStr) -> str:
        return str(email).strip().lower()

    @field_validator("nombre", mode="before")
    @classmethod
    def normalizar_nombre(cls, nombre: str) -> str:
        if isinstance(nombre, str):
            return " ".join(nombre.split())
        return nombre

    @field_validator("password")
    @classmethod
    def validar_password_fuerte(cls, password: str) -> str:
        return validar_password(password)

    @model_validator(mode="after")
    def validar_confirmacion(self) -> "SolicitudCreate":
        if self.password != self.confirm_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class SolicitudOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    estado: str
    motivo_rechazo: str | None
    creado_en: datetime
    revisado_en: datetime | None
    revisado_por_id: int | None


class SolicitudRechazoIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    motivo_rechazo: str | None = Field(default=None, max_length=500)

    @field_validator("motivo_rechazo")
    @classmethod
    def normalizar_motivo(cls, motivo: str | None) -> str | None:
        if motivo is None:
            return None
        motivo = motivo.strip()
        return motivo or None
