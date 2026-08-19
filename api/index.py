from http.server import BaseHTTPRequestHandler
import json


class handler(BaseHTTPRequestHandler):

    def enviar(self, codigo, dados):
        corpo = json.dumps(
            dados,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(codigo)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
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

        self.send_header(
            "Content-Length",
            str(len(corpo))
        )

        self.end_headers()

        self.wfile.write(corpo)


    def do_OPTIONS(self):
        self.enviar(
            200,
            {
                "status": "ok"
            }
        )


    def do_GET(self):
        self.enviar(
            200,
            {
                "status": "online",
                "sistema": "EV+ Futebol",
                "versao": "5.0",
                "motor": "EV+",
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

            odd = float(
                dados.get("odd")
            )

            probabilidade = float(
                dados.get("probabilidade")
            )

            if odd <= 1:

                raise ValueError(
                    "A odd deve ser maior que 1."
                )

            if (
                probabilidade <= 0
                or probabilidade > 100
            ):

                raise ValueError(
                    "A probabilidade deve estar entre 0 e 100."
                )


            prob = (
                probabilidade / 100
            )

            prob_implicita = (
                1 / odd
            ) * 100

            ev = (
                prob * odd - 1
            ) * 100

            odd_justa = (
                1 / prob
            )


            if ev < 0:

                decisao = "PASSA"
                classificacao = "C"

            elif ev < 3:

                decisao = "AGUARDA"
                classificacao = "C"

            elif ev < 5:

                decisao = "AGUARDA"
                classificacao = "C"

            elif ev < 8:

                decisao = "ENTRA"
                classificacao = "B"

            else:

                decisao = "ENTRA"
                classificacao = "A"


            momento = str(
                dados.get(
                    "momento",
                    "pre"
                )
            ).lower()


            if momento == "live":

                banca = 12.00

            else:

                banca = 25.00


            if decisao == "ENTRA":

                stake = banca * 0.02

            else:

                stake = 0.00


            resposta = {

                "status": "ok",

                "sistema": "EV+ Futebol",

                "versao": "5.0",

                "decisao": decisao,

                "classificacao": classificacao,

                "risco": "BAIXO",

                "odd": round(
                    odd,
                    2
                ),

                "probabilidade_estimada": round(
                    probabilidade,
                    2
                ),

                "probabilidade_implicita": round(
                    prob_implicita,
                    2
                ),

                "ev": round(
                    ev,
                    2
                ),

                "odd_justa": round(
                    odd_justa,
                    2
                ),

                "banca": round(
                    banca,
                    2
                ),

                "stake_recomendada": round(
                    stake,
                    2
                ),

                "stake_maxima": round(
                    banca * 0.03,
                    2
                ),

                "mercado": dados.get(
                    "mercado",
                    ""
                ),

                "momento": momento,

                "motivos": [
                    "Cálculo EV realizado pelo motor EV+.",
                    f"Probabilidade implícita: {prob_implicita:.2f}%.",
                    f"Odd justa: {odd_justa:.2f}.",
                    f"EV: {ev:.2f}%."
                ]

            }


            self.enviar(
                200,
                resposta
            )


        except Exception as erro:

            self.enviar(
                400,
                {
                    "status": "erro",
                    "mensagem": str(erro)
                }
            )