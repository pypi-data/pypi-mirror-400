"""API routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/items")
async def get_items():
    """Get all items."""
    return {"items": []}


@router.post("/items")
async def create_item(name: str):
    """Create a new item."""
    return {"message": f"Created item: {name}"}
