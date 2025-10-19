import pygame
import threading
import os
import sys
import styles
import math

class PygameGame:
    def __init__(self, client, embed_frame):
        self.client = client
        self.running = True
        self.board = [[' ' for _ in range(3)] for _ in range(3)]
        self.embed_frame = embed_frame
        self.animation_progress = {}  # Track animation for each cell
        self.hover_cell = None  # Track which cell is being hovere

        # Force Tkinter frame update
        self.embed_frame.update_idletasks()
        self.embed_frame.update()

        # Configure SDL for embedding in Tkinter
        os.environ['SDL_WINDOWID'] = str(self.embed_frame.winfo_id())
        
        # Detect OS and set correct driver
        if sys.platform.startswith('win'):
            os.environ['SDL_VIDEODRIVER'] = 'windows'
        elif sys.platform.startswith('linux'):
            os.environ['SDL_VIDEODRIVER'] = 'x11'
        elif sys.platform.startswith('darwin'):
            os.environ['SDL_VIDEODRIVER'] = 'cocoa'

        # Initialize Pygame
        pygame.init()
        pygame.display.init()
        
        try:
            self.screen = pygame.display.set_mode((450, 450))
            self.screen.fill(styles.BOARD_COLOR)
            pygame.display.flip()
        except Exception as e:
            print(f"Error initializing Pygame: {e}")
            self.running = False
            return

        # Fonts
        pygame.font.init()
        self.font = pygame.font.SysFont(styles.FONT_FAMILY, 100, bold=True)

        # Start game loop thread
        self.game_thread = threading.Thread(target=self.game_loop, daemon=True)
        self.game_thread.start()

    def game_loop(self):
        clock = pygame.time.Clock()
        while self.running:
            try:
                mouse_pos = pygame.mouse.get_pos()
                self.hover_cell = self.get_cell_from_pos(mouse_pos)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN and self.client.my_turn:
                        x, y = event.pos
                        col = x // 150
                        row = y // 150
                        if 0 <= row < 3 and 0 <= col < 3 and self.board[row][col] == ' ':
                            # Start animation for this cell
                            self.animation_progress[(row, col)] = 0
                            self.client.make_move(row, col)

                self.draw_board()
                self.update_animations()
                pygame.display.flip()
                clock.tick(60)  
            except Exception as e:
                print(f"Error in game loop: {e}")
                break

    def get_cell_from_pos(self, pos):
        """Get the cell coordinates from mouse position"""
        x, y = pos
        col = x // 150
        row = y // 150
        if 0 <= row < 3 and 0 <= col < 3:
            return (row, col)
        return None

    def draw_board(self):
        # Create gradient background
        for y in range(450):
            ratio = y / 450
            r = int(26 + (31 - 26) * ratio)
            g = int(26 + (33 - 26) * ratio)
            b = int(46 + (62 - 46) * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (450, y))

        # Draw hover effect
        if self.hover_cell and self.client.my_turn:
            row, col = self.hover_cell
            if self.board[row][col] == ' ':
                hover_rect = pygame.Rect(col * 150 + 5, row * 150 + 5, 140, 140)
                pygame.draw.rect(self.screen, (15, 52, 96, 100), hover_rect, border_radius=10)

        # Draw grid lines with glow effect
        self.draw_grid_with_glow()

        # Draw X and O symbols with animations
        for row in range(3):
            for col in range(3):
                if self.board[row][col] != ' ':
                    progress = self.animation_progress.get((row, col), 1.0)
                    if self.board[row][col] == 'X':
                        self.draw_x(row, col, progress)
                    else:
                        self.draw_o(row, col, progress)

    def draw_grid_with_glow(self):
        """Draw grid lines with a glowing effect"""
        glow_color = tuple(min(255, c + 30) for c in self.hex_to_rgb(styles.LINE_COLOR))
        
        # Draw glow 
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(self.screen, glow_color, (i * 150, 0), (i * 150, 450), styles.GRID_LINE_WIDTH + 4)
            # Horizontal lines
            pygame.draw.line(self.screen, glow_color, (0, i * 150), (450, i * 150), styles.GRID_LINE_WIDTH + 4)
        
        # Draw main lines
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(self.screen, self.hex_to_rgb(styles.LINE_COLOR), (i * 150, 0), (i * 150, 450), styles.GRID_LINE_WIDTH)
            # Horizontal lines
            pygame.draw.line(self.screen, self.hex_to_rgb(styles.LINE_COLOR), (0, i * 150), (450, i * 150), styles.GRID_LINE_WIDTH)

    def draw_x(self, row, col, progress):
        """Draw X with cross animation"""
        center_x = col * 150 + 75
        center_y = row * 150 + 75
        size = 50
        
        # Calculate animation
        line_progress = min(1.0, progress * 2)  # First line
        line2_progress = max(0, min(1.0, (progress - 0.5) * 2))  # Second line
        
        # Draw first diagonal with glow
        if line_progress > 0:
            end_x1 = center_x - size + (2 * size * line_progress)
            end_y1 = center_y - size + (2 * size * line_progress)
            
            # Glow effect
            glow_color = tuple(min(255, c + 50) for c in self.hex_to_rgb(styles.X_COLOR))
            pygame.draw.line(self.screen, glow_color, 
                           (center_x - size, center_y - size),
                           (end_x1, end_y1), 12)
            
            # Main line
            pygame.draw.line(self.screen, self.hex_to_rgb(styles.X_COLOR),
                           (center_x - size, center_y - size),
                           (end_x1, end_y1), 8)
        
        # Draw second diagonal with glow
        if line2_progress > 0:
            end_x2 = center_x + size - (2 * size * line2_progress)
            end_y2 = center_y - size + (2 * size * line2_progress)
            
            # Glow effect
            glow_color = tuple(min(255, c + 50) for c in self.hex_to_rgb(styles.X_COLOR))
            pygame.draw.line(self.screen, glow_color,
                           (center_x + size, center_y - size),
                           (end_x2, end_y2), 12)
            
            # Main line
            pygame.draw.line(self.screen, self.hex_to_rgb(styles.X_COLOR),
                           (center_x + size, center_y - size),
                           (end_x2, end_y2), 8)

    def draw_o(self, row, col, progress):
        """Draw O with circular animation"""
        center_x = col * 150 + 75
        center_y = row * 150 + 75
        radius = 50
        
        # Calculate arc angle based on progress
        end_angle = 360 * progress
        
        # Draw circle progressively with glow
        if progress > 0:
            # Glow effect
            glow_color = tuple(min(255, c + 50) for c in self.hex_to_rgb(styles.O_COLOR))
            
            # Draw multiple arcs for full circle effect
            segments = int(end_angle / 5) 
            for i in range(segments):
                start = math.radians(i * 5)
                end = math.radians((i + 1) * 5)
                
                # Calculate points for glow
                x1_glow = center_x + (radius + 6) * math.cos(start)
                y1_glow = center_y + (radius + 6) * math.sin(start)
                x2_glow = center_x + (radius + 6) * math.cos(end)
                y2_glow = center_y + (radius + 6) * math.sin(end)
                
                # Draw glow
                pygame.draw.line(self.screen, glow_color, 
                               (x1_glow, y1_glow), (x2_glow, y2_glow), 12)
            
            # Draw main circle
            for i in range(segments):
                start = math.radians(i * 5)
                end = math.radians((i + 1) * 5)
                
                x1 = center_x + radius * math.cos(start)
                y1 = center_y + radius * math.sin(start)
                x2 = center_x + radius * math.cos(end)
                y2 = center_y + radius * math.sin(end)
                
                pygame.draw.line(self.screen, self.hex_to_rgb(styles.O_COLOR),
                               (x1, y1), (x2, y2), 8)

    def update_animations(self):
        """Update animation progress for all cells"""
        to_remove = []
        for cell, progress in self.animation_progress.items():
            if progress < 1.0:
                self.animation_progress[cell] = min(1.0, progress + 0.05) 
            else:
                to_remove.append(cell)
        
        # Clean up completed animations
        for cell in to_remove:
            if self.animation_progress[cell] >= 1.0:
                del self.animation_progress[cell]

    def hex_to_rgb(self, hex_color):
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def update_board(self, board, turn):
        """Update board state and start animations for new moves"""
        # Check for new moves and start their animations
        for row in range(3):
            for col in range(3):
                if board[row][col] != ' ' and self.board[row][col] == ' ':
                    self.animation_progress[(row, col)] = 0
        
        self.board = board
        self.client.my_turn = turn

    def stop(self):
        self.running = False
        try:
            pygame.quit()
        except:
            pass