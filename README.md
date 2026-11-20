# Sistema de Locadora de Filmes

Este projeto consiste em uma interface gráfica de usuário desenvolvida para o gerenciamento completo do catálogo de uma locadora de filmes. O sistema foi criado e evoluído, utilizando a linguagem **Python** e a biblioteca **PySide6**.

Ao longo das etapas da disciplina, a aplicação evoluiu de forma contínua:
1. **1ª Etapa:** Construção da interface gráfica com listas em memória, múltiplos widgets, layouts, menus, eventos, sinais/slots e janelas secundárias.
2. **2ª Etapa:** Implementação de persistência local em disco (`JSON`), exportação/importação de arquivos em lote (`CSV` e `TXT`) e processamento assíncrono (*Multithreading*).
3. **3ª Etapa (Versão Final):** Migração para uma **arquitetura distribuída cliente-servidor em 3 camadas**, integrando a aplicação desktop via rede (**Requests + API REST Flask + SQLAlchemy ORM**) a um banco de dados relacional **PostgreSQL** executado remotamente em contêiner **Docker**, mantendo uma estratégia híbrida de arquivos locais para intercâmbio de planilhas e backups.

---

## Arquitetura do Sistema (3 Camadas)

1. **Camada de Apresentação (Cliente Desktop - PySide6 + Requests):**
   - Interface gráfica responsiva (`main.py`, `janelas/`, `componentes/`) acoplada ao módulo `dados/repositorio.py`, que atua como cliente HTTP utilizando `requests.Session` para consumir a API REST pela rede e tratar falhas de conexão (`ErroConexaoAPI`) sem congelar ou fechar o programa.
2. **Camada de Serviço / API Web (Backend - Flask + SQLAlchemy):**
   - Servidor web (`backend/app.py`, `backend/models.py`, `backend/database.py`, `backend/seed.py`) responsável por expor rotas REST em JSON, validar domínios de entrada e gerenciar transações **ACID** (`commit` e `rollback`) no banco de dados.
3. **Camada de Persistência Híbrida (PostgreSQL em Docker + Arquivos Locais):**
   - **Banco de Dados Relacional (`docker-compose.yml` - PostgreSQL 16):** Armazena o catálogo principal (`filmes`), a tabela normalizada até a 3ª Forma Normal de gêneros (`generos`) e o registro auditável de movimentações (`historico_locacoes`).
   - **Arquivos Locais (`CSV`, `TXT` e `JSON`):** Mantidos onde o uso de arquivos faz mais sentido prático — importação de listas externas em lote, exportação de planilhas compatíveis com Excel (`utf-8-sig`) e snapshots portáteis de contingência na pasta `backups/`.

---

## Funcionalidades

O sistema permite o gerenciamento completo do acervo com as seguintes funcionalidades:
- **Catálogo Interativo:** Visualização das obras através de uma tabela interativa com sistema de busca rápida e filtros dinâmicos por título e gênero.
- **Persistência Remota em Banco de Dados Relacional (PostgreSQL via Docker):** Salvamento e carregamento automático do catálogo através da rede, substituindo o antigo `dados.json` pelo SGBD PostgreSQL containerizado.
- **Histórico Relacional de Locações:** Registro automático em banco de dados (com data e hora em UTC) de cada aluguel e devolução realizada, consultável diretamente na janela de detalhes do filme.
- **Monitoramento de Conexão e Reconexão (`Ctrl+R`):** Indicador visual permanente na barra de status informando se o servidor Flask/PostgreSQL está Online ou Desconectado, com ação rápida de reconexão na barra de ferramentas.
- **Exportação de Dados:** Ação dedicada para salvar todo o catálogo remoto em um arquivo CSV padronizado (`utf-8-sig`) para leitura direta em planilhas como o Excel.
- **Importação em Lote Assíncrona:** Leitura e cadastro automatizado de múltiplos filmes a partir de arquivos `.txt` e `.csv`, processada em segundo plano e enviada em lote para a API (`POST /filmes/lote`) com prevenção de duplicidade.
- **Backup Automático:** Rotina discreta em segundo plano que consulta periodicamente o catálogo na API e gera snapshots JSON datados na pasta `backups/`.
- **Barra de Progresso Dinâmica:** Indicador visual que exibe a taxa de disponibilidade do acervo e se transforma em um medidor em tempo real (0–100%) durante a importação de grandes arquivos.
- **Janelas Modais e Secundárias:** Diálogo bloqueante para cadastro de novos filmes e janela independente (não-modal) para exibir a ficha técnica detalhada, histórico de locações e alternar o status do filme.

---

## Requisitos Técnicos Implementados

