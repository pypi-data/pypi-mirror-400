import json

from .exceptions.unprocessable_content import UnprocessableContent
from flask import request
from pydantic import BaseModel, ValidationError


class QueryModel(BaseModel):
    def __init__(self):
        data = request.args
        try:
            if isinstance(data, (str, bytes, bytearray)):
                super().__init__(**json.loads(data))
            if isinstance(data, dict):
                super().__init__(**data)
        except ValidationError as e:
            raise UnprocessableContent(message="Invalid Query Data", error=e)
