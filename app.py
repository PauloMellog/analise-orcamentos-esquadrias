"""
Painel interativo de orçamentos de esquadrias feito com streamlit (somente leitura).

Mostra os dados do orcamentos.csv com filtros, gráficos e uma calculadora de
simulação.Os dados só mudam se o CSV mudar.

Como rodar:
    pip install -r requirements.txt
    streamlit run app.py
"""

import inspect

import streamlit as st

import calculos
import dados

st.set_page_config(page_title="Orçamentos de esquadrias", page_icon="🪟", layout="wide")


def brl(valor):
    """1234.5 -> 'R$ 1.234,50'"""
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def pct(valor):
    return f"{valor:.1f}".replace(".", ",") + "%"


@st.cache_data
def carregar_dados():
    """Lê o CSV uma vez só (o Streamlit guarda o resultado)."""
    return dados.carregar()


# ---------------------------------------------------------------
# Cabeçalho e carregamento dos dados
# ---------------------------------------------------------------
st.title("Orçamentos de esquadrias")
st.caption("Painel interativo feito com Python, pandas e Streamlit.")

try:
    todos = carregar_dados()
except (FileNotFoundError, ValueError) as erro:
    st.error(f"Não foi possível carregar os dados: {erro}")
    st.stop()

for aviso in dados.checar(todos):
    st.warning(aviso)

# ---------------------------------------------------------------
# Filtros na lateral
# ---------------------------------------------------------------
st.sidebar.header("Filtros")
status = st.sidebar.multiselect("Status", calculos.STATUS, default=calculos.STATUS)
produtos = st.sidebar.multiselect("Produto", calculos.PRODUTOS, default=calculos.PRODUTOS)
vidros = st.sidebar.multiselect("Tipo de vidro", list(calculos.PRECOS_M2),
                                default=list(calculos.PRECOS_M2))
meses_disponiveis = sorted(todos["mes"].unique())
meses = st.sidebar.multiselect("Mês", meses_disponiveis, default=meses_disponiveis)

filtrados = dados.filtrar(todos, status, produtos, vidros, meses)

aba_painel, aba_calc, aba_codigo = st.tabs(["Painel", "Calculadora", "Como foi feito"])

# ---------------------------------------------------------------
# Aba 1: painel
# ---------------------------------------------------------------
with aba_painel:
    if filtrados.empty:
        st.info("Nenhum orçamento com esses filtros. Marque mais opções na lateral.")
    else:
        numeros = dados.indicadores(filtrados)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total orçado", brl(numeros["total"]))
        c2.metric("Orçamentos", numeros["qtd"])
        c3.metric("Ticket médio", brl(numeros["ticket"]))
        c4.metric("Taxa de aprovação", pct(numeros["aprovacao"]),
                  help="Orçamentos pendentes contam como não aprovados.")

        esquerda, direita = st.columns(2)
        with esquerda:
            st.subheader("Valor orçado por produto")
            st.bar_chart(dados.valor_por_produto(filtrados), color="#2F80ED")
        with direita:
            st.subheader("Aprovação por tipo de vidro (%)")
            st.bar_chart(dados.aprovacao_por_vidro(filtrados), color="#F2994A")

        st.subheader("Valor orçado por mês")
        st.bar_chart(dados.valor_por_mes(filtrados), color="#2F80ED")

        st.subheader("Orçamentos")
        st.dataframe(
            filtrados[["id", "data", "cliente", "produto", "tipo_vidro",
                       "largura_m", "altura_m", "area_m2", "valor", "status"]],
            hide_index=True,
            use_container_width=True,
            column_config={
                "id": st.column_config.NumberColumn("Nº", format="%d"),
                "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
                "cliente": "Cliente",
                "produto": "Produto",
                "tipo_vidro": "Vidro",
                "largura_m": st.column_config.NumberColumn("Largura (m)", format="%.2f"),
                "altura_m": st.column_config.NumberColumn("Altura (m)", format="%.2f"),
                "area_m2": st.column_config.NumberColumn("Área (m²)", format="%.2f"),
                "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                "status": "Status",
            },
        )
        st.caption(f"{len(filtrados)} de {len(todos)} orçamentos exibidos.")

