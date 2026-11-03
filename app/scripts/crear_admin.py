from pydantic import EmailStr, TypeAdapter
from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario
from app.schemas.usuario import validar_password


def main() -> None:
    print("--- CREACIÓN DE ADMINISTRADOR INICIAL ---")

    # 1. Validar correo en bucle
    while True:
        try:
            email_input = input("Correo del administrador: ").strip().lower()
            email = TypeAdapter(EmailStr).validate_python(email_input)
            break
        except Exception:
            print("❌ Correo inválido. Asegúrate de incluir el '@' y un dominio válido.\n")

    # 2. Validar nombre en bucle
    while True:
        nombre = " ".join(input("Nombre completo (3 a 100 caracteres): ").split())
        if 3 <= len(nombre) <= 100:
            break
        print("❌ El nombre debe tener entre 3 y 100 caracteres.\n")

    # 3. Validar contraseña ANTES de pedir la confirmación
    while True:
        password = input("Contraseña (8-64 chars, con mayúscula, minúscula y número): ")
        if not 8 <= len(password) <= 64:
            print("❌ La contraseña debe tener entre 8 y 64 caracteres.\n")
            continue
        try:
            validar_password(password)  # Valida mayúsculas, minúsculas y números de inmediato
            break
        except ValueError as e:
            print(f"❌ {e}\n")

    # 4. Confirmar contraseña
    while True:
        confirmar_password = input("Confirma la contraseña: ")
        if password == confirmar_password:
            break
        print("❌ Las contraseñas no coinciden. Intenta de nuevo.\n")

    # 5. Guardar en base de datos
    with SessionLocal() as db:
        existente = db.scalar(select(Usuario.id).where(Usuario.email == email))
        if existente is not None:
            print("❌ Error: Ya existe una cuenta con ese correo en la base de datos.")
            return

        administrador = Usuario(
            email=email,
            nombre=nombre,
            hashed_password=hash_password(password),
            rol="admin",
            is_active=True,
        )
        db.add(administrador)
        db.commit()
        print(f"\n🚀 ¡Administrador creado correctamente: {email}!")


if __name__ == "__main__":
    main()