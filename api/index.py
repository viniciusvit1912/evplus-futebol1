from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL
# MOTOR EV+ — FASE 2
# Mercados:
# Over 1.5
# Over 2.5
# Under 2.5
# BTTS
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
                "versao": "6.0",
                "fase": "2",
                "motor": "Gols",
                "mercados": [
                    "Over 1.5",
                    "Over 2.5",
                    "Under 2.5",
                    "BTTS"
                ],
                "mensagem": "Motor EV+ Fase 2 funcionando"
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
                    "0"
                )
            )

            corpo = self.rfile.read(
                tamanho
            )

            dados = json.loads(
                corpo.decode("utf-8")
            )

            # -------------------------------------------------
            # DADOS PRINCIPAIS
            # -------------------------------------------------

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
                    "0-0"
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
                prob_manual is None
                or prob_manual <= 0
                or prob_manual > 100
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


            # -------------------------------------------------
            # FILTRO EV+ CASA/FORA
            # -------------------------------------------------

            gols_marcados_casa = self.numero(
                dados.get("golsMarcadosCasa")
            )

            gols_sofridos_fora = self.numero(
                dados.get("golsSofridosFora")
            )

            filtro_ev1 = (
                gols_marcados_casa is not None
                and gols_marcados_casa >= 1.40
            )

            filtro_ev2 = (
                gols_sofridos_fora is not None
                and gols_sofridos_fora >= 1.20
            )

            intersecao_ev = (
                filtro_ev1
                and filtro_ev2
            )


            # -------------------------------------------------
            # MODELO
            # -------------------------------------------------

            prob_modelo = self.modelo_gols(
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


            # -------------------------------------------------
            # PROBABILIDADE FINAL
            # -------------------------------------------------

            if prob_modelo is not None:

                probabilidade = (
                    prob_manual * 0.50
                    +
                    prob_modelo * 0.50
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


            # -------------------------------------------------
            # EV
            # -------------------------------------------------

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


            # -------------------------------------------------
            # RISCO
            # -------------------------------------------------

            risco = self.calcular_risco(
                mercado=mercado,
                momento=momento,
                minuto=minuto,
                prob_modelo=prob_modelo,
                xg_casa=xg_casa,
                xg_fora=xg_fora
            )


            # -------------------------------------------------
            # DECISÃO
            # -------------------------------------------------

            decisao = self.decisao(
                ev,
                risco
            )


            classificacao = self.classificacao(
                ev,
                risco,
                decisao
            )


            # -------------------------------------------------
            # BANCA
            # -------------------------------------------------

            if momento == "live":

                banca = BANCA_LIVE

            else:

                banca = BANCA_PRE_JOGO


            # -------------------------------------------------
            # STAKE
            # -------------------------------------------------

            if decisao == "ENTRA":

                stake = banca * STAKE_PADRAO

            else:

                stake = 0.00


            stake_maxima = (
                banca * STAKE_MAXIMA
            )


            # -------------------------------------------------
            # MOTIVOS
            # -------------------------------------------------

            motivos = self.motivos(
                mercado=mercado,
                prob_manual=prob_manual,
                prob_modelo=prob_modelo,
                ev=ev,
                risco=risco,
                filtro_ev1=filtro_ev1,
                filtro_ev2=filtro_ev2,
                intersecao_ev=intersecao_ev,
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


            # -------------------------------------------------
            # RESPOSTA
            # -------------------------------------------------

            resposta = {

                "status": "ok",

                "sistema": "EV+ Futebol",

                "versao": "6.0",

                "fase": "2",

                "motor": "Gols",

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

                "filtros": {

                    "ev1_forca_ofensiva_casa":
                        filtro_ev1,

                    "ev2_vulnerabilidade_visitante":
                        filtro_ev2,

                    "intersecao_prioritaria":
                        intersecao_ev

                },

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
    # MODELO DE GOLS
    # =====================================================

    def modelo_gols(
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

        valores = []

        total_xg = None


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
                self.probabilidade_mercado(
                    total_xg,
                    mercado
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
                self.probabilidade_mercado(
                    total_xgot,
                    mercado
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

                valores.append(75)

            elif total >= 20:

                valores.append(68)

            elif total >= 15:

                valores.append(60)

            elif total >= 10:

                valores.append(52)


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

                valores.append(78)

            elif total >= 6:

                valores.append(70)

            elif total >= 4:

                valores.append(61)

            elif total >= 2:

                valores.append(52)


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

                valores.append(82)

            elif total >= 3:

                valores.append(72)

            elif total >= 2:

                valores.append(62)

            elif total >= 1:

                valores.append(53)


        if not valores:

            return None


        prob = (
            sum(valores) /
            len(valores)
        )


        # -------------------------------------------------
        # AJUSTE LIVE
        # -------------------------------------------------

        if momento == "live":

            minuto_num = (
                minuto
                if minuto is not None
                else 0
            )

            if minuto_num >= 75:

                prob -= 8

            elif minuto_num >= 60:

                prob -= 4


        return max(
            5,
            min(
                95,
                prob
            )
        )


    # =====================================================
    # PROBABILIDADE POR MERCADO
    # =====================================================

    def probabilidade_mercado(
        self,
        xg,
        mercado
    ):

        mercado_lower = (
            mercado.lower()
        )


        # -------------------------------------------------
        # OVER 1.5
        # -------------------------------------------------

        if "over 1.5" in mercado_lower:

            # P(X >= 2)

            p0 = math.exp(-xg)

            p1 = (
                p0 * xg
            )

            prob = (
                1 -
                p0 -
                p1
            ) * 100

            return max(
                5,
                min(
                    95,
                    prob
                )
            )


        # -------------------------------------------------
        # OVER 2.5
        # -------------------------------------------------

        if "over 2.5" in mercado_lower:

            p0 = math.exp(-xg)

            p1 = (
                p0 * xg
            )

            p2 = (
                p1 * xg / 2
            )

            prob = (
                1 -
                p0 -
                p1 -
                p2
            ) * 100

            return max(
                5,
                min(
                    95,
                    prob
                )
            )


        # -------------------------------------------------
        # UNDER 2.5
        # -------------------------------------------------

        if "under 2.5" in mercado_lower:

            p0 = math.exp(-xg)

            p1 = (
                p0 * xg
            )

            p2 = (
                p1 * xg / 2
            )

            prob = (
                p0 +
                p1 +
                p2
            ) * 100

            return max(
                5,
                min(
                    95,
                    prob
                )
            )


        # -------------------------------------------------
        # BTTS
        # -------------------------------------------------

        if (
            "btts" in mercado_lower
            or "ambas" in mercado_lower
        ):

            if xg <= 0:

                return 5


            # Aproximação independente:
            # P(casa marca) * P(fora marca)

            p_casa = (
                1 -
                math.exp(-xg * 0.55)
            )

            p_fora = (
                1 -
                math.exp(-xg * 0.45)
            )

            prob = (
                p_casa *
                p_fora
            ) * 100

            return max(
                5,
                min(
                    95,
                    prob
                )
            )


        # -------------------------------------------------
        # PADRÃO
        # -------------------------------------------------

        p0 = math.exp(-xg)

        p1 = (
            p0 * xg
        )

        prob = (
            1 -
            p0 -
            p1
        ) * 100

        return max(
            5,
            min(
                95,
                prob
            )
        )


    # =====================================================
    # RISCO
    # =====================================================

    def calcular_risco(
        self,
        mercado,
        momento,
        minuto,
        prob_modelo,
        xg_casa,
        xg_fora
  