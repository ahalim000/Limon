from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from server.dependencies import get_storage_manager
from server.storage.storage_manager import StorageManager
from server.storage.models import GroceryListItem

router = APIRouter(prefix="/api/grocery_list_items")


@router.put("/{id}/toggle", status_code=204)
def toggle_grocery_list_item(
    id: int, sm: StorageManager = Depends(get_storage_manager)
):
    grocery_list_item = sm.get(GroceryListItem, {"id": id})
    sm.update(GroceryListItem, {"id": id}, {"active": not grocery_list_item.active})
