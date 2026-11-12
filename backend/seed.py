from flask import Flask
from backend.database import db, montar_database_uri
from backend.models import Filme, Genero, HistoricoLocacao

GENEROS_PADRAO = [
    "Acao", "Comedia", "Drama", "Ficcao Cientifica",
    "Terror", "Romance", "Animacao", "Documentario"
]

FILMES_INICIAIS = [
    {
        "titulo": "Matrix",
        "genero": "Ficcao Cientifica",
        "ano": 1999,
        "preco": 7.50,
        "midia": "DVD",
        "disponivel": True,
        "avaliacao": 9,
        "sinopse": "Um jovem programador descobre a verdadeira natureza da sua realidade."
    },
    {
        "titulo": "Interestelar",
        "genero": "Ficcao Cientifica",
        "ano": 2014,
        "preco": 9.00,
        "midia": "Blu-ray",
        "disponivel": True,
        "avaliacao": 10,
        "sinopse": "Uma equipe de exploradores viaja atraves de um buraco de minhoca no espaco."
    },
    {
        "titulo": "O Poderoso Chefao",
        "genero": "Drama",
        "ano": 1972,
        "preco": 8.00,
        "midia": "DVD",
        "disponivel": False,
        "avaliacao": 10,
        "sinopse": "O patriarca idoso de uma dinastia do crime transfere o controle para seu filho relutante."
    }
]


def obter_ou_criar_genero(nome_genero):
    nome_limpo = str(nome_genero).strip() or "Outros"
    genero = Genero.query.filter(db.func.lower(Genero.nome) == nome_limpo.lower()).first()
    if not genero:
        genero = Genero(nome=nome_limpo)
        db.session.add(genero)
        db.session.flush()
    return genero


def popular_banco_inicial():

    #Cria tabelas e insere generos e filmes iniciais caso o catalogo esteja vazio.
    
    db.create_all()

    for nome in GENEROS_PADRAO:
        obter_ou_criar_genero(nome)

    if Filme.query.count() == 0:
        for item in FILMES_INICIAIS:
            genero = obter_ou_criar_genero(item["genero"])
            filme = Filme(
                titulo=item["titulo"],
                genero_id=genero.id,
                ano=item["ano"],
                preco=item["preco"],
                midia=item["midia"],
                disponivel=item["disponivel"],
                avaliacao=item["avaliacao"],
                sinopse=item["sinopse"],
            )
            db.session.add(filme)
            db.session.flush()
            if not item["disponivel"]:
                db.session.add(HistoricoLocacao(filme_id=filme.id, acao="ALUGUEL"))

    db.session.commit()


if __name__ == "__main__":
    app_temp = Flask(__name__)
    app_temp.config["SQLALCHEMY_DATABASE_URI"] = montar_database_uri()
    app_temp.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app_temp)
    with app_temp.app_context():
        popular_banco_inicial()
        print(f"Banco inicializado! Filmes cadastrados: {Filme.query.count()}")