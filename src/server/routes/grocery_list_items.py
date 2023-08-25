from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.dependencies import get_current_user, get_db
from server.storage.models import GroceryListItem, User
from server.storage.utils import safe_query

router = APIRouter(prefix="/api/grocery_list_items", tags=["grocery_list_items"])


@router.put("/{id}/toggle", status_code=204)
def toggle_grocery_list_item(
    id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    grocery_list_item = db.scalars(
        safe_query(select, [GroceryListItem], user).filter_by(id=id)
    ).one()

    setattr(grocery_list_item, "active", not grocery_list_item.active)

    db.add(grocery_list_item)
    db.commit()
