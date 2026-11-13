"""
Gera a página docs/index.html a partir do orcamentos.csv.

Como rodar:
    python gerar_relatorio.py

Depois é só abrir docs/index.html no navegador (dois cliques).
Só precisa do pandas; o resto é da biblioteca padrão do Python.
"""

from html import escape
from pathlib import Path
from string import Template

import pandas as pd

PASTA = Path(__file__).parent
MESES = {1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}


# ---------------------------------------------------------------
# Funções de formatação (padrão brasileiro: 1.234,56)
# ---------------------------------------------------------------
def brl(valor, casas=2):
    texto = f"{valor:,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def pct(valor):
    return f"{valor:.1f}".replace(".", ",") + "%"


# ---------------------------------------------------------------
# PARTE 1: ler os dados e calcular (mesma lógica do analise.py)
# ---------------------------------------------------------------
orcamentos = pd.read_csv(PASTA / "orcamentos.csv", parse_dates=["data"])
orcamentos["area_m2"] = orcamentos["largura_m"] * orcamentos["altura_m"]
orcamentos["valor"] = orcamentos["area_m2"] * orcamentos["preco_m2"]
orcamentos["aprovado"] = orcamentos["status"] == "aprovado"

qtd = len(orcamentos)
total = orcamentos["valor"].sum()
ticket = orcamentos["valor"].mean()
taxa_aprovacao = orcamentos["aprovado"].mean() * 100
qtd_pendentes = (orcamentos["status"] == "pendente").sum()

por_produto = orcamentos.groupby("produto")["valor"].agg(["sum", "mean", "count"])
por_produto = por_produto.sort_values("sum", ascending=False)

aprov_vidro = (orcamentos.groupby("tipo_vidro")["aprovado"].mean() * 100).sort_values(ascending=False)

valor_mes = orcamentos.groupby(orcamentos["data"].dt.to_period("M"))["valor"].sum()

inicio = orcamentos["data"].min()
fim = orcamentos["data"].max()
periodo = f"{MESES[inicio.month]}/{inicio.year} a {MESES[fim.month]}/{fim.year}"


# ---------------------------------------------------------------
# PARTE 2: conclusões geradas a partir dos números
# ---------------------------------------------------------------
produto_top = por_produto.index[0]
parte_top = por_produto.iloc[0]["sum"] / total * 100
qtd_top = int(por_produto.iloc[0]["count"])
vidro_top = aprov_vidro.index[0]
vidro_pior = aprov_vidro.index[-1]
mes_top = valor_mes.idxmax()

PLURAL = {"janela": "Janelas", "porta": "Portas", "painel": "Painéis"}
MESES_COMPLETOS = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
                   7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}

conclusoes = [
    f"<strong>{PLURAL.get(produto_top, produto_top.capitalize() + 's')}</strong> somam {pct(parte_top)} do valor total "
    f"({brl(por_produto.iloc[0]['sum'])}), com apenas {qtd_top} orçamentos.",
    f"Vidro <strong>{vidro_top}</strong> tem a maior aprovação ({pct(aprov_vidro.iloc[0])}); "
    f"o <strong>{vidro_pior}</strong> tem a menor ({pct(aprov_vidro.iloc[-1])}).",
    f"<strong>{MESES_COMPLETOS[mes_top.month]}</strong> foi o mês de maior valor orçado ({brl(valor_mes.max())}).",
]
html_conclusoes = "\n".join(f"      <li>{c}</li>" for c in conclusoes)


# ---------------------------------------------------------------
# PARTE 3: gráficos feitos só com HTML e CSS
# ---------------------------------------------------------------
def barras_horizontais(rotulos, valores, textos, maximo):
    """Uma linha por item: rótulo, barra proporcional e valor. A maior barra fica laranja."""
    linhas = []
    for i, (rotulo, valor, texto) in enumerate(zip(rotulos, valores, textos)):
        largura = valor / maximo * 100
        destaque = " destaque" if i == 0 else ""
        linhas.append(
            f'      <div class="barra-linha">'
            f'<span class="barra-rotulo">{escape(str(rotulo))}</span>'
            f'<div class="barra-trilho"><div class="barra{destaque}" style="width:{largura:.1f}%"></div></div>'
            f'<span class="barra-valor">{texto}</span></div>'
        )
    return "\n".join(linhas)


grafico_produto = barras_horizontais(
    por_produto.index, por_produto["sum"],
    [brl(v) for v in por_produto["sum"]], por_produto["sum"].max(),
)
grafico_vidro = barras_horizontais(
    aprov_vidro.index, aprov_vidro.values,
    [pct(v) for v in aprov_vidro.values], 100,
)

colunas, nomes = [], []
for mes, valor in valor_mes.items():
    altura = valor / valor_mes.max() * 85  # em % da altura da área do gráfico
    destaque = " destaque" if mes == mes_top else ""
    colunas.append(
        f'        <div class="coluna"><span class="num">{brl(valor, 0)}</span>'
        f'<div class="pilar{destaque}" style="height:{altura:.1f}%"></div></div>'
    )
    nomes.append(f"        <span>{MESES[mes.month]}/{mes.year}</span>")
grafico_mes = (
    '      <div class="colunas">\n' + "\n".join(colunas) + "\n      </div>\n"
    '      <div class="nomes-meses">\n' + "\n".join(nomes) + "\n      </div>"
)


# ---------------------------------------------------------------
# PARTE 4: linhas da tabela
# ---------------------------------------------------------------
linhas = []
for _, r in orcamentos.iterrows():
    area = f"{r['area_m2']:.2f}".replace(".", ",")
    linhas.append(
        "          <tr>"
        f"<td>{r['id']:04d}</td>"
        f"<td>{r['data'].strftime('%d/%m/%Y')}</td>"
        f"<td>{escape(r['cliente'])}</td>"
        f"<td>{r['produto'].capitalize()}</td>"
        f"<td>{r['tipo_vidro'].capitalize()}</td>"
        f"<td class='num'>{area}</td>"
        f"<td class='num'>{brl(r['valor'])}</td>"
        f"<td><span class='selo {r['status']}'>{r['status'].capitalize()}</span></td>"
        "</tr>"
    )


# ---------------------------------------------------------------
# PARTE 5: juntar tudo no template e salvar
# ---------------------------------------------------------------
template = Template((PASTA / "template" / "relatorio.html").read_text(encoding="utf-8"))
css = (PASTA / "template" / "estilo.css").read_text(encoding="utf-8")

pagina = template.substitute(
    css=css,
    qtd=qtd,
    qtd_pendentes=qtd_pendentes,
    total=brl(total),
    ticket=brl(ticket),
    aprovacao=pct(taxa_aprovacao),
    periodo=periodo,
    conclusoes=html_conclusoes,
    grafico_produto=grafico_produto,
    grafico_vidro=grafico_vidro,
    grafico_mes=grafico_mes,
    linhas="\n".join(linhas),
)

saida = PASTA / "docs" / "index.html"
saida.parent.mkdir(exist_ok=True)
saida.write_text(pagina, encoding="utf-8")
print(f"Página gerada: {saida}")
