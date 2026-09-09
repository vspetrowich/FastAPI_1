# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class CreateAdvertRequest(BaseModel):
    title: str
    description: str
    price: float
    author_id: int

class CreateAdvertResponse(BaseModel):
    id: int

class GetAdvertResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id : int
    start_time: Optional[str] = None


class FindAdvertRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author_id: Optional[int] = None
    start_time: Optional[str] = None

class FindAdvertResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id : int
    start_time: Optional[str]


class UpdateAdvertRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author_id: Optional[int] = None
    start_time: Optional[str] = None

class UpdateAdvertResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id: int
    start_time: Optional[str]

class OKResponse(BaseModel):
    status: str = "ok"