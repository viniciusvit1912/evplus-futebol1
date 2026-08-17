from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        resposta = {
            "status": "online",
            "sistema": "EV+ Futebol",
            "mensagem": "API funcionando"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(
            json.dumps(resposta, ensure_ascii=False).encode()
        )