# Desenvolvimento de uma Interface Grafica com PySide6 para Sistema de Locadora de Filmes

**Modelo de Artigo no Padrao SBC (Sociedade Brasileira de Computacao)**

**Autores:**
- Membro 1: Gustavo Antonio de Sousa - 20259010219
- Membro 2: Luan Cristian da Silva rufino - 20259026380
- Membro 3: Rian de Oliveira Leal - 20259010030

**Curso:** Sistemas de Informacao - 4 Período  
**Disciplina:** Programacao Orientada a Objetos II  
**Docente:** Prof. Evandro  
**Instituicao:** Universidade Federal do Piauí - UFPI  

---

## Resumo

Este artigo relata o desenvolvimento de uma aplicacao de interface grafica de usuario (GUI) voltada a gestao de uma Locadora de Filmes. O software foi concebido na linguagem Python com o framework oficial PySide6 (Qt para Python), contemplando de forma integrada todos os conceitos abordados nas aulas da disciplina de Programacao Orientada a Objetos II: ciclo de vida de aplicacoes e loop de eventos, sinais e slots, manipulacao de eventos de baixo nivel, diversidade de widgets, gerenciamento de layouts, barras de ferramentas, menus hierarquicos, caixas de dialogo modais, alertas e criacao de janelas adicionais independentes. A arquitetura foi estruturada de maneira modular, com baixo acoplamento e codigo generico, viabilizando manutencoes e extensoes futuras.

**Palavras-chave:** PySide6, Qt, Interface Grafica, Programacao Orientada a Objetos, Locadora de Filmes.

## Abstract

This paper reports the development of a graphical user interface (GUI) application designed for managing a Movie Rental Store. The software was developed in Python using the official PySide6 framework (Qt for Python), integrating all key concepts covered during the Object-Oriented Programming II course: application lifecycle and event loops, signals and slots, low-level event handling, a wide variety of widgets, layout management, toolbars, hierarchical menus, modal dialogs, message boxes, and independent additional windows. The software architecture was structured in a modular fashion, ensuring low coupling and generic code to facilitate future modifications.

**Keywords:** PySide6, Qt, Graphical User Interface, Object-Oriented Programming, Movie Rental Store.

---

## 1. Introducao

O desenvolvimento de interfaces graficas interativas e intuitivas constitui um dos pilares essenciais da Engenharia de Software e da Programacao Orientada a Objetos. No ecossistema Python, o framework Qt destaca-se como a principal tecnologia multiplataforma para construcao de aplicacoes desktop robustas.

O presente projeto tem por finalidade consolidar a aprendizagem pratica dos topicos ministrados no primeiro bloco da disciplina de Programacao Orientada a Objetos II, tendo como tema uma **Locadora de Filmes**. O objetivo principal consistiu em construir uma aplicacao funcional, simples e modularizada, que atenda a todos os requisitos tecnicos estipulados pelo docente:
1. Utilizacao da biblioteca oficial `PySide6`;
2. Emprego do mecanismo de **Sinais e Slots**;
3. Tratamento explicito de **Eventos** do sistema operacional/hardware;
4. Integracao de **diversos tipos de widgets**;
5. Organizacao espacial com **Layouts** variados;
6. Implementacao de **barras de ferramentas e menus**;
7. Aplicacao de **dialogos (Dialogs) e caixas de alerta (Alerts/QMessageBox)**;
8. Criacao de **pelo menos uma janela adicional independente**.

---

## 2. Descricao Geral do Projeto e da Interface

O sistema simula as operacoes essenciais de uma locadora de filmes, disponibilizando:
- Visualizacao tabular de titulos, com informacoes de identificador (ID), titulo, genero, ano de lancamento, preco da locacao diaria, formato de midia (DVD, Blu-ray ou Digital), status de disponibilidade e avaliacao de 0 a 10;
- Filtragem em tempo real por titulo (busca textual) e por genero cinematografico (selecao categorica);
- Cadastro de novos titulos atraves de formulario modal dedicado;
- Exibicao de ficha tecnica completa em janela secundaria nao-bloqueante;
- Alternancia dinamica do status de locacao (alugar/devolver) com atualizacao instantanea da interface;
- Painel interativo para demonstracao e monitoramento didatico de eventos de mouse e teclado do Qt;
- Barra de progresso informativa refletindo a taxa de disponibilidade do acervo em tempo real.

A interface grafica e centralizada em uma janela principal do tipo `QMainWindow`, contendo uma barra de menus no topo, uma barra de ferramentas com atalhos visuais e campo de busca rapida, uma area central flexivel baseada em layout empilhado (`QStackedLayout`) e uma barra de status na parte inferior.
---

