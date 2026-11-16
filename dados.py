"""
Leitura, checagem e análises dos orçamentos.
Este arquivo recebe e devolve tabelas do pandas.
"""

from pathlib import Path

import pandas as pd

import calculos

CAMINHO_CSV = Path(__file__).parent / "orcamentos.csv"
COLUNAS = ["id", "data", "cliente", "produto", "largura_m", "altura_m",
           "tipo_vidro", "preco_m2", "status"]


def carregar(caminho=CAMINHO_CSV):
    """Lê o CSV e calcula área, valor e mês de cada orçamento."""
    tabela = pd.read_csv(caminho, parse_dates=["data"])

    faltando = [c for c in COLUNAS if c not in tabela.columns]
    if faltando:
        raise ValueError("O CSV não tem as colunas: " + ", ".join(faltando))

    tabela["area_m2"] = tabela["largura_m"] * tabela["altura_m"]
    tabela["valor"] = (tabela["area_m2"] * tabela["preco_m2"]).round(2)
    tabela["mes"] = tabela["data"].dt.strftime("%Y-%m")
    tabela["aprovado"] = tabela["status"] == "aprovado"
    return tabela


def checar(tabela):
    """Procura problemas nos dados. Devolve uma lista de avisos."""
    avisos = []

    vazios = tabela[COLUNAS].isna().any(axis=1).sum()
    if vazios:
        avisos.append(f"{vazios} orçamento(s) com campo vazio.")

    repetidos = tabela["id"].duplicated().sum()
    if repetidos:
        avisos.append(f"{repetidos} número(s) de orçamento repetido(s).")

    regras = [
        ("produto fora da lista", ~tabela["produto"].isin(calculos.PRODUTOS)),
        ("tipo de vidro fora da lista", ~tabela["tipo_vidro"].isin(calculos.PRECOS_M2)),
        ("status fora da lista", ~tabela["status"].isin(calculos.STATUS)),
        ("largura ou altura menor ou igual a zero",
         (tabela["largura_m"] <= 0) | (tabela["altura_m"] <= 0)),
    ]
    for descricao, problema in regras:
        qtd = problema.sum()
        if qtd:
            numeros = ", ".join(str(n) for n in tabela.loc[problema, "id"])
            avisos.append(f"{qtd} orçamento(s) com {descricao} (nº {numeros}).")
    return avisos


def filtrar(tabela, status=None, produtos=None, vidros=None, meses=None):
    """Aplica os filtros. Um filtro None é ignorado."""
    if status is not None:
        tabela = tabela[tabela["status"].isin(status)]
    if produtos is not None:
        tabela = tabela[tabela["produto"].isin(produtos)]
    if vidros is not None:
        tabela = tabela[tabela["tipo_vidro"].isin(vidros)]
    if meses is not None:
        tabela = tabela[tabela["mes"].isin(meses)]
    return tabela


def indicadores(tabela):
    """Os quatro números do topo do painel. Pendentes contam como não aprovados."""
    if tabela.empty:
        return {"total": 0.0, "qtd": 0, "ticket": 0.0, "aprovacao": 0.0}
    return {
        "total": tabela["valor"].sum(),
        "qtd": len(tabela),
        "ticket": tabela["valor"].mean(),
        "aprovacao": tabela["aprovado"].mean() * 100,
    }


def valor_por_produto(tabela):
    """Soma do valor orçado em cada produto, do maior para o menor."""
    return tabela.groupby("produto")["valor"].sum().sort_values(ascending=False)


def aprovacao_por_vidro(tabela):
    """Porcentagem de orçamentos aprovados em cada tipo de vidro."""
    taxa = tabela.groupby("tipo_vidro")["aprovado"].mean() * 100
    return taxa.sort_values(ascending=False)


def valor_por_mes(tabela):
    """Soma do valor orçado em cada mês (formato AAAA-MM, em ordem de data)."""
    return tabela.groupby("mes")["valor"].sum()