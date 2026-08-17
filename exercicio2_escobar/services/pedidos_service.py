from datetime import datetime, timedelta
from collections import defaultdict

from repositories import estoque_repository
from repositories import pedidos_repository
from repositories import clientes_repository

LIMITE_ITENS_DIFERENTES = 5
LIMITE_QUANTIDADE_POR_ITEM = 50
VALOR_MINIMO_PEDIDO = 20
LIMITE_CANCELAMENTO_MINUTOS = 30
ESTOQUE_BAIXO = 5


class ErroDeNegocio(Exception):
    def __init__(self, mensagem, status_sugerido):
        super().__init__(mensagem)
        self.status_sugerido = status_sugerido


def validar_cliente(cliente_id):
    if not cliente_id:
        raise ErroDeNegocio("clienteId é obrigatório", 400)
    if not clientes_repository.cliente_existe(cliente_id):
        raise ErroDeNegocio(f"Cliente inexistente: {cliente_id}", 400)
    if not clientes_repository.cliente_ativo(cliente_id):
        raise ErroDeNegocio(f"Cliente inativo: {cliente_id}", 403)


def consolidar_itens(itens):
    if not isinstance(itens, list) or not itens:
        raise ErroDeNegocio("itens deve ser uma lista não vazia", 400)

    quantidades = defaultdict(int)
    precos = {}

    for item in itens:
        if "sku" not in item or "quantidade" not in item or "precoUnitario" not in item:
            raise ErroDeNegocio("cada item precisa de sku, quantidade e precoUnitario", 400)
        if item["quantidade"] <= 0:
            raise ErroDeNegocio(f"quantidade inválida para {item['sku']}", 400)
        if item["precoUnitario"] < 0:
            raise ErroDeNegocio(f"precoUnitario inválido para {item['sku']}", 400)

        sku = item["sku"]
        quantidades[sku] += item["quantidade"]
        precos[sku] = item["precoUnitario"]

    if len(quantidades) > LIMITE_ITENS_DIFERENTES:
        raise ErroDeNegocio(f"pedido não pode ter mais de {LIMITE_ITENS_DIFERENTES} produtos diferentes", 400)

    itens_consolidados = []
    for sku, quantidade in quantidades.items():
        if quantidade > LIMITE_QUANTIDADE_POR_ITEM:
            raise ErroDeNegocio(f"quantidade acima do limite para {sku}", 400)
        itens_consolidados.append({
            "sku": sku,
            "quantidade": quantidade,
            "precoUnitario": precos[sku],
        })

    return itens_consolidados


def verificar_estoque(itens):
    for item in itens:
        disponivel = estoque_repository.consultar_disponibilidade(item["sku"])
        if disponivel is None:
            raise ErroDeNegocio(f"SKU inexistente: {item['sku']}", 400)
        if disponivel < item["quantidade"]:
            raise ErroDeNegocio(f"Estoque insuficiente para {item['sku']}", 409)


def calcular_valores(itens):
    subtotal = sum(item["precoUnitario"] * item["quantidade"] for item in itens)
    quantidade_total = sum(item["quantidade"] for item in itens)

    if subtotal < VALOR_MINIMO_PEDIDO:
        raise ErroDeNegocio(f"valor do pedido abaixo do mínimo de R$ {VALOR_MINIMO_PEDIDO}", 400)

    percentual_desconto = 0
    if subtotal >= 500:
        percentual_desconto = 0.10
    elif quantidade_total >= 10:
        percentual_desconto = 0.05

    desconto = round(subtotal * percentual_desconto, 2)
    total = round(subtotal - desconto, 2)

    return subtotal, desconto, total


def criar_pedido(cliente_id, itens):
    validar_cliente(cliente_id)
    itens_consolidados = consolidar_itens(itens)
    verificar_estoque(itens_consolidados)

    subtotal, desconto, total = calcular_valores(itens_consolidados)

    estoque_baixo = []
    for item in itens_consolidados:
        estoque_repository.baixar_estoque(item["sku"], item["quantidade"])
        restante = estoque_repository.consultar_disponibilidade(item["sku"])
        if restante <= ESTOQUE_BAIXO:
            estoque_baixo.append(item["sku"])

    pedido = {
        "clienteId": cliente_id,
        "itens": itens_consolidados,
        "subtotal": subtotal,
        "desconto": desconto,
        "total": total,
        "status": "confirmado",
        "criadoEm": datetime.utcnow().isoformat(),
        "estoqueBaixo": estoque_baixo,
    }

    return pedidos_repository.salvar(pedido)


def buscar_pedido(id_pedido):
    pedido = pedidos_repository.buscar_por_id(id_pedido)
    if pedido is None:
        raise ErroDeNegocio("Pedido não encontrado", 404)
    return pedido


def listar_pedidos(cliente_id=None):
    todos = pedidos_repository.listar()
    if cliente_id is None:
        return todos
    return [pedido for pedido in todos if pedido["clienteId"] == cliente_id]


def cancelar_pedido(id_pedido):
    pedido = buscar_pedido(id_pedido)

    if pedido["status"] == "cancelado":
        raise ErroDeNegocio("Pedido já está cancelado", 409)
    if pedido["status"] == "entregue":
        raise ErroDeNegocio("Pedido entregue não pode ser cancelado", 409)

    criado_em = datetime.fromisoformat(pedido["criadoEm"])
    prazo_limite = criado_em + timedelta(minutes=LIMITE_CANCELAMENTO_MINUTOS)
    if datetime.utcnow() > prazo_limite:
        raise ErroDeNegocio(f"prazo de {LIMITE_CANCELAMENTO_MINUTOS} minutos para cancelamento expirou", 409)

    for item in pedido["itens"]:
        estoque_repository.repor_estoque(item["sku"], item["quantidade"])

    pedido["status"] = "cancelado"
    return pedido


def confirmar_entrega(id_pedido):
    pedido = buscar_pedido(id_pedido)

    if pedido["status"] == "cancelado":
        raise ErroDeNegocio("Pedido cancelado não pode ser entregue", 409)
    if pedido["status"] == "entregue":
        raise ErroDeNegocio("Pedido já foi entregue", 409)

    pedido["status"] = "entregue"
    return pedido
