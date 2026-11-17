import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta
from pwdlib import PasswordHash

# Cargar variables del .env
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No se encontró la DATABASE_URL en el archivo .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Instanciamos el sistema de hash de forma independiente
password_hash = PasswordHash.recommended()

def poblar_base_datos():
    db = SessionLocal()
    try:
        print("🧹 Limpiando base de datos y reiniciando contadores...")
        db.execute(text("TRUNCATE TABLE prestamos, libro_categoria, libros, socios, categorias, autores, refresh_tokens, usuarios RESTART IDENTITY CASCADE;"))
        db.commit()
        print("✔ Base de datos limpia.")

        print("🌱 Iniciando el proceso de poblado de la base de datos...")

        # 1. Crear Usuarios
        print("Creando usuarios...")
        from app.models.usuario import Usuario, RolUsuario

        usuarios_data = [
            Usuario(nombre="Admin General", email="admin@biblioteca.com", hashed_password=password_hash.hash("Carolina987"), rol=RolUsuario.admin if hasattr(RolUsuario, 'admin') else list(RolUsuario)[0]),
            Usuario(nombre="Carlos Pérez", email="carlos@biblioteca.com", hashed_password=password_hash.hash("123456"), rol=RolUsuario.admin if hasattr(RolUsuario, 'admin') else list(RolUsuario)[0]),
        ]
        for i in range(3, 11):
            usuarios_data.append(
                Usuario(nombre=f"Usuario {i}", email=f"usuario{i}@email.com", hashed_password=password_hash.hash("123456"), rol=RolUsuario.socio if hasattr(RolUsuario, 'socio') else list(RolUsuario)[-1])
            )
        db.add_all(usuarios_data)
        db.commit()
        print("✔ 10 Usuarios creados.")

        # 2. Crear Autores (IDs del 1 al 10 garantizados)
        print("Creando autores...")
        from app.models.autor import Autor
        nombres_autores = [
            ("Gabriel García Márquez", "Colombiana", 1927),
            ("Isabel Allende", "Chilena", 1942),
            ("Jorge Luis Borges", "Argentina", 1899),
            ("Mario Vargas Llosa", "Peruana", 1936),
            ("Julio Cortázar", "Argentina", 1914),
            ("Pablo Neruda", "Chilena", 1904),
            ("Laura Restrepo", "Colombiana", 1950),
            ("Rafael Pombo", "Colombiana", 1833),
            ("Mario Mendoza", "Colombiana", 1964),
            ("Héctor Abad Faciolince", "Colombiana", 1958)
        ]
        autores = [Autor(nombre=n[0], nacionalidad=n[1], anio_naci=n[2]) for n in nombres_autores]
        db.add_all(autores)
        db.commit()
        print("✔ 10 Autores creados.")

        # 3. Crear Categorías
        print("Creando categorías...")
        from app.models.categoria import Categoria
        nombres_categorias = [
            "Novela", "Ciencia Ficción", "Fantasía", "Poesía", 
            "Historia", "Ensayo", "Biografía", "Terror", 
            "Romántica", "Académico"
        ]
        categorias = [Categoria(nombre=cat, descripcion=f"Libros de género {cat}") for cat in nombres_categorias]
        db.add_all(categorias)
        db.commit()
        print("✔ 10 Categorías creadas.")

        # 4. Crear Socios
        print("Creando socios...")
        from app.models.socio import Socio
        socios = []
        for i in range(1, 11):
            socios.append(
                Socio(
                    nombre=f"Socio Nombre {i}", 
                    email=f"socio{i}@email.com", 
                    telefono=f"30012345{i:02d}",
                    activo=True,
                    fecha_alta=date.today() - timedelta(days=i)
                )
            )
        db.add_all(socios)
        db.commit()
        print("✔ 10 Socios creados.")

        # 5. Crear Libros con portadas integradas
        print("Creando libros con portadas...")
        from app.models.libro import Libro
        libros_data = [
            Libro(
                titulo="Cien Años de Soledad", isbn="9780307474728", anio_publicacion=1967, ejemplares=5, autor_id=1,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_cien_anios",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="La Casa de los Espíritus", isbn="9780553383803", anio_publicacion=1982, ejemplares=4, autor_id=2,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_casa_espiritus",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Ficciones", isbn="9780307950932", anio_publicacion=1944, ejemplares=3, autor_id=3,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_ficciones",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="La Ciudad y los Perros", isbn="9788466332156", anio_publicacion=1963, ejemplares=4, autor_id=4,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_ciudad_perros",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Rayuela", isbn="9788437604572", anio_publicacion=1963, ejemplares=2, autor_id=5,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_rayuela",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Veinte Poemas de Amor", isbn="9789561301382", anio_publicacion=1924, ejemplares=6, autor_id=6,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_veinte_poemas",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Delirio", isbn="9789584214560", anio_publicacion=2004, ejemplares=3, autor_id=7,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_delirio",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Cuentos Pintados", isbn="9789583001239", anio_publicacion=1867, ejemplares=5, autor_id=8,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_cuentos_pintados",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="Satanás", isbn="9789584205605", anio_publicacion=2002, ejemplares=4, autor_id=9,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_satanas",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
            Libro(
                titulo="El Olvido que Seremos", isbn="9789584508933", anio_publicacion=2006, ejemplares=5, autor_id=10,
                portada_url="https://res.cloudinary.com/demo/image/upload/sample.jpg",
                portada_public_id="portada_olvido",
                portada_thumbnail_url="https://res.cloudinary.com/demo/image/upload/c_thumb,w_200/sample.jpg"
            ),
        ]
        db.add_all(libros_data)
        db.commit()
        print("✔ 10 Libros con portadas creados.")

        # 6. Poblar la tabla intermedia libro_categoria
        print("Asociando libros con categorías...")
        # Usamos una consulta SQL directa para insertar en la tabla de asociación de muchos a muchos
        db.execute(text("""
            INSERT INTO libro_categoria (libro_id, categoria_id) VALUES 
            (1, 1), (1, 3),
            (2, 1), (2, 9),
            (3, 1), (3, 2),
            (4, 1), (5, 1),
            (6, 4), (7, 1),
            (8, 4), (9, 1),
            (10, 6)
            ON CONFLICT DO NOTHING;
        """))
        db.commit()
        print("✔ Relaciones de libros y categorías creadas.")

        # 7. Crear Préstamos adaptados al modelo real
        print("Creando préstamos de ejemplo...")
        from app.models.prestamo import Prestamo
        prestamos_data = [
            Prestamo(
                libro_id=1, 
                socio_id=1, 
                fecha_prestamo=date.today() - timedelta(days=5),
                fecha_limite=date.today() + timedelta(days=9),
                fecha_devolucion=None,
                multa=0.0,
                multa_pagada=False,
                registrado_por_id=1
            ),
            Prestamo(
                libro_id=2, 
                socio_id=2, 
                fecha_prestamo=date.today() - timedelta(days=10),
                fecha_limite=date.today() + timedelta(days=4),
                fecha_devolucion=None,
                multa=0.0,
                multa_pagada=False,
                registrado_por_id=1
            ),
            Prestamo(
                libro_id=3, 
                socio_id=3, 
                fecha_prestamo=date.today() - timedelta(days=15),
                fecha_limite=date.today() - timedelta(days=1),
                fecha_devolucion=date.today() - timedelta(days=2),
                multa=0.0,
                multa_pagada=True,
                registrado_por_id=2
            )
        ]
        db.add_all(prestamos_data)
        db.commit()
        print("✔ Préstamos de ejemplo creados.")

        print("🎉 ¡Base de datos poblada exitosamente de principio a fin!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error al poblar la base de datos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    poblar_base_datos()