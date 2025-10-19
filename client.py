import socket
import threading
import json
import customtkinter as ctk  
from gui import GUI
from game_pygame import PygameGame
from tkinter import messagebox

class Client:
    def __init__(self, host='localhost', port=55555):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.username = None
        self.current_game_id = None
        self.symbol = None
        self.my_turn = False
        self.pygame_game = None  

        # GUI
        self.root = ctk.CTk()
        self.root.title("Jogo Multiplayer - Jala Capstone")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.gui = GUI(self.root, self)
        self.gui.show_login_screen()

        # Thread para receber mensagens
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        self.root.mainloop()

    def on_close(self):
        if self.username and self.current_game_id:
            self.send_message({'type': 'quit_game', 'game_id': self.current_game_id})
        if self.pygame_game:
            self.pygame_game.stop()
        self.client.close()
        self.root.destroy()

    def send_message(self, message):
        try:
            self.client.send(json.dumps(message).encode('utf-8'))
            print(f"[CLIENT] Enviando: {message}")
        except Exception as e:
            print(f"[CLIENT] Erro ao enviar: {e}")

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                print(f"[CLIENT] Recebido: {message}")
                
                if message['type'] == 'register_success':
                    self.gui.show_custom_modal("✅ Sucesso", "Conta registrada com sucesso!", "success")
                    self.root.after(1500, self.gui.show_login_screen)
                elif message['type'] == 'login_success':
                    self.username = self.gui.login_username_entry.get()
                    self.gui.show_main_screen()
                elif message['type'] == 'error':
                    self.gui.show_custom_modal("❌ Erro", message['msg'], "error")
                elif message['type'] == 'online_users':
                    self.gui.update_online_list(message['users'])
                elif message['type'] == 'invite':
                    self.gui.show_invite_modal(message['from'])
                elif message['type'] == 'invite_sent':
                    self.gui.show_custom_modal("📨 Convite", "Convite enviado! Aguardando resposta...", "info")
                elif message['type'] == 'invite_rejected':
                    self.gui.show_custom_modal("😔 Convite Recusado", f"{message['from']} rejeitou seu convite.", "warning")
                elif message['type'] == 'game_start':
                    self.current_game_id = message['game_id']
                    self.symbol = message['symbol']
                    self.my_turn = message['turn']
                    self.opponent = message['opponent']
                    self.gui.show_game_screen()
                elif message['type'] == 'update_board':
                    if self.pygame_game:
                        self.pygame_game.update_board(message['board'], message['turn'])
                    self.gui.turn_label.configure(text="🎮 Sua vez!" if message['turn'] else "⏳ Vez do oponente")
                elif message['type'] == 'game_end':
                    result_type = "success" if "ganhou" in message['result'].lower() or "venceu" in message['result'].lower() else "info"
                    self.gui.show_custom_modal("🏁 Fim de Jogo", message['result'], result_type)
                    self.root.after(2500, self._end_game)
            except Exception as e:
                print(f"Erro na recepção: {e}")
                break

    def _end_game(self):
        """Helper to end game after modal"""
        if self.pygame_game:
            self.pygame_game.stop()
        self.gui.show_main_screen()
        self.current_game_id = None

    def register(self):
        username = self.gui.reg_username_entry.get()
        password = self.gui.reg_password_entry.get()
        if not username or not password:
            self.gui.show_custom_modal("⚠️ Atenção", "Preencha todos os campos!", "warning")
            return
        self.send_message({'type': 'register', 'username': username, 'password': password})

    def login(self):
        username = self.gui.login_username_entry.get()
        password = self.gui.login_password_entry.get()
        if username and password:
            self.send_message({'type': 'login', 'username': username, 'password': password})

    def get_online_users(self):
        self.send_message({'type': 'get_online'})

    def invite_selected(self):
        selected = self.gui.online_list.curselection()
        if selected:
            display_text = self.gui.online_list.get(selected[0])
            target = display_text.replace("👤", "").strip()
            
            print(f"[CLIENT] Convidando usuário: '{target}'")
            self.send_message({'type': 'invite', 'target': target})
        else:
            self.gui.show_custom_modal("⚠️ Atenção", "Selecione um usuário na lista!", "warning")

    def start_pygame_game(self, embed_frame):
        self.pygame_game = PygameGame(self, embed_frame)

    def make_move(self, x, y):
        if self.my_turn:
            self.send_message({'type': 'move', 'game_id': self.current_game_id, 'position': (x, y)})

    def quit_game(self):
        if self.current_game_id:
            self.send_message({'type': 'quit_game', 'game_id': self.current_game_id})
        self.gui.show_main_screen()

if __name__ == "__main__":
    Client()
