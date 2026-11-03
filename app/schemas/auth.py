from pydantic import BaseModel, Field, field_validator, model_validator

from app.schemas.usuario import validar_password


class TokenRespuesta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshSolicitud(BaseModel):
    refresh_token: str


class CambioPassword(BaseModel):
    password_actual: str
    password_nueva: str = Field(min_length=8, max_length=64)
    confirmar_password: str

    @field_validator("password_nueva")
    @classmethod
    def validar_password_fuerte(cls, password: str) -> str:
        return validar_password(password)

    @model_validator(mode="after")
    def validar_confirmacion(self) -> "CambioPassword":
        if self.password_nueva != self.confirmar_password:
            raise ValueError("Las contraseñas no coinciden")
        return self
