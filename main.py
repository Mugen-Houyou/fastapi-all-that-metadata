from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Create FastAPI app instance
app = FastAPI(
    title="FastAPI All That Metadata",
    description="A basic FastAPI web service with essential metadata",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Data models
class Item(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    created_at: Optional[datetime] = None

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

# In-memory storage (for demonstration purposes)
items_db: List[Item] = []
item_id_counter = 1


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": "Welcome to FastAPI All That Metadata",
        "version": "0.1.0",
        "docs": "/docs",
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


# Get all items
@app.get("/items", response_model=List[Item], tags=["items"])
async def get_items():
    """
    Retrieve all items from the database.
    """
    return items_db


# Get a specific item by ID
@app.get("/items/{item_id}", response_model=Item, tags=["items"])
async def get_item(item_id: int):
    """
    Retrieve a specific item by its ID.
    """
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


# Create a new item
@app.post("/items", response_model=Item, status_code=201, tags=["items"])
async def create_item(item: ItemCreate):
    """
    Create a new item in the database.
    """
    global item_id_counter
    
    new_item = Item(
        id=item_id_counter,
        name=item.name,
        description=item.description,
        price=item.price,
        created_at=datetime.now(),
    )
    items_db.append(new_item)
    item_id_counter += 1
    
    return new_item


# Update an existing item
@app.put("/items/{item_id}", response_model=Item, tags=["items"])
async def update_item(item_id: int, item_update: ItemUpdate):
    """
    Update an existing item by its ID.
    """
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            updated_data = item_update.model_dump(exclude_unset=True)
            updated_item = item.model_copy(update=updated_data)
            items_db[idx] = updated_item
            return updated_item
    
    raise HTTPException(status_code=404, detail="Item not found")


# Delete an item
@app.delete("/items/{item_id}", status_code=204, tags=["items"])
async def delete_item(item_id: int):
    """
    Delete an item by its ID.
    """
    for idx, item in enumerate(items_db):
        if item.id == item_id:
            items_db.pop(idx)
            return
    
    raise HTTPException(status_code=404, detail="Item not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
