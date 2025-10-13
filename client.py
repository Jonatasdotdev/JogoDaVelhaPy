import socket
import threading
import json
from tkinter import messagebox
import customtkinter as ctk  
from gui import GUI
from game_pygame import PygameGame

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
        self.root.geometry("400x500")
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
        self.client.send(json.dumps(message).encode('utf-8'))

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode('utf-8')
                if not data:
                    break
                message = json.loads(data)
                if message['type'] == 'register_success':
                    messagebox.showinfo("Sucesso", "Registrado!")
                    self.gui.show_login_screen()
                elif message['type'] == 'login_success':
                    self.username = self.gui.login_username_entry.get()
                    self.gui.show_main_screen()
                elif message['type'] == 'error':
                    messagebox.showerror("Erro", message['msg'])
                elif message['type'] == 'online_users':
                    self.gui.update_online_list(message['users'])
                elif message['type'] == 'invite':
                    response = messagebox.askyesno("Convite", f"{message['from']} te convidou para jogar. Aceitar?")
                    self.send_message({'type': 'accept_invite' if response else 'reject_invite', 'inviter': message['from']})
                elif message['type'] == 'invite_sent':
                    messagebox.showinfo("Convite", "Convite enviado!")
                elif message['type'] == 'invite_rejected':
                    messagebox.showinfo("Convite", f"{message['from']} rejeitou seu convite.")
                elif message['type'] == 'game_start':
                    self.current_game_id = message['game_id']
                    self.symbol = message['symbol']
                    self.my_turn = message['turn']
                    self.opponent = message['opponent']
                    self.gui.show_game_screen()
                elif message['type'] == 'update_board':
                    if self.pygame_game:
                        self.pygame_game.update_board(message['board'], message['turn'])
                    self.gui.turn_label.configure(text="Sua vez!" if message['turn'] else "Vez do oponente")
                elif message['type'] == 'game_end':
                    messagebox.showinfo("Fim de Jogo", f"Resultado: {message['result']}")
                    if self.pygame_game:
                        self.pygame_game.stop()
                    self.gui.show_main_screen()
                    self.current_game_id = None
            except Exception as e:
                print(f"Erro na recepção: {e}")
                break

    def register(self):
        username = self.gui.reg_username_entry.get()
        password = self.gui.reg_password_entry.get()
        if not username or not password:
            messagebox.showerror("Erro", "Preencha todos os campos!")
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
            target = self.gui.online_list.get(selected[0])
            self.send_message({'type': 'invite', 'target': target})
        else:
            messagebox.showerror("Erro", "Selecione um usuário na lista!")

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