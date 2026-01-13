from .parser import HttpxParser
from .request import HttpxRequest

class HttpxField:
    def __init__(self, field_type:type = str, required=False, default=None, validator=None):
        self.type=field_type
        self.required=required
        self.default=default
        self.validator=validator

class HttpxStructMeta(type):
    def __call__(cls, req):
        obj=object.__new__(cls)
        path_params=HttpxParser.path_params(cls.__route__, req.path) # type: ignore
        query_params=HttpxParser.query(req.path)
        body_params=HttpxParser.body(req.body)

        all_params = {**query_params, **body_params, **path_params}

        for name, field in cls.__fields__.items(): # type: ignore
            value=all_params.get(name, None)

            if field.required and value is None:
                raise ValueError(f"Field '{name}' is required")

            if value is None:
                value = field.default

            if value is not None:
                try:
                    value = field.type(value)
                except:
                    raise ValueError(f"Field '{name}' must be of type {field.type.__name__}")

            if field.validator and not field.validator(value):
                raise ValueError(f"Field '{name}' failed validation")

            setattr(obj, name, value)

        return obj

class HttpxStruct(HttpxRequest, metaclass=HttpxStructMeta):
    def __init__(self, req):
        pass

    __fields__ = {}
    __route__ = ""
