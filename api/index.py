from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL — MOTOR EV+ v5
# Fundação — API
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # GET
    # =====================================================

    def do_GET(self):

        self.enviar(200, {
            "status": "online",
            "sistema": "EV+ Futebol",
            "versao": "5.0",
            "motor": "EV+ Foundation",
            "mensagem": "Motor EV+ funcionando"
        })

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

            corpo = self.rfile.read(tamanho)

            dados = json.loads(
                corpo.decode("utf-8")
            )

            # =================================================
            # DADOS PRINCIPAIS
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

            # =================================================
            # VALIDAÇÃO
            # =================================================

            if odd is None or odd <= 1:

                raise ValueError(
                    "A odd deve ser maior que 1."
                )

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
            # MOTOR ESTATÍSTICO
            # =================================================

            prob_modelo = self.modelo(
                mercado=mercado,
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

            if prob_modelo is not None:

                probabilidade = (
                    prob_manual * 0.70
                    +
                    prob_modelo * 0.30
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
            # EV
            # =================================================

            prob = probabilidade / 100

            prob_implicita = (
                1 / odd
            ) * 100

            ev = (
                prob * odd
            ) - 1

            ev_percentual = ev * 100

            odd_justa = 1 / prob

            # =================================================
            # RISCO
            # =================================================

            risco = self.calcular_risco(
                momento=momento,
                minuto=minuto,
                mercado=mercado,
                prob_modelo=prob_modelo,
                xg_casa=xg_casa,
                xg_fora=xg_fora,
                final_casa=final_casa,
                final_fora=final_fora
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

            limite = banca * STAKE_MAXIMA

            if decisao == "ENTRA":

                stake = banca * STAKE_PADRAO

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
                mercado=mercado,
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

                "versao": "5.0",

                "motor": "EV+ Foundation",

                "casa": casa,

                "visitante": visitante,

                "mercado": mercado,

                "momento": momento,

                "minuto": minuto,

                "placar": placar,

                "decisao": decisao,

                "classificacao": classificacao,

                "risco": risco,

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
    # MOTOR PRINCIPAL
    # =====================================================

    def modelo(
        self,
        mercado,
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

        mercado_lower = mercado.lower()

        # =================================================
        # OVER 1.5
        # =================================================

        if (
            "over/under" in mercado_lower
            or "over 1.5" in mercado_lower
            or "over1.5" in mercado_lower
        ):

            return self.modelo_over15(
                momento=momento,
                minuto=minuto,
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
        # OUTROS MERCADOS
        # =================================================

        return self.modelo_generico(
            momento=momento,
            minuto=minuto,
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

    # =====================================================
    # MODELO OVER 1.5
    # =====================================================

    def modelo_over15(
        self,
        momento,
        minuto,
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
        # xG TOTAL
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
                self.prob_over15_xg(
                    total_xg
                )
            )

        # -------------------------------------------------
        # xGOT TOTAL
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
                self.prob_over15_xg(
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

            total_final = (
                final_casa +
                final_fora
            )

            if total_final >= 25:
                valores.append(88)

            elif total_final >= 20:
                valores.append(82)

            elif total_final >= 15:
                valores.append(76)

            elif total_final >= 10:
                valores.append(68)

        # -------------------------------------------------
        # FINALIZAÇÕES NO ALVO
        # -------------------------------------------------

        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            total_alvo = (
                alvo_casa