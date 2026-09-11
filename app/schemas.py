# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class CreateAdvertRequest(BaseModel):
    title: str
    description: str
    price: float
    author: str

class CreateAdvertResponse(BaseModel):
    id: int

class GetAdvertResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author : str
    created_at: Optional[str] = None


class FindAdvertRequest(BaseModel):
    title: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    author: Optional[str] = None

class FindAdvertResponse(BaseModel):
    query: list


class UpdateAdvertRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author: Optional[str] = None
    created_at: Optional[str] = None

class UpdateAdvertResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author: str
    created_at: Optional[str]

class OKResponse(BaseModel):
    status: str = "ok"