## 3. Arquitetura do Software e Modularizacao

Para garantir clareza, manutenibilidade e flexibilidade para customizacoes posteriores, a estrutura do projeto foi dividida em pacotes modulares, com responsabilidades bem delimitadas:

```
Trabalho/
│
├── main.py                     # Inicializacao da aplicacao e loop de eventos
├── README.md                   # Documentacao resumida e guia de execucao
├── RELATORIO.md                # Relatorio academico completo no padrao SBC
├── relatorio_sbc.tex           # Versao em LaTeX do relatorio academico
│
├── dados/
│   ├── __init__.py
│   └── repositorio.py          # Camada de armazenamento e logica de dados dos filmes
│
├── componentes/
│   ├── __init__.py
│   ├── area_eventos.py         # Subclasse de QFrame especializada em tratamento de eventos
│   ├── dialogo_cadastro.py     # Subclasse de QDialog para insercao de novos titulos
│   └── janela_detalhes.py      # Subclasse de QWidget atuando como janela adicional independente
│
└── janelas/
    ├── __init__.py
    └── janela_principal.py     # Subclasse de QMainWindow centralizando a interface
```

### Detalhamento das Responsabilidades:

1. **`main.py`**:
   - Criacao da instancia de `QApplication(sys.argv)`;
   - Instanciacao e chamada de `.show()` da `JanelaPrincipal`;
   - Ativacao e encerramento seguro do loop de eventos atraves de `sys.exit(app.exec())`.

2. **`dados/repositorio.py` (`RepositorioFilmes`)**:
   - Encapsula as operacoes sobre a colecao de filmes em memoria (`listar_todos`, `adicionar`, `remover_por_id`, `buscar_por_id`, `alterar_status`);
   - Isola a logica de negocio da camada visual, viabilizando futuras conexoes com bancos de dados.

3. **`componentes/dialogo_cadastro.py` (`DialogoCadastroFilme`)**:
   - Janela modal (`QDialog`) responsavel pela coleta e validacao de dados de um novo filme;
   - Agrupa multiplos componentes de entrada (`QLineEdit`, `QComboBox`, `QSpinBox`, `QDoubleSpinBox`, `QRadioButton`, `QCheckBox`, `QSlider`, `QTextEdit`) e botoes padronizados (`QDialogButtonBox`).

4. **`componentes/janela_detalhes.py` (`JanelaDetalhesFilme`)**:
   - Janela secundaria independente (`QWidget` sem no pai), responsavel pela exibicao dos detalhes de um filme selecionado;
   - Opera de forma assincrona/nao-bloqueante em relacao a janela principal e notifica alteracoes de status via sinal customizado.

5. **`componentes/area_eventos.py` (`AreaEventosWidget`)**:
   - Componente especializado na demonstracao pratica dos conceitos da Aula 02;
   - Sobrescreve metodos virtuais de baixo nivel de mouse e teclado e emite sinais customizados com as informacoes capturadas.

6. **`janelas/janela_principal.py` (`JanelaPrincipal`)**:
   - Janela mestra da aplicacao;
   - Monta menus (`QMenuBar`), barra de ferramentas (`QToolBar`), barra de status (`QStatusBar`), tabela (`QTableWidget`) e layout empilhado (`QStackedLayout`);
   - Conecta sinais aos respectivos slots de filtragem, atualizacao, dialogo e alertas.
---

## 4. Documentacao dos Topicos das Aulas e Widgets Criados

### 4.1 Sinais e Slots (Aulas 01 e 02)
O mecanismo de Sinais e Slots e o paradigma fundamental de comunicacao entre objetos no Qt. No projeto, foram implementadas as seguintes variacoes:
- **Conexao de acoes e cliques**: Botoes (`QPushButton.clicked`) e acoes (`QAction.triggered`) conectados a metodos responsaveis por disparar regras de negocio;
- **Recepcao de parametros**: Sinais que emitem parametros tipados, como `textChanged(str)` do `QLineEdit`, `currentIndexChanged(int)` do `QComboBox` e `valueChanged(int)` do `QSlider`;
- **Conexao direta entre widgets**: O campo de busca rapida da barra de ferramentas conecta seu sinal `textChanged` ao slot que altera o texto do campo de filtro principal;
- **Sinais customizados (`Signal`)**:
  - `JanelaDetalhesFilme.statusModificado = Signal(int, bool)`: Emite o ID do filme e a nova disponibilidade para sincronizar a tabela da janela principal;
  - `AreaEventosWidget.eventoDetectado = Signal(str)`: Emite a descricao formatada de eventos capturados para exibicao imediata na barra de status.

