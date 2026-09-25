"""
Modulo para a Janela Adicional Independente.
Conforme a Aula 04, qualquer widget sem um no pai atua como uma janela independente (nao-bloqueante).
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class JanelaDetalhesFilme(QWidget):
    """
    Janela secundaria independente para visualizacao detalhada de um filme.
    Permite alterar o status de locacao e emite sinal de volta a janela principal.
    """
    # Sinal customizado emitido quando o status do filme e modificado nesta janela
    statusModificado = Signal(int, bool)

    def __init__(self):
        # Sem no pai: torna-se uma janela independente
        super().__init__()

        self.setWindowTitle("Detalhes do Filme - Locadora")
        self.setMinimumSize(380, 320)

        self._filme_atual = None

        # Layout vertical principal
        layout_principal = QVBoxLayout()

        # Grupo com informacoes do filme
        grupo_info = QGroupBox("Ficha Tecnica")
        layout_info = QVBoxLayout()

        self.label_titulo = QLabel("Titulo: -")
        self.label_titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
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

        # Botoes de acao na janela secundaria
        layout_botoes = QHBoxLayout()
        self.botao_alternar_status = QPushButton("Alternar Locacao (Alugar/Devolver)")
        self.botao_alternar_status.clicked.connect(self._alternar_locacao)

        self.botao_fechar = QPushButton("Fechar")
        self.botao_fechar.clicked.connect(self.hide)

        layout_botoes.addWidget(self.botao_alternar_status)
        layout_botoes.addWidget(self.botao_fechar)
        layout_principal.addLayout(layout_botoes)

        self.setLayout(layout_principal)

    def exibir_filme(self, filme):
        """Atualiza a interface da janela secundaria com os dados do filme recebido."""
        self._filme_atual = filme
        if not filme:
            return

        self.label_titulo.setText(f"Titulo: {filme['titulo']}")
        self.label_genero.setText(f"Genero: {filme['genero']}")
        self.label_ano.setText(f"Ano: {filme['ano']}")
        self.label_preco.setText(f"Preco: R$ {filme['preco']:.2f}")
        self.label_midia.setText(f"Midia: {filme['midia']}")
        status_txt = "Disponivel" if filme["disponivel"] else "Alugado"
        self.label_status.setText(f"Status: {status_txt}")
        self.label_avaliacao.setText(f"Avaliacao: {filme['avaliacao']} / 10")
        self.label_sinopse.setText(f"Sinopse: {filme['sinopse'] or 'Sem sinopse cadastrada.'}")

        # Atualiza o texto do botao de acao
        if filme["disponivel"]:
            self.botao_alternar_status.setText("Realizar Locacao (Alugar)")
        else:
            self.botao_alternar_status.setText("Registrar Devolucao")

        # Exibe a janela (conforme exemplo da Aula 04)
        self.show()
        self.raise_()
        self.activateWindow()

    def _alternar_locacao(self):
        """Slot para inverter o status de locacao e notificar via sinal customizado."""
        if not self._filme_atual:
            return

        novo_status = not self._filme_atual["disponivel"]
        self._filme_atual["disponivel"] = novo_status
        self.statusModificado.emit(self._filme_atual["id"], novo_status)

        # Atualiza a propria interface
        self.exibir_filme(self._filme_atual)