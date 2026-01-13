from .logger import Logger
import socket
import json

class HttpxResponse:
    @staticmethod
    def resp(conn:(socket.socket|None), status:str, body="", content_type="text/plain"):
        if conn is None:
            Logger.error("SERV", "socket connection is null")
            return

        if isinstance(body, str):
            body_bytes = body.encode()
        elif isinstance(body, bytes):
            body_bytes = body
        else:
            body_bytes = str(body).encode()

        Logger.log("SERV", "-> {} {}".format(status, len(body)))

        headers=(
            "HTTP/1.1 {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n\r\n"
            .format(status, content_type, len(body))
        )

        conn.send(headers.encode())

        if body_bytes:
            conn.send(body_bytes)

    @staticmethod
    def json(conn:(socket.socket|None), status: str, payload):
        if not isinstance(payload, str):
            payload = json.dumps(payload)

        HttpxResponse.resp(conn, status, payload, "application/json")

    @staticmethod
    def html(conn:(socket.socket|None), status: str, html):
        HttpxResponse.resp(conn, status, html, "text/html")
