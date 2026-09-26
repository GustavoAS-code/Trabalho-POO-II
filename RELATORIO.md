# Sistema de Locadora de Filmes

Este projeto consiste em uma interface gráfica de usuário desenvolvida para o gerenciamento de uma locadora de filmes. O sistema foi criado como trabalho prático da disciplina utilizando a linguagem Python e a biblioteca PySide6.

## Funcionalidades

O sistema permite o gerenciamento do acervo com as seguintes funcionalidades:
* Visualização do catálogo através de uma tabela interativa.
* Cadastro de novos títulos utilizando um formulário em formato de diálogo modal.
* Janela secundária independente dedicada a exibir a ficha técnica e os detalhes do filme selecionado.
* Sistema de busca rápida e filtros de catálogo por título e gênero.
* Alternância no status dos filmes (locação e devolução) diretamente na tela principal ou na janela de detalhes.
* Remoção de filmes mediante alerta de confirmação.
* Barra de progresso visual que indica a taxa de disponibilidade atual do acervo.

## Requisitos Técnicos Implementados

O desenvolvimento do software atendeu às seguintes exigências técnicas:
* Sinais e Slots: Uso de conexões nativas e criação de um sinal customizado chamado statusModificado para sincronização entre janelas.
* Eventos: Sobrescrita de eventos virtuais, especificamente closeEvent (para confirmação de saída) e keyPressEvent (para atalhos).
* Widgets: Utilização de componentes variados como QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QRadioButton, QCheckBox, QSlider e QTextEdit.
* Layouts: Organização estrutural da interface utilizando QVBoxLayout, QHBoxLayout, QGridLayout e QStackedLayout.
* Menus e Barras de Ferramentas: Implementação de QMenuBar e QToolBar contendo ações principais e campo de busca rápida.
* Dialogs e Alertas: Uso de QMessageBox para interações rápidas e da classe QDialog para o formulário de cadastro bloqueante.
* Janela Adicional: Implementação de uma tela não-bloqueante extra para exibir os detalhes da obra.

## Estrutura do Projeto

O código-fonte foi modularizado em arquivos separados para facilitar a manutenção:
* main.py: Arquivo principal de execução e ponto de partida do sistema.
* janelas/: Módulo que contém a interface central e as barras do sistema.
* componentes/: Módulo que guarda o diálogo de cadastro e a janela secundária de detalhes.
* dados/: Módulo responsável pelo repositório que armazena os dados dos filmes em memória.

## Instruções de Execução

Primeiramente, certifique-se de ter o Python instalado em sua máquina.

### Linux

Para a primeira execução, crie um ambiente virtual e instale as dependências do projeto:
```bash
python3 -m venv venv
source venv/bin/activate
pip install pyside6