"""Data models."""
from pydantic import BaseModel


class Item(BaseModel):
    """Item model."""
    id: int
    name: str
    description: str | None = None
