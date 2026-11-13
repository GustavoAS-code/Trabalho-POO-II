import os
from flask import Flask, jsonify, request
from sqlalchemy import text

from backend.database import db, montar_database_uri
from backend.models import Filme, HistoricoLocacao
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

    @app.route("/filmes/<int:filme_id>/status", methods=["PATCH"])
    def alterar_status_filme(filme_id):
        filme = db.session.get(Filme, filme_id)
        if not filme:
            return jsonify({"erro": f"Filme ID {filme_id} nao encontrado."}), 404
        dados = request.get_json(silent=True) or {}
        if "disponivel" not in dados:
            return jsonify({"erro": "Informe o campo booleano 'disponivel'."}), 400
        try:
            novo_status = bool(dados["disponivel"])
            filme.disponivel = novo_status
            acao = "DEVOLUCAO" if novo_status else "ALUGUEL"
            registro = HistoricoLocacao(filme_id=filme.id, acao=acao)
            db.session.add(registro)
            db.session.commit()
            return jsonify(filme.to_dict()), 200
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Falha na transacao de locacao: {erro}"}), 500
        
    @app.route("/filmes/<int:filme_id>/historico", methods=["GET"])
    def listar_historico_filme(filme_id):
        filme = db.session.get(Filme, filme_id)
        if not filme:
            return jsonify({"erro": f"Filme ID {filme_id} nao encontrado."}), 404
        return jsonify([h.to_dict() for h in filme.historicos]), 200

    @app.route("/filmes/<int:filme_id>", methods=["DELETE"])
    def remover_filme(filme_id):
        filme = db.session.get(Filme, filme_id)
        if not filme:
            return jsonify({"erro": f"Filme ID {filme_id} nao encontrado."}), 404
        try:
            db.session.delete(filme)
            db.session.commit()
            return jsonify({"mensagem": f"Filme ID {filme_id} removido com sucesso."}), 200
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Erro ao remover filme: {erro}"}), 500

    @app.route("/filmes/lote", methods=["POST"])
    def importar_filmes_lote():
        dados = request.get_json(silent=True) or {}
        lista = dados.get("filmes", [])
        if not isinstance(lista, list):
            return jsonify({"erro": "O campo 'filmes' deve ser uma lista."}), 400
        try:
            existentes = Filme.query.all()
            chaves_existentes = {
                (
                    f.titulo.strip().lower(),
                    f.genero.nome.strip().lower() if f.genero else "",
                    int(f.ano),
                    round(float(f.preco), 2),
                    f.midia.strip(),
                    int(f.avaliacao),
                    f.sinopse.strip(),
                )
                for f in existentes
            }
            importados = []
            for item in lista:
                titulo = str(item.get("titulo", "")).strip()
                if not titulo:
                    continue
                genero_nome = str(item.get("genero", "Outros")).strip()
                ano = int(item.get("ano", 2024))
                preco = round(float(item.get("preco", 8.50)), 2)
                midia = str(item.get("midia", "DVD")).strip()
                if midia not in ["DVD", "Blu-ray", "Digital"]:
                    midia = "DVD"
                avaliacao = int(item.get("avaliacao", 8))
                sinopse = str(item.get("sinopse", "")).strip()
                disponivel = bool(item.get("disponivel", True))
                chave = (
                    titulo.lower(),
                    genero_nome.lower(),
                    ano,
                    preco,
                    midia,
                    avaliacao,
                    sinopse,
                )
                if chave in chaves_existentes:
                    continue
                genero_obj = obter_ou_criar_genero(genero_nome)
                novo_filme = Filme(
                    titulo=titulo,
                    genero_id=genero_obj.id,
                    ano=ano,
                    preco=preco,
                    midia=midia,
                    disponivel=disponivel,
                    avaliacao=avaliacao,
                    sinopse=sinopse,
                )
                db.session.add(novo_filme)
                chaves_existentes.add(chave)
                importados.append(novo_filme)
            db.session.commit()
            return jsonify({
                "importados": len(importados),
                "filmes": [f.to_dict() for f in importados],
            }), 201 if importados else 200
        except (ValueError, TypeError) as erro:
            db.session.rollback()
            return jsonify({"erro": f"Registro invalido no lote: {erro}"}), 400
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Erro ao importar lote: {erro}"}), 500

    
            
    return app


app = criar_app()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    porta = int(os.getenv("API_PORT", "5000"))
    app.run(host=host, port=porta, debug=True)