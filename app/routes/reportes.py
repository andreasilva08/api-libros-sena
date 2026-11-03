from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import Staff, get_db
from app.schemas.reporte import (
    ReporteLibroMasPrestado,
    ReporteCategoria,
    ReportePrestamoVencido,
    ReporteSocioMulta,
    ReporteAutor,
    ReporteResumen
)
from app.controllers import reporte as reporte_controller

router = APIRouter(prefix="/reportes", tags=["Reportes"])

@router.get("/libros-mas-prestados", response_model=List[ReporteLibroMasPrestado])
def libros_mas_prestados(
    _: Staff,
    limite: int = Query(5, ge=1),
    db: Session = Depends(get_db),
):
    return reporte_controller.get_libros_mas_prestados(db, limite)

@router.get("/categorias", response_model=List[ReporteCategoria])
def reporte_categorias(_: Staff, db: Session = Depends(get_db)):
    return reporte_controller.get_reporte_categorias(db)

@router.get("/prestamos-vencidos", response_model=List[ReportePrestamoVencido])
def prestamos_vencidos(_: Staff, db: Session = Depends(get_db)):
    return reporte_controller.get_prestamos_vencidos(db)

@router.get("/socios-con-multas", response_model=List[ReporteSocioMulta])
def socios_con_multas(_: Staff, db: Session = Depends(get_db)):
    return reporte_controller.get_socios_con_multas(db)

@router.get("/autores", response_model=List[ReporteAutor])
def reporte_autores(_: Staff, db: Session = Depends(get_db)):
    return reporte_controller.get_reporte_autores(db)

@router.get("/resumen", response_model=ReporteResumen)
def resumen_general(_: Staff, db: Session = Depends(get_db)):
    return reporte_controller.get_resumen_general(db)