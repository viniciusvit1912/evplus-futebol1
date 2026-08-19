from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL — FASE 2.1
# MOTOR OVER 1.5
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
    # GET
    # =====================================================

    def do_GET(self):

        self.enviar(
            200,
            {
                "status": "online",
                "sistema": "EV+ Futebol",
                "versao": "2.1",
                "motor": "Over 1.5",
                "mensagem": "API funcionando"
            }
        )


    # =====================================================
    # POST
    # =====================================================

    def do_POST:

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


            # =================================================
            # DADOS BÁSICOS
            # =================================================

            odd = self.numero(
                dados.get("odd")
            )

            prob_manual = self.numero(
                dados.get("probabilidade")
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
            # VALIDAÇÃO DA ODD
            # =================================================

            if odd is None or odd <= 1:

                raise ValueError(
                    "A odd deve ser maior que 1."
                )


            # =================================================
            # PROBABILIDADE MANUAL
            # =================================================

            if (
                prob_manual is not None
                and (
                    prob_manual <= 0
                    or prob_manual > 100
                )
            ):

                raise ValueError(
                    "A probabilidade deve estar entre 0 e 100."
                )


            # =================================================
            # DADOS ESTATÍSTICOS
            # =================================================

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


            # =================================================
            # MOTOR OVER 1.5
            # =================================================

            prob_modelo = self.modelo_over15(
                xg_casa=xg_casa,
                xg_fora=xg_fora,
                xgot_casa=xgot_casa,
                xgot_fora=xgot_fora,
                final_casa=final_casa,
                final_fora=final_fora,
                alvo_casa=alvo_casa,
                alvo_fora=alvo_fora,
                chances_casa=chances_casa,
                chances_fora=chances_fora
            )


            # =================================================
            # PROBABILIDADE FINAL
            # =================================================

            if (
                prob_modelo is not None
                and prob_manual is not None
            ):

                probabilidade = (
                    prob_manual * 0.50
                    +
                    prob_modelo * 0.50
                )

            elif prob_modelo is not None:

                probabilidade = prob_modelo

            elif prob_manual is not None:

                probabilidade = prob_manual

            else:

                raise ValueError(
                    "Informe uma probabilidade ou dados estatísticos."
                )


            probabilidade = max(
                1,
                min(
                    99,
                    probabilidade
                )
            )


            # =================================================
            # EV
            # =================================================

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


            # =================================================
            # RISCO
            # =================================================

            risco = self.calcular_risco(
                mercado=mercado,
                prob_modelo=prob_modelo,
                xg_casa=xg_casa,
                xg_fora=xg_fora
            )


            # =================================================
            # DECISÃO
            # =================================================

            decisao, classificacao = self.veredito(
                ev,
                risco
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

            if decisao == "ENTRA":

                stake = banca * STAKE_PADRAO

            else:

                stake = 0.00


            stake_maxima = (
                banca * STAKE_MAXIMA
            )


            # =================================================
            # RESPOSTA
            # =================================================

            resposta = {

                "status": "ok",

                "sistema": "EV+ Futebol",

                "versao": "2.1",

                "motor": "Over 1.5",

                "decisao": decisao,

                "classificacao": classificacao,

                "risco": risco,

                "mercado": mercado,

                "momento": momento,

                "odd": round(
                    odd,
                    2
                ),

                "probabilidade_manual": (
                    round(
                        prob_manual,
                        2
                    )
                    if prob_manual is not None
                    else None
                ),

                "probabilidade_modelo": (
                    round(
                        prob_modelo,
                        2
                    )
                    if prob_modelo is not None
                    else None
                ),

                "probabilidade_estimada": round(
                    probabilidade,
                    2
                ),

                "probabilidade_implicita": round(
                    prob_implicita,
                    2
                ),

                "odd_justa": round(
                    odd_justa,
                    2
                ),

                "ev": round(
                    ev,
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

                "motivos": self.motivos(
                    prob_modelo,
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
                    chances_fora
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
                    "mensagem": str(erro)
                }
            )


    # =====================================================
    # MOTOR OVER 1.5
    # =====================================================

    def modelo_over15(
        self,
        xg_casa,
        xg_fora,
        xgot_casa,
        xgot_fora,
        final_casa,
        final_fora,
        alvo_casa,
        alvo_fora,
        chances_casa,
        chances_fora
    ):

        valores = []


        # -------------------------------------------------
        # xG
        # -------------------------------------------------

        if (
            xg_casa is not None
            and xg_fora is not None
        ):

            total_xg = (
                xg_casa +
                xg_fora
            )

            valores.append(
                self.prob_over15_poisson(
                    total_xg
                )
            )


        # -------------------------------------------------
        # xGOT
        # -------------------------------------------------

        if (
            xgot_casa is not None
            and xgot_fora is not None
        ):

            total_xgot = (
                xgot_casa +
                xgot_fora
            )

            valores.append(
                self.prob_over15_poisson(
                    total_xgot
                )
            )


        # -------------------------------------------------
        # FINALIZAÇÕES
        # -------------------------------------------------

        if (
            final_casa is not None
            and final_fora is not None
        ):

            total = (
                final_casa +
                final_fora
            )

            if total >= 25:

                valores.append(82)

            elif total >= 20:

                valores.append(78)

            elif total >= 15:

                valores.append(73)

            elif total >= 10:

                valores.append(68)


        # -------------------------------------------------
        # FINALIZAÇÕES NO ALVO
        # -------------------------------------------------

        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            total = (
                alvo_casa +
                alvo_fora
            )

            if total >= 8:

                valores.append(85)

            elif total >= 6:

                valores.append(80)

            elif total >= 4:

                valores.append(74)

            elif total >= 2:

                valores.append(65)


        # -------------------------------------------------
        # GRANDES CHANCES
        # -------------------------------------------------

        if (
            chances_casa is not None
            and chances_fora is not None
        ):

            total = (
                chances_casa +
                chances_fora
            )

            if total >= 4:

                valores.append(88)

            elif total >= 3:

                valores.append(82)

            elif total >= 2:

                valores.append(76)

            elif total >= 1:

                valores.append(65)


        if not valores:

            return None


        probabilidade = (
            sum(valores) /
            len(valores)
        )


        return max(
            5,
            min(
                95,
                probabilidade
            )
        )


    # =====================================================
    # POISSON — OVER 1.5
    # =====================================================

    def prob_over15_poisson(
        self,
        media
    ):

        if media <= 0:

            return 5


        p0 = math.exp(
            -media
        )

        p1 = (
            p0 *
            media
        )


        # P(X >= 2)
        probabilidade = (
            1 -
            p0 -
            p1
        ) * 100


        return max(
            5,
            min(
                95,
                probabilidade
            )
        )


    # =====================================================
    # RISCO
    # =====================================================

    def calcular_risco(
        self,
        mercado,
        prob_modelo,
        xg_casa,
        xg_fora
    ):

        pontos = 0


        if prob_modelo is None:

            pontos += 2


        if (
            "over" in mercado.lower()
            and
            xg_casa is not None
            and
            xg_fora is not None
        ):

            total_xg = (
                xg_casa +
                xg_fora
            )

            if total_xg < 1.00:

                pontos += 2

            elif total_xg < 1.50:

                pontos += 1


        if pontos >= 3:

            return "ALTO"

        if pontos >= 1:

            return "MÉDIO"

        return "BAIXO"


    # =====================================================
    # VEREDITO
    # =====================================================

    def veredito(
        self,
        ev,
        risco
    ):

        if ev < 0:

            return (
                "PASSA",
                "C"
            )


        if ev < 3:

            return (
                "AGUARDA",
                "C"
            )


        if (
            risco == "ALTO"
            and
            ev < 8
        ):

            return (
                "AGUARDA",
                "C"
            )


        if ev >= 8:

            return (
                "ENTRA",
                "A"
            )


        if ev >= 5:

            return (
                "ENTRA",
                "B"
            )


        return (
            "AGUARDA",
            "C"
        )


    # =====================================================
    # MOTIVOS
    # =====================================================

    def motivos(
        self,
        prob_modelo,
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
        chances_fora
    ):

        lista = []


        if prob_modelo is not None:

            lista.append(
                "Modelo específico para Over 1.5 ativado."
            )

            lista.append(
                f"Probabilidade do modelo: "
                f"{prob_modelo:.2f}%."
            )

        else:

            lista.append(
                "Modelo estatístico não recebeu dados suficientes."
            )


        if (
            xg_casa is not None
            and xg_fora is not None
        ):

            lista.append(
                f"xG total: "
                f"{xg_casa + xg_fora:.2f}."
            )


        if (
            xgot_casa is not None
            and xgot_fora is not None
        ):

            lista.append(
                f"xGOT total: "
                f"{xgot_casa + xgot_fora:.2f}."
            )


        if (
            final_casa is not None
            and final_fora is not None
        ):

            lista.append(
                f"Finalizações totais: "
                f"{final_casa + final_fora:.0f}."
            )


        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            lista.append(
                f"Finalizações no alvo: "
                f"{alvo_casa + alvo_fora:.0f}."
            )


        if (
            chances_casa is not None
            and chances_fora is not None
        ):

            lista.append(
                f"Grandes chances: "
                f"{chances_casa + chances_fora:.0f}."
            )


        lista.append(
            f"EV calculado: {ev:.2f}%."
        )

        lista.append(
            f"Risco calculado: {risco}."
        )


        return lista


    # =====================================================
    # CONVERSÃO SEGURA PARA NÚMERO
    # =====================================================

    def numero(
        self,
        valor
    ):

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