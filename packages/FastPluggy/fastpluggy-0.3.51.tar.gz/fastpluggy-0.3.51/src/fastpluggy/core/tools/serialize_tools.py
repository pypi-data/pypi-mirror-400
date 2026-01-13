import inspect
from dataclasses import is_dataclass, asdict
from datetime import date, datetime
from pathlib import Path

from fastapi.routing import APIRouter
from jinja2 import FileSystemLoader
from pydantic_settings import BaseSettings

from fastpluggy.core.models_tools.sqlalchemy import ModelToolsSQLAlchemy
from fastpluggy.core.tools.fastapi import list_router_routes

try:
    from pydantic.fields import Undefined
except ImportError:
    Undefined = object()  # fallback dummy

try:
    from pydantic_core import PydanticUndefined
except ImportError:
    PydanticUndefined = object()  # fallback dummy


def serialize_value(value, serialize_dates=False):
    """
    Custom serialization logic for different types of values.

    Args:
        value: The value to serialize
        serialize_dates: If True, serialize date/datetime objects to ISO format strings
    """
    if value is Undefined or value is PydanticUndefined:
        return str(value)  # or skip it entirely
    elif isinstance(value, Path):
        return str(value)
    elif serialize_dates and isinstance(value, datetime):
        return value.isoformat()
    elif serialize_dates and isinstance(value, date):
        return value.isoformat()
    elif isinstance(value, FileSystemLoader):
        return value.list_templates()
    elif isinstance(value, BaseSettings):
        return value.dict()
    elif isinstance(value, APIRouter):
        return serialize_value(list_router_routes(value), serialize_dates=serialize_dates)  # Serialize router as a list of routes
    elif inspect.ismodule(value):
        # Represent modules as their names
        return value.__name__
    elif is_dataclass(value):
        return asdict(value)
    elif isinstance(value, dict):
        # Recursively serialize each key and value in the dictionary
        return {k: serialize_value(v, serialize_dates=serialize_dates) for k, v in value.items()}
    elif isinstance(value, list):
        # Serialize SQLAlchemy models
        if all(ModelToolsSQLAlchemy.is_sqlalchemy(v) for v in value):
            return [
                {
                    "class_name": v.__name__,
                    "table_name": v.__tablename__,
                    "columns": [col.key for col in v.__table__.columns],
                }
                for v in value
            ]
        return [serialize_value(item, serialize_dates=serialize_dates) for item in value]
    elif isinstance(value, (str, int, float, bool, type(None))):
        # Return directly serializable types as is
        return value
    elif hasattr(value, "to_dict"):
        # Serialize objects with a `to_dict` method
        return value.to_dict()
    else:
        # Fallback: Convert to string
        return str(value)