### 4.2 Eventos do Sistema Operacional (Aula 02)
Diferente dos sinais de alto nivel, os eventos representam ocorrencias de hardware e sistema operacional entregues pelo loop de eventos a um objeto receptor especifico:
- `mousePressEvent(event)`: Captura cliques dos botoes esquerdo, direito ou do meio, reportando coordenadas locais `event.pos()`;
- `mouseReleaseEvent(event)`: Detecta o momento da liberacao do botao do mouse;
- `mouseDoubleClickEvent(event)`: Identifica cliques duplos na area de interacao;
- `mouseMoveEvent(event)`: Rastreia a posicao continua do cursor sobre o componente (habilitado com `setMouseTracking(True)`);
- `keyPressEvent(event)`: Intercepta teclas fisicas digitadas no teclado (e.g. Enter para abrir detalhes de item selecionado);
- `closeEvent(event)`: Sobrescrito na `JanelaPrincipal` para interceptar a tentativa de fechamento da aplicacao, solicitando confirmacao do usuario via `QMessageBox.question` antes de aceitar (`event.accept()`) ou cancelar (`event.ignore()`).

### 4.3 Diversos Tipos de Widgets Utilizados
Conforme exigido pelo docente e exemplificado na Aula 02, foram utilizados diversos tipos de widgets nativos do Qt:

| Widget | Funcao na Aplicacao | Localizacao |
|---|---|---|
| `QLabel` | Apresentacao de rotulos de campos, titulos de secoes e status | Janela Principal, Dialogo, Detalhes e Eventos |
| `QPushButton` | Disparo de comandos (Novo Filme, Detalhes, Alugar, Remover, Voltar) | Janela Principal, Dialogo e Detalhes |
| `QLineEdit` | Entrada de texto simples para busca e titulo do filme | Janela Principal, Toolbar e Dialogo de Cadastro |
| `QComboBox` | Selecao em lista suspensa (Genero cinematografico) | Janela Principal (Filtro) e Dialogo de Cadastro |
| `QSpinBox` | Entrada numerica inteira para o ano de lancamento (1900-2030) | Dialogo de Cadastro |
| `QDoubleSpinBox` | Entrada numerica decimal para preco da diaria com prefixo "R$" | Dialogo de Cadastro |
| `QCheckBox` | Caixa de marcacao booleana para disponibilidade imediata | Dialogo de Cadastro |
| `QRadioButton` | Selecao exclusiva de midia fisica/digital (DVD, Blu-ray, Digital) | Dialogo de Cadastro (agrupados com `QButtonGroup`) |
| `QSlider` | Controle deslizante horizontal para atribuicao de nota/avaliacao (0 a 10) | Dialogo de Cadastro |
| `QProgressBar` | Indicador visual da taxa percentual de disponibilidade do acervo | Janela Principal |
| `QTableWidget` | Exibicao tabular e estruturada do catalogo com selecao de linhas | Janela Principal |
| `QTextEdit` | Area de edicao multilinha para sinopse do filme | Dialogo de Cadastro |
| `QGroupBox` | Agrupamento visual e logico de informacoes tecnicas | Janela de Detalhes |
| `QFrame` | Conteiner estilizado para painel de eventos com bordas afundadas | Area de Eventos |

### 4.4 Gerenciamento de Layouts (Aula 02)
Todos os quatro layouts abordados na disciplina foram aplicados:
- **`QVBoxLayout`**: Organizacao linear vertical dos paineis principais e fichas informativas;
- **`QHBoxLayout`**: Alinhamento linear horizontal de filtros, barras de progresso e fileiras de botoes;
- **`QGridLayout`**: Estruturacao tabular e alinhada do formulario de cadastro, correlacionando rotulos e campos de entrada;
- **`QStackedLayout`**: Layout em camadas/pilha permitindo alternar de forma transparente entre a visualizacao do Catalogo (indice 0) e a tela de Demonstracao de Eventos (indice 1);
- **Aninhamento e espacamento**: Uso de `addLayout`, `setContentsMargins(10, 10, 10, 10)` e `setSpacing(10)` para proporcionar uma interface coesa e responsiva.

