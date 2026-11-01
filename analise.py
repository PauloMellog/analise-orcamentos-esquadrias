"""
Experimento em dados: análise de orçamentos de esquadrias.

Lê o arquivo orcamentos.csv e calcula:
- valor total e média por tipo de produto
- taxa de aprovação geral e por tipo de vidro
- valor total orçado por mês
Os dados do orcamentos.csv são FICTÍCIOS

Como rodar:
    pip install pandas matplotlib
    python analise.py
"""

import pandas as pd

# ---------------------------------------------------------------
# PARTE 1 : carregar os dados e calcular área e valor
# ---------------------------------------------------------------
orcamentos = pd.read_csv("orcamentos.csv", parse_dates=["data"])

orcamentos["area_m2"] = orcamentos["largura_m"] * orcamentos["altura_m"]
orcamentos["valor"] = orcamentos["area_m2"] * orcamentos["preco_m2"]

print("=== Primeiras linhas ===")
print(orcamentos.head())
print("\n === Resumo geral ===")
print(f"Total de orçamentos: {len(orcamentos)}")
print(f"Valor total orçado: R$ {orcamentos['valor'].sum():,.2f}")

# ---------------------------------------------------------------
# PARTE 2: valor total e média por produto (janela, porta, painel)
# ---------------------------------------------------------------
resumo_produto = orcamentos.groupby("produto")["valor"].agg(["sum", "mean", "count"])
print("===Valor total e média===")
print(resumo_produto)


# ---------------------------------------------------------------
# PARTE 3: taxa de aprovação (% de orçamentos com status "aprovado") 
# e taxa por tipo de vidro.
# ---------------------------------------------------------------
print("===Taxa de aprovação===")
aprovacao_orcamentos = (orcamentos["status"] == "aprovado").mean() * 100
print(f"A porcentagem de aprovação dos orçamentos é de: {aprovacao_orcamentos}%.")
orcamentos["aprovados"] = orcamentos["status"] == "aprovado"
aprovacao_tipos = orcamentos.groupby("tipo_vidro")["aprovados"].mean() * 100
print("\n=== Taxa de aprovação por tipo de vidro ===")
for tipo_vidro, aprovados in aprovacao_tipos.items():
    print(f"{tipo_vidro:<12} {aprovados:>6.1f}%")


# ---------------------------------------------------------------
# PARTE 4: valor orçado por mês
# ---------------------------------------------------------------
# TODO: calcular o valor orçado no mês


# ---------------------------------------------------------------
# PARTE 5: um gráfico (salve como grafico.png e coloque no README)
# ---------------------------------------------------------------
# TODO: plotar o gráfico de barras do valor orçado e gerar um png.
