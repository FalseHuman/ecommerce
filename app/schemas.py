from pydantic import BaseModel
from datetime import datetime


class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int
    rating: float
    is_active: bool


class CreateCategory(BaseModel):
    name: str
    parent_id: int | None = None


class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str


class CreateRating(BaseModel):
    grade: float


class CreateReview(BaseModel):
    comment: str