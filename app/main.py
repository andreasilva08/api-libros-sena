import logging
import json
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.exceptions import ErrorAplicacion
from app.core.limiter import limiter

# Importar los routers bajo el estándar /api/v1 requerido
from app.routes.health import router as health_router
from app.routes.autores import router as autores_router
from app.routes.categorias import router as categorias_router
from app.routes.libros import router as libros_router
from app.routes.socios import router as socios_router
from app.routes.prestamos import router as prestamos_router
from app.routes.reportes import router as reportes_router
from app.routes import auth
from app.routes.usuarios import router as usuarios_router

# ⚠️ NOTA: Ya no va 'Base.metadata.create_all' aquí. 
# Las tablas se gestionan y aplican exclusivamente con Alembic.

# Crear la aplicación
app = FastAPI(
    title="API de Biblioteca Segura - Sistema Modular",
    version="2.0.0",
    description="API desarrollada con FastAPI, SQLAlchemy, Alembic y PostgreSQL."
)
settings = get_settings()
logger = logging.getLogger("app.request")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

app.state.limiter = limiter
async def rate_limit_exception_handler(
    _request: Request,
    _exc: RateLimitExceeded,
) -> JSONResponse:
    _ = (_request, _exc)
    return JSONResponse(
        status_code=429,
        content={"detail": "Límite de solicitudes excedido"},
    )


app.add_exception_handler(RateLimitExceeded, rate_limit_exception_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_and_logging(request: Request, call_next):
    request_id = str(uuid4())
    request.state.request_id = request_id
    started_at = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        logger.info(
            json.dumps(
                {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                },
                ensure_ascii=False,
            )
        )

# Registrar los routers con el prefijo obligatorio /api/v1
app.include_router(health_router, prefix="/api/v1")
app.include_router(autores_router, prefix="/api/v1")
app.include_router(categorias_router, prefix="/api/v1")
app.include_router(libros_router, prefix="/api/v1")
app.include_router(socios_router, prefix="/api/v1")
app.include_router(prestamos_router, prefix="/api/v1")
app.include_router(reportes_router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(usuarios_router, prefix="/api/v1")

# Manejar errores personalizados
@app.exception_handler(ErrorAplicacion)
async def custom_exception_handler(
    request: Request,
    exc: ErrorAplicacion,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={
            **(exc.headers or {}),
            "X-Request-ID": getattr(request.state, "request_id", ""),
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    _exc: Exception,
):
    _ = _exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
        headers={
            "X-Request-ID": getattr(request.state, "request_id", ""),
        },
    )

# Ruta principal de bienvenida
@app.get("/")
def read_root():
    return {
        "mensaje": "API de Biblioteca funcionando correctamente (Taller 2)",
        "base_datos": "PostgreSQL",
        "documentacion": "/docs"
    }