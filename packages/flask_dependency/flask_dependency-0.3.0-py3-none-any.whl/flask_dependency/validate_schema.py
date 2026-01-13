from typing import Type, Any, Dict

from pydantic import BaseModel


def validate_schema(schema: Type[BaseModel], data: Any) -> BaseModel:
    if isinstance(data, str):
        return schema.parse_raw(data)
    if isinstance(data, Dict):
        return schema(**data)
    return schema.from_orm(data)
