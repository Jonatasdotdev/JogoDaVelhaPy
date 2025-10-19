import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import styles
from PIL import Image, ImageTk, ImageDraw
import math

ctk.set_appearance_mode("dark") 
ctk.set_default_color_theme("blue")  

class GUI:
    def __init__(self, root, client):
        self.root = root
        self.client = client
        self.animation_id = None
        self.modal_window = None

    def show_custom_modal(self, title, message, modal_type="info"):
        """Show a custom styled modal dialog"""
        if self.modal_window:
            try:
                self.modal_window.destroy()
            except:
                pass
        
        self.modal_window = ctk.CTkToplevel(self.root)
        self.modal_window.title(title)
        self.modal_window.geometry("400x250")
        self.modal_window.resizable(False, False)
        
        # Center the modal
        self.modal_window.transient(self.root)
        self.modal_window.grab_set()
        
        # Color based on type
        colors = {
            "success": styles.SUCCESS_COLOR,
            "error": styles.HIGHLIGHT_COLOR,
            "warning": "#FFA500",
            "info": styles.ACCENT_COLOR
        }
        color = colors.get(modal_type, styles.ACCENT_COLOR)
        
        # Main frame
        frame = ctk.CTkFrame(self.modal_window, fg_color=styles.SECONDARY_COLOR)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header with colored bar
        header = ctk.CTkFrame(frame, fg_color=color, height=60)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=(styles.FONT_FAMILY, 22, "bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Message
        ctk.CTkLabel(
            frame,
            text=message,
            font=(styles.FONT_FAMILY, 16),
            text_color=styles.TEXT_COLOR,
            wraplength=350
        ).pack(pady=40, padx=20)
        
        # OK butto
        ctk.CTkButton(
            frame,
            text="OK",
            command=self.modal_window.destroy,
            fg_color=color,
            hover_color=self.darken_color(color),
            width=120,
            height=40,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 14, "bold")
        ).pack(pady=20)
        
        # Auto close after 3 seconds for info messages
        if modal_type == "info":
            self.root.after(3000, lambda: self.close_modal_safe())
    
    def show_invite_modal(self, inviter):
        """Show custom invite modal with accept/reject"""
        if self.modal_window:
            try:
                self.modal_window.destroy()
            except:
                pass
        
        self.modal_window = ctk.CTkToplevel(self.root)
        self.modal_window.title("🎮 Convite de Jogo")
        self.modal_window.geometry("450x300")
        self.modal_window.resizable(False, False)
        
        self.modal_window.transient(self.root)
        self.modal_window.grab_set()
        
        # Main frame
        frame = ctk.CTkFrame(self.modal_window, fg_color=styles.SECONDARY_COLOR)
        frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Header
        header = ctk.CTkFrame(frame, fg_color=styles.HIGHLIGHT_COLOR, height=70)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="⚔️ DESAFIO RECEBIDO!",
            font=(styles.FONT_FAMILY, 24, "bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Message
        ctk.CTkLabel(
            frame,
            text=f"{inviter} te desafiou para uma partida!",
            font=(styles.FONT_FAMILY, 18),
            text_color=styles.TEXT_COLOR
        ).pack(pady=30)
        
        ctk.CTkLabel(
            frame,
            text="Você aceita o desafio?",
            font=(styles.FONT_FAMILY, 14),
            text_color="#888888"
        ).pack(pady=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(frame, fg_color="transparent")
        button_frame.pack(pady=30)
        
        def accept():
            self.client.send_message({'type': 'accept_invite', 'inviter': inviter})
            self.modal_window.destroy()
        
        def reject():
            self.client.send_message({'type': 'reject_invite', 'inviter': inviter})
            self.modal_window.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="✅ ACEITAR",
            command=accept,
            fg_color=styles.SUCCESS_COLOR,
            hover_color="#00b8cc",
            width=150,
            height=45,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 16, "bold")
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="❌ RECUSAR",
            command=reject,
            fg_color=styles.HIGHLIGHT_COLOR,
            hover_color="#d63850",
            width=150,
            height=45,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 16, "bold")
        ).pack(side="left", padx=10)
    
    def close_modal_safe(self):
        """Safely close modal if it exists"""
        if self.modal_window:
            try:
                self.modal_window.destroy()
                self.modal_window = None
            except:
                pass
    
    def darken_color(self, hex_color):
        """Darken a hex color"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'

    def clear_screen(self):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
        self.root.after(100, lambda: [widget.destroy() for widget in self.root.winfo_children()])

    def create_gradient_canvas(self, parent, width, height):
        """Create a gradient background canvas"""
        canvas = tk.Canvas(parent, width=width, height=height, highlightthickness=0)
        canvas.pack(fill="both", expand=True)
        
        # Create gradient effect
        for i in range(height):
            ratio = i / height
            r = int(15 + (26 - 15) * ratio)
            g = int(15 + (33 - 15) * ratio)
            b = int(30 + (62 - 30) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            canvas.create_line(0, i, width, i, fill=color)
        
        return canvas

    def show_login_screen(self):
        self.clear_screen()
        self.root.configure(fg_color=styles.BG_COLOR)
        self.root.after(150, self._build_login_screen)  

    def _build_login_screen(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Left side - Illustration/Design
        left_frame = ctk.CTkFrame(main_frame, fg_color=styles.PRIMARY_COLOR, corner_radius=0)
        left_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        # Animated welcome text
        welcome_label = ctk.CTkLabel(
            left_frame, 
            text="WELCOME", 
            font=(styles.FONT_FAMILY, 48, "bold"),
            text_color=styles.HIGHLIGHT_COLOR
        )
        welcome_label.pack(pady=(80, 10))

        subtitle = ctk.CTkLabel(
            left_frame,
            text="Multiplayer Tic-Tac-Toe",
            font=(styles.FONT_FAMILY, 20),
            text_color=styles.SUCCESS_COLOR
        )
        subtitle.pack(pady=10)

        # Animated game icon
        self.create_animated_icon(left_frame)

        # Right side - Login form
        right_frame = ctk.CTkFrame(main_frame, fg_color=styles.SECONDARY_COLOR, corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        # Login container
        login_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        login_container.place(relx=0.5, rely=0.5, anchor="center")

        # Avatar circle
        avatar_frame = ctk.CTkFrame(
            login_container, 
            width=80, 
            height=80, 
            fg_color=styles.ACCENT_COLOR,
            corner_radius=40
        )
        avatar_frame.pack(pady=20)
        
        ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=(styles.FONT_FAMILY, 40)
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            login_container, 
            text="Sign In", 
            font=(styles.FONT_FAMILY, styles.FONT_SIZE_LARGE, "bold"),
            text_color=styles.TEXT_COLOR
        ).pack(pady=(0, 20))

        # Email field with icon
        email_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        email_frame.pack(pady=10)
        
        ctk.CTkLabel(email_frame, text="📧", font=(styles.FONT_FAMILY, 16)).pack(side="left", padx=(0, 5))
        self.login_username_entry = ctk.CTkEntry(
            email_frame, 
            placeholder_text="Username",
            width=250,
            height=40,
            border_width=2,
            corner_radius=10,
            border_color=styles.ACCENT_COLOR,
            fg_color=styles.PRIMARY_COLOR
        )
        self.login_username_entry.pack(side="left")

        # Password field with icon
        password_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        password_frame.pack(pady=10)
        
        ctk.CTkLabel(password_frame, text="🔒", font=(styles.FONT_FAMILY, 16)).pack(side="left", padx=(0, 5))
        self.login_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="Password",
            show="*",
            width=250,
            height=40,
            border_width=2,
            corner_radius=10,
            border_color=styles.ACCENT_COLOR,
            fg_color=styles.PRIMARY_COLOR
        )
        self.login_password_entry.pack(side="left")

        # Login button with gradient effect
        login_btn = ctk.CTkButton(
            login_container,
            text="LOGIN",
            command=self.client.login,
            fg_color=styles.HIGHLIGHT_COLOR,
            hover_color="#d63850",
            width=280,
            height=45,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 16, "bold")
        )
        login_btn.pack(pady=20)

        # Register link
        register_frame = ctk.CTkFrame(login_container, fg_color="transparent")
        register_frame.pack(pady=10)
        
        ctk.CTkLabel(
            register_frame,
            text="No account yet?",
            text_color="#888888",
            font=(styles.FONT_FAMILY, 12)
        ).pack(side="left", padx=(0, 5))
        
        register_link = ctk.CTkButton(
            register_frame,
            text="SIGN UP NOW",
            command=self.show_register_screen,
            fg_color="transparent",
            hover_color=styles.ACCENT_COLOR,
            width=100,
            height=25,
            font=(styles.FONT_FAMILY, 12, "bold"),
            text_color=styles.SUCCESS_COLOR
        )
        register_link.pack(side="left")

    def create_animated_icon(self, parent):
        """Create an animated tic-tac-toe board icon"""
        canvas_frame = ctk.CTkFrame(parent, fg_color="transparent")
        canvas_frame.pack(pady=30)
        
        canvas = tk.Canvas(canvas_frame, width=200, height=200, bg=styles.PRIMARY_COLOR, highlightthickness=0)
        canvas.pack()
        
        # Draw grid
        for i in range(1, 3):
            canvas.create_line(i * 66, 10, i * 66, 190, fill=styles.LINE_COLOR, width=3)
            canvas.create_line(10, i * 66, 190, i * 66, fill=styles.LINE_COLOR, width=3)
        
        # Draw X and O with glow effect
        # X at (0,0)
        canvas.create_line(20, 20, 56, 56, fill=styles.X_COLOR, width=5)
        canvas.create_line(56, 20, 20, 56, fill=styles.X_COLOR, width=5)
        
        # O at (1,2)
        canvas.create_oval(138, 138, 182, 182, outline=styles.O_COLOR, width=5)
        
        # X at (2,1)
        canvas.create_line(138, 72, 182, 116, fill=styles.X_COLOR, width=5)
        canvas.create_line(182, 72, 138, 116, fill=styles.X_COLOR, width=5)

    def show_register_screen(self):
        self.clear_screen()
        self.root.after(150, self._build_register_screen)  

    def _build_register_screen(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # Left side - Design
        left_frame = ctk.CTkFrame(main_frame, fg_color=styles.PRIMARY_COLOR, corner_radius=0)
        left_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)

        welcome_label = ctk.CTkLabel(
            left_frame, 
            text="JOIN US", 
            font=(styles.FONT_FAMILY, 48, "bold"),
            text_color=styles.HIGHLIGHT_COLOR
        )
        welcome_label.pack(pady=(80, 10))

        subtitle = ctk.CTkLabel(
            left_frame,
            text="Create Your Account",
            font=(styles.FONT_FAMILY, 20),
            text_color=styles.SUCCESS_COLOR
        )
        subtitle.pack(pady=10)

        self.create_animated_icon(left_frame)

        # Right side - Register form
        right_frame = ctk.CTkFrame(main_frame, fg_color=styles.SECONDARY_COLOR, corner_radius=0)
        right_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        register_container = ctk.CTkFrame(right_frame, fg_color="transparent")
        register_container.place(relx=0.5, rely=0.5, anchor="center")

        # Avatar
        avatar_frame = ctk.CTkFrame(
            register_container, 
            width=80, 
            height=80, 
            fg_color=styles.ACCENT_COLOR,
            corner_radius=40
        )
        avatar_frame.pack(pady=20)
        
        ctk.CTkLabel(
            avatar_frame,
            text="👤",
            font=(styles.FONT_FAMILY, 40)
        ).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            register_container, 
            text="Register", 
            font=(styles.FONT_FAMILY, styles.FONT_SIZE_LARGE, "bold"),
            text_color=styles.TEXT_COLOR
        ).pack(pady=(0, 20))

        # Username field
        username_frame = ctk.CTkFrame(register_container, fg_color="transparent")
        username_frame.pack(pady=10)
        
        ctk.CTkLabel(username_frame, text="📧", font=(styles.FONT_FAMILY, 16)).pack(side="left", padx=(0, 5))
        self.reg_username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="New Username",
            width=250,
            height=40,
            border_width=2,
            corner_radius=10,
            border_color=styles.ACCENT_COLOR,
            fg_color=styles.PRIMARY_COLOR
        )
        self.reg_username_entry.pack(side="left")

        # Password field
        password_frame = ctk.CTkFrame(register_container, fg_color="transparent")
        password_frame.pack(pady=10)
        
        ctk.CTkLabel(password_frame, text="🔒", font=(styles.FONT_FAMILY, 16)).pack(side="left", padx=(0, 5))
        self.reg_password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="New Password",
            show="*",
            width=250,
            height=40,
            border_width=2,
            corner_radius=10,
            border_color=styles.ACCENT_COLOR,
            fg_color=styles.PRIMARY_COLOR
        )
        self.reg_password_entry.pack(side="left")

        # Register button
        register_btn = ctk.CTkButton(
            register_container,
            text="REGISTER",
            command=self.client.register,
            fg_color=styles.HIGHLIGHT_COLOR,
            hover_color="#d63850",
            width=280,
            height=45,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 16, "bold")
        )
        register_btn.pack(pady=20)

        # Back link
        back_frame = ctk.CTkFrame(register_container, fg_color="transparent")
        back_frame.pack(pady=10)
        
        ctk.CTkLabel(
            back_frame,
            text="Already have an account?",
            text_color="#888888",
            font=(styles.FONT_FAMILY, 12)
        ).pack(side="left", padx=(0, 5))
        
        back_link = ctk.CTkButton(
            back_frame,
            text="SIGN IN",
            command=self.show_login_screen,
            fg_color="transparent",
            hover_color=styles.ACCENT_COLOR,
            width=80,
            height=25,
            font=(styles.FONT_FAMILY, 12, "bold"),
            text_color=styles.SUCCESS_COLOR
        )
        back_link.pack(side="left")

    def show_main_screen(self):
        self.clear_screen()
        self.root.after(150, self._build_main_screen) 

    def _build_main_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.PRIMARY_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(frame, fg_color=styles.SECONDARY_COLOR, corner_radius=10)
        header.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            header,
            text=f"👋 Welcome, {self.client.username}!",
            font=(styles.FONT_FAMILY, styles.FONT_SIZE_LARGE, "bold"),
            text_color=styles.SUCCESS_COLOR
        ).pack(pady=15)

        # Online users section
        content_frame = ctk.CTkFrame(frame, fg_color=styles.SECONDARY_COLOR, corner_radius=10)
        content_frame.pack(pady=10, padx=20, fill="both", expand=True)

        ctk.CTkLabel(
            content_frame,
            text="🌐 Online Players",
            font=(styles.FONT_FAMILY, 18, "bold"),
            text_color=styles.TEXT_COLOR
        ).pack(pady=10)

        # Listbox with custom styling
        list_frame = ctk.CTkFrame(content_frame, fg_color=styles.PRIMARY_COLOR, corner_radius=10)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.online_list = tk.Listbox(
            list_frame,
            width=30,
            height=8,
            font=(styles.FONT_FAMILY, styles.FONT_SIZE_SMALL),
            bg=styles.PRIMARY_COLOR,
            fg=styles.TEXT_COLOR,
            selectbackground=styles.HIGHLIGHT_COLOR,
            selectforeground=styles.TEXT_COLOR,
            borderwidth=0,
            highlightthickness=0
        )
        self.online_list.pack(pady=10, padx=10, fill="both", expand=True)

        # Buttons
        button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        button_frame.pack(pady=15)

        ctk.CTkButton(
            button_frame,
            text="🔄 Refresh",
            command=self.client.get_online_users,
            fg_color=styles.ACCENT_COLOR,
            hover_color="#0a2545",
            width=140,
            height=40,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 14, "bold")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="⚔️ Challenge",
            command=self.client.invite_selected,
            fg_color=styles.HIGHLIGHT_COLOR,
            hover_color="#d63850",
            width=140,
            height=40,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 14, "bold")
        ).pack(side="left", padx=5)

    def update_online_list(self, users):
        self.online_list.delete(0, tk.END)
        # Store clean usernames for later reference
        self.online_users_clean = users
        for user in users:
            self.online_list.insert(tk.END, f"  👤 {user}")

    def show_game_screen(self):
        self.clear_screen()
        self.root.geometry("450x650")  # Larger window for game
        self.root.after(150, self._build_game_screen)  

    def _build_game_screen(self):
        frame = ctk.CTkFrame(self.root, fg_color=styles.BG_COLOR, corner_radius=0)
        frame.pack(fill="both", expand=True)

        # Game header
        header = ctk.CTkFrame(frame, fg_color=styles.SECONDARY_COLOR, corner_radius=10)
        header.pack(pady=15, padx=15, fill="x")

        ctk.CTkLabel(
            header,
            text=f"⚔️ VS {self.client.opponent}",
            font=(styles.FONT_FAMILY, 20, "bold"),
            text_color=styles.HIGHLIGHT_COLOR
        ).pack(pady=5)

        symbol_text = f"You are: {'❌' if self.client.symbol == 'X' else '⭕'}"
        ctk.CTkLabel(
            header,
            text=symbol_text,
            font=(styles.FONT_FAMILY, 16),
            text_color=styles.SUCCESS_COLOR
        ).pack(pady=5)

        # Turn indicator
        self.turn_label = ctk.CTkLabel(
            frame,
            text="🎮 Your Turn!" if self.client.my_turn else "⏳ Opponent's Turn",
            font=(styles.FONT_FAMILY, 18, "bold"),
            text_color=styles.SUCCESS_COLOR if self.client.my_turn else "#888888"
        )
        self.turn_label.pack(pady=10)

        # Game board frame
        self.embed_frame = tk.Frame(frame, width=450, height=450, bg=styles.BOARD_COLOR)
        self.embed_frame.pack(pady=10)
        self.embed_frame.pack_propagate(False)
        
        self.embed_frame.update_idletasks()
        self.embed_frame.update()

        # Quit button
        ctk.CTkButton(
            frame,
            text="❌ Quit Game",
            command=self.client.quit_game,
            fg_color=styles.HIGHLIGHT_COLOR,
            hover_color="#d63850",
            width=200,
            height=40,
            corner_radius=10,
            font=(styles.FONT_FAMILY, 14, "bold")
        ).pack(pady=15)

        # Start Pygame
        self.root.after(200, lambda: self.client.start_pygame_game(self.embed_frame))