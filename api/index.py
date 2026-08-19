from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL
# FASE 2.1 — MOTOR OVER 1.5
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # GET — TESTE DA API
    # =====================================================

    def do_GET(self):

        self.enviar(200, {
            "status": "online",
            "sistema": "EV+ Futebol",
            "versao": "2.1",
            "motor": "Over 1.5",
            "mensagem": "API funcionando"
        })

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

            corpo = self.rfile.read(tamanho)

            if not corpo:
                raise ValueError("Corpo da requisição vazio.")

            dados = json.loads(
                corpo.decode("utf-8")
            )

            odd = self.numero(
                dados.get("odd")
            )

            probabilidade_manual = self.numero(
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
            # VALIDAÇÃO
            # =================================================

            if odd is None or odd <= 1:
                raise ValueError(
                    "A odd deve ser maior que 1."
                )

            if (
                probabilidade_manual is None
                or probabilidade_manual <= 0
                or probabilidade_manual > 100
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
            # MODELO OVER 1.5
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

            if prob_modelo is not None:

                probabilidade = (
                    probabilidade_manual * 0.70
                    +
                    prob_modelo * 0.30
                )

            else:

                probabilidade = (
                    probabilidade_manual
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

            stake_maxima = (
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
                    stake_maxima
                )

            else: