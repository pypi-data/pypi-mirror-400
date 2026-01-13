from .status import StatusNotFound
from .request import HttpxRequest
from .response import HttpxResponse
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

        print("[SERV] server started on {}:{}".format(host, port))

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

            handler=self.routes.get((method.upper(),path))
            if not handler:
                HttpxResponse.resp(conn, StatusNotFound(), "Page not found")
                return

            result = handler(HttpxRequest(data))

            if isinstance(result, dict):
                HttpxResponse.json(conn, "200 OK", json.dumps(result))
            elif isinstance(result, str):
                HttpxResponse.resp(conn, "200 OK", result)
            else:
                HttpxResponse.resp(conn, "200 OK", str(result))
        finally:
            conn.close()
