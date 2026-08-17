from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        resposta = {
            "status": "online",
            "sistema": "EV+ Futebol",
            "mensagem": "API funcionando"
        }

        self.enviar(200, resposta)

    def do_POST(self):
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            corpo = self.rfile.read(tamanho)

            dados = json.loads(corpo.decode("utf-8"))

            probabilidade = float(dados["probabilidade"])
            odd = float(dados["odd"])

            prob = probabilidade / 100

            ev = (prob * odd) - 1

            resposta = {
                "status": "ok",
                "probabilidade": probabilidade,
                "odd": odd,
                "ev": round(ev * 100, 2),
                "valor_justo": round(1 / prob, 2)
            }

            self.enviar(200, resposta)

        except Exception as erro:
            self.enviar(400, {
                "status": "erro",
                "mensagem": str(erro)
            })

    def enviar(self, codigo, dados):

        self.send_response(codigo)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(
            json.dumps(dados).encode("utf-8")
        )