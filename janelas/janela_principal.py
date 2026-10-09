from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar, QPushButton, QStackedLayout, QStatusBar, QTableWidget, QTableWidgetItem, QToolBar, QVBoxLayout, QWidget


from dados.repositorio import RepositorioFilmes
from componentes.dialogo_cadastro import DialogoCadastroFilme
from componentes.janela_detalhes import JanelaDetalhesFilme


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuracoes gerais da janela
        self.setWindowTitle("Sistema de Locadora de Filmes")
        self.resize(900, 600)
        self.setMinimumSize(700, 450)

        # Instancias de dados e janela adicional 
        self.repositorio = RepositorioFilmes()
        self.janela_detalhes = JanelaDetalhesFilme()

        self.janela_detalhes.statusModificado.connect(self._slot_status_modificado_externamente)

        # Inicializacao dos componentes da interface
        self._criar_acoes()
        self._criar_menu_ajuda()
        self._criar_barra_ferramentas()
        self._criar_barra_status()
        self._criar_interface_central()

        # Carga inicial de dados na tabela
        self._atualizar_tabela()

    
    # ACOES, MENUS E BARRAS 
    
    def _criar_acoes(self):
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

        # Acao Sobre
        self.acao_sobre = QAction("Sobre o Sistema", self)
        self.acao_sobre.setStatusTip("Informacoes sobre o projeto e a disciplina")
        self.acao_sobre.triggered.connect(self._mostrar_sobre)

# MENU

    def _criar_menu_ajuda(self):
        menu_bar = self.menuBar()
        menu_ajuda = menu_bar.addMenu("Ajuda")
        menu_ajuda.addAction(self.acao_sobre)

# ToolBar

    def _criar_barra_ferramentas(self):
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)
        toolbar.setMovable(False)

        # Acoes principais
        toolbar.addAction(self.acao_novo)
        toolbar.addAction(self.acao_detalhes)
        toolbar.addAction(self.acao_remover)

        toolbar.addSeparator()

        # Troca de tela no toolbar
        toolbar.addAction(self.acao_ver_catalogo)

        toolbar.addSeparator()

        # Adicionando widgets diretamente na Toolbar 
        toolbar.addWidget(QLabel(" Busca Rapida: "))
        self.campo_busca_rapida = QLineEdit()
        self.campo_busca_rapida.setPlaceholderText("Titulo...")

        # Resultado instantaneo de busca
        self.campo_busca_rapida.textChanged.connect(self._slot_busca_rapida)
        toolbar.addWidget(self.campo_busca_rapida)

