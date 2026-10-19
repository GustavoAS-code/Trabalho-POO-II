import csv
import json
import os
import shutil
import time
from datetime import datetime

class RepositorioFilmes:
    
    ARQUIVO_DADOS = "dados.json" # Constante com o nome do arquivo de banco de dados

    # Configuracoes da exportacao para CSV
    CABECALHO_CSV = ["ID", "Titulo", "Genero", "Ano", "Preco (R$)", "Midia", "Status", "Nota", "Sinopse"]
    DELIMITADOR_CSV = "," 
    
    def __init__(self): # Lista interna que armazena dicionarios com os dados de cada filme
        self._filmes = []
        self._proximo_id = 1
        
        self._carregar_dados()
        
    def _carregar_dados(self):
        # Verifica a existencia do arquivo de dados no computador
        if os.path.exists(self.ARQUIVO_DADOS):
            with open(self.ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
                try:
                    self._filmes = json.load(arquivo)
                    if self._filmes:
                        # Busca o maior id atual para definir o id do proximo cadastro
                        maior_id = max(filme["id"] for filme in self._filmes)
                        self._proximo_id = maior_id + 1
                except json.JSONDecodeError:
                    self._filmes = []
        else:
            # Preenche a lista com filmes de exemplo 
            self._filmes = [
                {
                    "id": 1,
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
                    "id": 2,
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
                    "id": 3,
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
            self._proximo_id = 4
            
            self._salvar_dados()  # Salva o arquivo inicial no disco

    def _salvar_dados(self): 
        with open(self.ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo: 
            json.dump(self._filmes, arquivo, indent=4, ensure_ascii=False)

    def listar_todos(self): 
        return list(self._filmes)

    def adicionar(self, titulo, genero, ano, preco, midia, disponivel, avaliacao, sinopse):
        filme = {
            "id": self._proximo_id,
            "titulo": str(titulo).strip(),
            "genero": str(genero).strip(),
            "ano": int(ano),
            "preco": float(preco),
            "midia": str(midia).strip(),
            "disponivel": bool(disponivel),
            "avaliacao": int(avaliacao),
            "sinopse": str(sinopse).strip()
        }
        self._filmes.append(filme)
        self._proximo_id += 1
        
        self._salvar_dados() # Atualiza o arquivo json apos a insercao do novo filme
        return filme

    def remover_por_id(self, filme_id):
        tamanho_anterior = len(self._filmes)
        self._filmes = [f for f in self._filmes if f["id"] != filme_id]
        
        # Salva as alteracoes no disco caso a exclusao ocorra com sucesso
        if len(self._filmes) < tamanho_anterior:
            self._salvar_dados()
            return True
            
        return False

    def buscar_por_id(self, filme_id):
        for f in self._filmes:
            if f["id"] == filme_id:
                return f
        return None

    def alterar_status(self, filme_id, disponivel):
        filme = self.buscar_por_id(filme_id)
        if filme:
            filme["disponivel"] = disponivel
            
            # Grava a nova disponibilidade do filme diretamente no arquivo
            self._salvar_dados()
            return True
        return False

    def exportar_csv(self, caminho):
        # Grava todo o catalogo (e nao apenas o que esta filtrado na tabela) em um arquivo CSV.
        filmes = self.listar_todos()

        # utf-8-sig adiciona um marcador que faz o Excel reconhecer os acentos corretamente.
        with open(caminho, 'w', encoding='utf-8-sig', newline='') as arquivo:
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

    def importar_lote(self, caminho, callback_progresso=None): # Le um arquivo de texto e cadastra multiplos filmes em lote.
        
        # Notifica a porcentagem a cada linha processada.

        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo '{caminho}' nao encontrado.")

        filmes_importados = 0

        with open(caminho, 'r', encoding='utf-8-sig') as arquivo:
            linhas = [linha for linha in arquivo if linha.strip()]

        if not linhas:
            if callback_progresso:
                callback_progresso(100)
            return 0

        delimitador = ';' if ';' in linhas[0] else ','
        leitor = csv.reader(linhas, delimiter=delimitador)
        linhas_csv = list(leitor)
        total_linhas = len(linhas_csv)

        for i, linha in enumerate(linhas_csv):
            # Pausa para visualizacao do carregamento na interface
            time.sleep(0.3)

            # Calcula e emite a porcentagem para a barra de progresso da interface
            if callback_progresso and total_linhas > 0:
                porcentagem = int(((i + 1) / total_linhas) * 100)
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
                
                preco_str = colunas[3].replace("R$", "").replace(" ", "").replace(",", ".").strip()
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

                novo_filme = {
                    "id": self._proximo_id,
                    "titulo": titulo,
                    "genero": genero,
                    "ano": ano,
                    "preco": preco,
                    "midia": midia,
                    "disponivel": disponivel,
                    "avaliacao": avaliacao,
                    "sinopse": sinopse
                }

                # Verifica se o filme já existe no catálogo
                existe = False
                novo_filmeLimpo = novo_filme.copy()
                novo_filmeLimpo.pop("id", None)
                novo_filmeLimpo.pop("disponivel", None)
                for teste in self._filmes:
                    testeLimpo = teste.copy()
                    testeLimpo.pop("id", None)
                    testeLimpo.pop("disponivel", None)
                    if novo_filmeLimpo == testeLimpo:
                        existe = True
                        break
                if not existe:
                    self._filmes.append(novo_filme)
                    self._proximo_id += 1
                    filmes_importados += 1

            except (ValueError, IndexError):
                continue

        if filmes_importados > 0:
            self._salvar_dados()

        return filmes_importados

    def fazer_backup(self): # Gera uma copia de seguranca do arquivo dados.json dentro da pasta 'backups/'.

        if not os.path.exists(self.ARQUIVO_DADOS):
            return None

        pasta_backup = "backups"
        os.makedirs(pasta_backup, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"dados_backup_{timestamp}.json"
        caminho_destino = os.path.join(pasta_backup, nome_backup)

        # Realiza a copia do arquivo preservando os metadados
        shutil.copy2(self.ARQUIVO_DADOS, caminho_destino)
        return caminho_destino