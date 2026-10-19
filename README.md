# Sistema de Locadora de Filmes

Este projeto consiste em uma interface gráfica de usuário desenvolvida para o gerenciamento de um catálogo de um locadora de filmes. O sistema foi criado como um trabalho da disciplina de Programação Orientada a Objetos II, utilizando a linguagem Python e a biblioteca PySide6.

Na versão final, a aplicação saiu de uma lista em memória para um sistema com persistência de dados local, manipulação de arquivos em lote e processamento assíncrono (Multithreading).

## Funcionalidades

O sistema permite o gerenciamento completo do acervo com as seguintes funcionalidades:
- **Catálogo Interativo:** Visualização das obras através de uma tabela interativa com sistema de busca rápida e filtros por título e gênero.
- **Persistência de Dados em JSON:** Salvamento automático e carregamento do catálogo localmente utilizando o arquivo "dados.json".
- **Exportação de Dados:** Ação dedicada (botão ou atalho "Ctrl+E") para salvar o catálogo em um arquivo CSV padronizado (utf-8-sig) para leitura em planilhas.
- **Importação em Lote Assíncrona:** Leitura e cadastro automatizado de múltiplos filmes a partir de arquivos ".txt" e ".csv", processada em segundo plano para não congelar a aplicação.
- **Backup Automático:** Rotina discreta que gera cópias de segurança por tem no banco de dados na pasta `backups/`.
- **Barra de Progresso Dinâmica:** Indicador visual que exibe a taxa de disponibilidade do acervo e se mostra em um medidor de tempo real (0-100%) durante a importação de grandes arquivos.
- **Janelas Modais e Secundárias:** Diálogo bloqueante para cadastro de novos filmes e uma janela solta para exibir a ficha técnica detalhada e alternar a locação.

## Requisitos Técnicos Implementados

O desenvolvimento do software atendeu a todas as exigências técnicas da disciplina:
- **Multithreading e Paralelismo:** Aplicação de duas abordagens distintas para evitar o travamento da interface Gráfica (GUI): 
  1. *Ecossistema Qt:* Uso de "QRunnable" e "QThreadPool" para a leitura de arquivos em lote.
  2. *Python Nativo:* Uso de "threading.Thread" em modo daemon ("daemon=True") para o laço contínuo de cópias de segurança.
- **Manipulação de Arquivos de I/O:** Uso das bibliotecas nativas "json", "csv", "os" e "shutil" para leitura, gravação e cópia de metadados.
- **Sinais e Slots Customizados:** Criação de classes "QObject" independentes ("SinaisImportacao" e "SinaisBackup") para promover a comunicação thread-safe entre o *background* e os componentes visuais, além do tráfego de parâmetros (ID e *status*).
- **Eventos (Events):** Sobrescrita de eventos virtuais, como "closeEvent" (para fechamento das threads em segundo plano e confirmação de saída) e "keyPressEvent" (para atalhos de teclado rápidos).
- **Componentes (Widgets e Layouts):** Organização avançada com "QStackedLayout", "QVBoxLayout", "QHBoxLayout" e "QGridLayout". Manipulação de dados com "QLineEdit", "QComboBox", "QSlider", "QTableWidget" e leitura visual por "QProgressBar" e "QStatusBar".
- **Menus e Barras de Ferramentas:** Integração de "QMenuBar" e uma "QToolBar" limpa, otimizada apenas para as ações principais.

## Estrutura do Projeto

O código-fonte foi fortemente modularizado, separando a lógica de interface das regras de negócio:
- "main.py": Arquivo principal de execução e ponto de partida do sistema.
- "janelas/": Módulo que contém a interface central (janela_principal.py), os menus e a classe *worker* das rotinas de processamento.
- "componentes/": Módulo que guarda o diálogo de formulário (dialogo_cadastro.py) e a ficha técnica (janela_detalhes.py).
- "dados/": Módulo do repositório (repositorio.py) responsável por acessar e manipular as informações dos filmes em disco (JSON), aplicar lógicas de não-duplicação e orquestrar arquivos.

## Instruções de Execução

Primeiramente, certifique-se de ter a linguagem Python (versão 3.8 ou superior) instalada em sua máquina.

### Execução em Linux / macOS

Recomenda-se a criação de um ambiente virtual para não causar conflitos com outros pacotes do sistema:
```bash
# 1. Crie o ambiente virtual
python3 -m venv venv

# 2. Ative o ambiente
source venv/bin/activate

# 3. Instale a biblioteca gráfica do Qt
pip install pyside6

# 4. Inicie o sistema
python3 main.py