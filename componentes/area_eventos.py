"""
Componente visual para demonstracao e manipulacao de Eventos de baixo nivel do Qt.
Conforme estudado na Aula 02, eventos tratam interacoes do sistema operacional/hardware.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class AreaEventosWidget(QFrame):
    """
    Widget customizado que sobrescreve metodos virtuais de eventos
    (mouse e teclado) e emite sinais customizados para a aplicacao.
    """
    # Sinal customizado emitido quando um evento de baixo nivel e capturado
    eventoDetectado = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuracao visual basica da area de eventos
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setMinimumHeight(100)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # Permite receber eventos de teclado

        # Habilita o rastreamento do mouse mesmo sem botoes pressionados (visto na Aula 02)
        self.setMouseTracking(True)

        # Layout interno e rotulos explicativos
        layout = QVBoxLayout()
        self.label_titulo = QLabel("Area Interativa de Captura de Eventos (Aula 02)")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setStyleSheet("font-weight: bold; color: #2c3e50;")

        self.label_info = QLabel("Passe o mouse, clique com botao esquerdo/direito ou pressione teclas aqui")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_info)
        self.setLayout(layout)

    def mousePressEvent(self, event):
        """Manipulador sobrescrito para clique do mouse."""
        botao = "Desconhecido"
        if event.button() == Qt.MouseButton.LeftButton:
            botao = "Esquerdo"
        elif event.button() == Qt.MouseButton.RightButton:
            botao = "Direito"
        elif event.button() == Qt.MouseButton.MiddleButton:
            botao = "Meio"

        pos = event.pos()
        mensagem = f"mousePressEvent: Botao {botao} pressionado na posicao ({pos.x()}, {pos.y()})"
        self.label_info.setText(mensagem)
        self.eventoDetectado.emit(mensagem)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Manipulador sobrescrito para liberacao do botao do mouse."""
        mensagem = f"mouseReleaseEvent: Botao liberado na posicao ({event.pos().x()}, {event.pos().y()})"
        self.label_info.setText(mensagem)
        self.eventoDetectado.emit(mensagem)
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Manipulador sobrescrito para deteccao de clique duplo."""
        mensagem = f"mouseDoubleClickEvent: Clique duplo na posicao ({event.pos().x()}, {event.pos().y()})"
        self.label_info.setText(mensagem)
        self.eventoDetectado.emit(mensagem)
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        """Manipulador sobrescrito para movimento do cursor."""
        pos = event.pos()
        mensagem = f"mouseMoveEvent: Cursor em ({pos.x()}, {pos.y()})"
        self.label_info.setText(mensagem)
        self.eventoDetectado.emit(mensagem)
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        """Manipulador sobrescrito para deteccao de teclas do teclado."""
        tecla = event.text()
        mensagem = f"keyPressEvent: Tecla pressionada: '{tecla}' (Codigo: {event.key()})"
        self.label_info.setText(mensagem)
        self.eventoDetectado.emit(mensagem)
        super().keyPressEvent(event)