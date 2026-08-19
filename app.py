import json
import math


# =========================================================
# EV+ FUTEBOL — MOTOR LOCAL FASE 2
# =========================================================

BANCA_PRE_JOGO = 25.00
BANCA_LIVE = 12.00

STAKE_PADRAO = 0.02
STAKE_MAXIMA = 0.03

VERSAO = "6.0"


def limitar(valor, minimo, maximo):

    return max(
        minimo,
        min(
            maximo,
            valor
        )
    )


def numero(valor):

    if valor is None or valor == "":
        return None

    try:

        valor = float(valor)

        if not math.isfinite(valor):
            return None

        return valor

    except:

        return None


def calcular_ev(probabilidade, odd):

    prob = probabilidade / 100

    probabilidade_implicita = (
        1 / odd
    ) * 100

    ev = (
        prob * odd - 1
    ) * 100

    odd_justa = (
        1 / prob
    )

    return {
        "probabilidade": round(
            probabilidade,
            2
        ),
        "probabilidade_implicita": round(
            probabilidade_implicita,
            2
        ),
        "odd": round(
            odd,
            2
        ),
        "odd_justa": round(
            odd_justa,
            2
        ),
        "ev": round(
            ev,
            2
        )
    }


def analisar(dados):

    odd = numero(
        dados.get("odd")
    )

    probabilidade = numero(
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


    resultado = calcular_ev(
        probabilidade,
        odd
    )


    ev = resultado["ev"]


    # =============================================
    # FILTRO EV+ 1
    # =============================================

    ev_plus_1 = (

        ev >= 5

        and
        probabilidade >
        resultado["probabilidade_implicita"]

        and
        odd >= resultado["odd_justa"]

    )


    # =============================================
    # FILTRO EV+ 2
    # =============================================

    ev_plus_2 = (
        ev >= 8
    )


    # =============================================
    # DECISÃO
    # =============================================

    if ev < 0:

        decisao = "PASSA"
        classificacao = "C"

    elif ev < 5:

        decisao = "AGUARDA"
        classificacao = "C"

    elif ev < 8:

        if ev_plus_1:

            decisao = "ENTRA"
            classificacao = "B"

        else:

            decisao = "AGUARDA"
            classificacao = "C"

    else:

        if ev_plus_2:

            decisao = "ENTRA"
            classificacao = "A"

        else:

            decisao = "AGUARDA"
            classificacao = "B"


    # =============================================
    # BANCA
    # =============================================

    if momento == "live":

        banca = BANCA_LIVE

    else:

        banca = BANCA_PRE_JOGO


    # =============================================
    # STAKE
    # =============================================

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

        stake = 0.00


    return {

        "status": "ok",

        "sistema": "EV+ Futebol",

        "versao": VERSAO,

        "mercado": mercado,

        "momento": momento,

        "decisao": decisao,

        "classificacao": classificacao,

        "risco": (
            "BAIXO"
            if ev >= 8
            else "MODERADO"
            if ev >= 5
            else "ALTO"
            if ev < 0
            else "MODERADO"
        ),

        "odd": resultado["odd"],

        "probabilidade_estimada":
            resultado["probabilidade"],

        "probabilidade_implicita":
            resultado["probabilidade_implicita"],

        "odd_justa":
            resultado["odd_justa"],

        "ev":
            resultado["ev"],

        "filtros": {

            "ev_plus_1":
                ev_plus_1,

            "ev_plus_2":
                ev_plus_2

        },

        "banca":
            round(
                banca,
                2
            ),

        "stake_recomendada":
            round(
                stake,
                2
            ),

        "stake_maxima":
            round(
                stake_maxima,
                2
            ),

        "motivos": [

            f"Mercado: {mercado}.",

            f"EV: {ev:.2f}%.",

            (
                "EV+ 1 aprovado."
                if ev_plus_1
                else
                "EV+ 1 não aprovado."
            ),

            (
                "EV+ 2 aprovado."
                if ev_plus_2
                else
                "EV+ 2 não aprovado."
            ),

            (
                "Entrada liberada pelo motor EV+."
                if decisao == "ENTRA"
                else
                "Entrada não liberada pelo motor EV+."
            )

        ]

    }


if __name__ == "__main__":

    exemplo = {

        "mercado": "Over 1.5",

        "odd": 1.80,

        "probabilidade": 62,

        "momento": "pre"

    }

    print(
        json.dumps(
            analisar(exemplo),
            indent=2,
            ensure_ascii=False
        )
    )