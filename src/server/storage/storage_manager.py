from typing import Any, Dict, List, Optional, Type, TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session
from server.storage.models import UserIdMixin, User

from sqlalchemy import inspect
from sqlalchemy.orm.collections import InstrumentedList


UserIdGeneric = TypeVar("UserIdGeneric", bound=UserIdMixin)


class StorageManager:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def list(
        self,
        model_cls: Type[UserIdGeneric],
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[Any]] = None,
    ) -> UserIdGeneric:
        query = self.db.query(model_cls)

        if self.user.role == "user":
            query = query.filter_by(user_id=self.user.user_id)

        if filters:
            if "start_date" in filters:
                query = query.filter(model_cls.date >= filters["start_date"])
                filters.pop("start_date")
            if "end_date" in filters:
                query = query.filter(model_cls.date <= filters["end_date"])
                filters.pop("end_date")
            query = query.filter_by(**filters)

        if order_by:
            query = query.order_by(*order_by)

        return query.all()

    def create(
        self, model_cls: Type[UserIdGeneric], data: Dict[str, Any]
    ) -> UserIdGeneric:
        data = data.copy()
        if "user_id" in inspect(model_cls).columns:
            data["user_id"] = self.user.id

        item = model_cls(**data)

        self.db.add(item)
        self.db.flush()

        return item

    def get(
        self, model_cls: Type[UserIdGeneric], filters: Dict[str, Any]
    ) -> UserIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(user_id=self.user.user_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        return item

    def update(
        self,
        model_cls: Type[UserIdGeneric],
        filters: Dict[str, Any],
        data: Dict[str, Any],
    ) -> UserIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(user_id=self.user.user_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        for key, val in data.items():
            attr_val = getattr(item, key)
            if isinstance(attr_val, InstrumentedList):
                attr_val.clear()
                attr_val.extend(val)
            else:
                setattr(item, key, val)

        self.db.add(item)
        self.db.flush()

        return item

    def delete(
        self, model_cls: Type[UserIdGeneric], filters: Dict[str, Any]
    ) -> UserIdGeneric:
        query = self.db.query(model_cls).filter_by(**filters)

        if self.user.role == "user":
            query = query.filter_by(user_id=self.user.user_id)

        item = query.one_or_none()

        if item is None:
            raise HTTPException(400, detail=f"{model_cls.__name__} doesn't exist")

        self.db.delete(item)
        self.db.flush()

        return item
