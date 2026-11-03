import re
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)

from app.models.usuario import RolUsuario


def validar_password(password: str) -> str:
    if not re.search(r"[A-Z]", password):
        raise ValueError("La contraseña debe incluir al menos una mayúscula")
    if not re.search(r"[a-z]", password):
        raise ValueError("La contraseña debe incluir al menos una minúscula")
    if not re.search(r"\d", password):
        raise ValueError("La contraseña debe incluir al menos un número")
    return password


class UsuarioRegistro(BaseModel):
    email: EmailStr = Field(max_length=100)
    nombre: str = Field(min_length=3, max_length=100)
    telefono: str | None = Field(
        default=None,
        max_length=20,
        pattern=r"^[0-9\s+]{7,15}$",
    )
    password: str = Field(min_length=8, max_length=64)
    confirmar_password: str

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
    def validar_confirmacion(self) -> "UsuarioRegistro":
        if self.password != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    nombre: str
    rol: RolUsuario
    activo: bool
    socio_id: int | None
    creado_en: datetime


class UsuarioAdminCreate(BaseModel):
    email: EmailStr = Field(max_length=100)
    nombre: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=64)
    rol: RolUsuario
    socio_id: int | None = None

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


class UsuarioRolActualizar(BaseModel):
    rol: RolUsuario


class UsuarioActivoActualizar(BaseModel):
    activo: bool