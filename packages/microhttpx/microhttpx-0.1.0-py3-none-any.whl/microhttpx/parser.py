from urllib.parse import parse_qs, unquote
import re

class HttpxParser:
    @staticmethod
    def query(path:str) -> dict:
        params={}
        if "?" in path:
            _, query = path.split("?", 1)
            parsed=parse_qs(query)
            for k, v in parsed.items():
                params[k]=unquote(v[0])
        return params

    @staticmethod
    def body(body:str) -> dict:
        params={}
        if body:
            parsed=parse_qs(body)
            for k, v in parsed.items():
                params[k]=unquote(v[0])
        return params

    @staticmethod
    def path_params(route_pattern:str, path:str) -> dict:
        path = path.split("?", 1)[0]

        r_parts = route_pattern.strip("/").split("/")
        p_parts = path.strip("/").split("/")

        if len(r_parts) != len(p_parts):
            return {}

        params = {}
        for r, p in zip(r_parts, p_parts):
            if r.startswith("{") and r.endswith("}"):
                params[r[1:-1]] = p
            elif r != p:
                return {}

        return params
