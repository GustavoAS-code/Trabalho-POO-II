import os
import threading
import time
from PySide6.QtCore import Qt, QSize, QObject, QRunnable, QThreadPool, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QStackedLayout, QStatusBar, QTableWidget,
    QTableWidgetItem, QToolBar, QVBoxLayout, QWidget
)

from config import API_BASE_URL
from dados.excecoes import ErroConexaoAPI
from dados.repositorio import RepositorioFilmes
from componentes.dialogo_cadastro import DialogoCadastroFilme
from componentes.janela_detalhes import JanelaDetalhesFilme

class SinaisImportacao(QObject):
    concluido = Signal(int, str)
    progresso = Signal(int)
    erro = Signal(str)

class SinaisBackup(QObject):
    backup_concluido = Signal(str)

class TrabalhadorImportacao(QRunnable):
    def __init__(self, repositorio, caminho):
        super().__init__()
        self.repositorio = repositorio
        self.caminho = caminho
        self.sinais = SinaisImportacao()
    @Slot()
    def run(self):
        try:
            quantidade = self.repositorio.importar_lote(
                self.caminho,
                callback_progresso=self.sinais.progresso.emit
            )
            self.sinais.concluido.emit(quantidade, self.caminho)
        except Exception as erro:
            self.sinais.erro.emit(str(erro))

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Sistema de Locadora de Filmes (Cliente + API Flask + PostgreSQL)")
        self.resize(940, 620)
        self.setMinimumSize(720, 460)
        
        self.repositorio = RepositorioFilmes()
        self.janela_detalhes = JanelaDetalhesFilme()
        self.threadpool = QThreadPool()
        
        self.sinais_backup = SinaisBackup()
        self.sinais_backup.backup_concluido.connect(self._slot_backup_concluido)
        self._backup_ativo = True
        self.thread_backup = threading.Thread(
            target=self._rotina_backup_automatico,
            daemon=True
        )
        self.thread_backup.start()

        self.janela_detalhes.statusModificado.connect(self._slot_status_modificado_externamente)
        
        self._criar_acoes()
        self._criar_menu_ajuda()
        self._criar_barra_ferramentas()
        self._criar_barra_status()
        self._criar_interface_central()
        
        self._carregar_inicial()

    def _criar_acoes(self):
        self.acao_novo = QAction("Novo Filme", self)
        self.acao_novo.setStatusTip("Cadastrar um novo filme no catalogo remoto")
        self.acao_novo.setShortcut(QKeySequence("Ctrl+N"))
        self.acao_novo.triggered.connect(self._abrir_dialogo_cadastro)
    
        self.acao_detalhes = QAction("Ver Detalhes", self)
        self.acao_detalhes.setStatusTip("Abrir janela adicional com detalhes e historico")
        self.acao_detalhes.setShortcut(QKeySequence("Ctrl+D"))
        self.acao_detalhes.triggered.connect(self._abrir_janela_detalhes)
    
        self.acao_remover = QAction("Remover Filme", self)
        self.acao_remover.setStatusTip("Excluir o filme selecionado do banco de dados")
        self.acao_remover.setShortcut(QKeySequence.StandardKey.Delete)
        self.acao_remover.triggered.connect(self._remover_filme_selecionado)
    
        self.acao_ver_catalogo = QAction("Ver Catalogo de Filmes", self)
        self.acao_ver_catalogo.setStatusTip("Exibir a tabela de catalogo")
        self.acao_ver_catalogo.setShortcut(QKeySequence("Ctrl+1"))
        self.acao_ver_catalogo.triggered.connect(lambda: self.layout_pilha.setCurrentIndex(0))
    
        self.acao_reconectar = QAction("Atualizar / Reconectar", self)
        self.acao_reconectar.setStatusTip("Testa a conexao com a API Flask e recarrega o catalogo")
        self.acao_reconectar.setShortcut(QKeySequence("Ctrl+R"))
        self.acao_reconectar.triggered.connect(self._reconectar_e_atualizar)
    
        self.acao_sobre = QAction("Sobre o Sistema", self)
        self.acao_sobre.setStatusTip("Informacoes sobre o projeto e a disciplina")
        self.acao_sobre.triggered.connect(self._mostrar_sobre)
    
    def _criar_menu_ajuda(self):
        menu_bar = self.menuBar()
        menu_ajuda = menu_bar.addMenu("Ajuda")
        menu_ajuda.addAction(self.acao_reconectar)
        menu_ajuda.addSeparator()
        menu_ajuda.addAction(self.acao_sobre)

    def _criar_barra_ferramentas(self):
        toolbar = QToolBar("Barra de Ferramentas Principal")
        toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(toolbar)
        toolbar.setMovable(False)
        
        toolbar.addAction(self.acao_novo)
        toolbar.addAction(self.acao_detalhes)
        toolbar.addAction(self.acao_remover)
        toolbar.addSeparator()
        toolbar.addAction(self.acao_ver_catalogo)
        toolbar.addAction(self.acao_reconectar)
        toolbar.addSeparator()
        
        toolbar.addWidget(QLabel(" Busca Rapida: "))
        self.campo_busca_rapida = QLineEdit()
        self.campo_busca_rapida.setPlaceholderText("Titulo...")
        self.campo_busca_rapida.textChanged.connect(self._slot_busca_rapida)
        toolbar.addWidget(self.campo_busca_rapida)

    def _criar_barra_status(self):
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.label_status_servidor = QLabel("Servidor: Verificando...")
        self.label_status_servidor.setStyleSheet("padding: 0 8px; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.label_status_servidor)
        self.status_bar.showMessage("Inicializando cliente...")

    def _criar_interface_central(self):
        container_central = QWidget()
        self.layout_pilha = QStackedLayout()

        widget_catalogo = QWidget()
        layout_catalogo = QVBoxLayout()
        layout_catalogo.setContentsMargins(10, 10, 10, 10)
        layout_catalogo.setSpacing(10)

        layout_filtros = QHBoxLayout()
        layout_filtros.addWidget(QLabel("Filtrar por Titulo:"))
        self.campo_filtro_titulo = QLineEdit()
        self.campo_filtro_titulo.setPlaceholderText("Digite para filtrar...")
        self.campo_filtro_titulo.textChanged.connect(lambda: self._atualizar_tabela(silencioso=True))
        layout_filtros.addWidget(self.campo_filtro_titulo)

        layout_filtros.addWidget(QLabel("Genero:"))
        self.combo_filtro_genero = QComboBox()
        self.combo_filtro_genero.addItems([
            "Todos", "Acao", "Comedia", "Drama", "Ficcao Cientifica",
            "Terror", "Romance", "Animacao", "Documentario"
        ])
        self.combo_filtro_genero.currentIndexChanged.connect(lambda: self._atualizar_tabela(silencioso=True))
        layout_filtros.addWidget(self.combo_filtro_genero)

        layout_catalogo.addLayout(layout_filtros)

        self.tabela_filmes = QTableWidget()
        self.tabela_filmes.setColumnCount(8)
        self.tabela_filmes.setHorizontalHeaderLabels([
            "ID", "Titulo", "Genero", "Ano", "Preco (R$)", "Midia", "Status", "Nota"
        ])
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_filmes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabela_filmes.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.tabela_filmes.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_filmes.cellDoubleClicked.connect(self._abrir_janela_detalhes)
        layout_catalogo.addWidget(self.tabela_filmes)

        layout_progresso = QHBoxLayout()
        self.label_progresso = QLabel("Taxa de Disponibilidade do Acervo:")
        layout_progresso.addWidget(self.label_progresso)
        self.barra_progresso = QProgressBar()
        self.barra_progresso.setRange(0, 100)
        self.barra_progresso.setValue(0)
        layout_progresso.addWidget(self.barra_progresso)
        layout_catalogo.addLayout(layout_progresso)
        
        layout_botoes = QHBoxLayout()
        self.btn_locar = QPushButton("Alugar / Devolver")
        self.btn_locar.clicked.connect(self._alternar_locacao_selecionado)
        
        self.btn_exportar = QPushButton("Exportar CSV")
        self.btn_exportar.setToolTip("Exporta todo o catalogo remoto para um arquivo CSV local")
        self.btn_exportar.clicked.connect(self._exportar_catalogo_csv)
        
        self.btn_importar = QPushButton("Importar em Lote")
        self.btn_importar.setToolTip("Importa filmes de um TXT ou CSV para o banco remoto")
        self.btn_importar.clicked.connect(self._importar_catalogo_lote)

        layout_botoes.addWidget(self.btn_locar)
        layout_botoes.addWidget(self.btn_exportar)
        layout_botoes.addWidget(self.btn_importar)
        layout_catalogo.addLayout(layout_botoes)

        widget_catalogo.setLayout(layout_catalogo)
        self.layout_pilha.addWidget(widget_catalogo)
        container_central.setLayout(self.layout_pilha)
        self.setCentralWidget(container_central)

    def _definir_indicador_servidor(self, online):
        if online:
            self.label_status_servidor.setText(f"Servidor: Online ({API_BASE_URL})")
            self.label_status_servidor.setStyleSheet("padding: 0 8px; color: #15803d; font-weight: bold;")
        else:
            self.label_status_servidor.setText(f"Servidor: Desconectado ({API_BASE_URL})")
            self.label_status_servidor.setStyleSheet("padding: 0 8px; color: #b91c1c; font-weight: bold;")

    def _carregar_inicial(self):
        ok = self._atualizar_tabela(silencioso=True)
        if ok:
            self.status_bar.showMessage("Conectado ao servidor Flask + PostgreSQL.", 4000)
        else:
            self.status_bar.showMessage("Servidor offline. Inicie o Docker e a API Flask e clique em Reconectar.")

    def _reconectar_e_atualizar(self):
        ok, msg = self.repositorio.verificar_conexao()
        if ok:
            self._atualizar_tabela(silencioso=True)
            QMessageBox.information(self, "Conexao Estabelecida", f"Conectado com sucesso a {API_BASE_URL}.")
        else:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Falha de Conexao", msg)

    def _atualizar_tabela(self, silencioso=False):
        filtro_texto = self.campo_filtro_titulo.text().lower().strip()
        filtro_genero = self.combo_filtro_genero.currentText()
        try:
            todos = self.repositorio.listar_todos()
            self._definir_indicador_servidor(True)
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            if not silencioso:
                QMessageBox.critical(self, "Erro de Comunicacao", str(erro))
            return False

        filtrados = [
        f for f in todos
            if (filtro_texto in f["titulo"].lower() if filtro_texto else True)
            and (filtro_genero == "Todos" or f["genero"] == filtro_genero)
        ]

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
            
        total = len(filtrados)
        porcentagem = int((disponiveis_count / total) * 100) if total > 0 else 0
        self.barra_progresso.setValue(porcentagem)
        return True

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
        try:
            filme = self.repositorio.adicionar(
                titulo=dados["titulo"],
                genero=dados["genero"],
                ano=dados["ano"],
                preco=dados["preco"],
                midia=dados["midia"],
                disponivel=dados["disponivel"],
                avaliacao=dados["avaliacao"],
                sinopse=dados["sinopse"],
            )         
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro ao Cadastrar", str(erro))
            return

        self._atualizar_tabela(silencioso=True)
        QMessageBox.information(
            self, "Cadastro Realizado",
            f"O filme '{filme['titulo']}' foi salvo no PostgreSQL com sucesso!"
        )
        self.status_bar.showMessage(f"Filme '{filme['titulo']}' cadastrado no banco remoto.", 3000)

    def _abrir_janela_detalhes(self):
        try:
            filme = self._obter_filme_selecionado()
            if not filme:
                QMessageBox.warning(
                    self, "Nenhuma Selecao",
                    "Por favor, selecione um filme na tabela para ver os detalhes."
                )
                return
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro de Comunicacao", str(erro))
            return

        self.janela_detalhes.exibir_filme(filme)
        self.status_bar.showMessage(f"Detalhes de '{filme['titulo']}' abertos.", 3000)

    def _alternar_locacao_selecionado(self):
        try:
            filme = self._obter_filme_selecionado()
            if not filme:
                QMessageBox.warning(self, "Nenhuma Selecao", "Selecione um filme para alterar a locacao.")
                return
            novo_status = not filme["disponivel"]
            filme_atualizado = self.repositorio.alterar_status(filme["id"], novo_status)
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro de Locacao", str(erro))
            return
        
        self._atualizar_tabela(silencioso=True)
        if (
            self.janela_detalhes.isVisible()
            and self.janela_detalhes._filme_atual
            and self.janela_detalhes._filme_atual["id"] == filme["id"]
        ):
            self.janela_detalhes.exibir_filme(filme_atualizado)

        acao = "locado" if not novo_status else "devolvido"
        self.status_bar.showMessage(f"Filme '{filme_atualizado['titulo']}' foi {acao}.", 3000)

    def _remover_filme_selecionado(self):
        try:
            filme = self._obter_filme_selecionado()
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro de Comunicacao", str(erro))
            return
        
        if not filme:
            QMessageBox.warning(self, "Nenhuma Selecao", "Selecione um filme para remover.")
            return
        
        resposta = QMessageBox.question(
            self, "Confirmar Remocao",
            f"Deseja realmente remover o filme '{filme['titulo']}' do banco de dados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self.repositorio.remover_por_id(filme["id"])
            except ErroConexaoAPI as erro:
                self._definir_indicador_servidor(False)
                QMessageBox.critical(self, "Erro ao Remover", str(erro))
                return
            self._atualizar_tabela(silencioso=True)
            self.status_bar.showMessage(f"Filme '{filme['titulo']}' removido.", 3000)

    def _exportar_catalogo_csv(self):
        try:
            filmes = self.repositorio.listar_todos()
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro de Comunicacao", str(erro))
            return

        if not filmes:
            QMessageBox.warning(self, "Catalogo Vazio", "Nao ha filmes cadastrados para exportar.")
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar Catalogo", "catalogo_filmes.csv", "Arquivos CSV (*.csv)"
        )
        if not caminho:
            self.status_bar.showMessage("Exportacao cancelada.", 3000)
            return
        if not caminho.lower().endswith(".csv"):
            caminho += ".csv"
        
        try:
            quantidade = self.repositorio.exportar_csv(caminho)
        except (OSError, ErroConexaoAPI) as erro:
            QMessageBox.critical(self, "Erro na Exportacao", f"Nao foi possivel exportar:\n{erro}")
            self.status_bar.showMessage("Falha ao exportar o catalogo.", 3000)
            return

        QMessageBox.information(
            self, "Exportacao Concluida",
            f"{quantidade} filme(s) exportado(s) com sucesso para:\n{os.path.abspath(caminho)}"
        )
        self.status_bar.showMessage(f"Catalogo exportado: {quantidade} filme(s).", 3000)

    def _importar_catalogo_lote(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Importar Filmes em Lote", os.getcwd(),
            "Todos os Arquivos (*.*);;Arquivos de Texto (*.txt);;Arquivos CSV (*.csv)"
        )
        if not caminho:
            self.status_bar.showMessage("Importacao cancelada.", 3000)
            return

        self.btn_importar.setEnabled(False)
        self.label_progresso.setText("Progresso da Importacao em Lote:")
        self.barra_progresso.setValue(0)
        self.status_bar.showMessage("Importando filmes e enviando ao servidor...")

        trabalhador = TrabalhadorImportacao(self.repositorio, caminho)
        trabalhador.sinais.progresso.connect(self._slot_progresso_importacao)
        trabalhador.sinais.concluido.connect(self._slot_importacao_concluida)
        trabalhador.sinais.erro.connect(self._slot_erro_importacao)
        self.threadpool.start(trabalhador)

    def _slot_progresso_importacao(self, valor):
        self.barra_progresso.setValue(valor)
        self.status_bar.showMessage(f"Importando filmes em lote... {valor}%")

    def _slot_importacao_concluida(self, quantidade, caminho):
        self.btn_importar.setEnabled(True)
        self.label_progresso.setText("Taxa de Disponibilidade do Acervo:")
        self._atualizar_tabela(silencioso=True)
        if quantidade > 0:
            QMessageBox.information(
                self, "Importacao Concluida",
                f"{quantidade} filme(s) importado(s) no PostgreSQL a partir de:\n{os.path.abspath(caminho)}"
            )
            self.status_bar.showMessage(f"Importacao concluida: {quantidade} filme(s).", 3000)
        else:
            QMessageBox.warning(
                self, "Nenhum Filme Importado",
                "Nenhum registro valido foi encontrado ou todos os filmes ja existem no banco."
            )
            self.status_bar.showMessage("Nenhum filme foi importado.", 3000)

    def _slot_erro_importacao(self, mensagem_erro):
        self.btn_importar.setEnabled(True)
        self.label_progresso.setText("Taxa de Disponibilidade do Acervo:")
        self._atualizar_tabela(silencioso=True)
        QMessageBox.critical(self, "Erro na Importacao", f"Ocorreu um erro:\n{mensagem_erro}")
        self.status_bar.showMessage("Falha ao importar filmes.", 3000)

    def _slot_busca_rapida(self, texto):
        self.campo_filtro_titulo.setText(texto)

    def _slot_status_modificado_externamente(self, filme_id, disponivel):
        try:
            self.repositorio.alterar_status(filme_id, disponivel)
        except ErroConexaoAPI as erro:
            self._definir_indicador_servidor(False)
            QMessageBox.critical(self, "Erro de Locacao", str(erro))
            return
        
        self._atualizar_tabela(silencioso=True)
        self.status_bar.showMessage(f"Status do filme ID {filme_id} atualizado no banco remoto.", 3000)

    def _mostrar_sobre(self):
        QMessageBox.about(
            self, "Sobre a Locadora de Filmes",
            "<h3>Locadora de Filmes - Trabalho 03</h3>"
            "<p>Trabalho Pratico da disciplina de <b>Programacao Orientada a Objetos II</b> (UFPI).</p>"
            "<p><b>Arquitetura:</b> Cliente Desktop (PySide6 + Requests) &rarr; "
            "API REST (Flask + SQLAlchemy) &rarr; PostgreSQL em Conteiner Docker.</p>"
            f"<p><b>Servidor configurado:</b> <code>{API_BASE_URL}</code></p>"
        )

    def closeEvent(self, event):
        resposta = QMessageBox.question(
            self, "Encerrar Aplicacao",
            "Deseja realmente fechar o Sistema de Locadora?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            self._backup_ativo = False
            self.janela_detalhes.close()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            try:
                if self._obter_filme_selecionado():
                    self._abrir_janela_detalhes()
            except ErroConexaoAPI as erro:
                QMessageBox.critical(self, "Erro de Comunicacao", str(erro))
        super().keyPressEvent(event)

    def _rotina_backup_automatico(self):
        for _ in range(60):
            if not self._backup_ativo:
                return
            time.sleep(1)

        while self._backup_ativo:
            try:
                caminho = self.repositorio.fazer_backup()
                if caminho:
                    self.sinais_backup.backup_concluido.emit(caminho)
            except Exception as erro:
                print(f"[Backup Automatico] Aviso: {erro}")
            
            for _ in range(600):
                if not self._backup_ativo:
                    break
                time.sleep(1)

    def _slot_backup_concluido(self, caminho_backup):
        nome_arquivo = os.path.basename(caminho_backup)
        self.status_bar.showMessage(f"[Backup Automatico] Snapshot salvo: {nome_arquivo}", 4000)