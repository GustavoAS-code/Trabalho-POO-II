# Instruções de Execução - Trabalho 03

Este documento descreve como configurar o ambiente, subir o Banco de Dados PostgreSQL em contêiner Docker, iniciar a API Flask e executar os testes da aplicação.

---

## 1. Pré-requisitos
- **Python 3.9** ou superior
- **Docker Desktop** (Windows/macOS) ou **Docker Engine** (Linux)
- **Git**

---

## 2. Configuração do Banco de Dados (PostgreSQL no Docker)

1. Crie o arquivo de variáveis de ambiente `.env` a partir do modelo `.env.example`:
   - **Windows (CMD):**
     ```cmd
     copy .env.example .env
     ```
   - **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

2. Inicie o contêiner do PostgreSQL em segundo plano:
   ```bash
   docker compose up -d
   ```

3. Verifique se o contêiner está ativo e com status `(healthy)`:
   ```bash
   docker ps
   ```

---

## 3. Ambiente Virtual Python e Dependências

### Linux / macOS:
```bash
# 1. Criar e ativar o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependências do backend e do cliente gráfico
pip install -r backend/requirements.txt
pip install pyside6
```

### Windows:
```cmd
# 1. Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate

# 2. Instalar dependências do backend e do cliente gráfico
pip install -r backend/requirements.txt
pip install pyside6
```

---

## 4. Inicialização da API REST (Flask)

Para iniciar o servidor web que conecta a aplicação ao banco de dados:
```bash
python -m backend.app
```
*A API será executada na porta `5000` (`http://0.0.0.0:5000`). Na primeira execução, as tabelas (`generos`, `filmes`, `historico_locacoes`) serão criadas automaticamente no PostgreSQL e os filmes padrão serão cadastrados.*

---

## 5. Testes Automatizados da API

Com o Docker e a API rodando, abra um **segundo terminal** (com a `venv` ativada) e execute a suíte de testes:
```bash
python tests/test_api.py
```
*Este comando valida o ciclo CRUD completo, transações de locação/devolução com histórico e as validações de dados da API.*

---

## 6. Execução da Interface Gráfica (PySide6)

Para executar a aplicação desktop:
- **Windows:**
  ```cmd
  python main.py
  ```
- **Linux / macOS:**
  ```bash
  python3 main.py
  ```
```