from .logger import Logger
import socket

class HttpxResponse:
    @staticmethod
    def resp(conn:socket.socket, status:str, body="", content_type="text/plain"):
        Logger.log("SERV", "-> {} {}".format(status, len(body)))

        headers=(
            "HTTP/1.1 {}\r\n"
            "Content-Type: {}\r\n"
            "Content-Length: {}\r\n\r\n"
            .format(status, content_type, len(body))
        )

        conn.send(headers.encode())

        if body:
            if isinstance(body, str):
                body=body.encode()
            conn.send(body)

    @staticmethod
    def json(conn:socket.socket, status: str, payload):
        HttpxResponse.resp(conn, status, payload, "application/json")

    @staticmethod
    def html(conn:socket.socket, status: str, html):
        HttpxResponse.resp(conn, status, html, "text/html")
