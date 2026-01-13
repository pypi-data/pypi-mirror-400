import json

from .exceptions.unprocessable_content import UnprocessableContent
from flask import request
from pydantic import BaseModel, ValidationError


class FormModel(BaseModel):
    def __init__(self):
        data = request.get_json()
        try:
            if isinstance(data, (str, bytes, bytearray)):
                super().__init__(**json.loads(data))
            if isinstance(data, dict):
                super().__init__(**data)
        except ValidationError as exc:
            raise UnprocessableContent(message="Invalid Input Data", error=exc)
