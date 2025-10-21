import socket
import threading
import json
import customtkinter as ctk  
from gui import GUI
from game_pygame import PygameGame
from tkinter import messagebox

class Client:
    def __init__(self, host='26.78.90.245', port=55555):
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
        self.root.geometry("900x600")  # Janela maior
        self.root.minsize(800, 550)  # Tamanho mínimo
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
            print(f"[CLIENT] Enviando: {message}")  # Debug
        except ConnectionAbortedError:
            print("[CLIENT] Conexão abortada ao enviar")
            try:
                self.root.after(0, lambda: messagebox.showerror("Erro", "Conexão com o servidor foi perdida."))
            except:
                pass
        except Exception as e:
            print(f"[CLIENT] Erro ao enviar: {e}")
            try:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao enviar mensagem: {e}"))
            except:
                pass

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(4096).decode('utf-8')
                if not data:
                    print("[CLIENT] Conexão fechada pelo servidor")
                    self.root.after(0, lambda: messagebox.showerror("Erro", "Conexão perdida com o servidor."))
                    break
                message = json.loads(data)
                print(f"[CLIENT] Recebido: {message}")  # Debug

                mtype = message.get('type')

                # Helper wrappers para executar no thread principal do Tkinter
                def show_register_success():
                    self.gui.show_custom_modal("✅ Sucesso", "Conta registrada com sucesso!", "success")
                    self.root.after(1500, self.gui.show_login_screen)

                def show_login_success():
                    # Se desejar, pode usar username do message, senão pega do entry
                    if 'username' in message:
                        self.username = message['username']
                    else:
                        try:
                            self.username = self.gui.login_username_entry.get()
                        except:
                            self.username = None
                    self.gui.show_main_screen()

                def show_error():
                    self.gui.show_custom_modal("❌ Erro", message.get('msg', 'Erro'), "error")

                def update_online():
                    self.gui.update_online_list(message.get('users', []))

                def show_invite():
                    self.gui.show_invite_modal(message.get('from'))

                def invite_sent():
                    self.gui.show_custom_modal("📨 Convite", "Convite enviado! Aguardando resposta...", "info")

                def invite_rejected():
                    self.gui.show_custom_modal("😔 Convite Recusado", f"{message.get('from')} rejeitou seu convite.", "warning")

                def start_game():
                    self.current_game_id = message.get('game_id')
                    self.symbol = message.get('symbol')
                    self.my_turn = message.get('turn', False)
                    self.opponent = message.get('opponent')
                    self.gui.show_game_screen()

                def update_board_and_turn():
                    board = message.get('board')
                    turn = message.get('turn', False)
                    if self.pygame_game and board is not None:
                        try:
                            self.pygame_game.update_board(board, turn)
                        except Exception as e:
                            print(f"[CLIENT] Erro ao atualizar pygame_game: {e}")
                    try:
                        self.gui.turn_label.configure(text="🎮 Sua vez!" if turn else "⏳ Vez do oponente")
                    except Exception:
                        pass

                def game_end():
                    result = message.get('result', '')
                    result_type = "success" if "ganhou" in result.lower() or "venceu" in result.lower() else "info"
                    self.gui.show_custom_modal("🏁 Fim de Jogo", result, result_type)
                    self.root.after(2500, self._end_game)

                # Map message types to actions (all scheduled in main thread)
                if mtype == 'register_success':
                    self.root.after(0, show_register_success)
                elif mtype == 'login_success':
                    self.root.after(0, show_login_success)
                elif mtype == 'error':
                    self.root.after(0, show_error)
                elif mtype == 'online_users':
                    self.root.after(0, update_online)
                elif mtype == 'invite':
                    self.root.after(0, show_invite)
                elif mtype == 'invite_sent':
                    self.root.after(0, invite_sent)
                elif mtype == 'invite_rejected':
                    self.root.after(0, invite_rejected)
                elif mtype == 'game_start':
                    self.root.after(0, start_game)
                elif mtype == 'update_board':
                    self.root.after(0, update_board_and_turn)
                elif mtype == 'game_end':
                    self.root.after(0, game_end)

            except Exception as e:
                print(f"Erro na recepção: {e}")
                try:
                    self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na recepção: {e}"))
                except:
                    pass
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
            # Pega o texto da lista que tem formato "  👤 username"
            display_text = self.gui.online_list.get(selected[0])
            # Remove o emoji e espaços para pegar só o username
            target = display_text.replace("👤", "").strip()
            
            print(f"[CLIENT] Convidando usuário: '{target}'")  # Debug
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