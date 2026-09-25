"""
Modulo responsavel pelo armazenamento e manipulacao dos dados dos filmes.
Mantem uma estrutura simples em memoria para facilitar alteracoes futuras.
"""

class RepositorioFilmes:
    """
    Classe para gerenciar o catalogo de filmes da locadora.
    """
    def __init__(self):
        # Lista interna que armazena dicionarios com os dados de cada filme
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

    def listar_todos(self):
        """Retorna todos os filmes cadastrados."""
        return list(self._filmes)

    def adicionar(self, titulo, genero, ano, preco, midia, disponivel, avaliacao, sinopse):
        """Adiciona um novo filme ao catalogo."""
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
        return filme

    def remover_por_id(self, filme_id):
        """Remove um filme a partir de seu identificador unico."""
        tamanho_anterior = len(self._filmes)
        self._filmes = [f for f in self._filmes if f["id"] != filme_id]
        return len(self._filmes) < tamanho_anterior

    def buscar_por_id(self, filme_id):
        """Busca um filme especifico pelo identificador."""
        for f in self._filmes:
            if f["id"] == filme_id:
                return f
        return None

    def alterar_status(self, filme_id, disponivel):
        """Altera a disponibilidade de locacao de um filme."""
        filme = self.buscar_por_id(filme_id)
        if filme:
            filme["disponivel"] = disponivel
            return True
        return False