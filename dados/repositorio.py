import csv
import json
import os
import shutil
import time
from datetime import datetime
import requests
from config import API_BASE_URL, REQUEST_TIMEOUT
from dados.excecoes import ErroConexaoAPI
class RepositorioFilmes:
    """Repositorio cliente que consome a API REST Flask via HTTP (requests)."""
    CABECALHO_CSV = [
        "ID", "Titulo", "Genero", "Ano", "Preco (R$)",
        "Midia", "Status", "Nota", "Sinopse"
    ]
    DELIMITADOR_CSV = ","
    def __init__(self, base_url=None):
        self.base_url = (base_url or API_BASE_URL).rstrip("/")
        self.sessao = requests.Session()
    def _requisitar(self, metodo, rota, **kwargs):
        url = f"{self.base_url}{rota}"
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        try:
            resposta = self.sessao.request(metodo, url, **kwargs)
        except requests.exceptions.Timeout as erro:
            raise ErroConexaoAPI(
                f"Tempo limite excedido ao conectar em {self.base_url}."
            ) from erro
        except requests.exceptions.ConnectionError as erro:
            raise ErroConexaoAPI(
                f"Nao foi possivel conectar ao servidor em {self.base_url}. "
                "Verifique se a API Flask e o PostgreSQL no Docker estao ativos."
            ) from erro
        except requests.exceptions.RequestException as erro:
            raise ErroConexaoAPI(f"Erro na requisicao HTTP: {erro}") from erro
        if resposta.status_code == 404:
            return None
        if resposta.status_code >= 400:
            try:
                detalhe = resposta.json().get("erro", resposta.text)
            except ValueError:
                detalhe = resposta.text
            raise ErroConexaoAPI(f"Erro do servidor ({resposta.status_code}): {detalhe}")
        return resposta.json()
    def verificar_conexao(self):
        try:
            dados = self._requisitar("GET", "/health")
            return bool(dados and dados.get("status") == "ok"), "Conectado"
        except ErroConexaoAPI as erro:
            return False, str(erro)
    def listar_todos(self):
        dados = self._requisitar("GET", "/filmes")
        return dados if isinstance(dados, list) else []
    def buscar_por_id(self, filme_id):
        return self._requisitar("GET", f"/filmes/{int(filme_id)}")
    def adicionar(self, titulo, genero, ano, preco, midia, disponivel, avaliacao, sinopse):
        payload = {
            "titulo": str(titulo).strip(),
            "genero": str(genero).strip(),
            "ano": int(ano),
            "preco": float(preco),
            "midia": str(midia).strip(),
            "disponivel": bool(disponivel),
            "avaliacao": int(avaliacao),
            "sinopse": str(sinopse).strip(),
        }
        return self._requisitar("POST", "/filmes", json=payload)
    def remover_por_id(self, filme_id):
        resultado = self._requisitar("DELETE", f"/filmes/{int(filme_id)}")
        return resultado is not None
    def alterar_status(self, filme_id, disponivel):
        resultado = self._requisitar(
            "PATCH",
            f"/filmes/{int(filme_id)}/status",
            json={"disponivel": bool(disponivel)},
        )
        return resultado
    def obter_historico(self, filme_id):
        dados = self._requisitar("GET", f"/filmes/{int(filme_id)}/historico")
        return dados if isinstance(dados, list) else []