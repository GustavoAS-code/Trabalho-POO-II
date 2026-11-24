import os
import tempfile
from config import API_BASE_URL
from dados.repositorio import RepositorioFilmes
def main():
    print(f"=== Verificacao Ponta a Ponta ({API_BASE_URL}) ===")
    repo = RepositorioFilmes()
    ok, msg = repo.verificar_conexao()
    assert ok, f"Falha de conexao: {msg}"
    print("[1/5] Conexao com API + PostgreSQL Docker: OK")
    inicial = repo.listar_todos()
    print(f"[2/5] Listagem inicial: {len(inicial)} filme(s)")
    criado = repo.adicionar(
        titulo="Filme Teste E2E",
        genero="Ficcao Cientifica",
        ano=2025,
        preco=10.0,
        midia="Digital",
        disponivel=True,
        avaliacao=9,
        sinopse="Teste automatizado ponta a ponta.",
    )
    fid = criado["id"]
    print(f"[3/5] Cadastro + busca OK (ID {fid})")
    repo.alterar_status(fid, False)
    hist = repo.obter_historico(fid)
    assert len(hist) == 1 and hist[0]["acao"] == "ALUGUEL"
    print("[4/5] Locacao transacional + historico relacional: OK")
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "export_teste.csv")
        qtd = repo.exportar_csv(csv_path)
        assert os.path.exists(csv_path) and qtd >= 1
    bkp_path = repo.fazer_backup()
    assert bkp_path and os.path.exists(bkp_path)
    print(f"[5/5] Exportacao CSV e Backup JSON ({bkp_path}): OK")
    assert repo.remover_por_id(fid) is True
    print("Limpeza concluida. Sistema 100% operacional!")
if __name__ == "__main__":
    main()