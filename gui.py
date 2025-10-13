import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import styles

ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue")  

class GUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client

    def clear_screen(self):
        self.root.after(100, lambda: [widget.destroy() for widget in self.root.winfo_children()])

    def show_login_screen(self):
        self.clear_screen()
        self.root.configure(fg_color=styles.BG_COLOR)
        self.root.after(150, self._build_login_screen)  

    def _build_login_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.PRIMARY_COLOR, corner_radius=10)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Login", font=(styles.FONT_FAMILY, styles.FONT_SIZE_LARGE), text_color=styles.TEXT_COLOR).pack(pady=10)

        self.login_username_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=200)
        self.login_username_entry.pack(pady=5)

        self.login_password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=200)
        self.login_password_entry.pack(pady=5)

        ctk.CTkButton(frame, text="Login", command=self.client.login, fg_color=styles.SECONDARY_COLOR, hover_color="#1A237E").pack(pady=10)
        ctk.CTkButton(frame, text="Registrar", command=self.show_register_screen, fg_color=styles.SECONDARY_COLOR, hover_color="#1A237E").pack(pady=5)

    def show_register_screen(self):
        self.clear_screen()
        self.root.after(150, self._build_register_screen)  

    def _build_register_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.PRIMARY_COLOR, corner_radius=10)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="Registro", font=(styles.FONT_FAMILY, styles.FONT_SIZE_LARGE), text_color=styles.TEXT_COLOR).pack(pady=10)

        self.reg_username_entry = ctk.CTkEntry(frame, placeholder_text="Novo Username", width=200)
        self.reg_username_entry.pack(pady=5)

        self.reg_password_entry = ctk.CTkEntry(frame, placeholder_text="Nova Password", show="*", width=200)
        self.reg_password_entry.pack(pady=5)

        ctk.CTkButton(frame, text="Registrar", command=self.client.register, fg_color=styles.SECONDARY_COLOR, hover_color="#1A237E").pack(pady=10)
        ctk.CTkButton(frame, text="Voltar", command=self.show_login_screen, fg_color=styles.SECONDARY_COLOR, hover_color="#1A237E").pack(pady=5)

    def show_main_screen(self):
        self.clear_screen()
        self.root.after(150, self._build_main_screen) 

    def _build_main_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.PRIMARY_COLOR, corner_radius=10)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text=f"Bem-vindo, {self.client.username}!", font=(styles.FONT_FAMILY, styles.FONT_SIZE_MEDIUM), text_color=styles.TEXT_COLOR).pack(pady=10)

        self.online_list = tk.Listbox(frame, width=30, height=10, font=(styles.FONT_FAMILY, styles.FONT_SIZE_SMALL))
        self.online_list.pack(pady=10)

        ctk.CTkButton(frame, text="Atualizar Online", command=self.client.get_online_users, fg_color=styles.SECONDARY_COLOR).pack(pady=5)
        ctk.CTkButton(frame, text="Convidar Selecionado", command=self.client.invite_selected, fg_color=styles.SECONDARY_COLOR).pack(pady=5)

    def update_online_list(self, users):
        self.online_list.delete(0, tk.END)
        for user in users:
            self.online_list.insert(tk.END, user)

    def show_game_screen(self):
        self.clear_screen()
        self.root.after(150, self._build_game_screen)  

    def _build_game_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.BG_COLOR)
        frame.pack(fill="both", expand=True)

        ctk.CTkLabel(frame, text=f"Jogando contra {self.client.opponent} | Seu símbolo: {self.client.symbol}", 
                     font=(styles.FONT_FAMILY, styles.FONT_SIZE_MEDIUM)).pack(pady=10)

        self.turn_label = ctk.CTkLabel(frame, text="Sua vez!" if self.client.my_turn else "Vez do oponente", 
                                       font=(styles.FONT_FAMILY, styles.FONT_SIZE_SMALL))
        self.turn_label.pack(pady=5)

        # Frame para embutir Pygame - usar tk.Frame ao invés de CTkFrame
        self.embed_frame = tk.Frame(frame, width=400, height=400, bg=styles.BOARD_COLOR)
        self.embed_frame.pack(pady=10)
        self.embed_frame.pack_propagate(False)  # Mantém o tamanho fixo
        
        # Força atualização antes de iniciar Pygame
        self.embed_frame.update_idletasks()
        self.embed_frame.update()

        ctk.CTkButton(frame, text="Abandonar", command=self.client.quit_game, fg_color=styles.SECONDARY_COLOR).pack(pady=10)

        # Iniciar Pygame embutido após um pequeno delay
        self.root.after(200, lambda: self.client.start_pygame_game(self.embed_frame))