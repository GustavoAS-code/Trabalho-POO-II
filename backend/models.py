from datetime import datetime
from backend.database import db


class Genero(db.Model):

    #Tabela normalizada (3FN) para os generos cinematograficos.
    
    __tablename__ = "generos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)

    filmes = db.relationship("Filme", back_populates="genero")

    def to_dict(self):
        return {"id": self.id, "nome": self.nome}


class Filme(db.Model):

    #Tabela principal do catalogo de filmes da locadora.

    __tablename__ = "filmes"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    genero_id = db.Column(db.Integer, db.ForeignKey("generos.id"), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    midia = db.Column(db.String(20), nullable=False)
    disponivel = db.Column(db.Boolean, nullable=False, default=True)
    avaliacao = db.Column(db.Integer, nullable=False)
    sinopse = db.Column(db.Text, nullable=False, default="")

    genero = db.relationship("Genero", back_populates="filmes")
    historicos = db.relationship(
        "HistoricoLocacao",
        back_populates="filme",
        cascade="all, delete-orphan",
        order_by="HistoricoLocacao.data_hora.desc()"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "genero": self.genero.nome if self.genero else "Outros",
            "ano": self.ano,
            "preco": float(self.preco),
            "midia": self.midia,
            "disponivel": bool(self.disponivel),
            "avaliacao": self.avaliacao,
            "sinopse": self.sinopse,
        }


class HistoricoLocacao(db.Model):

    #Registro historico de alugueis e devolucoes (relacionamento 1:N com Filme).

    __tablename__ = "historico_locacoes"

    id = db.Column(db.Integer, primary_key=True)
    filme_id = db.Column(
        db.Integer,
        db.ForeignKey("filmes.id", ondelete="CASCADE"),
        nullable=False
    )
    acao = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    filme = db.relationship("Filme", back_populates="historicos")

    def to_dict(self):
        return {
            "id": self.id,
            "filme_id": self.filme_id,
            "acao": self.acao,
            "data_hora": self.data_hora.strftime("%d/%m/%Y %H:%M:%S"),
        }