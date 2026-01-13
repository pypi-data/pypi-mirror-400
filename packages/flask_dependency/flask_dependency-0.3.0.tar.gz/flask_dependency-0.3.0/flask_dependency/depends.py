from typing import Any, Callable, Optional, get_origin, Union, get_args

from flask import g


class DependencyResolutionError(Exception):
    def __init__(self, dependency_type, errors: list[Exception]):
        self.dependency_type = dependency_type
        self.errors = errors

        message_lines = [
            f"Could not resolve dependency for: {dependency_type}",
            "Detected errors:"
        ]

        for i, err in enumerate(errors, start=1):
            message_lines.append(f"  {i}. {type(err).__name__}: {err}")

        super().__init__("\n".join(message_lines))


class Depends:
    def __init__(self, dependency: Optional[Callable[..., Any]] = None, cache: bool = True):
        self.dependency = dependency
        self.cache_key = f"_depends_cache_{id(dependency)}"
        self.cache = cache

    def _resolve_dependency(self, _dependency: Callable[..., Any]) -> Any:
        result = _dependency()
        if hasattr(result, "__enter__") and hasattr(result, "__exit__"):
            with result as ctx_result:
                setattr(g, self.cache_key, ctx_result)
                return ctx_result
        setattr(g, self.cache_key, result)
        return result

    def __call__(self):
        if not hasattr(g, self.cache_key) or not self.cache:
            origin = get_origin(self.dependency)
            errors: list[Exception] = []
            if origin is Union:
                for depend_type in get_args(self.dependency):
                    try:
                        return self._resolve_dependency(depend_type)
                    except Exception as exc:
                        errors.append(exc)
                raise DependencyResolutionError(self.dependency, errors)
            return self._resolve_dependency(self.dependency)

        return getattr(g, self.cache_key)

    @classmethod
    def attach_dependency(cls, dependency_instance: Any) -> Any:
        instance = cls(type(dependency_instance))
        setattr(g, instance.cache_key, dependency_instance)
        return dependency_instance
