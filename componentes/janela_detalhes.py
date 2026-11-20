from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
)


class JanelaDetalhesFilme(QWidget):
    # Sinal customizado emitido quando o usuario solicita alternar o status
    statusModificado = Signal(int, bool)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Detalhes do Filme - Locadora")
        self.setMinimumSize(440, 460)

        self._filme_atual = None

        layout_principal = QVBoxLayout()

        grupo_info = QGroupBox("Ficha Tecnica")
        layout_info = QVBoxLayout()

        self.label_titulo = QLabel("Titulo: -")
        self.label_titulo.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.label_genero = QLabel("Genero: -")
        self.label_ano = QLabel("Ano de Lancamento: -")
        self.label_preco = QLabel("Preco da Diaria: -")
        self.label_midia = QLabel("Midia: -")
        self.label_status = QLabel("Status: -")
        self.label_avaliacao = QLabel("Avaliacao: -")
        self.label_sinopse = QLabel("Sinopse: -")
        self.label_sinopse.setWordWrap(True)

        layout_info.addWidget(self.label_titulo)
        layout_info.addWidget(self.label_genero)
        layout_info.addWidget(self.label_ano)
        layout_info.addWidget(self.label_preco)
        layout_info.addWidget(self.label_midia)
        layout_info.addWidget(self.label_status)
        layout_info.addWidget(self.label_avaliacao)
        layout_info.addWidget(self.label_sinopse)
        grupo_info.setLayout(layout_info)

        layout_principal.addWidget(grupo_info)

        # Historico relacional vindo do PostgreSQL
        grupo_historico = QGroupBox("Historico de Locacoes (Banco de Dados)")
        layout_hist = QVBoxLayout()
        self.tabela_historico = QTableWidget(0, 2)
        self.tabela_historico.setHorizontalHeaderLabels(["Data / Hora (UTC)", "Movimentacao"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabela_historico.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabela_historico.setMaximumHeight(140)
        layout_hist.addWidget(self.tabela_historico)
        grupo_historico.setLayout(layout_hist)
        layout_principal.addWidget(grupo_historico)

        layout_botoes = QHBoxLayout()
        self.botao_alternar_status = QPushButton("Alternar Locacao (Alugar/Devolver)")
        self.botao_alternar_status.clicked.connect(self._alternar_locacao)

        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.clicked.connect(self.hide)

        layout_botoes.addWidget(self.botao_alternar_status)
        layout_botoes.addWidget(self.botao_fechar)
        layout_principal.addLayout(layout_botoes)

        self.setLayout(layout_principal)

    def exibir_filme(self, filme, historico=None):
        # Atualiza a ficha tecnica e o historico relacional do filme.
        self._filme_atual = filme
        if not filme:
            return

        self.label_titulo.setText(f"{filme['titulo']}")
        self.label_genero.setText(f"Genero: {filme['genero']}")
        self.label_ano.setText(f"Ano: {filme['ano']}")
        self.label_preco.setText(f"Preco: R$ {filme['preco']:.2f}")
        self.label_midia.setText(f"Midia: {filme['midia']}")
        status_txt = "Disponivel" if filme["disponivel"] else "Alugado"
        self.label_status.setText(f"Status: {status_txt}")
        self.label_avaliacao.setText(f"Avaliacao: {filme['avaliacao']} / 10")
        self.label_sinopse.setText(f"Sinopse: {filme['sinopse'] or 'Sem sinopse cadastrada.'}")

        if filme["disponivel"]:
            self.botao_alternar_status.setText("Realizar Locacao")
        else:
            self.botao_alternar_status.setText("Registrar Devolucao")

        registros = historico or []
        self.tabela_historico.setRowCount(len(registros))
        for linha, reg in enumerate(registros):
            self.tabela_historico.setItem(linha, 0, QTableWidgetItem(reg.get("data_hora", "-")))
            self.tabela_historico.setItem(linha, 1, QTableWidgetItem(reg.get("acao", "-")))

        self.show()
        self.raise_()
        self.activateWindow()

    def _alternar_locacao(self):
        if not self._filme_atual:
            return
        novo_status = not self._filme_atual["disponivel"]
        self.statusModificado.emit(self._filme_atual["id"], novo_status)