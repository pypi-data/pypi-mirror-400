import pygame
from pygame.locals import *
import os
from importlib import resources 
from .button import Button
import random

asset_path = resources.files("playbaghchal") / "assets"

class TigerGame:
    def __init__(self):
        pygame.init()
        self.screen_height = 700
        self.screen_width = 700
        self.line_width = 4
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption('Tiger Goat Game')
        self.win_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.win_surface.fill((0, 0, 0, 130))
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)
        self.placeholder_color = (200, 200, 200)
        self.font = pygame.font.SysFont(None, 40)
        self.turn = "Goats"
        self.game_over = False
        self.winner = ""
        self.game_start = False
        self.tigers_cornered = 0
        self.goats_captured = 0
        self.goats_outside = 20
        self.tiger_img = pygame.image.load(os.path.join(asset_path, "tiger.png")).convert_alpha()
        self.goat_img = pygame.image.load(os.path.join(asset_path,"goat.png")).convert_alpha()
        self.quit_img = pygame.image.load(os.path.join(asset_path,"Quit.png")).convert_alpha()
        self.start_img = pygame.image.load(os.path.join(asset_path,"Start.png")).convert_alpha()
        self.tiger_win_img = pygame.image.load(os.path.join(asset_path,"Tiger_win.png")).convert_alpha()
        self.goat_win_img = pygame.image.load(os.path.join(asset_path,"Goat_win.png")).convert_alpha()
        self.play_again_img = pygame.image.load(os.path.join(asset_path,"Play_Again.png")).convert_alpha()
        self.forest_img = pygame.image.load(os.path.join(asset_path,"forest.png")).convert_alpha()
        self.wood_img = pygame.image.load(os.path.join(asset_path,"wood.png")).convert_alpha()
        self.menu_img = pygame.image.load(os.path.join(asset_path, "Start.png")).convert_alpha()
        self.tiger_img = pygame.transform.scale(self.tiger_img, (50, 50))
        self.goat_img = pygame.transform.scale(self.goat_img, (60, 60))
        self.bg_image = pygame.transform.scale(self.forest_img, (self.screen_width, self.screen_height))
        self.bg_image_game = pygame.transform.scale(self.wood_img, (self.screen_width, self.screen_height))
        self.start_button = Button(200, 200, self.start_img, 0.5)
        self.quit_button = Button(200, 450, self.quit_img, 0.5)
        self.tiger_win_button = Button(30, 100, self.tiger_win_img, 0.5)
        self.goat_win_button = Button(50, 100, self.goat_win_img, 0.5)
        self.play_again_button = Button(100, 200, self.play_again_img, 0.5)
        self.menu_button = Button(175, 320, self.menu_img, 0.5)
        self.human_img = pygame.image.load(os.path.join(asset_path, "HumanvsHuman.png")).convert_alpha()
        self.ai_img = pygame.image.load(os.path.join(asset_path, "HumanvsAI.png")).convert_alpha()
        self.easy_img = pygame.image.load(os.path.join(asset_path, "easy.png")).convert_alpha()
        self.medium_img = pygame.image.load(os.path.join(asset_path, "medium.png")).convert_alpha()
        self.advanced_img = pygame.image.load(os.path.join(asset_path, "advance.png")).convert_alpha()
        self.human_button = Button(10, 200, self.human_img, 0.5)
        self.ai_button = Button(80, 300, self.ai_img, 0.5)
        self.easy_button = Button(250, 150, self.easy_img, 0.5)
        self.medium_button = Button(200, 250, self.medium_img, 0.5)
        self.advanced_button = Button(160, 350, self.advanced_img, 0.5)
        self.tiger_pos = [(0, 0), (0, 4), (4, 0), (4, 4)]
        self.goats = []
        self.board = [['' for _ in range(5)] for _ in range(5)]
        for pos in self.tiger_pos:
            self.board[pos[0]][pos[1]] = 'T'
        self.placeholders = []
        self.moves = {
            (0, 0): [(0, 1), (1, 0), (1, 1)], 
            (0, 1): [(0, 0), (1, 1), (0, 2)], 
            (0, 2): [(0, 1), (1, 1), (1, 2), (1, 3), (0, 3)],
            (0, 3): [(0, 2), (1, 3), (0, 4)], 
            (0, 4): [(0, 3), (1, 3), (1, 4)], 
            (1, 0): [(0, 0), (1, 1), (2, 0)],
            (1, 1): [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)],
            (1, 2): [(0, 2), (1, 1), (1, 3), (2, 2)],
            (1, 3): [(0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (2, 2), (2, 3), (2, 4)],
            (1, 4): [(0, 4), (1, 3), (2, 4)],
            (2, 0): [(1, 0), (1, 1), (2, 1), (3, 0), (3, 1)],
            (2, 1): [(2, 0), (1, 1), (2, 2), (3, 1)],
            (2, 2): [(1, 1), (1, 2), (1, 3), (2, 1), (3, 1), (3, 2), (2, 3), (3, 3)],
            (2, 3): [(2, 2), (1, 3), (2, 4), (3, 3)],
            (2, 4): [(1, 3), (2, 3), (1, 4), (3, 3), (3, 4)],
            (3, 0): [(2, 0), (3, 1), (4, 0)],
            (3, 1): [(2, 0), (3, 0), (2, 1), (2, 2), (3, 2), (4, 0), (4, 1), (4, 2)],
            (3, 2): [(2, 2), (3, 1), (4, 2), (3, 3)],
            (3, 3): [(2, 2), (3, 2), (2, 3), (2, 4), (3, 4), (4, 2), (4, 3), (4, 4)],
            (3, 4): [(3, 3), (2, 4), (4, 4)],
            (4, 0): [(3, 0), (3, 1), (4, 1)],
            (4, 1): [(4, 0), (3, 1), (4, 2)],
            (4, 2): [(4, 1), (3, 1), (3, 2), (3, 3), (4, 3)],
            (4, 3): [(4, 2), (4, 4), (3, 3)],
            (4, 4): [(4, 3), (3, 3), (3, 4)]
        }
        self.jumps = {
            (0, 0): [(0, 2), (2, 0), (2, 2)],
            (0, 1): [(0, 3), (2, 1)],
            (0, 2): [(0, 0), (0, 4), (2, 0), (2, 2), (2, 4)],
            (0, 3): [(0, 1), (2, 3)],
            (0, 4): [(0, 2), (2, 2), (2, 4)],
            (1, 0): [(3, 0), (1, 2)],
            (1, 1): [(3, 1), (1, 3),(3, 3)],
            (1, 2): [(1, 0), (1, 4),(3, 2)],
            (1, 3): [(1, 1), (3, 1), (3, 3)],
            (1, 4): [(1, 2), (3, 4)],
            (2, 0): [(0, 0), (0, 2), (2, 2), (4, 0), (4, 2)],
            (2, 1): [(0, 1), (4, 1), (2, 3)],
            (2, 2): [(0, 0), (0, 2), (0, 4), (2, 0), (2, 4), (4, 0), (4, 2), (4, 4)],
            (2, 3): [(0, 3), (2, 1), (4, 3)],
            (2, 4): [(0, 2), (0, 4), (4, 2), (2, 2), (4, 4)],
            (3, 0): [(1, 0), (3, 2)],
            (3, 1): [(1, 1), (1, 3), (3, 3)],
            (3, 2): [(1, 2), (3, 0), (3, 4)],
            (3, 3): [(1, 1), (3, 1), (1, 3)],
            (3, 4): [(3, 2), (1, 4)],
            (4, 0): [(2, 0), (2, 2), (4, 2)],
            (4, 1): [(2, 1), (4, 3)],
            (4, 2): [(2, 0), (2, 2), (2, 4), (4, 0), (4, 4)],
            (4, 3): [(4, 1), (2, 3)],
            (4, 4): [(2, 2), (2, 4), (4, 2)]
        }
        self.click_pos = []
        self.game_mode = "Human"
        self.ai_level = "Easy"
        self.as_goat_img = pygame.image.load(os.path.join(asset_path, "asGoat.png")).convert_alpha()
        self.as_tiger_img = pygame.image.load(os.path.join(asset_path, "asTiger.png")).convert_alpha()
        self.as_goat_button = Button(200, 250, self.as_goat_img, 0.5)
        self.as_tiger_button = Button(190, 350, self.as_tiger_img, 0.5)
        self.player_side = "Goats"  # Default

    def draw_board(self):
        color = (50, 50, 50)
        spacing = 120
        self.screen.blit(self.bg_image_game, (0, 0)) # bg = 'burlywood4'  # self.screen.fill(bg)
        for x in range(1, 6):
            # rows and columns
            pygame.draw.line(self.screen, color, (spacing, spacing * x),
                            (self.screen_width-100, spacing * x), self.line_width)
            pygame.draw.line(self.screen, color, (spacing * x, spacing),
                            (spacing * x, self.screen_height-100), self.line_width)
        # diagonal lines
        pygame.draw.line(self.screen, color, (spacing, spacing),
                        (self.screen_height-100, spacing * 5), self.line_width)
        pygame.draw.line(self.screen, color, (spacing, spacing*5),
                        (self.screen_width-100, spacing), self.line_width)

        # secondary diagonal lines
        pygame.draw.line(self.screen, color, (spacing, spacing * 3),
                        (spacing * 3, spacing), self.line_width)
        pygame.draw.line(self.screen, color, (spacing * 3, self.screen_height - 100),
                        (self.screen_width - 100, spacing * 3), self.line_width)
        pygame.draw.line(self.screen, color, (spacing * 3, spacing),
                        (self.screen_height - 100, spacing * 3), self.line_width)
        pygame.draw.line(self.screen, color, (spacing, spacing * 3),
                        (spacing * 3, self.screen_height - 100), self.line_width)

        # Draw the placeholders and store their positions
        self.placeholders.clear()
        for row in range(5):
            for col in range(5):
                center_x = spacing * col + spacing
                center_y = spacing * row + spacing
                pygame.draw.circle(self.screen, self.placeholder_color,
                                (center_x, center_y), 15)
                self.placeholders.append((center_x, center_y, row, col))

        # Draw the tigers and goats on the self.board
        for row in range(5):
            for col in range(5):
                if self.board[row][col] == 'T':
                    self.screen.blit(self.tiger_img, (spacing * col + spacing -
                                23, spacing * row + spacing - 24))
                elif self.board[row][col] == 'G':
                    self.screen.blit(self.goat_img, (spacing * col + spacing -
                                30, spacing * row + spacing - 28))

        # Draw the turn text
        turn_text = self.font.render(f'{self.turn} Turn!', True, self.black)
        self.screen.blit(turn_text, (300, 50))


    def draw_stats(self, tigers_cornered, goats_captured, goats_outside):
        font = pygame.font.SysFont(None, 25)
        # Render the text
        tigers_text = font.render(
            f'TIGERS CORNERED: {tigers_cornered}/4', True, self.black)
        goats_text = font.render(
            f'GOATS CAPTURED: {goats_captured}/20', True, self.black)
        outside_text = font.render(
            f'GOATS OUTSIDE: {goats_outside}/20', True, self.black)

        # Display the text on the self.screen
        self.screen.blit(tigers_text, (250, self.screen_height - 80))
        self.screen.blit(goats_text, (250, self.screen_height - 50))
        self.screen.blit(outside_text, (250, self.screen_height - 20))

    def is_valid_move(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if not (0 <= x2 < 5 and 0 <= y2 < 5):
            return False  # Out of bounds
        if self.board[x2][y2] != '':
            return False  # Not an empty spot
        if (x2, y2) in self.moves[(x1, y1)]:
            return True  # Adjacent move
        return False

    def is_valid_jump(self, start, end):
        x1, y1 = start
        x2, y2 = end
        if not (0 <= x2 < 5 and 0 <= y2 < 5):
            return False  # Out of bounds
        if self.board[x2][y2] != '':
            return False  # Not an empty spot
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        if self.board[mid_x][mid_y] != 'G':
            return False  # No goat to jump over
        if (x2, y2) in self.jumps[(x1, y1)]:
            return True  # Valid jump
        return False

    def move_tiger(self, start, end):
        ismove = self.is_valid_move(start, end)
        isjump = self.is_valid_jump(start, end)
        if ismove or isjump:
            x1, y1 = start
            x2, y2 = end
            self.board[x1][y1] = ''
            self.board[x2][y2] = 'T'
            self.tiger_pos.remove((x1, y1))
            self.tiger_pos.append((x2, y2))
            if not ismove:
                if isjump:
                    mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
                    self.board[mid_x][mid_y] = ''  # Remove jumped goat
                    self.goats.remove((mid_x, mid_y))
                    self.goats_captured += 1
                    if self.goats_captured == 6:
                        self.game_over = True
                        self.winner = 'Tigers'
            return True
        return False

    def move_goat(self, start, end):
        if self.is_valid_move(start, end):
            x1, y1 = start
            x2, y2 = end
            self.board[x1][y1] = ''
            self.board[x2][y2] = 'G'
            self.goats.append((x2, y2))
            self.goats.remove((x1, y1))
            return True
        return False

    def place_goat(self, position):
        x, y = position
        if self.board[x][y] == '':
            self.board[x][y] = 'G'
            self.goats.append((x, y))
            self.goats_outside -= 1
            return True
        return False

    def is_trap_tiger(self):
        self.tigers_cornered = 0
        for pos in self.tiger_pos:
            for move in self.moves[pos] + self.jumps[pos]:
                if self.board[move[0]][move[1]] == '':
                    break
            else: # if all moves are blocked(if break is not executed)
                self.tigers_cornered += 1
        if self.tigers_cornered == 4:
            self.game_over = True
            self.winner = 'Goats'
            return True
        return False 

    def ai_move(self):
        # 1. AI Logic for TIGERS
        if self.turn == "Tigers":
            if self.ai_level == "Easy":
                self.ai_move_easy()
            elif self.ai_level == "Medium":
                self.ai_move_medium()
            elif self.ai_level == "Advanced":
                self.ai_move_hard()
        
        # 2. AI Logic for GOATS
        elif self.turn == "Goats":
            self.ai_move_goat()
    def ai_move_goat(self):
        # Easy/Medium: Random moves (Goats need to place first, then move)
        if self.ai_level == "Easy" or self.ai_level == "Medium":
            moves = self.get_goat_moves(self.board, self.goats, self.goats_outside)
            if moves:
                type, start, end = random.choice(moves)
                if type == 'place':
                    self.place_goat(end)
                else:
                    self.move_goat(start, end)
                self.turn = "Tigers"

        # Advanced: Minimax (Minimizing score)
        elif self.ai_level == "Advanced":
            depth = 3 # Look ahead 3 moves
            best_score = float('inf') # We want the LOWEST score for Goats
            best_move = None
            
            possible_moves = self.get_goat_moves(self.board, self.goats, self.goats_outside)
            
            # Optimization: Shuffle and limit to prevent lag during placement phase
            if len(possible_moves) > 20: 
                random.shuffle(possible_moves)
                possible_moves = possible_moves[:15]

            alpha = float('-inf')
            beta = float('inf')

            for type, start, end in possible_moves:
                # Simulate Move
                new_board = [row[:] for row in self.board]
                new_goats = self.goats[:]
                new_goats_outside = self.goats_outside
                
                if type == 'place':
                    new_board[end[0]][end[1]] = 'G'
                    new_goats.append(end)
                    new_goats_outside -= 1
                else: # Move
                    new_board[start[0]][start[1]] = ''
                    new_board[end[0]][end[1]] = 'G'
                    new_goats.remove(start)
                    new_goats.append(end)

                # Call Minimax (Next turn is Tigers, so maximizing=True)
                score = self.minimax_hard(new_board, self.tiger_pos, new_goats, new_goats_outside, self.goats_captured, depth - 1, alpha, beta, True)
                
                if score < best_score:
                    best_score = score
                    best_move = (type, start, end)
                
                beta = min(beta, best_score)
                # Alpha-Beta Pruning
                if beta <= alpha:
                    break

            # Execute Best Move
            if best_move:
                type, start, end = best_move
                if type == 'place':
                    self.place_goat(end)
                else:
                    self.move_goat(start, end)
                self.turn = "Tigers"

    def ai_move_easy(self):
        # Random valid move for tiger
        moves = []
        for pos in self.tiger_pos:
            for move in self.moves[pos]:
                if self.board[move[0]][move[1]] == '':
                    moves.append((pos, move))
            for jump in self.jumps[pos]:
                if self.is_valid_jump(pos, jump):
                    moves.append((pos, jump))
        if moves:
            start, end = random.choice(moves)
            self.move_tiger(start, end)
            self.turn = "Goats"

    def ai_move_medium(self):
        # Prefer jumps (captures), else random move
        jumps = []
        moves = []
        for pos in self.tiger_pos:
            for jump in self.jumps[pos]:
                if self.is_valid_jump(pos, jump):
                    jumps.append((pos, jump))
            for move in self.moves[pos]:
                if self.board[move[0]][move[1]] == '':
                    moves.append((pos, move))
        if jumps:
            start, end = random.choice(jumps)
            self.move_tiger(start, end)
        elif moves:
            start, end = random.choice(moves)
            self.move_tiger(start, end)
        self.turn = "Goats"

    def get_tiger_moves(self, board, tiger_pos):
        """Generates all valid tiger moves (walks and jumps) for a specific board state."""
        moves = []
        for start in tiger_pos:
            # Check adjacent moves
            for end in self.moves[start]:
                if board[end[0]][end[1]] == '':
                    moves.append(('move', start, end))
            
            # Check jumps
            for end in self.jumps[start]:
                mid_x, mid_y = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
                if board[end[0]][end[1]] == '' and board[mid_x][mid_y] == 'G':
                    moves.append(('jump', start, end))
        return moves

    def get_goat_moves(self, board, goats, goats_outside):
        """Generates all valid goat moves or placements."""
        moves = []
        if goats_outside > 0:
            # Phase 1: Placement - Try all empty spots
            for r in range(5):
                for c in range(5):
                    if board[r][c] == '':
                        moves.append(('place', None, (r, c)))
        else:
            # Phase 2: Movement
            for start in goats:
                for end in self.moves[start]:
                    if board[end[0]][end[1]] == '':
                        moves.append(('move', start, end))
        return moves
    def evaluate_state(self, board, tiger_pos, goats_captured):
        """
        Score the board from the Tiger's perspective.
        High Score = Good for Tiger. Low Score = Good for Goat.
        """
        if goats_captured >= 5: # Win condition for Tiger
            return 100000
        
        score = 0
        
        # 1. Reward capturing goats heavily
        score += goats_captured * 500
        
        # 2. Reward Mobility (Crucial to avoid being trapped)
        mobility = 0
        for pos in tiger_pos:
            # Count walking moves
            for move in self.moves[pos]:
                if board[move[0]][move[1]] == '':
                    mobility += 1
            # Count jump moves
            for jump in self.jumps[pos]:
                mid_x, mid_y = (pos[0] + jump[0]) // 2, (pos[1] + jump[1]) // 2
                if board[jump[0]][jump[1]] == '' and board[mid_x][mid_y] == 'G':
                    mobility += 2 # Jumps are valuable
        
        score += mobility * 10
        
        # If mobility is 0, Tigers lose (Trapped)
        if mobility == 0:
            return -100000

        return score

    def minimax_hard(self, board, tiger_pos, goats, goats_outside, goats_captured, depth, alpha, beta, is_maximizing):
        # Base case: Leaf node or game over
        if depth == 0 or goats_captured >= 5:
            return self.evaluate_state(board, tiger_pos, goats_captured)

        if is_maximizing: # Tiger's Turn
            max_eval = float('-inf')
            possible_moves = self.get_tiger_moves(board, tiger_pos)
            
            # Sort moves to improve pruning (check jumps first)
            possible_moves.sort(key=lambda x: 1 if x[0] == 'jump' else 0, reverse=True)
            
            if not possible_moves: # No moves available (Trapped)
                return -100000

            for type, start, end in possible_moves:
                # Create copies for simulation
                new_board = [row[:] for row in board]
                new_tiger_pos = tiger_pos[:]
                new_goats = goats[:] # Only needed if we track goat positions strictly
                new_captured = goats_captured
                
                # Apply Move
                new_board[start[0]][start[1]] = ''
                new_board[end[0]][end[1]] = 'T'
                new_tiger_pos.remove(start)
                new_tiger_pos.append(end)
                
                if type == 'jump':
                    mid_x, mid_y = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
                    new_board[mid_x][mid_y] = ''
                    if (mid_x, mid_y) in new_goats:
                        new_goats.remove((mid_x, mid_y))
                    new_captured += 1
                
                eval = self.minimax_hard(new_board, new_tiger_pos, new_goats, goats_outside, new_captured, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else: # Goat's Turn
            min_eval = float('inf')
            possible_moves = self.get_goat_moves(board, goats, goats_outside)
            
            # Optimization: If placing, limiting checks to save time if needed
            if len(possible_moves) > 20: 
                import random
                random.shuffle(possible_moves)
                possible_moves = possible_moves[:12] # Limit branching factor for performance
            
            for type, start, end in possible_moves:
                new_board = [row[:] for row in board]
                new_goats = goats[:]
                new_goats_outside = goats_outside
                
                if type == 'place':
                    new_board[end[0]][end[1]] = 'G'
                    new_goats.append(end)
                    new_goats_outside -= 1
                else: # Move
                    new_board[start[0]][start[1]] = ''
                    new_board[end[0]][end[1]] = 'G'
                    new_goats.remove(start)
                    new_goats.append(end)
                
                eval = self.minimax_hard(new_board, tiger_pos, new_goats, new_goats_outside, goats_captured, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
        
    def ai_move_hard(self):
        # High depth for "Hard" (Depth 4 checks: Tiger -> Goat -> Tiger -> Goat)
        # Note: If it's too slow, reduce depth to 3.
        depth = 4 
        best_score = float('-inf')
        best_move = None
        
        possible_moves = self.get_tiger_moves(self.board, self.tiger_pos)
        
        # Prioritize jumps in the root call too
        possible_moves.sort(key=lambda x: 1 if x[0] == 'jump' else 0, reverse=True)

        alpha = float('-inf')
        beta = float('inf')

        for type, start, end in possible_moves:
            # --- Simulation Setup ---
            new_board = [row[:] for row in self.board]
            new_tiger_pos = self.tiger_pos[:]
            new_goats = self.goats[:]
            new_captured = self.goats_captured
            
            # --- Apply Move ---
            new_board[start[0]][start[1]] = ''
            new_board[end[0]][end[1]] = 'T'
            new_tiger_pos.remove(start)
            new_tiger_pos.append(end)
            
            if type == 'jump':
                mid_x, mid_y = (start[0] + end[0]) // 2, (start[1] + end[1]) // 2
                new_board[mid_x][mid_y] = ''
                if (mid_x, mid_y) in new_goats:
                    new_goats.remove((mid_x, mid_y))
                new_captured += 1
            
            # --- Call Minimax ---
            # Next turn is Goats (maximizing=False)
            score = self.minimax_hard(new_board, new_tiger_pos, new_goats, self.goats_outside, new_captured, depth - 1, alpha, beta, False)
            
            if score > best_score:
                best_score = score
                best_move = (start, end)
            
            # Root alpha update
            alpha = max(alpha, best_score)

        # Execute the best move found
        if best_move:
            self.move_tiger(best_move[0], best_move[1])
            self.turn = "Goats"
    def reset_game(self):
        """Resets the board and game state variables."""
        self.game_over = False
        self.winner = ""
        self.tigers_cornered = 0
        self.goats_captured = 0
        self.goats_outside = 20
        self.turn = "Goats"
        self.tiger_pos = [(0, 0), (0, 4), (4, 0), (4, 4)]
        self.goats = []
        self.board = [['' for _ in range(5)] for _ in range(5)]
        for pos in self.tiger_pos:
            self.board[pos[0]][pos[1]] = 'T'
        self.click_pos.clear()

    def run(self):
            run = True
            while run:
                # --- MAIN MENU ---
                if not self.game_start:
                    self.screen.blit(self.bg_image, (0, 0))
                    # Draw Menu Buttons
                    self.human_button.draw(self.screen)
                    self.ai_button.draw(self.screen)
                    self.quit_button.draw(self.screen)
                    
                    # Draw Title
                    font = pygame.font.SysFont(None, 100)
                    title_text = font.render("Bagh-Chal", True, self.black)
                    self.screen.blit(title_text, (170, 10))
                    mode_text = self.font.render("Choose Game Mode:", True, self.white)
                    self.screen.blit(mode_text, (200, 200))
                    
                    pygame.display.update()
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                        
                        if self.quit_button.draw(self.screen):
                            run = False

                        # Human vs Human
                        if self.human_button.draw(self.screen):
                            self.game_mode = "Human"
                            self.reset_game() # Ensure fresh start
                            self.game_start = True
                        
                        # Human vs AI Setup
                        if self.ai_button.draw(self.screen):
                            # 1. Select Difficulty
                            selecting = True
                            while selecting:
                                self.screen.blit(self.bg_image, (0, 0))
                                diff_text = self.font.render("Select AI Difficulty:", True, self.white)
                                self.screen.blit(diff_text, (200, 150))
                                self.easy_button.draw(self.screen)
                                self.medium_button.draw(self.screen)
                                self.advanced_button.draw(self.screen)
                                pygame.display.update()
                                
                                for event2 in pygame.event.get():
                                    if event2.type == pygame.QUIT:
                                        run = False
                                        selecting = False
                                    
                                    if self.easy_button.draw(self.screen):
                                        self.ai_level = "Easy"
                                        selecting = False
                                    if self.medium_button.draw(self.screen):
                                        self.ai_level = "Medium"
                                        selecting = False
                                    if self.advanced_button.draw(self.screen):
                                        self.ai_level = "Advanced"
                                        selecting = False

                            # 2. Select Side
                            if run: # Only if user didn't quit
                                side_selecting = True
                                while side_selecting:
                                    self.screen.blit(self.bg_image, (0, 0))
                                    side_text = self.font.render("Choose Your Side:", True, self.white)
                                    self.screen.blit(side_text, (200, 250))
                                    self.as_goat_button.draw(self.screen)
                                    self.as_tiger_button.draw(self.screen)
                                    pygame.display.update()
                                    
                                    for event3 in pygame.event.get():
                                        if event3.type == pygame.QUIT:
                                            run = False
                                            side_selecting = False
                                        
                                        if self.as_goat_button.draw(self.screen):
                                            self.player_side = "Goats"
                                            self.game_mode = "AI"
                                            self.reset_game()
                                            self.game_start = True
                                            side_selecting = False
                                        
                                        if self.as_tiger_button.draw(self.screen):
                                            self.player_side = "Tigers"
                                            self.game_mode = "AI"
                                            self.reset_game()
                                            self.game_start = True
                                            side_selecting = False
                    continue

                # --- GAME LOOP ---
                self.draw_board()
                self.draw_stats(self.tigers_cornered, self.goats_captured, self.goats_outside)
                
                # --- GAME OVER SCREEN ---
                if self.game_over:
                    # Draw Winner
                    if self.winner == 'Tigers':
                        self.tiger_win_button.draw(self.win_surface)
                    elif self.winner == 'Goats':
                        self.goat_win_button.draw(self.win_surface)
                    
                    self.screen.blit(self.win_surface, (0, 0))
                    
                    # Draw Buttons
                    self.play_again_button.draw(self.win_surface)
                    self.menu_button.draw(self.win_surface) # Draw Menu Button
                    self.quit_button.draw(self.win_surface)
                    
                    # Handle Game Over Events
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False
                        
                        if self.quit_button.draw(self.screen):
                            run = False
                            
                        if self.play_again_button.draw(self.screen):
                            self.reset_game()
                            self.game_start = True # Restart match
                        
                        if self.menu_button.draw(self.screen):
                            self.reset_game()
                            self.game_start = False # Go back to Main Menu
                    
                    pygame.display.update()
                    continue

                # --- GAMEPLAY EVENTS ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
                    
                    # Only handle human clicks if game is not over
                    if not self.game_over:
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_x, mouse_y = event.pos
                            for center_x, center_y, row, col in self.placeholders:
                                if (mouse_x - center_x) ** 2 + (mouse_y - center_y) ** 2 <= 15 ** 2:
                                    
                                    # GOAT TURN
                                    if self.turn == 'Goats':
                                        if self.board[row][col] == '' and self.goats_outside > 0:
                                            if self.place_goat((row, col)):
                                                self.turn = 'Tigers'
                                        elif self.goats_outside == 0:
                                            if len(self.click_pos) == 0 and self.board[row][col] == 'G':
                                                self.click_pos.append((row, col))
                                            elif len(self.click_pos) == 1 and self.board[row][col] == '':
                                                self.click_pos.append((row, col))
                                                if self.move_goat(*self.click_pos):
                                                    self.click_pos.clear()
                                                    self.turn = 'Tigers'
                                                else:
                                                    self.click_pos.pop()
                                            elif len(self.click_pos) == 1 and self.board[row][col] == 'G':
                                                self.click_pos.clear()
                                                self.click_pos.append((row, col))
                                            else:
                                                self.click_pos.clear()
                                        self.is_trap_tiger()
                                    
                                    # TIGER TURN
                                    elif self.turn == 'Tigers':
                                        if len(self.click_pos) == 0 and self.board[row][col] == 'T':
                                            self.click_pos.append((row, col))
                                        elif len(self.click_pos) == 1 and self.board[row][col] == '':
                                            self.click_pos.append((row, col))
                                            if self.move_tiger(*self.click_pos):
                                                self.click_pos.clear()
                                                self.turn = 'Goats'
                                            else:
                                                self.click_pos.pop()
                                        elif len(self.click_pos) == 1 and self.board[row][col] == 'T':
                                            self.click_pos.clear()
                                            self.click_pos.append((row, col))
                                        else:
                                            self.click_pos.clear()

                # --- AI MOVE LOGIC ---
                if self.game_mode == "AI" and not self.game_over:
                    # If it is NOT the human player's turn, let AI move
                    if self.turn != self.player_side:
                        pygame.time.wait(500) # Small delay for natural feel
                        self.ai_move()
                        self.is_trap_tiger()

                pygame.display.update()
            
            pygame.quit()

def start_game():
    game = TigerGame()
    game.run()
