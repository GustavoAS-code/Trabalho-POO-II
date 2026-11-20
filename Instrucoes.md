# Instruções de Execução - Trabalho 03

Este documento descreve como configurar o ambiente, subir o Banco de Dados PostgreSQL em contêiner Docker, iniciar a API REST em Flask, executar a interface gráfica PySide6 (localmente ou via rede remota) e rodar os testes automatizados da aplicação.

---

## 1. Pré-requisitos
- **Python 3.9** ou superior
- **Docker Desktop** (Windows/macOS) ou **Docker Engine + Docker Compose** (Linux)
- **Git**

---

## 2. Configuração do Banco de Dados (PostgreSQL no Docker)

1. Crie o arquivo de variáveis de ambiente `.env` a partir do modelo `.env.example`:
   - **Windows (CMD):**
     ```cmd
     copy .env.example .env
     ```
   - **Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
   - **Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

2. Inicie o contêiner do PostgreSQL em segundo plano:
   ```bash
   docker compose up -d
   ```

3. Verifique se o contêiner `locadora_postgres` está ativo e com status `(healthy)`:
   ```bash
   docker ps
   ```

---

## 3. Ambiente Virtual Python e Dependências

### Linux / macOS:
```bash
# 1. Criar e ativar o ambiente virtual (obrigatorio ativar sempre que for rodar)
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias do cliente desktop (PySide6, requests) e do servidor (Flask, SQLAlchemy, psycopg2)
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### Windows (CMD):
```cmd
:: 1. Criar e ativar o ambiente virtual (obrigatorio ativar sempre que for rodar)
python -m venv venv
venv\Scripts\activate

:: 2. Instalar dependencias do cliente desktop (PySide6, requests) e do servidor (Flask, SQLAlchemy, psycopg2)
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## 4. Inicialização do Servidor API REST (Flask)

Com o contêiner do PostgreSQL ativo no Docker e a `venv` ativada, inicie o servidor web que conecta a aplicação ao banco de dados:

- **Windows:**
  ```cmd
  python -m backend.app
  ```
- **Linux / macOS:**
  ```bash
  python3 -m backend.app
  ```

*A API será executada na porta `5000` (`http://0.0.0.0:5000`). Na primeira execução, as tabelas (`generos`, `filmes`, `historico_locacoes`) serão criadas automaticamente no PostgreSQL e os 3 filmes iniciais padrão serão cadastrados caso o banco esteja vazio.*

---

## 5. Execução da Interface Gráfica (Cliente Desktop PySide6)

Deixe o terminal da API Flask aberto e abra um **segundo terminal** na pasta do projeto (ativando a `venv` novamente):

- **Windows:**
  ```cmd
  venv\Scripts\activate
  python main.py
  ```
- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  python3 main.py
  ```

---

## 6. Execução Remota (Banco de Dados e API em Outra Máquina na Rede)

Para executar o sistema em computadores separados conectados à mesma rede local:

1. **Na Máquina Servidora (onde rodam o Docker e a API Flask):**
   - Suba o banco de dados (`docker compose up -d`) e inicie a API (`python -m backend.app`).
   - Certifique-se de que as portas `5000` (Flask) e/ou `5432` (PostgreSQL) estejam liberadas no firewall da máquina.
   - Descubra o endereço IPv4 da máquina servidora na rede local:
     - **Windows:** `ipconfig`
     - **Linux:** `ip addr` ou `hostname -I`

2. **Na Máquina Cliente (onde roda apenas a interface gráfica PySide6):**
   - Edite o arquivo `.env` local apontando para o IP da máquina servidora:
     ```ini
     LOCADORA_API_URL=http://<IP_DO_SERVIDOR>:5000
     ```
   - Ative a `venv` e inicie a aplicação desktop normalmente com `python main.py` (ou `python3 main.py`).

---

## 7. Testes Automatizados

Com o Docker e a API Flask em execução, abra outro terminal (com a `venv` ativada) para validar o funcionamento das rotas REST, transações ACID com histórico de locação e regras de validação:

```bash
python tests/test_api.py
```