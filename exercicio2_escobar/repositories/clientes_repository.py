clientes = {
    "c1": {"nome": "Ana Souza", "ativo": True},
    "c2": {"nome": "Carlos Lima", "ativo": True},
    "c3": {"nome": "Marcos Vieira", "ativo": False},
}


def cliente_existe(cliente_id):
    return cliente_id in clientes


def cliente_ativo(cliente_id):
    cliente = clientes.get(cliente_id)
    return cliente is not None and cliente["ativo"]
