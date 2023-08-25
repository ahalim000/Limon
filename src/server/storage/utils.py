from inspect import get_annotations
from typing import (Any, Callable, Dict, Iterable, List, Optional, Tuple, Type,
                    TypeVar, overload)

from pydantic import BaseConfig, BaseModel, create_model
from sqlalchemy import Delete, Select, Update
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.properties import ColumnProperty

from server.storage.database import Base
from server.storage.models import User

SQLAlchemyModelClass = TypeVar("SQLAlchemyModelClass", bound=Base)

SelectSignature = Callable[..., Select[Tuple[SQLAlchemyModelClass]]]
UpdateSignature = Callable[[Type[SQLAlchemyModelClass]], Update]
DeleteSignature = Callable[[Type[SQLAlchemyModelClass]], Delete]
QuerySignature = TypeVar(
    "QuerySignature", SelectSignature, UpdateSignature, DeleteSignature
)


class OrmConfig(BaseConfig):
    orm_mode = True


def sqlalchemy_to_pydantic(
    model_cls: Type[SQLAlchemyModelClass],
    include_fields: Optional[Iterable[str]] = None,
    exclude_fields: Optional[Iterable[str]] = None,
    treat_default_as_optional: bool = False,
    all_fields_optional: bool = False,
    additional_attributes: Optional[Dict[str, Tuple[Any, Any]]] = None,
    name: Optional[str] = None,
    config: Type = OrmConfig,
) -> Type[BaseModel]:
    insp = inspect(model_cls)

    if include_fields is None:
        include_fields = set()
        for attr in insp.attrs:
            include_fields.add(attr.key)
    else:
        include_fields = set(include_fields)

    if exclude_fields is None:
        exclude_fields = set()
    else:
        exclude_fields = set(exclude_fields)

    if additional_attributes is None:
        additional_attributes = {}

    total_include_fields = include_fields - exclude_fields
    annotations = get_annotations(model_cls)
    fields = {}
    for attr in insp.attrs:
        if attr.key not in total_include_fields:
            continue

        if isinstance(attr, ColumnProperty):
            attr_name = attr.key
            column = attr.columns[0]
            col_type = annotations[attr_name].__args__[0]
            is_optional = col_type.__name__ == "Optional"

            if all_fields_optional:
                if not is_optional:
                    col_type = Optional[col_type]

                fields[attr_name] = (col_type, None)
                continue

            default = None
            if column.default is None and not column.nullable:
                default = ...
            else:
                if treat_default_as_optional and not is_optional:
                    col_type = Optional[col_type]
            fields[attr_name] = (col_type, default)

    fields.update(additional_attributes)
    name = model_cls.__name__ if name is None else name
    pydantic_model = create_model(name, __config__=config, **fields)  # type: ignore
    return pydantic_model


@overload
def safe_query(
    query_func: SelectSignature,
    models: List[Type[SQLAlchemyModelClass]],
    user: User,
) -> Select[Tuple[SQLAlchemyModelClass]]:
    ...


@overload
def safe_query(
    query_func: UpdateSignature,
    models: List[Type[SQLAlchemyModelClass]],
    user: User,
) -> Update:
    ...


@overload
def safe_query(
    query_func: DeleteSignature,
    models: List[Type[SQLAlchemyModelClass]],
    user: User,
) -> Delete:
    ...


def safe_query(
    query_func: QuerySignature,
    models: List[Type[SQLAlchemyModelClass]],
    user: User,
) -> Select[Tuple[SQLAlchemyModelClass]] | Update | Delete:
    query = query_func(*models)

    if user.role == "user":
        query = query.filter_by(user_id=user.id)

    return query
