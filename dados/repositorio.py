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
    # Repositorio cliente que consome a API REST Flask via HTTP (requests).

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

    def exportar_csv(self, caminho):
        # Exporta todo o catalogo obtido da API para um arquivo CSV local (utf-8-sig).
        filmes = self.listar_todos()
        with open(caminho, "w", encoding="utf-8-sig", newline="") as arquivo:
            escritor = csv.writer(arquivo, delimiter=self.DELIMITADOR_CSV)
            escritor.writerow(self.CABECALHO_CSV)
            for f in filmes:
                escritor.writerow([
                    f["id"],
                    f["titulo"],
                    f["genero"],
                    f["ano"],
                    f"{f['preco']:.2f}",
                    f["midia"],
                    "Disponivel" if f["disponivel"] else "Alugado",
                    f["avaliacao"],
                    f["sinopse"],
                ])
        return len(filmes)

    def importar_lote(self, caminho, callback_progresso=None):
        # Le arquivo local TXT/CSV e envia filmes validos para o BD via API Flask.
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo '{caminho}' nao encontrado.")

        with open(caminho, "r", encoding="utf-8-sig") as arquivo:
            linhas = [linha for linha in arquivo if linha.strip()]

        if not linhas:
            if callback_progresso:
                callback_progresso(100)
            return 0

        delimitador = ";" if ";" in linhas[0] else ","
        linhas_csv = list(csv.reader(linhas, delimiter=delimitador))
        total_linhas = len(linhas_csv)
        lote_filmes = []

        for i, linha in enumerate(linhas_csv):
            time.sleep(0.15)
            if callback_progresso and total_linhas > 0:
                porcentagem = int(((i + 1) / total_linhas) * 90)
                callback_progresso(porcentagem)

            if not linha or not any(campo.strip() for campo in linha):
                continue

            primeira_coluna = linha[0].strip().lower()
            if primeira_coluna in ["id", "titulo", "título"]:
                continue

            if len(linha) >= 9:
                colunas = linha[1:]
            elif len(linha) >= 8:
                colunas = linha
            else:
                continue

            try:
                titulo = colunas[0].strip()
                genero = colunas[1].strip()
                ano = int(colunas[2].strip())
                preco_str = (
                    colunas[3].replace("R$", "").replace(" ", "").replace(",", ".").strip()
                )
                preco = float(preco_str)
                midia = colunas[4].strip()
                if midia not in ["DVD", "Blu-ray", "Digital"]:
                    midia = "DVD"
                disp_str = colunas[5].strip().lower()
                disponivel = disp_str in ["disponivel", "disponível", "true", "1", "sim", "yes"]
                nota_str = colunas[6].replace("/10", "").strip()
                avaliacao = int(float(nota_str))
                sinopse = colunas[7].strip() if len(colunas) > 7 else ""

                if not titulo:
                    continue

                lote_filmes.append({
                    "titulo": titulo,
                    "genero": genero,
                    "ano": ano,
                    "preco": preco,
                    "midia": midia,
                    "disponivel": disponivel,
                    "avaliacao": avaliacao,
                    "sinopse": sinopse,
                })
            except (ValueError, IndexError):
                continue

        if not lote_filmes:
            if callback_progresso:
                callback_progresso(100)
            return 0

        resposta = self._requisitar("POST", "/filmes/lote", json={"filmes": lote_filmes})
        if callback_progresso:
            callback_progresso(100)
        return int(resposta.get("importados", 0)) if resposta else 0

    def fazer_backup(self):
        # Consulta o catalogo remoto na API e grava snapshot JSON offline em backups/.
        filmes = self.listar_todos()
        pasta_backup = "backups"
        os.makedirs(pasta_backup, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"dados_backup_{timestamp}.json"
        caminho_destino = os.path.join(pasta_backup, nome_backup)

        with open(caminho_destino, "w", encoding="utf-8") as arquivo:
            json.dump(filmes, arquivo, indent=4, ensure_ascii=False)

        return caminho_destino