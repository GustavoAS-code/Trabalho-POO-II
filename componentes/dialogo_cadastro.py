"""
Modulo que define o dialogo modal de cadastro de filmes.
Utiliza a classe QDialog e QDialogButtonBox conforme apresentado na Aula 04,
alem de multiplos widgets e layouts das Aulas 01, 02 e 04.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTextEdit,
    QVBoxLayout
)


class DialogoCadastroFilme(QDialog):
    """
    Dialogo modal para inclusao de novos filmes na locadora.
    """
    def __init__(self, parent=None):
        # Passando o parent para manter a janela modal centralizada sobre a principal
        super().__init__(parent)

        self.setWindowTitle("Cadastrar Novo Filme")
        self.setMinimumWidth(420)

        # Layout vertical principal do dialogo
        layout_principal = QVBoxLayout()

        # Layout em grade (QGridLayout) para o formulario
        layout_grid = QGridLayout()

        # 1. Campo de Titulo (QLineEdit)
        layout_grid.addWidget(QLabel("Titulo:"), 0, 0)
        self.campo_titulo = QLineEdit()
        self.campo_titulo.setPlaceholderText("Digite o titulo do filme...")
        layout_grid.addWidget(self.campo_titulo, 0, 1)

        # 2. Campo de Genero (QComboBox)
        layout_grid.addWidget(QLabel("Genero:"), 1, 0)
        self.combo_genero = QComboBox()
        self.combo_genero.addItems([
            "Acao", "Comedia", "Drama", "Ficcao Cientifica",
            "Terror", "Romance", "Animacao", "Documentario"
        ])
        layout_grid.addWidget(self.combo_genero, 1, 1)

        # 3. Campo de Ano de Lancamento (QSpinBox)
        layout_grid.addWidget(QLabel("Ano:"), 2, 0)
        self.spin_ano = QSpinBox()
        self.spin_ano.setRange(1900, 2030)
        self.spin_ano.setValue(2024)
        layout_grid.addWidget(self.spin_ano, 2, 1)

        # 4. Campo de Preco da Diaria (QDoubleSpinBox)
        layout_grid.addWidget(QLabel("Preco (R$):"), 3, 0)
        self.spin_preco = QDoubleSpinBox()
        self.spin_preco.setRange(1.00, 100.00)
        self.spin_preco.setValue(8.50)
        self.spin_preco.setPrefix("R$ ")
        layout_grid.addWidget(self.spin_preco, 3, 1)

        # 5. Midia fisica/digital (QRadioButton agrupados)
        layout_grid.addWidget(QLabel("Tipo de Midia:"), 4, 0)
        layout_midia = QHBoxLayout()
        self.radio_dvd = QRadioButton("DVD")
        self.radio_bluray = QRadioButton("Blu-ray")
        self.radio_digital = QRadioButton("Digital")
        self.radio_dvd.setChecked(True)

        self.grupo_midia = QButtonGroup(self)
        self.grupo_midia.addButton(self.radio_dvd)
        self.grupo_midia.addButton(self.radio_bluray)
        self.grupo_midia.addButton(self.radio_digital)

        layout_midia.addWidget(self.radio_dvd)
        layout_midia.addWidget(self.radio_bluray)
        layout_midia.addWidget(self.radio_digital)
        layout_grid.addLayout(layout_midia, 4, 1)

        # 6. Disponibilidade (QCheckBox)
        layout_grid.addWidget(QLabel("Status:"), 5, 0)
        self.check_disponivel = QCheckBox("Disponivel para locacao imediata")
        self.check_disponivel.setChecked(True)
        layout_grid.addWidget(self.check_disponivel, 5, 1)

        # 7. Avaliacao inicial (QSlider conectado dinamicamente a QLabel via sinal/slot)
        layout_grid.addWidget(QLabel("Avaliacao (0-10):"), 6, 0)
        layout_slider = QHBoxLayout()
        self.slider_avaliacao = QSlider(Qt.Orientation.Horizontal)
        self.slider_avaliacao.setRange(0, 10)
        self.slider_avaliacao.setValue(8)

        self.label_valor_slider = QLabel(str(self.slider_avaliacao.value()))
        # Conexao de sinal valueChanged com slot que altera o texto do label (Aula 01 e 02)
        self.slider_avaliacao.valueChanged.connect(self._atualizar_label_avaliacao)

        layout_slider.addWidget(self.slider_avaliacao)
        layout_slider.addWidget(self.label_valor_slider)
        layout_grid.addLayout(layout_slider, 6, 1)

        # 8. Sinopse (QTextEdit)
        layout_grid.addWidget(QLabel("Sinopse:"), 7, 0)
        self.texto_sinopse = QTextEdit()
        self.texto_sinopse.setPlaceholderText("Breve descricao do filme...")
        self.texto_sinopse.setMaximumHeight(80)
        layout_grid.addWidget(self.texto_sinopse, 7, 1)

        # Adiciona o grid ao layout principal
        layout_principal.addLayout(layout_grid)

        # Botoes padrao de dialogo (QDialogButtonBox) vistos na Aula 04
        botoes = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.caixa_botoes = QDialogButtonBox(botoes)
        self.caixa_botoes.accepted.connect(self._validar_e_aceitar)
        self.caixa_botoes.rejected.connect(self.reject)
        layout_principal.addWidget(self.caixa_botoes)

        self.setLayout(layout_principal)

    def _atualizar_label_avaliacao(self, valor):
        """Slot para atualizar o texto do label com o valor do slider."""
        self.label_valor_slider.setText(str(valor))

    def _validar_e_aceitar(self):
        """Slot para validacao antes de aceitar o fechamento do dialogo."""
        titulo = self.campo_titulo.text().strip()
        if not titulo:
            # Demonstracao de alerta com QMessageBox (Aula 04)
            QMessageBox.warning(self, "Aviso de Validacao", "O titulo do filme nao pode ficar vazio.")
            self.campo_titulo.setFocus()
            return
        self.accept()

    def obter_dados(self):
        """Retorna os dados preenchidos no formulario em formato de dicionario."""
        midia = "DVD"
        if self.radio_bluray.isChecked():
            midia = "Blu-ray"
        elif self.radio_digital.isChecked():
            midia = "Digital"

        return {
            "titulo": self.campo_titulo.text().strip(),
            "genero": self.combo_genero.currentText(),
            "ano": self.spin_ano.value(),
            "preco": self.spin_preco.value(),
            "midia": midia,
            "disponivel": self.check_disponivel.isChecked(),
            "avaliacao": self.slider_avaliacao.value(),
            "sinopse": self.texto_sinopse.toPlainText().strip()
        }