### 4.5 Barras de Ferramentas, Menus e Barra de Status (Aula 03)
- **`QMenuBar`**: Barra de menus contendo os menus "Arquivo", "Filmes", "Exibicao" (com submenu hierarquico "Alternar Telas") e "Ajuda";
- **`QToolBar`**: Barra de ferramentas com atalhos rapidos para as principais acoes do sistema, separadores visuais (`addSeparator()`) e um widget interativo embutido (`QLineEdit` para busca);
- **`QAction`**: Objetos abstratos reaproveitados simultaneamente no menu e na toolbar, contendo descricoes, atalhos de teclado (`Ctrl+N`, `Ctrl+D`, `Ctrl+L`, `Ctrl+1`, `Ctrl+2`, `Ctrl+Q`) e dicas de status (`setStatusTip`);
- **`QStatusBar`**: Exibicao continua de dicas de acoes e notificacoes temporarias de feedback (`showMessage`).

### 4.6 Dialogos e Alertas (Dialogs e Alerts - Aula 04)
- **`QDialog` com `QDialogButtonBox`**: Implementado na classe `DialogoCadastroFilme`. A chamada com `exec()` bloqueia a janela principal ate que o usuario conclua o preenchimento ou cancele a operacao atraves dos botoes padronizados (OK / Cancel);
- **`QMessageBox`**: Empregado para diferentes niveis de comunicacao com o operador:
  - *Warning* (`QMessageBox.warning`): Validacao de campos vazios ou ausencia de linha selecionada;
  - *Question* (`QMessageBox.question`): Confirmacao de exclusao de filme e confirmacao de encerramento da aplicacao no `closeEvent`;
  - *Information* (`QMessageBox.information`): Notificacao de sucesso no cadastro de filme;
  - *About* (`QMessageBox.about`): Apresentacao dos creditos e escopo academico do sistema.

### 4.7 Janela Adicional Independente (Aula 04)
Conforme discutido na Aula 04, qualquer instancia de `QWidget` desprovida de um no pai comporta-se como uma janela independente. A classe `JanelaDetalhesFilme` foi criada sob essa premissa. Diferente dos dialogos modais, ela nao bloqueia a janela principal: ambas podem permanecer abertas e ativas simultaneamente na area de trabalho. A sincronizacao de dados entre elas e realizada de forma desacoplada atraves do sinal customizado `statusModificado`.
---

## 5. Registro do Uso de Inteligencia Artificial

Em consonancia com as orientacoes do trabalho e as diretrizes eticas da disciplina, registra-se formalmente a forma e o escopo de utilizacao de ferramentas de Inteligencia Artificial Generativa durante o desenvolvimento:

> **Declaracao de Uso de IA:**  
> As ferramentas de Inteligencia Artificial Generativa foram utilizadas **exclusivamente como ferramenta de auxilio para tirar duvidas pontuais de sintaxe e consultar regras e parametros acerca dos topicos das aulas (PySide6/Qt)** necessarios para a construcao do trabalho.  
> Toda a arquitetura modular, modelagem orientada a objetos, estruturacao dos layouts, escolha dos widgets, definicao de fluxos de interacao e redacao deste relatorio foram concebidos e validados pela equipe de estudantes.

---

## 6. Consideracoes Finais

O projeto da Locadora de Filmes atingiu com exito todos os objetivos propostos para a Primeira Avaliacao de Programacao Orientada a Objetos II. A implementacao pratica propiciou a consolidacao de conceitos centrais de desenvolvimento GUI no ecossistema Python, em especial a compreensao clara das diferencas entre eventos de baixo nivel e sinais de alto nivel, o uso de layouts responsivos aninhados e o gerenciamento do ciclo de vida de dialogos modais e janelas secundarias independentes.

Por ter sido projetado com codigo limpo, comentarios objetivos e estrutura generica, o sistema esta plenamente preparado para alteracoes, expansoes de regras de negocio ou integracao com mecanismos de persistencia externa.

---

## Referencias

1. THE QT COMPANY. **Qt for Python Documentation (PySide6)**. Disponivel em: <https://doc.qt.io/qtforpython-6/>. Acesso em: set. 2026.
2. PYTHON GUIS. **PySide6 Tutorials: Create GUI Applications with Python & Qt6**. Disponivel em: <https://www.pythonguis.com/>. Acesso em: set. 2026.
3. PROF. EVANDRO. **Notas de Aula e Materiais da Disciplina de Programacao Orientada a Objetos II (Aulas 01 a 04)**. Curso de Sistemas de Informacao, 2026.
4. SOCIEDADE BRASILEIRA DE COMPUTACAO (SBC). **Modelos para Publicacao de Artigos**. Disponivel em: <https://www.sbc.org.br/>. Acesso em: set. 2026.