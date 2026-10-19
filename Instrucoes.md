# Instruções para execução

Primeiramente, certifique-se de ter o Python instalado em sua máquina.

## Linux / macOS

**1. Primeira vez rodando (Configuração do ambiente):** 
Você deve criar um ambiente virtual (venv) para isolar as dependências do projeto:
```bash
python3 -m venv venv
```

**2. Ativação (Obrigatório sempre que for rodar):** 
Para executar o projeto, você deve ativar a venv:
```bash
source venv/bin/activate
```

**3. Instalação de dependências (Primeira vez):** 
Instale a biblioteca gráfica do Qt:
```bash
pip install pyside6
```

**4. Execução (Obrigatório):** 
Em seguida, rode o comando para iniciar o programa principal:
```bash
python3 main.py
```

## Windows

**1. Primeira vez rodando (Configuração do ambiente):** 
Abra o terminal na pasta do projeto e crie o ambiente virtual:
```cmd
python -m venv venv
```

**2. Ativação (Obrigatório sempre que for rodar):** 
Ative o ambiente virtual com o comando:
```cmd
venv\Scripts\activate
```

**3. Instalação de dependências (Primeira vez):** 
Instale a biblioteca gráfica do Qt:
```cmd
pip install pyside6
```

**4. Execução (Obrigatório):** 
Rode o comando para iniciar o programa principal:
```cmd
python main.py
```