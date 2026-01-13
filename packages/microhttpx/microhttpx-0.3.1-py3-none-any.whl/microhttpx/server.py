from .status import StatusOK, StatusNotFound
from .request import HttpxRequest
from .response import HttpxResponse
from .logger import Logger
import socket
import json

class HttpxServer:
    def __init__(self):
        self.routes={}

    def route(self, path, methods=("GET",)):
        def decorator(func):
            for method in methods:
                self.routes[(method.upper(),path)]=func
            return func
        return decorator

    def listen(self, host="0.0.0.0", port=80):
        s=socket.socket()
        s.bind((host, port))
        s.listen(1)

        Logger.log("SERV", "server started on {}:{}".format(host, port))

        while True:
            conn, _ = s.accept()
            self.handle(conn)

    def handle(self, conn:socket.socket):
        try:
            data = conn.recv(1024).decode()
            if not data:
                return

            line = data.split("\r\n")[0]
            method, path, _ = line.split(" ")

            Logger.log("SERV", "{} {} HTTP/1.1".format(method.upper(), path))

            handler = None
            path_params = {}

            from .parser import HttpxParser
            for (m, route), func in self.routes.items():
                if m == method.upper():
                    params = HttpxParser.path_params(route, path)
                    if params is not None:
                        handler = func
                        path_params = params
                        break

            if not handler:
                HttpxResponse.resp(conn, StatusNotFound(), "Page not found")
                return

            req=HttpxRequest(data)
            req.conn=conn
            req.params=path_params

            result = handler(req)

            if result is None:
                return
            elif isinstance(result, dict):
                HttpxResponse.json(conn, StatusOK(), json.dumps(result))
            elif isinstance(result, str):
                HttpxResponse.resp(conn, StatusOK(), result)
            else:
                HttpxResponse.resp(conn, StatusOK(), str(result))
        finally:
            conn.close()
