

from pydantic import BaseModel, validator
from datetime import datetime
import re
from typing import Optional


class InventarioUpdate(BaseModel):
    id_proveedor: int
    id_categoria: int
    nombre: str
    cantidad: int
    precio: float
    observacion: Optional[str] = None

class InventarioCreate(BaseModel):
    id_proveedor: int
    id_categoria: int
    nombre: str
    cantidad: int
    precio: float
    observacion: Optional[str] = None


class InventarioPrestamo(BaseModel):
    id_usuario: int
    cantidad: int
    fecha_devolucion: datetime

