import os
import time

from PySide6.QtCore import Qt, QSize, QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QStackedLayout, QStatusBar, QTableWidget,
    QTableWidgetItem, QToolBar, QVBoxLayout, QWidget
)

from dados.repositorio import RepositorioFilmes
from componentes.dialogo_cadastro import DialogoCadastroFilme
from componentes.janela_detalhes import JanelaDetalhesFilme

# Sinais para comunicar o resultado da thread secundaria para a janela principal
class SinaisImportacao(QObject):

    concluido = Signal(int, str)
    progresso = Signal(int)
    erro = Signal(str)

# Thread de trabalho para processar a importacao em lote sem travar a GUI.
class TrabalhadorImportacao(QRunnable):

    def __init__(self, repositorio, caminho):
        super().__init__()
        self.repositorio = repositorio
        self.caminho = caminho
        self.sinais = SinaisImportacao()

    @Slot()
    def run(self):
        try:
            # Conecta o sinal de progresso como callback do leitor de arquivo
            quantidade = self.repositorio.importar_lote(self.caminho, callback_progresso = self.sinais.progresso.emit)
            self.sinais.concluido.emit(quantidade, self.caminho)
        except Exception as erro:
            self.sinais.erro.emit(str(erro))

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

        # Gerenciador de threads para execucao em paralelo
        self.threadpool = QThreadPool()

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

        # Acao Exportar CSV
        self.acao_exportar = QAction("Exportar CSV", self)
        self.acao_exportar.setStatusTip("Exportar todo o catalogo de filmes para um arquivo CSV")
        self.acao_exportar.setShortcut(QKeySequence("Ctrl+E"))
        self.acao_exportar.triggered.connect(self._exportar_catalogo_csv)

        # Acao Importar CSV
        self.acao_importar = QAction("Importar em Lote", self)
        self.acao_importar.setStatusTip("Importar filmes a partir de um arquivo TXT ou CSV")
        self.acao_importar.setShortcut(QKeySequence("Ctrl+I"))
        self.acao_importar.triggered.connect(self._importar_catalogo_lote)

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
        toolbar.addAction(self.acao_exportar)
        toolbar.addAction(self.acao_importar)

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

        # Barra de Progresso / Disponibilidade
        layout_progresso = QHBoxLayout()
        self.label_progresso = QLabel("Taxa de Disponibilidade do Acervo:")
        layout_progresso.addWidget(self.label_progresso)
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        layout_progresso.addWidget(self.barra_progresso)
        layout_catalogo.addLayout(layout_progresso)

        # Botões
        layout_botoes = QHBoxLayout()
        self.btn_locar = QPushButton("Alugar / Devolver")
        self.btn_locar.clicked.connect(self._alternar_locacao_selecionado)

        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.setToolTip("Exporta todo o catalogo para um arquivo CSV")
        self.btn_exportar.clicked.connect(self._exportar_catalogo_csv)

        self.btn_importar = QPushButton("Importar em Lote")
        self.btn_importar.setToolTip("Importa filmes a partir de um arquivo TXT ou CSV")
        self.btn_importar.clicked.connect(self._importar_catalogo_lote)

        layout_botoes.addWidget(self.btn_locar)
        layout_botoes.addWidget(self.btn_exportar)
        layout_botoes.addWidget(self.btn_importar)
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

    def _exportar_catalogo_csv(self):
        # Exporta o catalogo completo, ignorando os filtros ativos na tabela
        if not self.repositorio.listar_todos():
            QMessageBox.warning(self, "Catalogo Vazio", "Nao ha filmes cadastrados para exportar.")
            return

        # Dialogo nativo para o usuario escolher onde salvar o arquivo
        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar Catalogo", "catalogo_filmes.csv", "Arquivos CSV (*.csv)")

        # Retorno vazio significa que o usuario cancelou o dialogo
        if not caminho:
            self.status_bar.showMessage("Exportacao cancelada.", 3000)
            return

        # Garante a extensao .csv caso o usuario tenha digitado apenas o nome
        if not caminho.lower().endswith(".csv"):
            caminho += ".csv"

        try:
            quantidade = self.repositorio.exportar_csv(caminho)
        except OSError as erro:
            # Ex.: sem permissao de escrita ou arquivo aberto em outro programa
            QMessageBox.critical(self, "Erro na Exportacao", f"Nao foi possivel salvar o arquivo:\n{erro}")
            self.status_bar.showMessage("Falha ao exportar o catalogo.", 3000)
            return

        QMessageBox.information(self, "Exportacao Concluida", f"{quantidade} filme(s) exportado(s) com sucesso para:\n{os.path.abspath(caminho)}")
        self.status_bar.showMessage(f"Catalogo exportado: {quantidade} filme(s).", 3000)

    def _importar_catalogo_lote(self):
        # Dialogo para escolher arquivo CSV ou TXT
        caminho, _ = QFileDialog.getOpenFileName(self, "Importar Filmes em Lote", os.getcwd(),
            "Todos os Arquivos (*.*);;Arquivos de Texto (*.txt);;Arquivos CSV (*.csv)")

        if not caminho:
            self.status_bar.showMessage("Importacao cancelada.", 3000)
            return

        # Prepara a interface para exibir o progresso da thread
        self.btn_importar.setEnabled(False)
        self.acao_importar.setEnabled(False)
        self.label_progresso.setText("Progresso da Importacao em Lote:")
        self.barra_progresso.setValue(0)
        self.status_bar.showMessage("Importando filmes em segundo plano (Thread ativa)...")

        # Instancia o Worker e conecta os sinais aos slots da interface
        trabalhador = TrabalhadorImportacao(self.repositorio, caminho)
        trabalhador.sinais.progresso.connect(self._slot_progresso_importacao)
        trabalhador.sinais.concluido.connect(self._slot_importacao_concluida)
        trabalhador.sinais.erro.connect(self._slot_erro_importacao)
        self.threadpool.start(trabalhador)

    def _slot_progresso_importacao(self, valor):
        # Atualiza a barra de progresso em tempo real conforme a thread processa cada linha
        self.barra_progresso.setValue(valor)
        self.status_bar.showMessage(f"Importando filmes em lote... {valor}%")

    def _slot_importacao_concluida(self, quantidade, caminho):
        self.btn_importar.setEnabled(True)
        self.acao_importar.setEnabled(True)
        self.label_progresso.setText("Taxa de Disponibilidade do Acervo:")

        if quantidade > 0:
            self._atualizar_tabela()
            QMessageBox.information(self, "Importacao Concluida",
                f"{quantidade} filme(s) importado(s) com sucesso a partir de:\n{os.path.abspath(caminho)}"
            )
            self.status_bar.showMessage(f"Importacao concluida: {quantidade} filme(s) adicionado(s).", 3000)
        else:
            self._atualizar_tabela()
            QMessageBox.warning(self, "Nenhum Filme Importado",
                "Nenhum registro valido foi encontrado no arquivo selecionado. Verifique o formato do arquivo."
            )
            self.status_bar.showMessage("Nenhum filme foi importado.", 3000)

    def _slot_erro_importacao(self, mensagem_erro):
        self.btn_importar.setEnabled(True)
        self.acao_importar.setEnabled(True)
        self.label_progresso.setText("Taxa de Disponibilidade do Acervo:")
        self._atualizar_tabela()

        QMessageBox.critical(self, "Erro na Importacao", f"Ocorreu um erro ao processar o arquivo:\n{mensagem_erro}")
        self.status_bar.showMessage("Falha ao importar filmes.", 3000)

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