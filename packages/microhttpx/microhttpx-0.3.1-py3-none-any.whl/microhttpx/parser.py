try:
    import ure # type:ignore
except:
    import re as ure

class HttpxParser:
    @staticmethod
    def _unquote(s):
        res = s.replace("+", " ")
        hexes = ure.findall(r'%([0-9A-Fa-f]{2})', res)
        for h in hexes:
            res = res.replace('%' + h, chr(int(h, 16)))
        return res

    @staticmethod
    def _parse_qs(qs):
        params = {}
        if qs:
            pairs = qs.split("&")
            for pair in pairs:
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    params[k] = HttpxParser._unquote(v)
                else:
                    params[pair] = ""
        return params

    @staticmethod
    def query(path: str) -> dict:
        if "?" in path:
            _, query = path.split("?", 1)
            return HttpxParser._parse_qs(query)
        return {}

    @staticmethod
    def body(body:str) -> dict:
        return HttpxParser._parse_qs(body)

    @staticmethod
    def path_params(route_pattern:str, path:str):
        path = path.split("?", 1)[0]

        r_parts = route_pattern.strip("/").split("/")
        p_parts = path.strip("/").split("/")

        if r_parts == [''] and p_parts == ['']:
            return {}

        if len(r_parts) != len(p_parts):
            return None

        params = {}
        for r, p in zip(r_parts, p_parts):
            if r.startswith("{") and r.endswith("}"):
                params[r[1:-1]] = p
            elif r != p:
                return None

        return params
