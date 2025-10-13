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

     
        self.embed_frame.update_idletasks()
        self.embed_frame.update()

       
        os.environ['SDL_WINDOWID'] = str(self.embed_frame.winfo_id())
        
        # Detecta o sistema operacional e define o driver correto
        if sys.platform.startswith('win'):
            os.environ['SDL_VIDEODRIVER'] = 'windows'
        elif sys.platform.startswith('linux'):
            os.environ['SDL_VIDEODRIVER'] = 'x11'
        elif sys.platform.startswith('darwin'):
            os.environ['SDL_VIDEODRIVER'] = 'cocoa'

       
        pygame.init()
        pygame.display.init()
        
        try:
            self.screen = pygame.display.set_mode((400, 400))
            self.screen.fill(styles.BOARD_COLOR)
            pygame.display.flip()
        except Exception as e:
            print(f"Erro ao inicializar Pygame: {e}")
            self.running = False
            return

      
        pygame.font.init()
        self.font = pygame.font.SysFont(styles.FONT_FAMILY, 100)

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
        self.screen.fill(styles.BOARD_COLOR)
        
        # Linhas do tabuleiro
        for i in range(1, 3):
            pygame.draw.line(self.screen, styles.LINE_COLOR, (0, i * 133), (400, i * 133), styles.LINE_WIDTH)
            pygame.draw.line(self.screen, styles.LINE_COLOR, (i * 133, 0), (i * 133, 400), styles.LINE_WIDTH)

        # Desenhar X/O
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 'X':
                    text = self.font.render('X', True, styles.X_COLOR)
                    self.screen.blit(text, (col * 133 + 40, row * 133 + 20))
                elif self.board[row][col] == 'O':
                    text = self.font.render('O', True, styles.O_COLOR)
                    self.screen.blit(text, (col * 133 + 40, row * 133 + 20))

    def update_board(self, board, turn):
        self.board = board
        self.client.my_turn = turn

    def stop(self):
        self.running = False
        try:
            pygame.quit()
        except:
            pass