from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL — MOTOR DE GOLS v4
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
            "versao": "4.0",
            "motor": "Gols",
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
            # MOTOR DE GOLS
            # =================================================

            prob_modelo = self.modelo_gols(
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

                # A probabilidade manual continua tendo
                # peso maior nesta primeira versão.

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

            prob = (
                probabilidade / 100
            )

            prob_implicita = (
                1 / odd
            ) * 100

            ev = (
                prob * odd
            ) - 1

            ev_percentual = ev * 100

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

            stake = 0.00

            if decisao == "ENTRA":

                stake = banca * STAKE_PADRAO

                limite = (
                    banca *
                    STAKE_MAXIMA
                )

                stake = min(
                    stake,
                    limite
                )

            else:

                limite = (
                    banca *
                    STAKE_MAXIMA
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

                "versao": "4.0",

                "motor": "gols",

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
    # MOTOR ESTATÍSTICO DE GOLS
    # =====================================================

    def modelo_gols(
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
                self.prob_over25_xg(
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
                self.prob_over25_xg(
                    total_xgot
                )
            )


        # -------------------------------------------------
        # VOLUME DE FINALIZAÇÕES
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

                valores.append(65)

            elif total_final >= 20:

                valores.append(58)

            elif total_final >= 15:

                valores.append(52)

            elif total_final >= 10:

                valores.append(45)


        # -------------------------------------------------
        # CHUTES NO ALVO
        # -------------------------------------------------

        if (
            alvo_casa is not None
            and alvo_fora is not None
        ):

            total_alvo = (
                alvo_casa +
                alvo_fora
            )

            if total_alvo >= 8:

                valores.append(68)

            elif total_alvo >= 6:

                valores.append(60)

            elif total_alvo >= 4:

                valores.append(53)

            elif total_alvo >= 2:

                valores.append(46)


        # -------------------------------------------------
        # GRANDES CHANCES
        # -------------------------------------------------

        if (
            chances_casa is not None
            and chances_fora is not None
        ):

            total_chances = (
                chances_casa +
                chances_fora
            )

            if total_chances >= 4:

                valores.append(70)

            elif total_chances >= 3:

                valores.append(62)

            elif total_chances >= 2:

                valores.append(54)

            elif total_chances >= 1:

                valores.append(47)


        if not valores:

            return None


        # -------------------------------------------------
        # MÉDIA DO MODELO
        # -------------------------------------------------

        prob = sum(valores) / len(valores)


        # -------------------------------------------------
        # AJUSTE LIVE
        # -------------------------------------------------

        if momento == "live":

            minuto_num = (
                minuto
                if minuto is not None
                else 0
            )

            # No segundo tempo, a interpretação do
            # volume muda conforme o tempo restante.

            if minuto_num >= 75:

                prob -= 5

            elif minuto_num >= 60:

                prob -= 2


        return max(
            5,
            min(
                95,
                prob
            )
        )


    # =====================================================
    # CONVERSÃO xG → PROBABILIDADE OVER 2.5
    # =====================================================

    def prob_over25_xg(
        self,
        xg
    ):

        if xg <= 0:

            return 5


        # Distribuição de Poisson.
        # P(X > 2) = 1 - P(0) - P(1) - P(2)

        p0 = math.exp(-xg)

        p1 = (
            p0 *
            xg
        )

        p2 = (
            p1 *
            xg /
            2
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


    # =====================================================
    # RISCO
    # =====================================================

    def calcular_risco(
        self,
        momento,
        minuto,
        mercado,
        prob_modelo,
        xg_casa,
        xg_fora,
        final_casa,
        final_fora
    ):

        pontos = 0


        if prob_modelo is None:

            pontos += 2


        if momento == "live":

            if minuto is None:

                pontos += 1

            if (
                xg_casa is None
                or xg_fora is None
            ):

                pontos += 1


        if "over" in mercado.lower():

            if (
                xg_casa is not None
                and xg_fora is not None
            ):

                total_xg = (
                    xg_casa +
                    xg_fora
                )

                if total_xg < 0.80:

                    pontos += 2


        if pontos >= 4:

            return "ALTO"

        if pontos >= 2:

            return "MÉDIO"

        return "BAIXO"


    # =====================================================
    # DECISÃO
    # =====================================================

    def decisao(
        self,
        ev,
        risco
    ):

        if ev < 0:

            return "PASSA"


        if ev < 3:

            return "AGUARDA"


        if (
            risco == "ALTO"
            and ev < 8
        ):

            return "AGUARDA"


        if ev >= 5:

            return "ENTRA"


        return "AGUARDA"


    # =====================================================
    # CLASSIFICAÇÃO
    # =====================================================

    def classificacao(
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

    def motivos(
        self,
        prob_manual,
        prob_modelo,
        prob_final,
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


        lista.append(
            "Probabilidade final combina "
            "a estimativa informada com o "
            "modelo estatístico."
        )


        if prob_modelo is not None:

            lista.append(
                f"Probabilidade calculada pelo "
                f"modelo: {prob_modelo:.2f}%."
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
            f"Risco: {risco}."
        )


        return lista


    # =====================================================
    # NÚMERO
    # =====================================================

    def numero(
        self,
        valor
    ):

        if value_empty(valor):

            return None

        try:

            numero = float(valor)

            if numero < 0:

                return None

            return numero

        except:

            return None


    # =====================================================
    # HTTP
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

        self.send_heade