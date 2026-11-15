'''
Regras de negócio dos orçamentos (Preços, lista de opções e cálculos)
'''

# Preço por m² de cada tipo de vidro(baseado no arquivo CSV do projeto.)
PRECOS_M2 = {"comum": 180.0, "temperado": 320.0, "laminado": 420.0}
PRODUTOS = ["janela", "porta", "painel"]
STATUS = ["pendente", "aprovado", "recusado"]

def calcular_area(largura_m, altura_m):
    """Área em m²."""
    return largura_m * altura_m

def calcular_valor(largura_m, altura_m, preco_m2):
    """Valor do orçamento em reais: área x preço por m²."""
    return round(calcular_area(largura_m, altura_m) * preco_m2, 2)

