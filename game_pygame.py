import pygame
import threading
import os
import sys
import styles  

class PygameGame:
    def __init__(self, client, embed_frame):
        self.client = client
        self.running = True
        self.board = [[' ' for _ in range(3)] for _ in range(3)]  
        self.embed_frame = embed_frame

        # Força a atualização do frame Tkinter
        self.embed_frame.update_idletasks()
        self.embed_frame.update()

        # Configura o SDL para embutir no Tkinter
        os.environ['SDL_WINDOWID'] = str(self.embed_frame.winfo_id())
        
        # Detecta o sistema operacional e define o driver correto
        if sys.platform.startswith('win'):
            os.environ['SDL_VIDEODRIVER'] = 'windows'
        elif sys.platform.startswith('linux'):
            os.environ['SDL_VIDEODRIVER'] = 'x11'
        elif sys.platform.startswith('darwin'):
            os.environ['SDL_VIDEODRIVER'] = 'cocoa'

        # Inicializa Pygame
        pygame.init()
        pygame.display.init()
        
        try:
            self.screen = pygame.display.set_mode((400, 400))
            self.screen.fill(styles.BOARD_COLOR)  # Fundo inicial (será sobrescrito pelo gradiente)
            pygame.display.flip()
        except Exception as e:
            print(f"Erro ao inicializar Pygame: {e}")
            self.running = False
            return

        # Fontes e estilo
        pygame.font.init()
        self.font = pygame.font.SysFont(styles.FONT_FAMILY, 120)  # Aumenta o tamanho para destacar
        self.font_outline = pygame.font.SysFont(styles.FONT_FAMILY, 120)  # Para contorno

        # Thread para loop Pygame
        self.game_thread = threading.Thread(target=self.game_loop, daemon=True)
        self.game_thread.start()

    def game_loop(self):
        clock = pygame.time.Clock()
        while self.running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.client.my_turn:
                        x, y = event.pos
                        col = x // (400 // 3)
                        row = y // (400 // 3)
                        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' ':
                            self.client.make_move(row, col)

                self.draw_board()
                pygame.display.flip()
                clock.tick(30)  # 30 FPS
            except Exception as e:
                print(f"Erro no game loop: {e}")
                break

    def draw_board(self):
        # Gradiente de fundo (azul escuro para claro)
        for y in range(400):
            r = int(10 + (y / 400) * (65 - 10))  # Ajusta o vermelho do gradiente
            g = int(36 + (y / 400) * (81 - 36))  # Ajusta o verde
            b = int(114 + (y / 400) * (181 - 114))  # Ajusta o azul (de #0A2472 para #3F51B5)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (400, y))

        # Borda externa do tabuleiro
        pygame.draw.rect(self.screen, styles.LINE_COLOR, (10, 10, 380, 380), 10)  # Borda grossa

        # Linhas do tabuleiro com espessura maior e arredondamento
        for i in range(1, 3):
            pygame.draw.line(self.screen, styles.LINE_COLOR, (0, i * 133 + 10), (400, i * 133 + 10), 15)
            pygame.draw.line(self.screen, styles.LINE_COLOR, (i * 133 + 10, 0), (i * 133 + 10, 400), 15)

        # Desenhar X/O com contorno
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 'X':
                    text = self.font.render('X', True, styles.X_COLOR)
                    outline = self.font_outline.render('X', True, (0, 0, 0))  # Contorno preto
                    self.screen.blit(outline, (col * 133 + 30, row * 133 + 10))  # Desloca para alinhar
                    self.screen.blit(text, (col * 133 + 30, row * 133 + 10))
                elif self.board[row][col] == 'O':
                    text = self.font.render('O', True, styles.O_COLOR)
                    outline = self.font_outline.render('O', True, (0, 0, 0))  # Contorno preto
                    self.screen.blit(outline, (col * 133 + 30, row * 133 + 10))
                    self.screen.blit(text, (col * 133 + 30, row * 133 + 10))

    def update_board(self, board, turn):
        self.board = board
        self.client.my_turn = turn

    def stop(self):
        self.running = False
        try:
            pygame.quit()
        except:
            pass