# Barra de Status

    def _criar_barra_status(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema de Locadora pronto para uso.")

    
    # LAYOUTS E WIDGETS CENTRAIS 
    
    def _criar_interface_central(self):
        container_central = QWidget()
        self.layout_pilha = QStackedLayout()  

        # Tela Principal de Catalogo de Filmes
        widget_catalogo = QWidget()
        layout_catalogo = QVBoxLayout()
        layout_catalogo.setContentsMargins(10, 10, 10, 10)
        layout_catalogo.setSpacing(10)

        # Painel Superior
        layout_filtros = QHBoxLayout()

        layout_filtros.addWidget(QLabel("Filtrar por Titulo:"))
        self.campo_filtro_titulo = QLineEdit()
        self.campo_filtro_titulo.setPlaceholderText("Digite para filtrar...")
        self.campo_filtro_titulo.textChanged.connect(self._atualizar_tabela)
        layout_filtros.addWidget(self.campo_filtro_titulo)

        layout_filtros.addWidget(QLabel("Genero:"))
        self.combo_filtro_genero = QComboBox()
        self.combo_filtro_genero.addItems(["Todos", "Acao", "Comedia", "Drama", "Ficcao Cientifica", "Terror", "Romance", "Animacao"])
        self.combo_filtro_genero.currentIndexChanged.connect(self._atualizar_tabela)
        layout_filtros.addWidget(self.combo_filtro_genero)

        layout_catalogo.addLayout(layout_filtros)

        # Tabela de Filmes
        self.tabela_filmes = QTableWidget()
        self.tabela_filmes.setColumnCount(8)
        self.tabela_filmes.setHorizontalHeaderLabels(["ID", "Titulo", "Genero", "Ano", "Preco (R$)", "Midia", "Status", "Nota"])
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_filmes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_filmes.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela_filmes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Duplo clique na linha abre a janela de detalhes
        self.tabela_filmes.cellDoubleClicked.connect(self._abrir_janela_detalhes)

        layout_catalogo.addWidget(self.tabela_filmes)

        # Barra de Disponibilidade
        layout_progresso = QHBoxLayout()
        layout_progresso.addWidget(QLabel("Taxa de Disponibilidade do Acervo:"))
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        layout_progresso.addWidget(self.barra_progresso)
        layout_catalogo.addLayout(layout_progresso)

        # Botões
        layout_botoes = QHBoxLayout()
        self.btn_locar = QPushButton("Alugar / Devolver")
        self.btn_locar.clicked.connect(self._alternar_locacao_selecionado)

        layout_botoes.addWidget(self.btn_locar)
        layout_catalogo.addLayout(layout_botoes)

        widget_catalogo.setLayout(layout_catalogo)

        # Adiciona a pagina ao QStackedLayout
        self.layout_pilha.addWidget(widget_catalogo)

        container_central.setLayout(self.layout_pilha)
        self.setCentralWidget(container_central)

    # SLOTS DE OPERACAO E REGRAS DE NEGOCIO 

    def _atualizar_tabela(self):
        # Recarrega os filmes na tabela aplicando filtros ativos.
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
        linha_selecionada = self.tabela_filmes.currentRow()
        if linha_selecionada < 0:
            return None

        item_id = self.tabela_filmes.item(linha_selecionada, 0)
        if not item_id:
            return None

        filme_id = int(item_id.text())
        return self.repositorio.buscar_por_id(filme_id)

    def _abrir_dialogo_cadastro(self):
        dialogo = DialogoCadastroFilme(self)
        if dialogo.exec():
            dados = dialogo.obter_dados()
            filme = self.repositorio.adicionar(titulo=dados["titulo"], genero=dados["genero"], ano=dados["ano"], preco=dados["preco"], midia=dados["midia"], disponivel=dados["disponivel"], avaliacao=dados["avaliacao"], sinopse=dados["sinopse"])
            self._atualizar_tabela()
            QMessageBox.information(self, "Cadastro Realizado", f"O filme '{filme['titulo']}' foi cadastrado com sucesso!")
            self.status_bar.showMessage(f"Filme '{filme['titulo']}' cadastrado.", 3000)

    def _abrir_janela_detalhes(self):
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(self, "Nenhuma Selecao", "Por favor, selecione um filme na tabela para ver os detalhes.")
            return

        # Exibe a janela adicional independente
        self.janela_detalhes.exibir_filme(filme)
        self.status_bar.showMessage(f"Detalhes de '{filme['titulo']}' abertos na janela secundaria.", 3000)

    def _alternar_locacao_selecionado(self):
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(self, "Nenhuma Selecao", "Selecione um filme para alterar a locacao.")
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
        filme = self._obter_filme_selecionado()
        if not filme:
            QMessageBox.warning(self, "Nenhuma Selecao", "Selecione um filme para remover.")
            return

        resposta = QMessageBox.question(self, "Confirmar Remocao", f"Deseja realmente remover o filme '{filme['titulo']}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if resposta == QMessageBox.StandardButton.Yes:
            self.repositorio.remover_por_id(filme["id"])
            self._atualizar_tabela()
            self.status_bar.showMessage(f"Filme '{filme['titulo']}' removido.", 3000)

    def _slot_busca_rapida(self, texto):
        # Sincroniza com o campo de filtro principal
        self.campo_filtro_titulo.setText(texto)

    def _slot_status_modificado_externamente(self, filme_id, disponivel):
        self.repositorio.alterar_status(filme_id, disponivel)
        self._atualizar_tabela()
        self.status_bar.showMessage(f"Status do filme ID {filme_id} atualizado via janela secundaria.", 3000)

    def _mostrar_sobre(self):
        # A forma de escrita nessa página foi inspirada nas aulas de PWEB 
        QMessageBox.about(self, "Sobre a Locadora de Filmes", "<h3>Locadora de Filmes</h3>" "<p>Trabalho Pratico da disciplina de <b>Programacao Orientada a Objetos II</b>.</p>" "<p>Desenvolvido com <b>Python e PySide6</b> cobrindo todos os topicos vistos em sala de aula.</p>")


    # EVENTOS VIRTUAIS SOBRESCRITOS 


    def closeEvent(self, event):
        resposta = QMessageBox.question(self, "Encerrar Aplicacao", "Deseja realmente fechar o Sistema de Locadora?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if resposta == QMessageBox.StandardButton.Yes:
            # Fecha tambem a janela adicional caso esteja aberta
            self.janela_detalhes.close()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # Ao pressionar Enter com um item selecionado, abre os detalhes
            if self._obter_filme_selecionado():
                self._abrir_janela_detalhes()
        super().keyPressEvent(event)