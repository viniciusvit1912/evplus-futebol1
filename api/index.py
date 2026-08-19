from http.server import BaseHTTPRequestHandler
import json


# =========================================================
# EV+ FUTEBOL — API BASE ESTÁVEL
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # RESPOSTA HTTP
    # =====================================================

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


    # =====================================================
    # OPTIONS
    # =====================================================

    def do_OPTIONS(self):

        self.enviar(
            200,
            {
                "status": "ok"
            }
        )


    # =====================================================
    # GET — TESTE DA API
    # =====================================================

    def do_GET(self):

        self.enviar(
            200,
            {
                "status": "online",
                "sistema": "EV+ Futebol",
                "versao": "5.3",
                "motor": "EV+",
                "mensagem": "API funcionando"
            }
        )


    # =====================================================
    # POST — ANÁLISE
    # =====================================================

    def do_POST(self):

        try:

            tamanho = int(
                self.headers.get(
                    "Content-Length",
                    "0"
                )
            )

            corpo = self.rfile.read(
                tamanho
            )

            dados = json.loads(
                corpo.decode("utf-8")
            )


            # =================================================
            # DADOS PRINCIPAIS
            # =================================================

            casa = str(
                dados.get(
                    "casa",
                    ""
                )
            )

            visitante = str(
                dados.get(
                    "visitante",
                    ""
                )
            )

            mercado = str(
                dados.get(
                    "mercado",
                    ""
                )
            )

            momento = str(
                dados.get(
                    "momento",
                    "pre"
                )
            ).lower()


            # =================================================
            # DADOS DA APOSTA
            # =================================================

            odd = float(
                dados.get("odd")
            )

            probabilidade = float(
                dados.get("probabilidade")
            )


            # =================================================
            # VALIDAÇÃO
            # =================================================

            if odd <= 1:

                raise ValueError(
                    "A odd deve ser maior que 1."
                )


            if (
                probabilidade <= 0
                or probabilidade > 100
            ):

                raise ValueError(
                    "A probabilidade deve estar "
                    "entre 0 e 100."
                )


            # =================================================
            # PROBABILIDADE
            # =================================================

            prob = (
                probabilidade / 100
            )


            # =================================================
            # PROBABILIDADE IMPLÍCITA
            # =================================================

            prob_implicita = (
                1 / odd
            ) * 100


            # =================================================
            # EV
            # =================================================

            ev = (
                prob * odd - 1
            ) * 100


            # =================================================
            # ODD JUSTA
            # =================================================

            odd_justa = (
                1 / prob
            )


            # =================================================
            # DECISÃO EV+
            #
            # EV < 0%       → PASSA
            # EV < 5%       → AGUARDA
            # EV < 8%       → ENTRA B
            # EV >= 8%      → ENTRA A
            # =================================================

            if ev < 0:

                decisao = "PASSA"
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


            # =================================================
            # BANCA
            # =================================================

            if momento == "live":

                banca = BANCA_LIVE

            else:

                banca = BANCA_PRE_JOGO


            # =================================================
            # STAKE
            # =================================================

            if decisao == "ENTRA":

                stake = (
                    banca *
                    STAKE_PADRAO
                )

            else:

                stake = 0.00


            stake_maxima = (
                banca *
                STAKE_MAXIMA
            )


            # =================================================
            # RESPOSTA
            # =================================================

            resposta = {

                "status": "ok",

                "sistema": "EV+ Futebol",

                "versao": "5.3",

                "decisao": decisao,

                "classificacao": classificacao,

                "risco": "BAIXO",

                "casa": casa,

                "visitante": visitante,

                "mercado": mercado,

                "momento": momento,

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
                    stake_maxima,
                    2
                ),

                "motivos": [

                    "Cálculo EV realizado "
                    "pelo motor EV+.",

                    f"Probabilidade estimada: "
                    f"{probabilidade:.2f}%.",

                    f"Probabilidade implícita: "
                    f"{prob_implicita:.2f}%.",

                    f"Odd justa: "
                    f"{odd_justa:.2f}.",

                    f"EV: "
                    f"{ev:.2f}%."

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