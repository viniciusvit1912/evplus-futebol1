from http.server import BaseHTTPRequestHandler
import json


BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00


class handler(BaseHTTPRequestHandler):

    def do_GET(self):

        resposta = {
            "status": "online",
            "sistema": "EV+ Futebol",
            "versao": "2.0",
            "mensagem": "API funcionando"
        }

        self.enviar(200, resposta)


    def do_POST(self):

        try:

            tamanho = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            corpo = self.rfile.read(tamanho)

            dados = json.loads(
                corpo.decode("utf-8")
            )

            odd = float(
                dados["odd"]
            )

            probabilidade = float(
                dados["probabilidade"]
            )

            momento = dados.get(
                "momento",
                "pre"
            )


            # ==========================
            # VALIDAÇÕES
            # ==========================

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


            # ==========================
            # CÁLCULOS
            # ==========================

            prob = (
                probabilidade / 100
            )

            probabilidade_implicita = (
                1 / odd
            ) * 100

            ev = (
                prob * odd
            ) - 1

            ev_percentual = (
                ev * 100
            )

            odd_justa = (
                1 / prob
            )


            # ==========================
            # DECISÃO
            # ==========================

            if ev_percentual >= 5:

                decisao = "ENTRA"

            elif ev_percentual >= 0:

                decisao = "AGUARDA"

            else:

                decisao = "PASSA"


            # ==========================
            # CLASSIFICAÇÃO
            # ==========================

            if ev_percentual >= 8:

                classificacao = "A"

            elif ev_percentual >= 3:

                classificacao = "B"

            else:

                classificacao = "C"


            # ==========================
            # BANCA
            # ==========================

            if momento.lower() == "live":

                banca = BANCA_LIVE

            else:

                banca = BANCA_PRE_JOGO


            # Stake padrão de 2% da banca

            stake_padrao = banca * 0.02

            stake_maxima = banca * 0.03


            # O sistema não aumenta stake
            # automaticamente para recuperar perdas.

            if decisao == "ENTRA":

                stake_recomendada = round(
                    stake_padrao,
                    2
                )

            else:

                stake_recomendada = 0.00


            # ==========================
            # RESPOSTA
            # ==========================

            resposta = {

                "status": "ok",

                "decisao": decisao,

                "classificacao":
                    classificacao,

                "odd": round(
                    odd,
                    2
                ),

                "probabilidade_estimada":
                    round(
                        probabilidade,
                        2
                    ),

                "probabilidade_implicita":
                    round(
                        probabilidade_implicita,
                        2
                    ),

                "ev":
                    round(
                        ev_percentual,
                        2
                    ),

                "odd_justa":
                    round(
                        odd_justa,
                        2
                    ),

                "momento":
                    momento,

                "banca":
                    round(
                        banca,
                        2
                    ),

                "stake_recomendada":
                    stake_recomendada,

                "stake_maxima":
                    round(
                        stake_maxima,
                        2
                    )

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

                    "mensagem":
                        str(erro)
                }

            )


    def enviar(
        self,
        codigo,
        dados
    ):

        self.send_response(
            codigo
        )

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

        self.wfile.write(

            json.dumps(
                dados
            ).encode("utf-8")

        )