import csv
import json
import os

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

    def importar_lote(self, caminho): # Le um arquivo de texto (.txt ou .csv) e cadastra multiplos filmes em lote.
    
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo '{caminho}' nao encontrado.")

        filmes_importados = 0

        # utf-8-sig trata tanto arquivos UTF-8 padrao quanto criados pelo Windows/Excel
        with open(caminho, 'r', encoding='utf-8-sig') as arquivo:
            primeira_linha = arquivo.readline()
            if not primeira_linha:
                return 0

            # Detecta se o separador e ';' ou ','
            delimitador = ';' if ';' in primeira_linha else ','
            arquivo.seek(0)

            leitor = csv.reader(arquivo, delimiter=delimitador)

            for linha in leitor:
                # Pula linhas vazias
                if not linha or not any(campo.strip() for campo in linha):
                    continue

                # Pula cabecalho
                primeira_coluna = linha[0].strip().lower()
                if primeira_coluna in ["id", "titulo", "título"]:
                    continue

                # Se o arquivo tiver a coluna ID (9 colunas como o exportado), comeca da coluna 1
                # Se nao tiver coluna ID (8 colunas), comeca da coluna 0
                if len(linha) >= 9:
                    colunas = linha[1:]
                elif len(linha) >= 8:
                    colunas = linha
                else:
                    continue  # Linha incompleta, ignora

                try:
                    titulo = colunas[0].strip()
                    genero = colunas[1].strip()
                    ano = int(colunas[2].strip())
                    
                    # Converte formato de preco (remove 'R$', espacos e troca virgula por ponto)
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

                    # Cria o novo filme garantindo ID sequencial unico
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
                    self._filmes.append(novo_filme)
                    self._proximo_id += 1
                    filmes_importados += 1

                except (ValueError, IndexError):
                    # Se alguma linha tiver formato invalido, apenas ignora e pula para a proxima
                    continue

        # Salva o JSON no disco apenas uma vez ao final de toda a leitura
        if filmes_importados > 0:
            self._salvar_dados()

        return filmes_importados