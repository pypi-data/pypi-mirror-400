from .parser import HttpxParser

class HttpxField:
    def __init__(self, field_type:type = str, required=False, default=None, validator=None):
        self.type=field_type
        self.required=required
        self.default=default
        self.validator=validator

class HttpxStruct:
    def __init__(self, req):
        path_params = HttpxParser.path_params(getattr(self, "__route__", ""), getattr(req, "path", ""))
        query_params = HttpxParser.query(getattr(req, "path", ""))
        body_params = HttpxParser.body(getattr(req, "body", ""))

        all_params = {}
        for d in (query_params, body_params, path_params):
            if not d:
                continue
            for k, v in d.items():
                all_params[k] = v

        for name, field in getattr(self, "__fields__", {}).items():
            value = all_params.get(name, None)

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

            setattr(self, name, value)

        self.raw     = getattr(req, "raw", "")
        self.method  = getattr(req, "method", None)
        self.path    = getattr(req, "path", None)
        self.headers = getattr(req, "headers", {})
        self.body    = getattr(req, "body", "")
        self.params  = all_params
