from functools import wraps
from typing import List, Literal, Type

from flask import Blueprint
from pydantic import BaseModel

from .depends import Depends
from .inject import inject
from .validate_schema import validate_schema


def route(
        blueprint: Blueprint,
        rule: str,
        endpoint: str,
        methods: List[Literal["GET", "POST", "PUT", "PATCH", "DELETE"]],
        response_schema: Type[BaseModel] = None,
        status_code_response: int = 200,
        dependencies: List[Depends] = None,
):
    def decorator(func):
        func = inject(func)

        @wraps(func)
        @blueprint.route(rule, methods=methods, endpoint=endpoint)
        def wrapper(*args, **kwargs):

            if dependencies:
                [_() for _ in dependencies]
            data_response = func(*args, **kwargs)
            if response_schema:
                data_response = validate_schema(response_schema, data_response).dict()
            return data_response, status_code_response

        return wrapper

    return decorator