O desenvolvimento do software atendeu a todas as exigências técnicas da disciplina:
- **Banco de Dados Relacional, Normalização (3FN) e ORM:** Modelagem no PostgreSQL utilizando `SQLAlchemy` com chaves primárias, chaves estrangeiras (`genero_id` e `filme_id` com `ON DELETE CASCADE`) e transações atômicas (**ACID**).
- **Containerização e Execução Remota (Docker):** Provisionamento do PostgreSQL via `docker-compose.yml` com volume persistente (`postgres_locadora_data`), mapeamento de porta (`5432`) e `healthcheck` automatizado (`pg_isready`).
- **Comunicação em Rede (Sockets, HTTP REST, Flask e Requests):** Servidor Flask escutando em `0.0.0.0:5000` (permitindo conexões locais ou de outras máquinas na rede via IP configurável em `.env`) e cliente desktop consumindo rotas `GET`, `POST`, `PATCH` e `DELETE`.
- **Multithreading e Paralelismo:** Aplicação de duas abordagens distintas para evitar o travamento da Interface Gráfica (GUI):
  1. *Ecossistema Qt:* Uso de `QRunnable` e `QThreadPool` para a leitura e envio de arquivos em lote.
  2. *Python Nativo:* Uso de `threading.Thread` em modo daemon (`daemon=True`) para o laço contínuo de cópias de segurança.
- **Manipulação de Arquivos de I/O:** Uso das bibliotecas nativas `json`, `csv` e `os` para exportação tabular, leitura de lotes e gravação de snapshots de backup.
- **Sinais e Slots Customizados:** Classes `QObject` independentes (`SinaisImportacao` e `SinaisBackup`) para promover comunicação *thread-safe* entre as tarefas de segundo plano e a interface principal, além do sinal `statusModificado` na janela de detalhes.
- **Eventos (Events):** Sobrescrita de eventos virtuais, como `closeEvent` (para encerramento limpo das threads e confirmação de saída) e `keyPressEvent` (atalho com a tecla `Enter` para abrir detalhes).
- **Componentes (Widgets, Layouts, Menus e Toolbars):** Organização com `QStackedLayout`, `QVBoxLayout`, `QHBoxLayout` e `QGridLayout`; manipulação de dados com `QLineEdit`, `QComboBox`, `QSlider`, `QTableWidget`, `QProgressBar`, `QStatusBar`, `QMenuBar` e `QToolBar`.

---

## Estrutura do Projeto

O código-fonte foi fortemente modularizado, separando interface gráfica, cliente de rede e servidor backend:
- `main.py`: Arquivo principal de execução e ponto de partida do cliente desktop.
- `config.py`: Carregamento das variáveis de ambiente (`.env`), definindo `API_BASE_URL` e `REQUEST_TIMEOUT` para conexão local ou remota.
- `docker-compose.yml` e `.env.example`: Definição do contêiner Docker do PostgreSQL 16 e modelo de variáveis de ambiente.
- `backend/`: Módulo do servidor web e banco de dados:
  - `app.py`: Aplicação Flask com todas as rotas REST, validações de domínio e tratamento global de erros HTTP.
  - `database.py`: Configuração da instância do SQLAlchemy e montagem da URI de conexão com o PostgreSQL.
  - `models.py`: Classes ORM (`Genero`, `Filme` e `HistoricoLocacao`) normalizadas em 3FN.
  - `seed.py`: Script de criação automática das tabelas e inserção dos gêneros e filmes iniciais.
  - `requirements.txt`: Dependências exclusivas do servidor backend.
- `janelas/`: Módulo que contém a interface central (`janela_principal.py`), menus, barra de ferramentas, indicadores de conexão e a classe *worker* (`TrabalhadorImportacao`).
- `componentes/`: Módulo que guarda o diálogo modal de formulário (`dialogo_cadastro.py`) e a janela secundária com ficha técnica e tabela de histórico (`janela_detalhes.py`).
- `dados/`: Módulo do repositório cliente (`repositorio.py`) e exceções de rede (`excecoes.py`), responsável pelas requisições HTTP à API Flask, prevenção de duplicidade, exportação/importação CSV/TXT e geração de backups JSON.
- `tests/`: Scripts automatizados (`test_api.py` e `verificar_sistema.py`) para validação das rotas REST, transações no PostgreSQL e integração ponta a ponta.

---

## Instruções de Execução

Primeiramente, certifique-se de ter o **Python (versão 3.9 ou superior)** e o **Docker** (Docker Desktop no Windows/macOS ou Docker Engine no Linux) instalados em sua máquina.

Para detalhes avançados (incluindo execução remota em computadores diferentes na rede), consulte também o arquivo [Instrucoes.md](Instrucoes.md).

### Execução em Linux / macOS

```bash
# 1. Crie o arquivo .env a partir do modelo e suba o banco PostgreSQL no Docker
cp .env.example .env
docker compose up -d

# 2. Crie e ative o ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 3. Instale as dependências do cliente e do servidor
pip install -r requirements.txt
pip install -r backend/requirements.txt

# 4. Em um terminal, inicie o servidor da API Flask
python3 -m backend.app

# 5. Em outro terminal (com a venv ativa), inicie a interface gráfica
python3 main.py
```

### Execução no Windows (CMD)

```cmd
:: 1. Crie o arquivo .env a partir do modelo e suba o banco PostgreSQL no Docker
copy .env.example .env
docker compose up -d

:: 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate

:: 3. Instale as dependências do cliente e do servidor
pip install -r requirements.txt
pip install -r backend/requirements.txt

:: 4. Em um terminal, inicie o servidor da API Flask
python -m backend.app

:: 5. Em outro terminal (com a venv ativa), inicie a interface gráfica
python main.py
```