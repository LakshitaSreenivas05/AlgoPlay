import tkinter as tk
from tkinter import messagebox
import numpy as np
import random

ROWS = 6
COLS = 7
PLAYER_COLOR = "#e74c3c"
BOT_COLOR = "#f4d03f"
EMPTY_COLOR = "#eaf2f8"
HIGHLIGHT_COLOR = "#76d7c4"
GRID_BORDER_COLOR = "#34495e"
HEADER_BG = "#5dade2"
HEADER_ACTIVE_BG = "#2e86c1"
BG_COLOR = "#f0f6ff"

class Connect4(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect 4 with Undo & Keyboard Control")
        self.configure(bg=BG_COLOR)
        self.resizable(False, False)
        self.board = np.zeros((ROWS, COLS), dtype=int)  # 0=empty, 1=player, 2=bot
        self.move_history = []  # Each move: (row, col, player)
        self.buttons = []
        self.labels = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = 1  # 1=player, 2=bot
        self.gameover = False
        self.selected_col = 0  # For keyboard control

        self.status_var = tk.StringVar(value="Your turn! Use ←/→ or A/D to select column, Enter/Space to drop.")
        self.create_widgets()
        self.draw_board()
        self.highlight_selected_col()
        self.bind_all('<Key>', self.on_key_press)

    def create_widgets(self):
        title = tk.Label(self, text="Connect 4", font=("Arial Rounded MT Bold", 30, "bold"),
                        fg="#21618c", bg=BG_COLOR, pady=10)
        title.pack()

        status_label = tk.Label(self, textvariable=self.status_var, font=("Arial", 13), bg=BG_COLOR, fg="#424949")
        status_label.pack()

        frame = tk.Frame(self, bg=BG_COLOR)
        frame.pack(pady=8)
        for c in range(COLS):
            btn = tk.Button(
                frame, text=str(c+1), width=4, height=2,
                font=("Arial Rounded MT Bold", 13, "bold"),
                bg=HEADER_BG, activebackground=HEADER_ACTIVE_BG,
                fg="#fff",
                command=lambda cc=c: self.player_move(cc)
            )
            btn.grid(row=0, column=c, padx=2, pady=3)
            self.buttons.append(btn)
        board_frame = tk.Frame(self, bg=GRID_BORDER_COLOR, bd=2, relief="solid")
        board_frame.pack(padx=8, pady=6)
        for r in range(ROWS):
            for c in range(COLS):
                lbl = tk.Label(board_frame, width=4, height=2, relief="ridge",
                               font=("Arial Rounded MT Bold", 22),
                               bg=EMPTY_COLOR, fg="#273746", text="",
                               bd=2, borderwidth=2)
                lbl.grid(row=r, column=c, padx=1, pady=1)
                self.labels[r][c] = lbl
        btn_frame = tk.Frame(self, bg=BG_COLOR)
        btn_frame.pack(pady=10)
        style = {"font": ("Arial", 12), "bg": "#aed6f1", "fg": "#1a5276", "activebackground": "#5499c7"}
        tk.Button(btn_frame, text="Undo Own Move", command=self.undo_self, **style).grid(row=0, column=0, padx=8)
        tk.Button(btn_frame, text="Undo Opponent Move", command=self.undo_opponent, **style).grid(row=0, column=1, padx=8)
        tk.Button(btn_frame, text="Reset", command=self.reset_board, **style).grid(row=0, column=2, padx=8)

    def draw_board(self):
        for r in range(ROWS):
            for c in range(COLS):
                val = self.board[r][c]
                if val == 0:
                    self.labels[r][c].config(bg=EMPTY_COLOR, text="")
                elif val == 1:
                    self.labels[r][c].config(bg=PLAYER_COLOR, fg="#fff", text="●")
                else:
                    self.labels[r][c].config(bg=BOT_COLOR, fg="#fff", text="●")
        self.highlight_selected_col()
        self.update_status()

    def highlight_selected_col(self):
        for i, btn in enumerate(self.buttons):
            btn.config(relief="raised", bg=HEADER_BG)
        self.buttons[self.selected_col].config(relief="sunken", bg=HIGHLIGHT_COLOR)
        # Highlight the entire column (top cell border)
        for r in range(ROWS):
            if self.board[r][self.selected_col] == 0:
                self.labels[r][self.selected_col].config(bg=HIGHLIGHT_COLOR)
            elif self.board[r][self.selected_col] == 1:
                self.labels[r][self.selected_col].config(bg=PLAYER_COLOR)
            elif self.board[r][self.selected_col] == 2:
                self.labels[r][self.selected_col].config(bg=BOT_COLOR)

    def player_move(self, col):
        if self.gameover or self.current_player != 1:
            return
        row = self.get_row_for_col(col)
        if row is None:
            self.status_var.set("Column is full! Try another column.")
            return
        self.board[row][col] = 1
        self.move_history.append((row, col, 1))
        self.current_player = 2
        self.draw_board()
        if self.check_win(1):
            self.gameover = True
            self.status_var.set("You win! 🎉")
            messagebox.showinfo("Game Over", "You win!")
            return
        if self.check_draw():
            self.gameover = True
            self.status_var.set("It's a draw!")
            messagebox.showinfo("Draw", "It's a draw!")
            return
        self.status_var.set("Bot's turn...")
        self.after(700, self.bot_move)

    def bot_move(self):
        if self.gameover or self.current_player != 2:
            return
        available = [c for c in range(COLS) if self.get_row_for_col(c) is not None]
        if not available:
            return
        col = self.pick_bot_column(available)
        row = self.get_row_for_col(col)
        self.board[row][col] = 2
        self.move_history.append((row, col, 2))
        self.current_player = 1
        self.draw_board()
        if self.check_win(2):
            self.gameover = True
            self.status_var.set("Bot wins! 😭")
            messagebox.showinfo("Game Over", "Bot wins!")
            return
        if self.check_draw():
            self.gameover = True
            self.status_var.set("It's a draw!")
            messagebox.showinfo("Draw", "It's a draw!")
            return
        self.status_var.set("Your turn! Use ←/→ or A/D to select column, Enter/Space to drop.")

    def pick_bot_column(self, available):
        # Simple: block player's win if possible, else random
        for c in available:
            r = self.get_row_for_col(c)
            self.board[r][c] = 2
            if self.check_win(2):
                self.board[r][c] = 0
                return c
            self.board[r][c] = 0
        for c in available:
            r = self.get_row_for_col(c)
            self.board[r][c] = 1
            if self.check_win(1):
                self.board[r][c] = 0
                return c
            self.board[r][c] = 0
        return random.choice(available)

    def get_row_for_col(self, col):
        for r in reversed(range(ROWS)):
            if self.board[r][col] == 0:
                return r
        return None

    def check_win(self, player):
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS-3):
                if all(self.board[r][c+i]==player for i in range(4)):
                    return True
        # Vertical
        for c in range(COLS):
            for r in range(ROWS-3):
                if all(self.board[r+i][c]==player for i in range(4)):
                    return True
        # Diagonal /
        for r in range(3, ROWS):
            for c in range(COLS-3):
                if all(self.board[r-i][c+i]==player for i in range(4)):
                    return True
        # Diagonal \
        for r in range(ROWS-3):
            for c in range(COLS-3):
                if all(self.board[r+i][c+i]==player for i in range(4)):
                    return True
        return False

    def check_draw(self):
        return all(self.board[0][c] != 0 for c in range(COLS))

    def undo_self(self):
        if self.gameover or not self.move_history:
            self.status_var.set("Nothing to undo!")
            return
        idx = None
        for i in range(len(self.move_history)-1, -1, -1):
            if self.move_history[i][2] == 1:
                idx = i
                break
        if idx is None:
            self.status_var.set("No move of yours to undo.")
            return
        self.move_history = self.move_history[:idx]
        self.rebuild_from_history()
        self.current_player = 1
        self.gameover = False
        self.status_var.set("Your turn! Use ←/→ or A/D to select column, Enter/Space to drop.")

    def undo_opponent(self):
        if self.gameover or not self.move_history:
            self.status_var.set("Nothing to undo!")
            return
        idx = None
        for i in range(len(self.move_history)-1, -1, -1):
            if self.move_history[i][2] == 2:
                idx = i
                break
        if idx is None:
            self.status_var.set("No bot's move to undo.")
            return
        self.move_history = self.move_history[:idx]
        self.rebuild_from_history()
        self.current_player = 2
        self.gameover = False
        self.status_var.set("Bot's turn (after your undo)...")
        self.after(700, self.bot_move)

    def rebuild_from_history(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        for (r, c, p) in self.move_history:
            self.board[r][c] = p
        self.draw_board()

    def reset_board(self):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.move_history = []
        self.current_player = 1
        self.selected_col = 0
        self.gameover = False
        self.draw_board()
        self.status_var.set("Your turn! Use ←/→ or A/D to select column, Enter/Space to drop.")

    def update_status(self):
        if self.gameover:
            return
        if self.current_player == 1:
            self.status_var.set("Your turn! Use ←/→ or A/D to select column, Enter/Space to drop.")
        else:
            self.status_var.set("Bot's turn...")

    def on_key_press(self, event):
        if self.gameover or self.current_player != 1:
            return
        key = event.keysym.lower()
        if key in ("left", "a"):
            self.selected_col = (self.selected_col - 1) % COLS
            self.highlight_selected_col()
        elif key in ("right", "d"):
            self.selected_col = (self.selected_col + 1) % COLS
            self.highlight_selected_col()
        elif key in ("return", "space"):
            self.player_move(self.selected_col)

if __name__ == "__main__":
    Connect4().mainloop()