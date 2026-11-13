import os
from flask import Flask, jsonify, request
from sqlalchemy import text

from backend.database import db, montar_database_uri
from backend.models import Filme
from backend.seed import obter_ou_criar_genero, popular_banco_inicial

def criar_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = montar_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.ensure_ascii = False

    db.init_app(app)
    with app.app_context():
        popular_banco_inicial()
    
    @app.route("/health", methods=["GET"])
    def health_check():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"status": "ok", "banco": "conectado"}), 200
        except Exception as erro:
            return jsonify({"status": "erro", "detalhes": str(erro)}), 503
    
    @app.route("/filmes", methods=["GET"])
    def listar_filmes():
        filmes = Filme.query.order_by(Filme.id.asc()).all()
        return jsonify([f.to_dict() for f in filmes]), 200
    
    @app.route("/filmes/<int:filme_id>", methods=["GET"])
    def buscar_filme(filme_id):
        filme = db.session.get(Filme, filme_id)
        if not filme:
            return jsonify({"erro": f"Filme ID {filme_id} nao encontrado."}), 404
        return jsonify(filme.to_dict()), 200

    @app.route("/filmes", methods=["POST"])
    def cadastrar_filme():
        dados = request.get_json(silent=True) or {}
        titulo = str(dados.get("titulo", "")).strip()
        if not titulo:
            return jsonify({"erro": "O campo 'titulo' e obrigatorio."}), 400
        try:
            genero_obj = obter_ou_criar_genero(dados.get("genero", "Outros"))
            novo_filme = Filme(
                titulo=titulo,
                genero_id=genero_obj.id,
                ano=int(dados.get("ano", 2024)),
                preco=float(dados.get("preco", 8.50)),
                midia=str(dados.get("midia", "DVD")).strip(),
                disponivel=bool(dados.get("disponivel", True)),
                avaliacao=int(dados.get("avaliacao", 8)),
                sinopse=str(dados.get("sinopse", "")).strip(),
            )
            db.session.add(novo_filme)
            db.session.commit()
            return jsonify(novo_filme.to_dict()), 201
        except (ValueError, TypeError) as erro:
            db.session.rollback()
            return jsonify({"erro": f"Dados invalidos: {erro}"}), 400
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Erro interno ao salvar filme: {erro}"}), 500
            
    return app


app = criar_app()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    porta = int(os.getenv("API_PORT", "5000"))
    app.run(host=host, port=porta, debug=True)