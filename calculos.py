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

def validar_orcamento(cliente, produto, largura_m, altura_m, tipo_vidro):
    """Devolve uma lista de mensagens de erro para dados inválidos"""
    erros = []
    if not str(cliente).strip():
        erros.append("Informe o nome do cliente")
    if produto not in PRODUTOS:
        erros.append(f"Produto inválido: {produto}.")
    if largura_m is None or largura_m <= 0:
        erros.append("Largura inválida.")
    if altura_m is None or altura_m <= 0:
        erros.append("Altura inválida.")
    if tipo_vidro not in PRECOS_M2:
        erros.append(f"tipo de vidro inválido: {tipo_vidro}.")
    return erros

