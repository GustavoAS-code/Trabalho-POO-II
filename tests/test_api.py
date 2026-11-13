import os
import requests


BASE_URL = os.getenv("LOCADORA_API_URL", "http://127.0.0.1:5000").rstrip("/")


def executar_testes():
    print(f"Testando API em {BASE_URL} ...")

    r = requests.get(f"{BASE_URL}/health", timeout=5)
    assert r.status_code == 200 and r.json()["banco"] == "conectado", r.text
    print("[OK] GET /health")

    r = requests.get(f"{BASE_URL}/filmes", timeout=5)
    assert r.status_code == 200 and isinstance(r.json(), list), r.text
    print(f"[OK] GET /filmes ({len(r.json())} filmes)")

    novo = {
        "titulo": "Teste Automatizado POO II",
        "genero": "Acao",
        "ano": 2024,
        "preco": 9.90,
        "midia": "Blu-ray",
        "disponivel": True,
        "avaliacao": 9,
        "sinopse": "Registro temporario de teste."
    }
    r = requests.post(f"{BASE_URL}/filmes", json=novo, timeout=5)
    assert r.status_code == 201, r.text
    filme_id = r.json()["id"]
    print(f"[OK] POST /filmes (ID criado: {filme_id})")

    r = requests.patch(f"{BASE_URL}/filmes/{filme_id}/status", json={"disponivel": False}, timeout=5)
    assert r.status_code == 200 and r.json()["disponivel"] is False, r.text
    print("[OK] PATCH /filmes/<id>/status (alugado)")

    r = requests.get(f"{BASE_URL}/filmes/{filme_id}/historico", timeout=5)
    assert r.status_code == 200 and len(r.json()) >= 1, r.text
    print(f"[OK] GET /filmes/<id>/historico ({len(r.json())} registro)")

    r = requests.post(f"{BASE_URL}/filmes", json={"titulo": ""}, timeout=5)
    assert r.status_code == 400, r.text
    print("[OK] Validacao HTTP 400 para titulo vazio")

    r = requests.delete(f"{BASE_URL}/filmes/{filme_id}", timeout=5)
    assert r.status_code == 200, r.text
    print(f"[OK] DELETE /filmes/{filme_id}")
    print("\nTodos os testes da API + PostgreSQL passaram com sucesso!")


if __name__ == "__main__":
    executar_testes()