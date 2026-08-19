from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL
# FASE 2.1 — MOTOR OVER 1.5
# =========================================================


# =========================================================
# BANCA
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # HTTP — RESPOSTA
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
            "Cache-Control",
            "no-store"
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
                "mensagem": "Motor EV+ Over 1.5 funcionando"
            }
        )


    # =====================================================
    # POST
    # =====================================================

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

            # =================================================
            # DADOS BÁSICOS
            # =================================================

            odd = self.numero(
                dados.get("odd")
            )

            prob_manual = self.numero(
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
                    "Over 1.5"
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
            #
            # Continua aceita nesta fase para manter
            # compatibilidade com o frontend atual.
            #
            # Quando o modelo possuir dados suficientes,
            # a probabilidade estatística terá prioridade.
            # =================================================

            if (
                prob_manual is None
                or prob_manual <= 0
                or prob_manual > 100
            ):

                raise ValueError(
                    "A probabilidade deve estar entre 0 e 100."
                )


            # =================================================
            # ESTATÍSTICAS
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
                momento=momento,
                minuto=minuto,
                placar=placar,
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
            #
            # Sem dados estatísticos:
            #   usa a probabilidade manual.
            #
            # Com dados estatísticos:
            #   modelo = 70%
            #   estimativa manual = 30%
            #
            # Nesta fase mantemos uma combinação conservadora.
            # =================================================

            if prob_modelo is not None:

                probabilidade = (
                    prob_modelo * 0.70
                    +
                    prob_manual * 0.30
                )

            else:

                probabilidade = prob_manual


            probabilidade = max(
                1,
                min(
                    99,
                    probabilidade
                )
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

            prob = (
                probabilidade / 100
            )

            ev = (
                prob * odd
            ) - 1

            ev_percentual = (
                ev * 100
            )


            # =================================================
            # ODD JUSTA
            # =================================================

            odd_justa = (
                1 / prob
            )


            # =================================================
            # RISCO
            # =================================================

            risco = self.calcular_risco(
                momento=momento,
                minuto=minuto,
                placar=placar,
                mercado=mercado,
                prob_modelo=prob_modelo,
                xg_casa=xg_casa,
                xg_fora=xg_fora,
                final_casa=final_casa,
                final_fora=final_fora,
                alvo_casa=alvo_casa,
                alvo_fora=alvo_fora,
                chances_casa=chances_casa,
                chances_fora=chances_fora
            )


            # =================================================
            # DECISÃO
            # =================================================

            decisao = self.decisao(
                ev_percentual,
                risco
            )


            # =================================================
            # CLASSIFICAÇÃO
            # =================================================

            classificacao = self.classificacao(
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

            limite = (
                banca *
                STAKE_MAXIMA
            )


            if decisao == "ENTRA":

                stake = (
                    banca *
                    STAKE_PADRAO
                )

                stake = min(
                    stake,
                    limite
                )


            stake = round(
                stake,
                2
            )


            # =================================================
            # MOTIVOS
            # =================================================

            motivos = self.motivos(
                prob_manual=prob_manual,
                prob_modelo=prob_modelo,
                prob_final=probabilidade,
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
                chances_fora=chances_fora
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

                "minuto": minuto,

                "placar": placar,

                "odd": round(
                    odd,
                    2
                ),

                "probabilidade_manual": round(
                    prob_manual,
                    2
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

                "ev": round(
                    ev_percentual,
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

                "stake_recomendada": stake,

                "stake_maxima": round(
                    limite,
                    2
                ),

                "motivos": motivos

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
        momento,
        minuto,
        placar,
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


        # =================================================
        # xG
        # =================================================

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


        # =================================================
        # xGOT
        # =================================================

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


        # =================================================
        # FINALIZAÇÕES
        # =================================================

        if (
            final_casa is not None
            and final_fora is not None
        ):

            total_final = (
                final_casa +
                final_fora
            )

            if total_final >= 25:

                valores.append(86)

            elif total_final >= 20:

                valores.append(82)

            elif total_final >= 15:

                valores.append(77)

            elif total_final >= 10:

                valores.append(70)

            elif total_final >= 6:

                valores.append(63)


        # =================================================
        # FINALIZAÇÕES NO ALVO
        # =================================================

        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            total_alvo = (
                alvo_casa +
                alvo_fora
            )

            if total_alvo >= 10:

                valores.append(91)

            elif total_alvo >= 8:

                valores.append(87)

            elif total_alvo >= 6:

                valores.append(82)

            elif total_alvo >= 4:

                valores.append(76)

            elif total_alvo >= 2:

                valores.append(67)


        # =================================================
        # GRANDES CHANCES
        # =================================================

        if (
            chances_casa is not None
            and chances_fora is not None
        ):

            total_chances = (
                chances_casa +
                chances_fora
            )

            if total_chances >= 5:

                valores.append(92)

            elif total_chances >= 4:

                valores.append(88)

            elif total_chances >= 3:

                valores.append(83)

            elif total_chances >= 2:

                valores.append(76)

            elif total_chances >= 1:

                valores.append(65)


        # =================================================
        # SEM DADOS
        # =================================================

        if not valores:

            return None


        # =================================================
        # MÉDIA
        # =================================================

        prob = (
            sum(valores) /
            len(valores)
        )


        # =================================================
        # AJUSTE LIVE
        # =================================================

        if momento == "live":

            minuto_num = (
                minuto
                if minuto is not None
                else 0
            )


            gols = self.total_gols(
                placar
            )


            # ---------------------------------------------
            # Se já existem 2 gols:
            # Over 1.5 já está matematicamente cumprido.
            # ---------------------------------------------

            if gols >= 2:

                return 99.9


            # ---------------------------------------------
            # Se ainda não existem 2 gols,
            # considerar o tempo restante.
            # ---------------------------------------------

            if minuto_num >= 80:

                prob -= 18

            elif minuto_num >= 75:

                prob -= 12

            elif minuto_num >= 65:

                prob -= 7

            elif minuto_num >= 55:

                prob -= 3


            # ---------------------------------------------
            # 0-0 é diferente de 1-0.
            # ---------------------------------------------

            if gols == 0:

                if minuto_num >= 70:

                    prob -= 8

                elif minuto_num >= 60:

                    prob -= 4


            elif gols == 1:

                if minuto_num >= 70:

                    prob -= 3


        return max(
            5,
            min(
                99,
                prob
            )
        )


    # =====================================================
    # POISSON — PROBABILIDADE DE OVER 1.5
    # =====================================================

    def prob_over15_poisson(
        self,
        xg
    ):

        if xg <= 0:

            return 5


        # P(X >= 2)
        #
        # = 1 - P(0) - P(1)

        p0 = math.exp(
            -xg
        )

        p1 = (
            p0 *
            xg
        )

        prob = (
            1 -
            p0 -
            p1
        ) * 100


        return max(
            5,
            min(
                99,
                prob
            )
        )


    # =====================================================
    # TOTAL DE GOLS DO PLACAR
    # =====================================================

    def total_gols(
        self,
        placar
    ):

        if not placar:

            return 0


        try:

            partes = (
                placar
                .replace(" ", "")
                .split("-")
            )

            if len(partes) != 2:

                return 0


            casa = int(
                partes[0]
            )

            fora = int(
                partes[1]
            )


            if casa < 0 or fora < 0:

                return 0


            return casa + fora


      