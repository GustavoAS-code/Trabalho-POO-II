# Sistema de Locadora de Filmes - POO II

Projeto pratico desenvolvido para a disciplina de **Programacao Orientada a Objetos II**, utilizando a biblioteca oficial **PySide6** (Qt para Python).

---

## 1. Estrutura Modular do Projeto

O projeto foi organizado de forma modular para manter o codigo limpo, de facil manutencao e facilmente customizavel:

```
Trabalho/
│
├── main.py                     # Ponto de entrada da aplicacao (QApplication e loop de eventos)
├── README.md                   # Instrucoes de uso e arquitetura modular
├── RELATORIO.md                # Relatorio academico completo no padrao SBC
├── relatorio_sbc.tex           # Versao em LaTeX do relatorio no padrao SBC
│
├── dados/                      # Camada de manipulacao e armazenamento de dados
│   ├── __init__.py
│   └── repositorio.py          # Repositorio em memoria para controle dos filmes
│
├── componentes/                # Componentes visuais auxiliares e reutilizaveis
│   ├── __init__.py
│   ├── area_eventos.py         # Demonstracao de eventos de baixo nivel (mouse e teclado)
│   ├── dialogo_cadastro.py     # Dialogo modal (QDialog) para cadastro de novos filmes
│   └── janela_detalhes.py      # Janela adicional independente (nao-bloqueante)
│
└── janelas/                    # Janelas principais da aplicacao
    ├── __init__.py
    └── janela_principal.py     # Janela principal (QMainWindow) integrando todos os topicos
```

---

## 2. Responsabilidade de Cada Modulo

- **`main.py`**: Responsavel por inicializar a instancia unica de `QApplication`, instanciar e exibir a `JanelaPrincipal` e executar o loop de eventos (`app.exec()`).
- **`dados/repositorio.py`**: Responsavel pelas operacoes sobre os dados dos filmes (adicionar, listar, buscar por ID, alternar status de locacao e remover).
- **`componentes/dialogo_cadastro.py`**: Responsavel pelo formulario modal de insercao de filmes (`QDialog`), contendo validacao de campos, multiplos widgets e botoes de confirmacao/cancelamento (`QDialogButtonBox`).
- **`componentes/janela_detalhes.py`**: Responsavel por funcionar como a **janela adicional independente** solicitada pelo professor. Nao bloqueia a janela principal e emite sinais quando o status do filme e alterado.
- **`componentes/area_eventos.py`**: Responsavel pela captura direta e tratamento de **eventos do sistema operacional** (`mousePressEvent`, `mouseReleaseEvent`, `mouseDoubleClickEvent`, `mouseMoveEvent`, `keyPressEvent`).
- **`janelas/janela_principal.py`**: Responsavel por centralizar toda a interface do usuario, incluindo:
  - Menus suspensos (`QMenuBar`);
  - Barra de ferramentas (`QToolBar`) com acoes e campo de busca rapida embutido;
  - Barra de status (`QStatusBar`);
  - Gerenciamento de layouts aninhados e alternancia de telas (`QStackedLayout`);
  - Tabela interativa com filtros dinamicos (`QTableWidget`);
  - Mensagens e confirmacoes (`QMessageBox`).

---

## 3. Topicos das Aulas Implementados

| Topico das Aulas | Onde foi aplicado no projeto |
|---|---|
| **Sinais e Slots** | Conexoes de cliques de botoes, alteracao de textos de busca (`textChanged`), mudancas de combo (`currentIndexChanged`), slider (`valueChanged`), conexoes diretas entre widgets e sinais customizados (`Signal`). |
| **Eventos** | Metodos virtuais sobrescritos: `mousePressEvent`, `mouseReleaseEvent`, `mouseDoubleClickEvent`, `mouseMoveEvent`, `keyPressEvent` e `closeEvent` (com confirmacao ao sair). |
| **Diversos Widgets** | `QLabel`, `QPushButton`, `QLineEdit`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QCheckBox`, `QRadioButton`, `QSlider`, `QProgressBar`, `QTableWidget`, `QTextEdit`, `QGroupBox`, `QFrame`. |
| **Layouts** | `QVBoxLayout`, `QHBoxLayout`, `QGridLayout` e `QStackedLayout` (com aninhamento, margens e espacamentos). |
| **Toolbars e Menus** | `QToolBar` com acoes, atalhos, separadores e widget de busca; `QMenuBar` com menus e submenus; `QAction`; `QStatusBar`. |
| **Dialogs e Alerts** | `QDialog` modal com `QDialogButtonBox`; `QMessageBox` (alertas de validacao, confirmacao de exclusao e sobre). |
| **Janela Adicional** | `JanelaDetalhesFilme` (janela secundaria nao-bloqueante que comunica alteracoes via sinal customizado). |

---

## 4. Como Executar a Aplicacao

1. Certifique-se de que o Python e a biblioteca PySide6 estejam instalados:
   ```bash
   pip install pyside6
   ```

2. Execute o arquivo principal a partir da pasta `Trabalho`:
   ```bash
   python main.py
   ```