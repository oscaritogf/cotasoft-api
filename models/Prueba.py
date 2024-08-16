
#models/Prueba.py
from pydantic import BaseModel, validator
from typing import Optional
import re


class UserLogin(BaseModel):
    email: str
    password: str