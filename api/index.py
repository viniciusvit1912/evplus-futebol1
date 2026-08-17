from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

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

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS"
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )

        self.end_headers()

        resposta = json.dumps(
            dados,
            ensure_ascii=False
        ).encode("utf-8")

        self.wfile.write(resposta)


    def do_OPTIONS(self):

        self.enviar(
            200,
            {
                "status": "online"
            }
        )


    def do_GET(self):

        self.enviar(
            200,
            {
                "status": "online",
                "sistema": "EV+ Futebol",
                "mensagem": "API funcionando"
            }
        )


    def do_POST(self):

        try:

            tamanho = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            corpo = self.rfile.read(
                tamanho
            )

            dados = json.loads(
                corpo.decode("utf-8")
            )

            probabilidade = float(
                dados["probabilidade"]
            )

            odd = float(
                dados["odd"]
            )

            if probabilidade <= 0 or probabilidade > 100:
                raise ValueError(
                    "Probabilidade deve estar entre 0 e 100."
                )

            if odd <= 1:
                raise ValueError(
                    "Odd deve ser maior que 1."
                )

            prob = probabilidade / 100

            ev = (prob * odd) - 1

            valor_justo = 1 / prob

            self.enviar(
                200,
                {
                    "status": "ok",
                    "probabilidade": probabilidade,
                    "odd": odd,
                    "probabilidade_implicita":
                        round((1 / odd) * 100, 2),
                    "ev":
                        round(ev * 100, 2),
                    "valor_justo":
                        round(valor_justo, 2)
                }
            )

        except Exception as erro:

            self.enviar(
                400,
                {
                    "status": "erro",
                    "mensagem": str(erro)
                }
            )