from fastapi import HTTPException

class ErrorAplicacion(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class NoEncontrado(ErrorAplicacion):
    def __init__(self, detail: str = "El recurso no existe"):
        super().__init__(status_code=404, detail=detail)

class Conflicto(ErrorAplicacion):
    def __init__(self, detail: str = "Conflicto con los datos existentes"):
        super().__init__(status_code=409, detail=detail)

class ReglaNegocio(ErrorAplicacion):
    def __init__(self, detail: str = "Una regla de la biblioteca no se cumple"):
        super().__init__(status_code=422, detail=detail)


class NoAutenticado(ErrorAplicacion):
    def __init__(self, detail: str = "No se pudo validar la autenticación"):
        super().__init__(
            status_code=401,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class Prohibido(ErrorAplicacion):
    def __init__(self, detail: str = "No tienes permiso para esta operación"):
        super().__init__(status_code=403, detail=detail)


class CuentaBloqueada(ErrorAplicacion):
    def __init__(self, detail: str = "La cuenta está bloqueada temporalmente"):
        super().__init__(status_code=423, detail=detail)