from http.server import BaseHTTPRequestHandler
import json
import math


# =========================================================
# EV+ FUTEBOL — FASE 2
# MOTOR ESTRATÉGICO
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03

VERSAO = "6.0"


class handler(BaseHTTPRequestHandler):

    # =====================================================
    # UTILITÁRIOS
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


    def numero(self, valor):

        if valor is None:
            return None

        if valor == "":
            return None

        try:

            numero = float(valor)

            if not math.isfinite(numero):
                return None

            return numero

        except:

            return None


    def limitar(self, valor, minimo, maximo):

        return max(
            minimo,
            min(
                maximo,
                valor
            )
        )


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
                "versao": VERSAO,
                "motor": "EV+ Fase 2",
                "mensagem": "API funcionando",
                "mercados": [
                    "Over 1.5",
                    "Over 2.5",
                    "Under 2.5",
                    "BTTS"
                ]
            }
        )


    # =====================================================
    # NORMALIZAÇÃO DO MERCADO
    # =====================================================

    def mercado_normalizado(self, mercado):

        texto = str(
            mercado or ""
        ).lower().strip()

        if "over 1.5" in texto:
            return "Over 1.5"

        if "over 2.5" in texto:
            return "Over 2.5"

        if "under 2.5" in texto:
            return "Under 2.5"

        if "btts" in texto:
            return "BTTS"

        if "ambas" in texto:
            return "BTTS"

        return mercado


    # =====================================================
    # MOTOR ESTATÍSTICO
    # =====================================================

    def calcular_suporte_estatistico(
        self,
        mercado,
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
        gols_sofridos_casa,
        gols_sofridos_fora,
        forca_casa,
        forca_fora
    ):

        valores = [
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
            gols_sofridos_casa,
            gols_sofridos_fora
        ]

        disponiveis = [
            x for x in valores
            if x is not None
        ]

        if len(disponiveis) == 0:
            return None

        suporte = 50.0

        xg_total = (
            (xg_casa or 0)
            +
            (xg_fora or 0)
        )

        xgot_total = (
            (xgot_casa or 0)
            +
            (xgot_fora or 0)
        )

        final_total = (
            (final_casa or 0)
            +
            (final_fora or 0)
        )

        alvo_total = (
            (alvo_casa or 0)
            +
            (alvo_fora or 0)
        )

        chances_total = (
            (chances_casa or 0)
            +
            (chances_fora or 0)
        )

        gols_sofridos_total = (
            (gols_sofridos_casa or 0)
            +
            (gols_sofridos_fora or 0)
        )

        # -----------------------------------------------
        # OVER 1.5
        # -----------------------------------------------

        if mercado == "Over 1.5":

            if xg_total >= 2.20:
                suporte += 14

            elif xg_total >= 1.70:
                suporte += 8

            elif xg_total < 1.20 and xg_total > 0:
                suporte -= 10

            if xgot_total >= 1.40:
                suporte += 7

            if alvo_total >= 5:
                suporte += 5

            if chances_total >= 4:
                suporte += 5

            if gols_sofridos_total >= 2:
                suporte += 5


        # -----------------------------------------------
        # OVER 2.5
        # -----------------------------------------------

        elif mercado == "Over 2.5":

            if xg_total >= 2.80:
                suporte += 15

            elif xg_total >= 2.30:
                suporte += 9

            elif xg_total < 1.70 and xg_total > 0:
                suporte -= 12

            if xgot_total >= 1.80:
                suporte += 8

            if alvo_total >= 6:
                suporte += 6

            if chances_total >= 5:
                suporte += 6

            if gols_sofridos_total >= 2:
                suporte += 5


        # -----------------------------------------------
        # UNDER 2.5
        # -----------------------------------------------

        elif mercado == "Under 2.5":

            if xg_total <= 2.00 and xg_total > 0:
                suporte += 12

            elif xg_total <= 2.40 and xg_total > 0:
                suporte += 5

            elif xg_total >= 3.00:
                suporte -= 14

            if xgot_total >= 2.20:
                suporte -= 8

            if final_total >= 25:
                suporte -= 6

            if chances_total >= 6:
                suporte -= 6


        # -----------------------------------------------
        # BTTS
        # -----------------------------------------------

        elif mercado == "BTTS":

            if xg_casa is not None and xg_fora is not None:

                if (
                    xg_casa >= 0.80
                    and xg_fora >= 0.80
                ):
                    suporte += 15

                elif (
                    xg_casa >= 0.60
                    and xg_fora >= 0.60
                ):
                    suporte += 8

                elif (
                    xg_casa < 0.40
                    or xg_fora < 0.40
                ):
                    suporte -= 12

            if xgot_casa is not None and xgot_fora is not None:

                if (
                    xgot_casa >= 0.50
                    and xgot_fora >= 0.50
                ):
                    suporte += 7

            if (
                gols_sofridos_casa is not None
                and gols_sofridos_fora is not None
            ):

                if (
                    gols_sofridos_casa >= 0.80
                    and gols_sofridos_fora >= 0.80
                ):
                    suporte += 8


        # -----------------------------------------------
        # FORÇA CASA/FORA
        # -----------------------------------------------

        if forca_casa is not None:

            if forca_casa >= 70:
                suporte += 3

            elif forca_casa <= 30:
                suporte -= 3


        if forca_fora is not None:

            if forca_fora >= 70:
                suporte += 3

            elif forca_fora <= 30:
                suporte -= 3


        return round(
            self.limitar(
                suporte,
                5,
                95
            ),
            2
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
        xgot_casa,
        xgot_fora,
        final_casa,
        final_fora,
        chances_casa,
        chances_fora
    ):

        risco = 0

        if prob_modelo is None:
            risco += 2

        if momento == "live":

            if minuto is None:
                risco += 2

            elif minuto >= 80:
                risco += 3

            elif minuto >= 70:
                risco += 2

            elif minuto >= 60:
                risco += 1


        estatisticas = [
            xg_casa,
            xg_fora,
            xgot_casa,
            xgot_fora,
            final_casa,
            final_fora,
            chances_casa,
            chances_fora
        ]

        quantidade = len([
            x for x in estatisticas
            if x is not None
        ])

        if quantidade < 2:
            risco += 2

        elif quantidade < 4:
            risco += 1


        if risco <= 1:
            return "BAIXO"

        if risco <= 3:
            return "MODERADO"

        return "ALTO"


    # =====================================================
    # DECISÃO
    # =====================================================

    def decisao(
        self,
        ev,
        risco,
        filtro_1,
        filtro_2
    ):

        if ev < 0:
            return "PASSA"

        if risco == "ALTO":
            return "PASSA"

        if ev < 5:
            return "AGUARDA"

        if not filtro_1:
            return "AGUARDA"

        if ev < 8:
            return "ENTRA"

        if not filtro_2:
            return "AGUARDA"

        return "ENTRA"


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

        if risco == "ALTO":
            return "C"

        if ev >= 8 and risco == "BAIXO":
            return "A"

        if ev >= 5:
            return "B"

        return "C"


    # =====================================================
    # MOTIVOS
    # =====================================================

    def criar_motivos(
        self,
        mercado,
        ev,
        odd,
        odd_justa,
        probabilidade,
        prob_implicita,
        risco,
        filtro_1,
        filtro_2,
        suporte
    ):

        motivos = []

        motivos.append(
            f"Mercado analisado: {mercado}."
        )

        motivos.append(
            f"Probabilidade estimada: {probabilidade:.2f}%."
        )

        motivos.append(
            f"Probabilidade implícita: {prob_implicita:.2f}%."
        )

        motivos.append(
            f"Odd justa: {odd_justa:.2f}."
        )

        motivos.append(
            f"EV calculado: {ev:.2f}%."
        )

        motivos.append(
            f"Risco operacional: {risco}."
        )

        if suporte is not None:

            motivos.append(
                f"Suporte estatístico: {suporte:.2f}/100."
            )

        if filtro_1:
            motivos.append(
                "EV+ 1 aprovado."
            )
        else:
            motivos.append(
                "EV+ 1 não aprovado."
            )

        if filtro_2:
            motivos.append(
                "EV+ 2 aprovado."
            )
        else:
            motivos.append(
                "EV+ 2 não aprovado."
            )

        if ev >= 8 and risco == "BAIXO":
            motivos.append(
                "Cenário apresenta EV forte com risco controlado."
            )

        elif ev >= 5:
            motivos.append(
                "Existe valor matemático, mas exige controle de risco."
            )

        elif ev >= 0:
            motivos.append(
                "EV positivo insuficiente para entrada imediata."
            )

        else:
            motivos.append(
                "EV negativo: não há valor matemático."
            )

        return motivos


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

            if tamanho <= 0:
                raise ValueError(
                    "Corpo da requisição vazio."
                )

            corpo = self.rfile.read(
                tamanho
            )

            dados = json.loads(
                corpo.decode("utf-8")
            )

            # =============================================
            # DADOS BÁSICOS
            # =============================================

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

            mercado = self.mercado_normalizado(
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

            minuto = self.numero(
                dados.get("minuto")
            )

            placar = str(
                dados.get(
                    "placar",
                    ""
                )
            )


            # =============================================
            # APOSTA
            # =============================================

            odd = self.numero(
                dados.get("odd")
            )

            prob_manual = self.numero(
                dados.get("probabilidade")
            )


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


            # =============================================
            # ESTATÍSTICAS
            # =============================================

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

            gols_sofridos_casa = self.numero(
                dados.get("golsSofridosCasa")
            )

            gols_sofridos_fora = self.numero(
                dados.get("golsSofridosFora")
            )

            forca_casa = self.numero(
                dados.get("forcaCasa")
            )

            forca_fora = self.numero(
                dados.get("forcaFora")
            )


            # =============================================
            # SUPORTE ESTATÍSTICO
            # =============================================

            suporte = self.calcular_suporte_estatistico(

                mercado,

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

                gols_sofridos_casa,
                gols_sofridos_fora,

                forca_casa,
                forca_fora
            )


            # =============================================
            # PROBABILIDADE FINAL
            # =============================================

            if suporte is not None:

                # Mantém a probabilidade informada
                # como principal referência.
                probabilidade = (
                    prob_manual * 0.70
                    +
                    suporte * 0.30
                )

            else:

                probabilidade = prob_manual


            probabilidade = self.limitar(
                probabilidade,
                1,
                99
            )


            # =============================================
            # MATEMÁTICA EV
            # =============================================

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


            # =============================================
            # FILTRO EV+ 1
            # =============================================

            filtro_1 = (
                ev >= 5
                and probabilidade > prob_implicita
                and odd >= odd_justa
            )


            # =============================================
            # FILTRO EV+ 2
            # =============================================

            filtro_2 = (

                ev >= 8

                and
                (
                    suporte is None
                    or suporte >= 60
                )

            )


            # =============================================
            # RISCO
            # =============================================

            risco = self.calcular_risco(

                momento=momento,

                minuto=minuto,

                mercado=mercado,

                prob_modelo=suporte,

                xg_casa=xg_casa,
                xg_fora=xg_fora,

                xgot_casa=xgot_casa,
                xgot_fora=xgot_fora,

                final_casa=final_casa,
                final_fora=final_fora,

                chances_casa=chances_casa,
                chances_fora=chances_fora
            )


            # =============================================
            # DECISÃO
            # =============================================

            decisao = self.deci