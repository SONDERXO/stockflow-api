from typing import Annotated, Literal
from pydantic import BaseModel, Field, StringConstraints

NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1)
]

class ProductCreate(BaseModel):
    name: NonEmptyText
    price: float = Field(gt=0)
    stock: int = Field(ge=0)

class ProductUpdate(BaseModel):
    name: NonEmptyText | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)

class StockMovementCreate(BaseModel):
    movement_type: Literal["IN", "OUT"]
    quantity: int = Field(gt=0)
