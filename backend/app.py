import os
from flask import Flask, jsonify, request
from sqlalchemy import text

from backend.database import db, montar_database_uri
from backend.models import Filme, HistoricoLocacao
from backend.seed import obter_ou_criar_genero, popular_banco_inicial

MIDIAS_VALIDAS = {"DVD", "Blu-ray", "Digital"}


def validar_dados_filme(dados):
    # Valida os dominios dos atributos conforme o esquema do sistema.
    if not isinstance(dados, dict):
        return None, "Corpo da requisicao deve ser um JSON valido."

    titulo = str(dados.get("titulo", "")).strip()
    if not titulo:
        return None, "O campo 'titulo' nao pode ficar vazio."

    try:
        ano = int(dados.get("ano", 2024))
        preco = round(float(dados.get("preco", 8.50)), 2)
        avaliacao = int(dados.get("avaliacao", 8))
    except (ValueError, TypeError):
        return None, "Campos numericos (ano, preco, avaliacao) possuem formato invalido."

    if not (1900 <= ano <= 2030):
        return None, "O campo 'ano' deve estar entre 1900 e 2030."
    if not (1.0 <= preco <= 100.0):
        return None, "O campo 'preco' deve estar entre R$ 1,00 e R$ 100,00."
    if not (0 <= avaliacao <= 10):
        return None, "O campo 'avaliacao' deve estar entre 0 e 10."

    midia = str(dados.get("midia", "DVD")).strip()
    if midia not in MIDIAS_VALIDAS:
        return None, f"Midia invalida. Valores permitidos: {', '.join(sorted(MIDIAS_VALIDAS))}."

    limpo = {
        "titulo": titulo,
        "genero": str(dados.get("genero", "Outros")).strip() or "Outros",
        "ano": ano,
        "preco": preco,
        "midia": midia,
        "disponivel": bool(dados.get("disponivel", True)),
        "avaliacao": avaliacao,
        "sinopse": str(dados.get("sinopse", "")).strip(),
    }
    return limpo, None


def criar_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = montar_database_uri()
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.ensure_ascii = False

    db.init_app(app)

    with app.app_context():
        popular_banco_inicial()

    @app.errorhandler(404)
    def erro_404(_erro):
        return jsonify({"erro": "Recurso nao encontrado na API."}), 404

    @app.errorhandler(405)
    def erro_405(_erro):
        return jsonify({"erro": "Metodo HTTP nao permitido para esta rota."}), 405

    @app.errorhandler(Exception)
    def erro_inesperado(erro):
        db.session.rollback()
        return jsonify({"erro": f"Erro interno do servidor: {erro}"}), 500

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
        dados = request.get_json(silent=True)
        limpo, msg_erro = validar_dados_filme(dados)
        if msg_erro:
            return jsonify({"erro": msg_erro}), 400

        try:
            genero_obj = obter_ou_criar_genero(limpo["genero"])
            novo_filme = Filme(
                titulo=limpo["titulo"],
                genero_id=genero_obj.id,
                ano=limpo["ano"],
                preco=limpo["preco"],
                midia=limpo["midia"],
                disponivel=limpo["disponivel"],
                avaliacao=limpo["avaliacao"],
                sinopse=limpo["sinopse"],
            )
            db.session.add(novo_filme)
            db.session.commit()
            return jsonify(novo_filme.to_dict()), 201
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Erro ao salvar filme: {erro}"}), 500

    @app.route("/filmes/<int:filme_id>/status", methods=["PATCH"])
    def alterar_status_filme(filme_id):
        filme = db.session.get(Filme, filme_id)
        if not filme:
            return jsonify({"erro": f"Filme ID {filme_id} nao encontrado."}), 404

        dados = request.get_json(silent=True) or {}
        if "disponivel" not in dados or not isinstance(dados["disponivel"], bool):
            return jsonify({"erro": "Informe o campo booleano 'disponivel' (true/false)."}), 400

        try:
            novo_status = dados["disponivel"]
            filme.disponivel = novo_status
            acao = "DEVOLUCAO" if novo_status else "ALUGUEL"
            db.session.add(HistoricoLocacao(filme_id=filme.id, acao=acao))
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
                limpo, msg_erro = validar_dados_filme(item)
                if msg_erro:
                    continue

                chave = (
                    limpo["titulo"].lower(),
                    limpo["genero"].lower(),
                    limpo["ano"],
                    limpo["preco"],
                    limpo["midia"],
                    limpo["avaliacao"],
                    limpo["sinopse"],
                )
                if chave in chaves_existentes:
                    continue

                genero_obj = obter_ou_criar_genero(limpo["genero"])
                novo_filme = Filme(
                    titulo=limpo["titulo"],
                    genero_id=genero_obj.id,
                    ano=limpo["ano"],
                    preco=limpo["preco"],
                    midia=limpo["midia"],
                    disponivel=limpo["disponivel"],
                    avaliacao=limpo["avaliacao"],
                    sinopse=limpo["sinopse"],
                )
                db.session.add(novo_filme)
                chaves_existentes.add(chave)
                importados.append(novo_filme)

            db.session.commit()
            return jsonify({
                "importados": len(importados),
                "filmes": [f.to_dict() for f in importados],
            }), 201 if importados else 200
        except Exception as erro:
            db.session.rollback()
            return jsonify({"erro": f"Erro ao importar lote: {erro}"}), 500

    return app


app = criar_app()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    porta = int(os.getenv("API_PORT", "5000"))
    app.run(host=host, port=porta, debug=True)