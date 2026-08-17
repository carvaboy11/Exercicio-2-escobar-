from flask import Blueprint, request, jsonify
from services import pedidos_service
from services.pedidos_service import ErroDeNegocio

pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    try:
        dados = request.get_json(force=True)
        cliente_id = dados.get("clienteId")
        itens = dados.get("itens")
        pedido = pedidos_service.criar_pedido(cliente_id, itens)
        return jsonify(pedido), 201
    except ErroDeNegocio as erro:
        return jsonify({"erro": str(erro)}), erro.status_sugerido


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_pedidos():
    cliente_id = request.args.get("clienteId")
    pedidos = pedidos_service.listar_pedidos(cliente_id)
    return jsonify(pedidos)


@pedidos_bp.route("/pedidos/<int:id_pedido>", methods=["GET"])
def buscar_pedido(id_pedido):
    try:
        pedido = pedidos_service.buscar_pedido(id_pedido)
        return jsonify(pedido)
    except ErroDeNegocio as erro:
        return jsonify({"erro": str(erro)}), erro.status_sugerido


@pedidos_bp.route("/pedidos/<int:id_pedido>/cancelar", methods=["POST"])
def cancelar_pedido(id_pedido):
    try:
        pedido = pedidos_service.cancelar_pedido(id_pedido)
        return jsonify(pedido)
    except ErroDeNegocio as erro:
        return jsonify({"erro": str(erro)}), erro.status_sugerido


@pedidos_bp.route("/pedidos/<int:id_pedido>/entregar", methods=["POST"])
def confirmar_entrega(id_pedido):
    try:
        pedido = pedidos_service.confirmar_entrega(id_pedido)
        return jsonify(pedido)
    except ErroDeNegocio as erro:
        return jsonify({"erro": str(erro)}), erro.status_sugerido
