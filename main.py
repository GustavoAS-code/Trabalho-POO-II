"""
Ponto de entrada principal da aplicacao de Locadora de Filmes.
Conforme visto na Aula 01:
- Instanciacao de QApplication passando sys.argv;
- Instanciacao da janela principal (QMainWindow);
- Chamada do metodo .show();
- Inicio do loop de eventos com app.exec().
"""
import sys
from PySide6.QtWidgets import QApplication

from janelas.janela_principal import JanelaPrincipal


def main():
    # Cria a instancia unica da aplicacao Qt
    app = QApplication(sys.argv)

    # Cria e exibe a janela principal
    janela = JanelaPrincipal()
    janela.show()

    # Inicia o loop de eventos da aplicacao
    sys.exit(app.exec())


if __name__ == "__main__":
    main()