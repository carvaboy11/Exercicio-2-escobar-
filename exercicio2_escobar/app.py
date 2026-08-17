from flask import Flask, jsonify
from routes.pedidos_routes import pedidos_bp


def criar_app():
    app = Flask(__name__)
    app.register_blueprint(pedidos_bp)

    @app.errorhandler(404)
    def rota_nao_encontrada(erro):
        return jsonify({"erro": "Rota não encontrada"}), 404

    @app.errorhandler(500)
    def erro_interno(erro):
        return jsonify({"erro": "Erro interno"}), 500

    return app


app = criar_app()

if __name__ == "__main__":
    app.run(port=3000)