# ---------------------------------------------------------------
# Aba 2: calculadora de simulação
# ---------------------------------------------------------------
with aba_calc:
    st.subheader("Simule o valor de uma esquadria de vidro")
    st.caption("Experimente à vontade: nada digitado aqui é salvo.")

    campos, resultado = st.columns(2)
    with campos:
        tipo_vidro = st.selectbox("Tipo de vidro", list(calculos.PRECOS_M2))
        largura = st.number_input("Largura (m)", min_value=0.1, value=1.0, step=0.05, format="%.2f")
        altura = st.number_input("Altura (m)", min_value=0.1, value=1.0, step=0.05, format="%.2f")
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

    preco_m2 = calculos.PRECOS_M2[tipo_vidro]
    area = calculos.calcular_area(largura, altura)
    unitario = calculos.calcular_valor(largura, altura, preco_m2)

    with resultado:
        st.metric("Valor de cada peça", brl(unitario))
        st.metric("Total", brl(unitario * quantidade))

    st.markdown("**Como o valor foi calculado**")
    st.code(
        f"área     = {largura:.2f} m x {altura:.2f} m = {area:.2f} m²\n"
        f"valor    = {area:.2f} m² x {brl(preco_m2)} por m² = {brl(unitario)}\n"
        f"total    = {brl(unitario)} x {quantidade} = {brl(unitario * quantidade)}",
        language="text",
    )

    st.markdown("**Tabela de preços usada**")
    st.table({"Tipo de vidro": list(calculos.PRECOS_M2),
              "Preço por m²": [brl(p) for p in calculos.PRECOS_M2.values()]})

# ---------------------------------------------------------------
# Aba 3: o código por trás do painel
# ---------------------------------------------------------------
with aba_codigo:
    st.subheader("Como este painel foi feito")
    st.markdown(
        "Os números e gráficos vêm de funções em Python com pandas. "
        "Abaixo está o código real de cada passo, lido do próprio projeto."
    )

    passos = [
        ("1. Carregar o CSV e calcular área e valor", dados.carregar,
         "Lê o arquivo, confere se as colunas existem e calcula `area_m2 = largura x altura` "
         "e `valor = area x preço por m²` para cada orçamento."),
        ("2. Conferir a qualidade dos dados", dados.checar,
         "Procura campos vazios, números repetidos, opções inválidas e medidas zeradas. "
         "Se achar algo, o painel mostra um aviso amarelo no topo."),
        ("3. Calcular os indicadores", dados.indicadores,
         "Total, quantidade, ticket médio e taxa de aprovação. Pendentes contam como não aprovados."),
        ("4. Valor total por produto", dados.valor_por_produto,
         "Agrupa por produto (`groupby`) e soma o valor de cada grupo."),
        ("5. Taxa de aprovação por tipo de vidro", dados.aprovacao_por_vidro,
         "A média de uma coluna Verdadeiro/Falso é a proporção de aprovados."),
        ("6. Valor orçado por mês", dados.valor_por_mes,
         "Agrupa pelo mês (AAAA-MM) e soma o valor."),
        ("7. Aplicar os filtros da lateral", dados.filtrar,
         "Cada filtro escolhido reduz a tabela. Os indicadores e gráficos são recalculados sobre o resultado."),
    ]
    for titulo, funcao, explicacao in passos:
        with st.expander(titulo):
            st.markdown(explicacao)
            st.code(inspect.getsource(funcao), language="python")

    st.markdown("**Tecnologias:** Python, pandas, Streamlit, Git e GitHub.")

st.divider()
st.caption(
    "Feito por Paulo Augusto · "
    "[Código no GitHub](https://github.com/PauloMellog/analise-orcamentos-esquadrias) · "
    "[LinkedIn](https://www.linkedin.com/in/paulo-augusto-82018723a)"
)