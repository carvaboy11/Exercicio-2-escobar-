estoque = {
    "SKU-CAMISETA-M": 50,
    "SKU-CANECA-BRANCA": 30,
    "SKU-BONE-PRETO": 10,
}


def consultar_disponibilidade(sku):
    return estoque.get(sku)


def baixar_estoque(sku, quantidade):
    estoque[sku] -= quantidade


def repor_estoque(sku, quantidade):
    estoque[sku] += quantidade
