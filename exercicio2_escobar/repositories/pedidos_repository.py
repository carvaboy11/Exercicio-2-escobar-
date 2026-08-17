pedidos = []
proximo_id = 1


def salvar(pedido):
    global proximo_id
    pedido["id"] = proximo_id
    pedidos.append(pedido)
    proximo_id += 1
    return pedido


def buscar_por_id(id_pedido):
    for pedido in pedidos:
        if pedido["id"] == id_pedido:
            return pedido
    return None


def listar():
    return pedidos
