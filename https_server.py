from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
import os

class MyHttpsServer():
    def __init__(self) -> None:
        load_dotenv()
        self._start()

    def __del__(self):
        self._stop()
    
    def _start(self):
        print("Starting server on localhost 8000...")
        self.httpd = HTTPServer(('localhost', 8000), MyHTTPRequestHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="cert/rth_cert.pem", keyfile="cert/rth_key.pem", password=os.getenv("CERT_PSW"))
        self.httpd.socket = context.wrap_socket(self.httpd.socket, server_side=True)
        print("Server: start serving...")
        self.t = Thread(target=self.httpd.serve_forever, daemon=True)
        self.t.start()

    def _stop(self):
        print("Stopping server...")
        # print(self.t.is_alive())
        # self.httpd.shutdown()
        print("Server stopped.")

class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("Server: GET")
        self.send_response(200)
        self.end_headers()
        data = bytearray(f"<head></head><body><h1>RTH D2 client</h1><p>{datetime.now()}</p></body>", encoding="ASCII")
        self.wfile.write(data)
