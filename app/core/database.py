from collections.abc import Generator

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from app.core.config import get_settings

# Obtenemos la configuración centralizada desde pydantic-settings
settings = get_settings()

# Convención de nombres requerida por Alembic para que funcionen los upgrades y downgrades
convencion = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Base declarativa moderna (SQLAlchemy 2.0) con la convención de nombres
class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convencion)

# Crea el motor de la base de datos usando la URL del entorno
engine = create_engine(settings.database_url, echo=False)

# Configura la sesión local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Dependencia para inyectar la sesión de base de datos en los endpoints de FastAPI
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def bloquear_email_registro(db: Session, email: str) -> None:
    if db.get_bind().dialect.name == "postgresql":
        db.execute(
            text(
                "SELECT pg_advisory_xact_lock("
                "hashtextextended(:email, 0))"
            ),
            {"email": email.strip().lower()},
        )