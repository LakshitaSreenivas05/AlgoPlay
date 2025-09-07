from tkinter import *
import numpy as np
import random

size_of_board = 600
symbol_size = (size_of_board / 3 - size_of_board / 8) / 2
symbol_thickness = 50
symbol_X_color = '#EE4035'
symbol_O_color = '#0492CF'
Green_color = '#7BC043'


class Tic_Tac_Toe():
    def __init__(self):
        self.window = Tk()
        self.window.title('Tic-Tac-Toe')
        self.canvas = Canvas(self.window, width=size_of_board, height=size_of_board)
        self.canvas.pack()

        button_frame = Frame(self.window)
        button_frame.pack()
        self.undo_self_btn = Button(button_frame, text="Undo Your Action", command=self.undo_self, state=NORMAL)
        self.undo_self_btn.pack(side=LEFT, padx=10, pady=10)
        self.undo_opponent_btn = Button(button_frame, text="Undo Opponent's Action", command=self.undo_opponent, state=NORMAL)
        self.undo_opponent_btn.pack(side=LEFT, padx=10, pady=10)

        self.window.bind('<Button-1>', self.click)

        self.initialize_board()
        self.player_X_turns = True
        self.board_status = np.zeros(shape=(3, 3))

        self.player_X_starts = True
        self.reset_board = False
        self.gameover = False
        self.tie = False
        self.X_wins = False
        self.O_wins = False

        self.against_bot = True

        self.X_score = 0
        self.O_score = 0
        self.tie_score = 0

        self.move_history = []

        if not self.player_X_starts and self.against_bot:
            self.window.after(500, self.bot_move)

    def mainloop(self):
        self.window.mainloop()

    def initialize_board(self):
        for i in range(2):
            self.canvas.create_line((i + 1) * size_of_board / 3, 0, (i + 1) * size_of_board / 3, size_of_board)
        for i in range(2):
            self.canvas.create_line(0, (i + 1) * size_of_board / 3, size_of_board, (i + 1) * size_of_board / 3)

    def play_again(self):
        self.canvas.delete("all")
        self.initialize_board()
        self.player_X_starts = not self.player_X_starts
        self.player_X_turns = self.player_X_starts
        self.board_status = np.zeros(shape=(3, 3))
        self.reset_board = False
        self.gameover = False
        self.tie = False
        self.X_wins = False
        self.O_wins = False
        self.move_history = []
        self.undo_self_btn.config(state=NORMAL)
        self.undo_opponent_btn.config(state=NORMAL)

        if not self.player_X_starts and self.against_bot:
            self.window.after(500, self.bot_move)

    def draw_O(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_oval(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                 grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                 outline=symbol_O_color)

    def draw_X(self, logical_position):
        grid_position = self.convert_logical_to_grid_position(logical_position)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] - symbol_size,
                                 grid_position[0] + symbol_size, grid_position[1] + symbol_size, width=symbol_thickness,
                                 fill=symbol_X_color)
        self.canvas.create_line(grid_position[0] - symbol_size, grid_position[1] + symbol_size,
                                 grid_position[0] + symbol_size, grid_position[1] - symbol_size, width=symbol_thickness,
                                 fill=symbol_X_color)

    def display_gameover(self):
        if self.X_wins:
            self.X_score += 1
            text = 'Player(X) wins'
            color = symbol_X_color
        elif self.O_wins:
            self.O_score += 1
            text = 'Bot(O) wins'
            color = symbol_O_color
        else:
            self.tie_score += 1
            text = 'Its a tie'
            color = 'gray'

        self.canvas.delete("all")
        self.canvas.create_text(size_of_board / 2, size_of_board / 3, font="cmr 60 bold", fill=color, text=text)

        
        self.reset_board = True

        play_again_text = 'Click to play again \n'
        self.canvas.create_text(size_of_board / 2, 15 * size_of_board / 16, font="cmr 20 bold", fill="gray",
                                 text=play_again_text)
        self.undo_self_btn.config(state=DISABLED)
        self.undo_opponent_btn.config(state=DISABLED)

    def draw_winning_line(self, win_type, number):
        line_width = 15
        if win_type == 'row':
            y = (number * size_of_board / 3) + size_of_board / 6
            x1, y1, x2, y2 = size_of_board / 6, y, size_of_board - size_of_board / 6, y
        elif win_type == 'col':
            x = (number * size_of_board / 3) + size_of_board / 6
            x1, y1, x2, y2 = x, size_of_board / 6, x, size_of_board - size_of_board / 6
        elif win_type == 'diag':
            if number == 1:
                x1, y1 = size_of_board / 6, size_of_board / 6
                x2, y2 = size_of_board - size_of_board / 6, size_of_board - size_of_board / 6
            else:
                x1, y1 = size_of_board - size_of_board / 6, size_of_board / 6
                x2, y2 = size_of_board / 6, size_of_board - size_of_board / 6
        
        self.canvas.create_line(x1, y1, x2, y2, width=line_width, fill=Green_color)

    def convert_logical_to_grid_position(self, logical_position):
        logical_position = np.array(logical_position, dtype=int)
        return (size_of_board / 3) * logical_position + size_of_board / 6

    def convert_grid_to_logical_position(self, grid_position):
        grid_position = np.array(grid_position)
        return np.array(grid_position // (size_of_board / 3), dtype=int)

    def is_grid_occupied(self, logical_position):
        return self.board_status[logical_position[0]][logical_position[1]] != 0

    def is_winner(self, player):
        player_value = -1 if player == 'X' else 1
        board_T = self.board_status.transpose()
        for i in range(3):
            if np.all(self.board_status[i, :] == player_value): return True
            if np.all(board_T[i, :] == player_value): return True
        if np.all(np.diag(self.board_status) == player_value): return True
        if np.all(np.diag(np.fliplr(self.board_status)) == player_value): return True
        return False

    def get_winning_line(self, player):
            """Checks for a win and returns the CORRECT type for visual drawing."""
            player_value = -1 if player == 'X' else 1
            
            # A win in a row of the data array is a VISUAL VERTICAL line.
            for i in range(3):
                if np.all(self.board_status[i, :] == player_value):
                    # Return it as a 'col' for the drawing function.
                    return ('col', i)
                    
            # A win in a column of the data array is a VISUAL HORIZONTAL line.
            for i in range(3):
                if np.all(self.board_status[:, i] == player_value):
                    # Return it as a 'row' for the drawing function.
                    return ('row', i)
                    
            # Diagonals are visually and logically the same.
            if np.all(np.diag(self.board_status) == player_value):
                return ('diag', 1)
            if np.all(np.diag(np.fliplr(self.board_status)) == player_value):
                return ('diag', 2)
                
            return None
    def draw_winning_line(self, win_type, number):
            """Draws a line based on the corrected win_type."""
            line_width = 15
            
            # Draws a HORIZONTAL line for a 'row' win
            if win_type == 'row':
                y = (number * size_of_board / 3) + size_of_board / 6
                x1, y1, x2, y2 = size_of_board / 6, y, size_of_board - size_of_board / 6, y
                
            # Draws a VERTICAL line for a 'col' win
            elif win_type == 'col':
                x = (number * size_of_board / 3) + size_of_board / 6
                x1, y1, x2, y2 = x, size_of_board / 6, x, size_of_board - size_of_board / 6
                
            elif win_type == 'diag':
                if number == 1:  # Main diagonal
                    x1, y1 = size_of_board / 6, size_of_board / 6
                    x2, y2 = size_of_board - size_of_board / 6, size_of_board - size_of_board / 6
                else:  # Anti-diagonal
                    x1, y1 = size_of_board - size_of_board / 6, size_of_board / 6
                    x2, y2 = size_of_board / 6, size_of_board - size_of_board / 6
            
            self.canvas.create_line(x1, y1, x2, y2, width=line_width, fill=Green_color)

    def is_tie(self):
        return np.all(self.board_status != 0)

    def is_gameover(self):
        self.X_wins = self.is_winner('X')
        if not self.X_wins:
            self.O_wins = self.is_winner('O')
        if not self.O_wins:
            self.tie = self.is_tie()
        return self.X_wins or self.O_wins or self.tie

    def get_empty_grids(self):
        empty_grids = []
        for r in range(3):
            for c in range(3):
                if self.board_status[r][c] == 0:
                    empty_grids.append((r, c))
        return empty_grids

    def bot_move(self):
        if self.gameover: return
        empty_grids = self.get_empty_grids()
        if not empty_grids: return

        for r, c in empty_grids:
            temp_board = np.copy(self.board_status); temp_board[r][c] = 1
            if self.check_win_for_board(temp_board, 1):
                self.place_move((r, c), bot_move=True); return

        for r, c in empty_grids:
            temp_board = np.copy(self.board_status); temp_board[r][c] = -1
            if self.check_win_for_board(temp_board, -1):
                self.place_move((r, c), bot_move=True); return
        
        if self.board_status[1][1] == 0:
            self.place_move((1, 1), bot_move=True); return

        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        available_corners = [c for c in corners if self.board_status[c[0]][c[1]] == 0]
        if available_corners:
            self.place_move(random.choice(available_corners), bot_move=True); return

        self.place_move(random.choice(empty_grids), bot_move=True)

    def check_win_for_board(self, board, player_value):
        for i in range(3):
            if np.all(board[i, :] == player_value) or np.all(board[:, i] == player_value): return True
        if np.all(np.diag(board) == player_value) or np.all(np.diag(np.fliplr(board)) == player_value): return True
        return False

    def place_move(self, logical_position, bot_move=False):
        player = 'O' if bot_move else 'X'
        value = 1 if bot_move else -1
        
        if not self.is_grid_occupied(logical_position):
            if bot_move:
                self.draw_O(logical_position)
            else:
                self.draw_X(logical_position)
            
            self.board_status[logical_position[0]][logical_position[1]] = value
            self.move_history.append((player, tuple(logical_position)))
            
            # --- THIS IS THE CORRECTED LINE ---
            self.player_X_turns = bot_move

            if self.is_gameover():
                self.gameover = True
                if self.X_wins or self.O_wins:
                    winner = 'X' if self.X_wins else 'O'
                    win_info = self.get_winning_line(winner)
                    if win_info:
                        win_type, number = win_info
                        self.draw_winning_line(win_type, number)
                    self.window.after(1000, self.display_gameover)
                else:
                    self.display_gameover()

    def click(self, event):
        if self.reset_board:
            self.play_again(); return
        if not self.player_X_turns or self.gameover:
            return

        grid_position = [event.x, event.y]
        logical_position = self.convert_grid_to_logical_position(grid_position)

        if not self.is_grid_occupied(logical_position):
            self.place_move(logical_position, bot_move=False)
            if not self.gameover:
                self.window.after(500, self.bot_move)
    
    def update_game_state(self):
        if self.is_gameover():
            self.gameover = True
            self.display_gameover()

    def undo_self(self):
        if not self.move_history or self.gameover or self.reset_board: return
        for i in range(len(self.move_history)-1, -1, -1):
            player, pos = self.move_history[i]
            if player == 'X':
                self.move_history = self.move_history[:i]
                self.board_status = np.zeros((3, 3))
                for p, position in self.move_history:
                    self.board_status[position[0]][position[1]] = -1 if p == 'X' else 1
                self.player_X_turns = True
                self.redraw_board()
                self.update_game_state()
                break

    def undo_opponent(self):
        if not self.move_history or self.gameover or self.reset_board: return
        for i in range(len(self.move_history)-1, -1, -1):
            player, pos = self.move_history[i]
            if player == 'O':
                self.move_history = self.move_history[:i]
                self.board_status = np.zeros((3, 3))
                for p, position in self.move_history:
                    self.board_status[position[0]][position[1]] = -1 if p == 'X' else 1
                self.player_X_turns = False
                self.redraw_board()
                self.update_game_state()
                if not self.gameover:
                    self.window.after(500, self.bot_move)
                break
            
    def redraw_board(self):
        self.canvas.delete("all")
        self.initialize_board()
        for player, pos in self.move_history:
            if player == 'X': self.draw_X(pos)
            else: self.draw_O(pos)

game_instance = Tic_Tac_Toe()
game_instance.mainloop()