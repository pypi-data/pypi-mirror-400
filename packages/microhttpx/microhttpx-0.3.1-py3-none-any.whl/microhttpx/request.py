from .logger import Logger
import socket

class HttpxRequest:
    def __init__(self, raw:str, conn:(socket.socket|None)=None):
        self.raw=raw
        self.conn=conn
        self.method=None
        self.path=None
        self.headers={}
        self.body=""
        self.params={}

        self._parse()

    @staticmethod
    def _unquote(s: str) -> str:
        s = s.replace("+", " ")
        i = 0
        res = ""
        while i < len(s):
            if s[i] == "%" and i + 2 < len(s):
                try:
                    res += chr(int(s[i + 1:i + 3], 16))
                    i += 3
                except ValueError:
                    res += s[i]
                    i += 1
            else:
                res += s[i]
                i += 1
        return res

    def _parse(self):
        parts=self.raw.split("\r\n\r\n", 1)
        head=parts[0]
        body=parts[1] if len(parts) > 1 else ""

        lines=head.split("\r\n")

        self.method, self.path, _ = lines[0].split(" ")

        # Headers
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                self.headers[k.strip()] = v.strip()

        self.body=body

        if body:
            try:
                for param in body.split("&"):
                    k, v = param.split("=", 1)
                    self.params[self._unquote(k)] = self._unquote(v)
            except Exception as e:
                Logger.error("REQUEST", "{}: {}".format(type(e).__name__, e))
