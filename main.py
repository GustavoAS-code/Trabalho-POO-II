"""
Ponto de entrada principal da aplicacao de Locadora de Filmes.
"""
import sys
from PySide6.QtWidgets import QApplication

from janelas.janela_principal import JanelaPrincipal


def main():
    app = QApplication(sys.argv)

    janela = JanelaPrincipal()
    janela.show()

    app.exec()

if __name__ == "__main__":
    main()