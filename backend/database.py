import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

db = SQLAlchemy()


def montar_database_uri():
    #Monta a string de conexao PostgreSQL a partir das variaveis de ambiente.
    url_direta = os.getenv("DATABASE_URL")
    if url_direta:
        return url_direta

    usuario = os.getenv("POSTGRES_USER", "locadora_user")
    senha = os.getenv("POSTGRES_PASSWORD", "locadora_pass")
    host = os.getenv("POSTGRES_HOST", "localhost")
    porta = os.getenv("POSTGRES_PORT", "5432")
    banco = os.getenv("POSTGRES_DB", "locadora_db")
    return f"postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}"