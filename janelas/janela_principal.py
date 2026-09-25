"""
Modulo da Janela Principal do sistema de Locadora de Filmes.
Integra todos os conceitos vistos em aula:
- Aula 01: QMainWindow, loop, propriedades, sinais e slots, conexao direta;
- Aula 02: Layouts (QVBoxLayout, QHBoxLayout, QGridLayout, QStackedLayout), diversos widgets e eventos;
- Aula 03: QToolBar, QMenuBar, QAction, QStatusBar;
- Aula 04: QDialog, QMessageBox e Janela Adicional Independente.
"""
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedLayout,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget
)

from dados.repositorio import RepositorioFilmes
from componentes.dialogo_cadastro import DialogoCadastroFilme
from componentes.janela_detalhes import JanelaDetalhesFilme
from componentes.area_eventos import AreaEventosWidget


class JanelaPrincipal(QMainWindow):
    """
    Janela principal da aplicacao de Locadora de Filmes.
    """
    def __init__(self):
        super().__init__()

        # 1. Configuracoes gerais da janela (Aula 01)
        self.setWindowTitle("Sistema de Locadora de Filmes - POO II")
        self.resize(900, 600)
        self.setMinimumSize(700, 450)

        # 2. Instancias de dados e janela adicional (Aula 04)
        self.repositorio = RepositorioFilmes()
        self.janela_detalhes = JanelaDetalhesFilme()
        # Conexao do sinal customizado da janela adicional com slot da principal
        self.janela_detalhes.statusModificado.connect(self._slot_status_modificado_externamente)

        # 3. Inicializacao dos componentes da interface
        self._criar_acoes()
        self._criar_menus()
        self._criar_barra_ferramentas()
        self._criar_barra_status()
        self._criar_interface_central()

        # 4. Carga inicial de dados na tabela
        self._atualizar_tabela()

    # =========================================================================
    # ACOES, MENUS E BARRAS (Aula 03)
    # =========================================================================
    def _criar_acoes(self):
        """Cria as instancias de QAction reutilizaveis em menus e toolbars."""
        # Acao Novo Filme
        self.acao_novo = QAction("Novo Filme", self)
        self.acao_novo.setStatusTip("Cadastrar um novo filme no catalogo")
        self.acao_novo.setShortcut(QKeySequence("Ctrl+N"))
        self.acao_novo.triggered.connect(self._abrir_dialogo_cadastro)

        # Acao Detalhes
        self.acao_detalhes = QAction("Ver Detalhes", self)
        self.acao_detalhes.setStatusTip("Abrir janela adicional com detalhes do filme selecionado")
        self.acao_detalhes.setShortcut(QKeySequence("Ctrl+D"))
        self.acao_detalhes.triggered.connect(self._abrir_janela_detalhes)

        # Acao Alternar Locacao
        self.acao_locar = QAction("Alugar / Devolver", self)
        self.acao_locar.setStatusTip("Alterar o status de locacao do filme selecionado")
        self.acao_locar.setShortcut(QKeySequence("Ctrl+L"))
        self.acao_locar.triggered.connect(self._alternar_locacao_selecionado)

        # Acao Remover
        self.acao_remover = QAction("Remover Filme", self)
        self.acao_remover.setStatusTip("Excluir o filme selecionado do sistema")
        self.acao_remover.setShortcut(QKeySequence.StandardKey.Delete)
        self.acao_remover.triggered.connect(self._remover_filme_selecionado)

        # Acao Alternar Visualizacao: Catalogo
        self.acao_ver_catalogo = QAction("Ver Catalogo de Filmes", self)
        self.acao_ver_catalogo.setStatusTip("Exibir a tabela de catalogo")
        self.acao_ver_catalogo.setShortcut(QKeySequence("Ctrl+1"))
        self.acao_ver_catalogo.triggered.connect(lambda: self.layout_pilha.setCurrentIndex(0))

        # Acao Alternar Visualizacao: Area de Eventos
        self.acao_ver_eventos = QAction("Ver Area de Eventos", self)
        self.acao_ver_eventos.setStatusTip("Exibir o painel de demonstracao de eventos do Qt")
        self.acao_ver_eventos.setShortcut(QKeySequence("Ctrl+2"))
        self.acao_ver_eventos.triggered.connect(lambda: self.layout_pilha.setCurrentIndex(1))

        # Acao Sobre
        self.acao_sobre = QAction("Sobre o Sistema", self)
        self.acao_sobre.setStatusTip("Informacoes sobre o projeto e a disciplina")
        self.acao_sobre.triggered.connect(self._mostrar_sobre)

        # Acao Sair
        self.acao_sair = QAction("Sair", self)
        self.acao_sair.setStatusTip("Encerrar a aplicacao")
        self.acao_sair.setShortcut(QKeySequence("Ctrl+Q"))
        self.acao_sair.triggered.connect(self.close)

    def _criar_menus(self):
        """Cria a barra de menus e submenus hierarquicos (Aula 03)."""
        menu_bar = self.menuBar()

        # Menu Arquivo
        menu_arquivo = menu_bar.addMenu("Arquivo")
        menu_arquivo.addAction(self.acao_novo)
        menu_arquivo.addSeparator()
        menu_arquivo.addAction(self.acao_sair)

        # Menu Filmes
        menu_filmes = menu_bar.addMenu("Filmes")
        menu_filmes.addAction(self.acao_detalhes)
        menu_filmes.addAction(self.acao_locar)
        menu_filmes.addSeparator()
        menu_filmes.addAction(self.acao_remover)

        # Menu Exibicao com Submenu
        menu_exibicao = menu_bar.addMenu("Exibicao")
        submenu_visoes = menu_exibicao.addMenu("Alternar Telas")
        submenu_visoes.addAction(self.acao_ver_catalogo)
        submenu_visoes.addAction(self.acao_ver_eventos)

        # Menu Ajuda
        menu_ajuda = menu_bar.addMenu("Ajuda")
        menu_ajuda.addAction(self.acao_sobre)

    def _criar_barra_ferramentas(self):
        """Configura a QToolBar com acoes e widgets embutidos (Aula 03)."""
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)

        # Adiciona acoes principais
        toolbar.addAction(self.acao_novo)
        toolbar.addAction(self.acao_detalhes)
        toolbar.addAction(self.acao_locar)
        toolbar.addAction(self.acao_remover)

        toolbar.addSeparator()

        # Adiciona acoes de troca de tela no toolbar
        toolbar.addAction(self.acao_ver_catalogo)
        toolbar.addAction(self.acao_ver_eventos)

        toolbar.addSeparator()

        # Adicionando widgets diretamente na Toolbar (conforme visto na Aula 03)
        toolbar.addWidget(QLabel(" Busca Rapida: "))
        self.campo_busca_rapida = QLineEdit()
        self.campo_busca_rapida.setMaximumWidth(150)
        self.campo_busca_rapida.setPlaceholderText("Titulo...")
        # Conexao direta entre sinal textChanged do campo da toolbar e slot de busca
        self.campo_busca_rapida.textChanged.connect(self._slot_busca_rapida)
        toolbar.addWidget(self.campo_busca_rapida)

    def _criar_barra_status(self):
        """Cria e define a QStatusBar da janela principal (Aula 03)."""
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema de Locadora pronto para uso.")

    # =========================================================================
    # LAYOUTS E WIDGETS CENTRAIS (Aula 02)
    # =========================================================================
    def _criar_interface_central(self):
        """
        Organiza o widget central com QStackedLayout, aninhando
        QVBoxLayout, QHBoxLayout e QGridLayout (Aula 02).
        """
        container_central = QWidget()
        self.layout_pilha = QStackedLayout()  # QStackedLayout visto na Aula 02

        # -------------------------------------------------------------
        # PAGINA 0: Tela Principal de Catalogo de Filmes
        # -------------------------------------------------------------
        widget_catalogo = QWidget()
        layout_catalogo = QVBoxLayout()
        layout_catalogo.setContentsMargins(10, 10, 10, 10)
        layout_catalogo.setSpacing(10)

        # Painel Superior: Filtros com QHBoxLayout e QComboBox
        layout_filtros = QHBoxLayout()

        layout_filtros.addWidget(QLabel("Filtrar por Titulo:"))
        self.campo_filtro_titulo = QLineEdit()
        self.campo_filtro_titulo.setPlaceholderText("Digite para filtrar...")
        self.campo_filtro_titulo.textChanged.connect(self._atualizar_tabela)
        layout_filtros.addWidget(self.campo_filtro_titulo)

        layout_filtros.addWidget(QLabel("Genero:"))
        self.combo_filtro_genero = QComboBox()
        self.combo_filtro_genero.addItems([
            "Todos", "Acao", "Comedia", "Drama",
            "Ficcao Cientifica", "Terror", "Romance", "Animacao"
        ])
        self.combo_filtro_genero.currentIndexChanged.connect(self._atualizar_tabela)
        layout_filtros.addWidget(self.combo_filtro_genero)

        layout_catalogo.addLayout(layout_filtros)

        # Tabela de Filmes (QTableWidget)
        self.tabela_filmes = QTableWidget()
        self.tabela_filmes.setColumnCount(8)
        self.tabela_filmes.setHorizontalHeaderLabels([
            "ID", "Titulo", "Genero", "Ano", "Preco (R$)", "Midia", "Status", "Nota"
        ])
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_filmes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_filmes.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela_filmes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Duplo clique na linha abre a janela de detalhes (Sinal/Slot)
        self.tabela_filmes.cellDoubleClicked.connect(self._abrir_janela_detalhes)

        layout_catalogo.addWidget(self.tabela_filmes)

        # Barra de Estatistica / Capacidade (QProgressBar)
        layout_progresso = QHBoxLayout()
        layout_progresso.addWidget(QLabel("Taxa de Disponibilidade do Acervo:"))
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        layout_progresso.addWidget(self.barra_progresso)
        layout_catalogo.addLayout(layout_progresso)

        # Painel Inferior de Botoes (QHBoxLayout com QPushButton)
        layout_botoes = QHBoxLayout()

        self.btn_novo = QPushButton("Novo Filme")
        self.btn_novo.clicked.connect(self._abrir_dialogo_cadastro)

        self.btn_detalhes = QPushButton("Ver Detalhes (Janela Adicional)")
        self.btn_detalhes.clicked.connect(self._abrir_janela_detalhes)

        self.btn_locar = QPushButton("Alugar / Devolver")
        self.btn_locar.clicked.connect(self._alternar_locacao_selecionado)

        self.btn_remover = QPushButton("Remover Filme")
        self.btn_remover.clicked.connect(self._remover_filme_selecionado)

        layout_botoes.addWidget(self.btn_novo)
        layout_botoes.addWidget(self.btn_detalhes)
        layout_botoes.addWidget(self.btn_locar)
        layout_botoes.addWidget(self.btn_remover)
        layout_catalogo.addLayout(layout_botoes)

        widget_catalogo.setLayout(layout_catalogo)

        # -------------------------------------------------------------
        # PAGINA 1: Tela de Demonstracao de Eventos (Aula 02)
        # -------------------------------------------------------------
        widget_eventos = QWidget()
        layout_eventos = QVBoxLayout()
        layout_eventos.setContentsMargins(15, 15, 15, 15)

        label_desc_eventos = QLabel(
            "Painel de demonstracao de manipulacao de Eventos do Sistema Operacional.\n"
            "Interaja com a area abaixo para disparar e monitorar eventos de mouse e teclado."
        )
        label_desc_eventos.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_eventos.addWidget(label_desc_eventos)

        # Instanciacao do componente de eventos customizado
        self.area_eventos = AreaEventosWidget()
        # Conecta o sinal emitido pelo widget de eventos a barra de status da janela principal
        self.area_eventos.eventoDetectado.connect(self.status_bar.showMessage)
        layout_eventos.addWidget(self.area_eventos)

        # Botao para retornar ao catalogo
        btn_voltar = QPushButton("Voltar para o Catalogo de Filmes")
        btn_voltar.clicked.connect(lambda: self.layout_pilha.setCurrentIndex(0))
        layout_eventos.addWidget(btn_voltar)

        widget_eventos.setLayout(layout_eventos)

        # Adiciona ambas as paginas ao QStackedLayout
        self.layout_pilha.addWidget(widget_catalogo)
        self.layout_pilha.addWidget(widget_eventos)

        container_central.setLayout(self.layout_pilha)
        self.setCentralWidget(container_central)

    # =========================================================================
    # SLOTS DE OPERACAO E REGRAS DE NEGOCIO (Sinais & Slots - Aula 01 e 04)
    # =========================================================================
    def _atualizar_tabela(self):
        """Recarrega os filmes na tabela aplicando filtros ativos."""
        filtro_texto = self.campo_filtro_titulo.text().lower().strip()
        filtro_genero = self.combo_filtro_genero.currentText()

        todos = self.repositorio.listar_todos()
        filtrados = []

        for f in todos:
            passa_texto = filtro_texto in f["titulo"].lower() if filtro_texto else True
            passa_genero = (filtro_genero == "Todos") or (f["genero"] == filtro_genero)
            if passa_texto and passa_genero:
                filtrados.append(f)

        self.tabela_filmes.setRowCount(len(filtrados))

        disponiveis_count = 0
        for linha, filme in enumerate(filtrados):
            if filme["disponivel"]:
                disponiveis_count += 1

            self.tabela_filmes.setItem(linha, 0, QTableWidgetItem(str(filme["id"])))
            self.tabela_filmes.setItem(linha, 1, QTableWidgetItem(filme["titulo"]))
            self.tabela_filmes.setItem(linha, 2, QTableWidgetItem(filme["genero"]))
            self.tabela_filmes.setItem(linha, 3, QTableWidgetItem(str(filme["ano"])))
            self.tabela_filmes.setItem(linha, 4, QTableWidgetItem(f"{filme['preco']:.2f}"))
            self.tabela_filmes.setItem(linha, 5, QTableWidgetItem(filme["midia"]))

            status_str = "Disponivel" if filme["disponivel"] else "Alugado"
            self.tabela_filmes.setItem(linha, 6, QTableWidgetItem(status_str))
            self.tabela_filmes.setItem(linha, 7, QTableWidgetItem(f"{filme['avaliacao']}/10"))

        # Atualiza a barra de progresso com porcentagem de titulos disponiveis
        total = len(filtrados)
        if total > 0:
            porcentagem = int((disponiveis_count / total) * 100)
            self.barra_progresso.setValue(porcentagem)
        else:
            self.barra_progresso.setValue(0)

    def _obter_filme_selecionado(self):
        """Retorna o dicionario do filme selecionado na tabela ou None."""
        linha_selecionada = self.tabela_filmes.currentRow()
        if linha_selecionada < 0:
            return None

        item_id = self.tabela_filmes.item(linha_selecionada, 0)
        if not item_id:
            return None

        filme_id = int(item_id.text())
        return self.repositorio.buscar_por_id(filme_id)

    def _abrir_dialogo_cadastro(self):
        """Abre o QDialog modal para cadastrar novo filme (Aula 04)."""
        dialogo = DialogoCadastroFilme(self)
        # Execucao bloqueante do dialogo conforme Aula 04
        if dialogo.exec():
            dados = dialogo.obter_dados()
            filme = self.repositorio.adicionar(
                titulo=dados["titulo"],
                genero=dados["genero"],
                ano=dados["ano"],
                preco=dados["preco"],
                midia=dados["midia"],
                disponivel=dados["disponivel"],
                avaliacao=dados["avaliacao"],
                sinopse=dados["sinopse"]
            )
            self._atualizar_tabela()
            # Alerta informativo com QMessageBox (Aula 04)
            QMessageBox.information(
                self,
                "Cadastro Realizado",
                f"O filme '{filme['titulo']}' foi cadastrado com sucesso!"
            )
            self.status_bar.showMessage(f"Filme '{filme['titulo']}' cadastrado.", 3000)

    def _abrir_janela_detalhes(self):
        """Abre a Janela Adicional Independente com o filme selecionado (Aula 04)."""
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(
                self,
                "Nenhuma Selecao",
                "Por favor, selecione um filme na tabela para ver os detalhes."
            )
            return

        # Exibe a janela adicional independente
        self.janela_detalhes.exibir_filme(filme)
        self.status_bar.showMessage(f"Detalhes de '{filme['titulo']}' abertos na janela secundaria.", 3000)

    def _alternar_locacao_selecionado(self):
        """Alterna a disponibilidade do filme selecionado."""
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(
                self,
                "Nenhuma Selecao",
                "Selecione um filme para alterar a locacao."
            )
            return

        novo_status = not filme["disponivel"]
        self.repositorio.alterar_status(filme["id"], novo_status)
        self._atualizar_tabela()

        # Se a janela adicional estiver aberta com este filme, sincroniza
        if self.janela_detalhes.isVisible() and self.janela_detalhes._filme_atual and self.janela_detalhes._filme_atual["id"] == filme["id"]:
            self.janela_detalhes.exibir_filme(filme)

        acao = "locado" if not novo_status else "devolvido"
        self.status_bar.showMessage(f"Filme '{filme['titulo']}' foi {acao}.", 3000)

    def _remover_filme_selecionado(self):
        """Remove o filme selecionado apos confirmacao com QMessageBox."""
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(
                self,
                "Nenhuma Selecao",
                "Selecione um filme para remover."
            )
            return

        # Dialogo de confirmacao usando QMessageBox.question (Aula 04)
        resposta = QMessageBox.question(
            self,
            "Confirmar Remocao",
            f"Deseja realmente remover o filme '{filme['titulo']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            self.repositorio.remover_por_id(filme["id"])
            self._atualizar_tabela()
            self.status_bar.showMessage(f"Filme '{filme['titulo']}' removido.", 3000)

    def _slot_busca_rapida(self, texto):
        """Slot conectado ao campo de busca rapida da toolbar."""
        # Sincroniza com o campo de filtro principal
        self.campo_filtro_titulo.setText(texto)

    def _slot_status_modificado_externamente(self, filme_id, disponivel):
        """Slot acionado quando a janela adicional altera o status do filme."""
        self.repositorio.alterar_status(filme_id, disponivel)
        self._atualizar_tabela()
        self.status_bar.showMessage(f"Status do filme ID {filme_id} atualizado via janela secundaria.", 3000)

    def _mostrar_sobre(self):
        """Apresenta a caixa de dialogo 'Sobre' (Aula 04)."""
        QMessageBox.about(
            self,
            "Sobre a Locadora de Filmes",
            "<h3>Locadora de Filmes</h3>"
            "<p>Trabalho Pratico da disciplina de <b>Programacao Orientada a Objetos II</b>.</p>"
            "<p>Desenvolvido com <b>Python e PySide6</b> cobrindo todos os topicos vistos em sala de aula.</p>"
        )

    # =========================================================================
    # EVENTOS VIRTUAIS SOBRESCRITOS (Aula 02)
    # =========================================================================
    def closeEvent(self, event):
        """
        Sobrescreve o metodo virtual closeEvent (Aula 02) para confirmar
        se o usuario realmente deseja fechar o aplicativo.
        """
        resposta = QMessageBox.question(
            self,
            "Encerrar Aplicacao",
            "Deseja realmente fechar o Sistema de Locadora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            # Fecha tambem a janela adicional caso esteja aberta
            self.janela_detalhes.close()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        Sobrescreve keyPressEvent (Aula 02) para atalhos de teclado diretos.
        """
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Ao pressionar Enter com um item selecionado, abre os detalhes
            if self._obter_filme_selecionado():
                self._abrir_janela_detalhes()
        super().keyPressEvent(event)