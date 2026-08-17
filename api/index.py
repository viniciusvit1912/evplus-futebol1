from http.server import BaseHTTPRequestHandler
import json


# =========================================================
# BANCA
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03
STAKE_EXPLORATORIA = 0.50


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # GET — TESTE DA API
    # =====================================================

    def do_GET(self):

        resposta = {
            "status": "online",
            "sistema": "EV+ Futebol",
            "versao": "3.0",
            "mensagem": "Motor EV+ funcionando"
        }

        self.enviar(200, resposta)


    # =====================================================
    # POST — MOTOR EV+
    # =====================================================

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

            # -------------------------------------------------
            # DADOS PRINCIPAIS
            # -------------------------------------------------

            odd = self.numero(
                dados.get("odd")
            )

            probabilidade = self.numero(
                dados.get("probabilidade")
            )

            momento = str(
                dados.get(
                    "momento",
                    "pre"
                )
            ).lower()

            mercado = str(
                dados.get(
                    "mercado",
                    ""
                )
            )

            minuto = self.numero(
                dados.get("minuto")
            )

            placar = str(
                dados.get(
                    "placar",
                    ""
                )
            )


            # -------------------------------------------------
            # VALIDAÇÃO
            # -------------------------------------------------

            if odd is None or odd <= 1:

                raise ValueError(
                    "A odd deve ser maior que 1."
                )

            if (
                probabilidade is None
                or probabilidade <= 0
                or probabilidade > 100
            ):

                raise ValueError(
                    "A probabilidade deve estar entre 0 e 100."
                )


            # -------------------------------------------------
            # ESTATÍSTICAS
            # -------------------------------------------------

            xg_casa = self.numero(
                dados.get("xgCasa")
            )

            xg_fora = self.numero(
                dados.get("xgFora")
            )

            xgot_casa = self.numero(
                dados.get("xgotCasa")
            )

            xgot_fora = self.numero(
                dados.get("xgotFora")
            )

            final_casa = self.numero(
                dados.get("finalCasa")
            )

            final_fora = self.numero(
                dados.get("finalFora")
            )

            alvo_casa = self.numero(
                dados.get("alvoCasa")
            )

            alvo_fora = self.numero(
                dados.get("alvoFora")
            )

            chances_casa = self.numero(
                dados.get("chancesCasa")
            )

            chances_fora = self.numero(
                dados.get("chancesFora")
            )

            esc_casa = self.numero(
                dados.get("escCasa")
            )

            esc_fora = self.numero(
                dados.get("escFora")
            )

            cart_casa = self.numero(
                dados.get("cartCasa")
            )

            cart_fora = self.numero(
                dados.get("cartFora")
            )


            # =================================================
            # PROBABILIDADE / EV
            # =================================================

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


            # =================================================
            # RISCO
            # =================================================

            risco = self.calcular_risco(
                momento=momento,
                minuto=minuto,
                mercado=mercado,
                ev=ev_percentual,
                xg_casa=xg_casa,
                xg_fora=xg_fora,
                final_casa=final_casa,
                final_fora=final_fora,
                alvo_casa=alvo_casa,
                alvo_fora=alvo_fora,
                esc_casa=esc_casa,
                esc_fora=esc_fora,
                cart_casa=cart_casa,
                cart_fora=cart_fora
            )


            # =================================================
            # DECISÃO
            # =================================================

            decisao = self.definir_decisao(
                ev_percentual,
                risco
            )


            # =================================================
            # CLASSIFICAÇÃO
            # =================================================

            classificacao = self.definir_classificacao(
                ev_percentual,
                risco,
                decisao
            )


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

            stake = 0.00

            if decisao == "ENTRA":

                if classificacao == "A":

                    stake = banca * STAKE_PADRAO

                elif classificacao == "B":

                    stake = banca * STAKE_PADRAO

                else:

                    stake = STAKE_EXPLORATORIA

            # Nunca ultrapassar 3% automaticamente

            limite = banca * STAKE_MAXIMA

            if stake > limite:

                stake = limite


            stake = round(
                stake,
                2
            )


            # =================================================
            # MOTIVOS
            # =================================================

            motivos = self.gerar_motivos(
                mercado=mercado,
                momento=momento,
                ev=ev_percentual,
                risco=risco,
                xg_casa=xg_casa,
                xg_fora=xg_fora,
                xgot_casa=xgot_casa,
                xgot_fora=xgot_fora,
                final_casa=final_casa,
                final_fora=final_fora,
                alvo_casa=alvo_casa,
                alvo_fora=alvo_fora,
                chances_casa=chances_casa,
                chances_fora=chances_fora,
                esc_casa=esc_casa,
                esc_fora=esc_fora,
                cart_casa=cart_casa,
                cart_fora=cart_fora
            )


            # =================================================
            # RESPOSTA
            # =================================================

            resposta = {

                "status": "ok",

                "versao": "3.0",

                "decisao": decisao,

                "classificacao":
                    classificacao,

                "risco":
                    risco,

                "mercado":
                    mercado,

                "momento":
                    momento,

                "minuto":
                    minuto,

                "placar":
                    placar,

                "odd":
                    round(
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

                "banca":
                    round(
                        banca,
                        2
                    ),

                "stake_recomendada":
                    stake,

                "stake_maxima":
                    round(
                        limite,
                        2
                    ),

                "motivos":
                    motivos

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


    # =====================================================
    # CONVERTER NÚMEROS
    # =====================================================

    def numero(self, valor):

        if valor is None:
            return None

        if valor == "":
            return None

        try:

            numero = float(valor)

            if numero < 0:
                return None

            return numero

        except:

            return None


    # =====================================================
    # RISCO
    # =====================================================

    def calcular_risco(
        self,
        momento,
        minuto,
        mercado,
        ev,
        xg_casa,
        xg_fora,
        final_casa,
        final_fora,
        alvo_casa,
        alvo_fora,
        esc_casa,
        esc_fora,
        cart_casa,
        cart_fora
    ):

        pontos = 0


        # EV negativo aumenta risco

        if ev < 0:
            pontos += 3

        elif ev < 3:
            pontos += 2

        elif ev < 5:
            pontos += 1


        # LIVE sem dados suficientes

        if momento == "live":

            dados = [
                xg_casa,
                xg_fora,
                final_casa,
                final_fora
            ]

            disponiveis = sum(
                x is not None
                for x in dados
            )

            if disponiveis < 2:
                pontos += 2


        # Mercados naturalmente mais voláteis

        mercados_variancia = [
            "autor do gol",
            "cabeceio no gol",
            "chute de fora da área no gol"
        ]

        mercado_lower = mercado.lower()

        if any(
            item in mercado_lower
            for item in mercados_variancia
        ):

            pontos += 1


        if pontos >= 4:

            return "ALTO"

        elif pontos >= 2:

            return "MÉDIO"

        else:

            return "BAIXO"


    # =====================================================
    # DECISÃO
    # =====================================================

    def definir_decisao(
        self,
        ev,
        risco
    ):

        if ev < 0:

            return "PASSA"


        if ev < 3:

            return "AGUARDA"


        if risco == "ALTO" and ev < 8:

            return "AGUARDA"


        if ev >= 5:

            return "ENTRA"


        return "AGUARDA"


    # =====================================================
    # CLASSIFICAÇÃO
    # =====================================================

    def definir_classificacao(
        self,
        ev,
        risco,
        decisao
    ):

        if decisao == "PASSA":

            return "C"


        if (
            ev >= 8
            and risco == "BAIXO"
        ):

            return "A"


        if ev >= 5:

            return "B"


        return "C"


    # =====================================================
    # MOTIVOS
    # =====================================================

    def gerar_motivos(
        self,
        mercado,
        momento,
        ev,
        risco,
        xg_casa,
        xg_fora,
        xgot_casa,
        xgot_fora,
        final_casa,
        final_fora,
        alvo_casa,
        alvo_fora,
        chances_casa,
        chances_fora,
        esc_casa,
        esc_fora,
        cart_casa,
        cart_fora
    ):

        motivos = []


        # EV

        if ev > 0:

            motivos.append(
                "O preço apresenta EV positivo."
            )

        elif ev == 0:

            motivos.append(
                "O preço está próximo do valor justo."
            )

        else:

            motivos.append(
                "O preço não apresenta EV positivo."
            )


        # xG

        if (
            xg_casa is not None
            and xg_fora is not None
        ):

            total_xg = (
                xg_casa +
                xg_fora
            )

            motivos.append(
                f"xG informado no jogo: {total_xg:.2f}."
            )


        # xGOT

        if (
            xgot_casa is not None
            and xgot_fora is not None
        ):

            total_xgot = (
                xgot_casa +
                xgot_fora
            )

            motivos.append(
                f"xGOT informado: {total_xgot:.2f}."
            )


        # Finalizações

        if (
            final_casa is not None
            and final_fora is not None
        ):

            total_finalizacoes = (
                final_casa +
                final_fora
            )

            motivos.append(
                "Volume total de finalizações informado: "
                f"{total_finalizacoes:.0f}."
            )


        # Chutes no alvo

        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            total_alvo = (
                alvo_casa +
                alvo_fora
            )

            motivos.append(
                "Finalizações no alvo: "
                f"{total_alvo:.0f}."
            )


        # Grandes chances

        if (
            chances_casa is not None
            and chances_fora is not None
        ):

            total_chances = (
                chances_casa +
                chances_fora
            )

            motivos.append(
                "Grandes chances registradas: "
                f"{total_chances:.0f}."
            )


        # Escanteios

        if (
            esc_casa is not None
            and esc_fora is not None
        ):

            total_escanteios = (
                esc_casa +
                esc_fora
            )

            motivos.append(
                "Escanteios registrados: "
                f"{total_escanteios:.0f}."
            )


        # Cartões

        if (
            cart_casa is not None
            and cart_fora is not None
        ):

            total_cartoes = (
                cart_casa +
                cart_fora
            )

            motivos.append(
                "Cartões registrados: "
                f"{total_cartoes:.0f}."
            )


        # Risco

        motivos.append(
            f"Nível de risco calculado: {risco}."
        )


        return motivos


    # =====================================================
    # RESPOSTA HTTP
    # =====================================================

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
                dados,
                ensure_ascii=False
            ).encode("utf-8")
        )