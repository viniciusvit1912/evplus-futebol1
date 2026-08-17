from http.server import BaseHTTPRequestHandler
import json


def calcular_ev(probabilidade, odd):
    """
    probabilidade: porcentagem de chance, ex: 60
    odd: odd decimal, ex: 2.00
    """
    prob = probabilidade / 100
    ev = (prob * odd) - 1

    return {
        "probabilidade": probabilidade,
        "odd": odd,
        "ev": round(ev * 100, 2),
        "valor_justo": round(1 / prob, 2)
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        resposta = {
            "status": "online",
            "sistema": "EV+ Futebol",
            "mensagem": "Motor de análise funcionando"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(
            json.dumps(resposta, ensure_ascii=False).encode()
        )

    def do_POST(self):
        tamanho = int(self.headers.get("Content-Length", 0))
        dados = json.loads(self.rfile.read(tamanho))

        probabilidade = float(dados["probabilidade"])
        odd = float(dados["odd"])

        resultado = calcular_ev(probabilidade, odd)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        self.wfile.write(
            json.dumps(resultado, ensure_ascii=False).encode()
        )