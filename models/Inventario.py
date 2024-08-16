

from pydantic import BaseModel, validator

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