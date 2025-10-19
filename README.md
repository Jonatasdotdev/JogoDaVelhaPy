# Jogo da Velha Multiplayer 

Este é um projeto de Jogo da Velha multiplayer. O jogo permite que dois jogadores se conectem via rede (cliente-servidor) usando Python, com interface gráfica estilizada e suporte a banco de dados PostgreSQL.

## Descrição
O jogo inclui:
- Registro e login de usuários.
- Lista de jogadores online.
- Sistema de convites para partidas.
- Tabuleiro estilizado com Pygame, embutido em uma interface Tkinter personalizada.
- Sincronização de jogadas em tempo real.
- Registro de partidas no banco de dados.

## Imagens
<img width="887" height="597" alt="image" src="https://github.com/user-attachments/assets/c14bf051-3b53-4337-bf13-d69fd8858743" />
<img width="897" height="606" alt="image" src="https://github.com/user-attachments/assets/aea6e082-ff88-4351-97da-a0d9d9c19032" />

https://github.com/user-attachments/assets/234252ff-4b46-4038-b631-ac1a8bb003e0







## Tecnologias Utilizadas
- **Linguagem:** Python 3.x
- **Interface Gráfica:** Tkinter com CustomTkinter
- **Jogo:** Pygame
- **Rede:** Sockets TCP
- **Banco de Dados:** PostgreSQL
- **Controle de Versão:** Git

## Pré-requisitos
- Python 3.8 ou superior
- PostgreSQL instalado e configurado
- Bibliotecas Python: `customtkinter`, `pygame`, `psycopg2-binary`

## Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/seu-repositorio.git
   cd seu-repositorio
   ```

## Instale as dependências:
```
pip install -r requirements.txt
```


## Crie um banco chamado multiplayer_game.

Execute os comandos SQL no arquivo database_setup.sql
Edite server.py com suas credenciais de banco de dados no DB_CONFIG.

## Como Executar

Inicie o servidor:
```
python server.py
```
Inicie um ou mais clientes:
```
python client.py
```
