import socket
import threading
import json
import psycopg2
import hashlib
import logging
from datetime import datetime

# Configuração de Logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Config DB
DB_CONFIG = {
    'dbname': 'multiplayer_game',
    'user': 'postgres',  
    'password': 'jonatasariel',  
    'host': 'localhost'
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class Server:
    def __init__(self, host='localhost', port=55555):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}  # {username: client_socket}
        self.games = {}    # {game_id: {'players': [p1, p2], 'board': [[' ']*3 for _ in range(3)], 'turn': p1, 'status': 'active'}}
        self.game_id_counter = 0
        self.lock = threading.Lock()
        logging.info("Servidor iniciado.")
        print("Servidor rodando em", host, port)

    def handle_client(self, client, addr):
        username = None
        try:
            while True:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                with self.lock:
                    if message['type'] == 'register':
                        self.register_user(message['username'], message['password'], client)
                    elif message['type'] == 'login':
                        username = self.login_user(message['username'], message['password'], client, addr)
                    elif username:  # Só processa se logado
                        if message['type'] == 'get_online':
                            self.send_online_users(client)
                        elif message['type'] == 'invite':
                            self.send_invite(message['target'], username, client)
                        elif message['type'] == 'accept_invite':
                            self.start_game(username, message['inviter'])
                        elif message['type'] == 'reject_invite':
                            self.notify_reject(message['inviter'], username)
                        elif message['type'] == 'move':
                            self.process_move(message['game_id'], username, message['position'])
                        elif message['type'] == 'quit_game':
                            self.quit_game(message['game_id'], username)
        except Exception as e:
            logging.error(f"Erro com cliente {addr}: {e}")
        finally:
            if username in self.clients:
                del self.clients[username]
            client.close()
            logging.info(f"Cliente {username} desconectado.")

    def register_user(self, username, password, client):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hash_password(password)))
            conn.commit()
            client.send(json.dumps({'type': 'register_success'}).encode('utf-8'))
            logging.info(f"Usuário registrado: {username}")
        except psycopg2.IntegrityError as e:
            client.send(json.dumps({'type': 'error', 'msg': 'Username já existe'}).encode('utf-8'))
            logging.error(f"Erro de duplicidade: {e}")
        except Exception as e:
            client.send(json.dumps({'type': 'error', 'msg': 'Erro no servidor'}).encode('utf-8'))
            logging.error(f"Erro no registro: {e}")
        finally:
            cur.close()
            conn.close()

    

    def login_user(self, username, password, client, addr):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user and user[1] == hash_password(password):
            if username in self.clients:
                client.send(json.dumps({'type': 'error', 'msg': 'Já logado'}).encode('utf-8'))
                return None
            self.clients[username] = client
            client.send(json.dumps({'type': 'login_success'}).encode('utf-8'))
            logging.info(f"Login: {username} de {addr}")
            return username
        else:
            client.send(json.dumps({'type': 'error', 'msg': 'Credenciais inválidas'}).encode('utf-8'))
            return None

    def send_online_users(self, client):
        online = [u for u in self.clients if u != self.get_username_from_client(client)]
        client.send(json.dumps({'type': 'online_users', 'users': online}).encode('utf-8'))

    def get_username_from_client(self, client):
        for u, c in self.clients.items():
            if c == client:
                return u
        return None

    def send_invite(self, target, inviter, client):
        if target in self.clients:
            self.clients[target].send(json.dumps({'type': 'invite', 'from': inviter}).encode('utf-8'))
            client.send(json.dumps({'type': 'invite_sent'}).encode('utf-8'))
            logging.info(f"Convite de {inviter} para {target}")
        else:
            client.send(json.dumps({'type': 'error', 'msg': 'Usuário offline'}).encode('utf-8'))

    def start_game(self, acceptor, inviter):
        if inviter not in self.clients or acceptor not in self.clients:
            return
        self.game_id_counter += 1
        game_id = self.game_id_counter
        players = [inviter, acceptor]
        board = [[' ' for _ in range(3)] for _ in range(3)]
        turn = players[0]  # Inviter começa
        self.games[game_id] = {'players': players, 'board': board, 'turn': turn, 'status': 'active'}

        # Notificar ambos
        for player in players:
            symbol = 'X' if player == turn else 'O'
            self.clients[player].send(json.dumps({
                'type': 'game_start',
                'game_id': game_id,
                'opponent': players[0] if player == players[1] else players[1],
                'symbol': symbol,
                'turn': turn == player
            }).encode('utf-8'))
        logging.info(f"Partida {game_id} iniciada: {inviter} vs {acceptor}")

        # Salvar no DB
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (inviter,))
        p1_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM users WHERE username = %s", (acceptor,))
        p2_id = cur.fetchone()[0]
        cur.execute("INSERT INTO games (player1_id, player2_id) VALUES (%s, %s)", (p1_id, p2_id))
        conn.commit()
        cur.close()
        conn.close()

    def notify_reject(self, inviter, rejector):
        if inviter in self.clients:
            self.clients[inviter].send(json.dumps({'type': 'invite_rejected', 'from': rejector}).encode('utf-8'))
            logging.info(f"Convite rejeitado por {rejector} para {inviter}")

    def process_move(self, game_id, player, position):
        if game_id not in self.games:
            return
        game = self.games[game_id]
        if game['status'] != 'active' or game['turn'] != player or game['board'][position[0]][position[1]] != ' ':
            return  # Jogada inválida

        symbol = 'X' if player == game['players'][0] else 'O'
        game['board'][position[0]][position[1]] = symbol
        winner = self.check_winner(game['board'])
        if winner:
            self.end_game(game_id, winner)
        elif all(all(cell != ' ' for cell in row) for row in game['board']):
            self.end_game(game_id, 'empate')
        else:
            game['turn'] = game['players'][1] if game['turn'] == game['players'][0] else game['players'][0]

        # Atualizar ambos os jogadores
        for p in game['players']:
            self.clients[p].send(json.dumps({
                'type': 'update_board',
                'game_id': game_id,
                'board': game['board'],
                'turn': game['turn'] == p
            }).encode('utf-8'))

    def check_winner(self, board):
        # Linhas, colunas, diagonais
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ':
                return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != ' ':
                return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != ' ':
            return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ':
            return board[0][2]
        return None

    def end_game(self, game_id, winner):
        game = self.games[game_id]
        game['status'] = 'finished'
        result = 'empate' if winner == 'empate' else winner
        for p in game['players']:
            is_winner = (winner != 'empate' and ((p == game['players'][0] and winner == 'X') or (p == game['players'][1] and winner == 'O')))
            self.clients[p].send(json.dumps({
                'type': 'game_end',
                'game_id': game_id,
                'result': 'vitória' if is_winner else 'derrota' if winner != 'empate' else 'empate'
            }).encode('utf-8'))
        logging.info(f"Partida {game_id} terminada: {result}")

        # Atualizar DB
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        winner_id = None
        if winner != 'empate':
            winner_username = game['players'][0] if winner == 'X' else game['players'][1]
            cur.execute("SELECT id FROM users WHERE username = %s", (winner_username,))
            winner_id = cur.fetchone()[0]
        cur.execute("UPDATE games SET status = 'finished', winner_id = %s WHERE id = %s", (winner_id, game_id))
        conn.commit()
        cur.close()
        conn.close()

    def quit_game(self, game_id, player):
        if game_id in self.games:
            game = self.games[game_id]
            opponent = game['players'][1] if player == game['players'][0] else game['players'][0]
            self.end_game(game_id, 'X' if opponent == game['players'][0] else 'O')  # Concede vitória ao oponente
            logging.info(f"Jogador {player} abandonou partida {game_id}")

    def run(self):
        while True:
            client, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client, addr))
            thread.start()

if __name__ == "__main__":
    server = Server()
    server.run()