## Flask Dependency

Dependency injection is a powerful concept that allows you to manage and inject dependencies into your application
components. In Flask, we can create a simple dependency injection system inspired by FastAPI's `Depends`.

### Approach

1. **Create a Dependency Class**: We'll define a class called `Depends` that will handle our dependencies. This class
   will allow us to declare dependencies for specific route handlers.

2. **Decorator for Dependency Resolution**: We'll create a decorator that inspects the function and resolves any
   dependencies when called. This decorator will be applied to our route handlers.

3. **Dependency Functions**: We'll define individual functions (similar to FastAPI's dependencies) that represent our
   dependencies. These functions will be called automatically when needed.

### Sample Code

```python
# app.py
from flask import Flask, Blueprint
from pydantic import BaseModel
from flask_dependency import BackgroundTask, Depends, route, FormModel

app = Flask(__name__)
blueprint = Blueprint("example_blueprint", __name__)
app.debug = True


def sample_task(duration):
    import time
    time.sleep(duration)
    return f"Slept for {duration} seconds"


# Example Backgraund Task
@route(blueprint, "/backgraund_task", methods=["POST"], endpoint="route_test")
def route_test(background_task: BackgroundTask = Depends()):
    background_task.run(sample_task, 1)
    return {"message": "OK"}


class InputModelForm(FormModel):
    id: int
    name: str


class ResponseInputModelForm(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# Example Form
@route(blueprint, "/example_form", methods=["POST"], endpoint="route_test", response_schema=ResponseInputModelForm)
def route_test(input_data: InputModelForm = Depends()):
    return {"message": "success"}


app.register_blueprint(blueprint)
```

