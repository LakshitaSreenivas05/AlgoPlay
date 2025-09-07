import tkinter as tk
from tkinter import messagebox
import sys
import random

# --- New UI Style Constants ---
STYLE = {
    "font_main": ("Segoe UI", 12),
    "font_bold": ("Segoe UI Bold", 12),
    "font_header": ("Segoe UI Semibold", 16),
    "bg_main": "#bdbdbd",      # Light gray background
    "bg_cell": "#c0c0c0",      # Classic cell color
    "bg_cell_rev": "#bdbdbd",  # Revealed cell color
    "border_color": "#7b7b7b", # Dark gray border
    "header_bg": "#c0c0c0",
    "num_colors": {
        "1": "#0000ff", "2": "#008000", "3": "#ff0000",
        "4": "#000080", "5": "#800000", "6": "#008080",
        "7": "#000000", "8": "#808080"
    }
}

# --- Game Logic (Unchanged) ---
def generateRandomBoard(rows, col):
    choices = ["E", "E", "E", "E", "E", "M"]
    mineCount = 0
    details = []
    board = [[] for _ in range(rows)]
    for i in range(rows):
        for _ in range(col):
            ranchar = random.choice(choices)
            if ranchar == "M":
                mineCount += 1
            board[i].append(ranchar)

    details.append(board)
    details.append(mineCount)
    return details

def numberMineBoard(board):
    vis = [["0" for _ in range(len(board[0]))] for _ in range(len(board))]
    numberOfRows = len(board)
    numberOfColumns = len(board[0])
    for i in range(0, numberOfRows):
        for j in range(0, numberOfColumns):
            if board[i][j] == "M":
                vis[i][j] = "M"
                for drow in range(-1, 2):
                    for dcol in range(-1, 2):
                        nrow = i + drow
                        ncol = j + dcol
                        if nrow >= 0 and nrow < numberOfRows and ncol >= 0 and ncol < numberOfColumns:
                            if board[nrow][ncol] == "M":
                                continue
                            tmp = int(vis[nrow][ncol]) + 1
                            vis[nrow][ncol] = str(tmp)
    return vis

def dfs(row, col, board, actualBoard, vis, buttons):
    vis[row][col] = 1
    board[row][col] = "B"
    buttons.add(len(board[0]) * row + col)
    for drow in range(-1, 2):
        for dcol in range(-1, 2):
            nrow = row + drow
            ncol = col + dcol
            if nrow >= 0 and nrow < len(board) and ncol >= 0 and ncol < len(board[0]) and not vis[nrow][ncol]:
                if actualBoard[nrow][ncol] == "0":
                    dfs(nrow, ncol, board, actualBoard, vis, buttons)
                else:
                    board[nrow][ncol] = actualBoard[nrow][ncol]
                    buttons.add(len(board[0]) * nrow + ncol)

def checkSpaces(mineCount, flagged_count, board):
    empty_cells = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 'E':
                empty_cells += 1
    return empty_cells == mineCount

# --- UI and Interaction Logic (Redesigned) ---
class MinesweeperGame:
    def __init__(self, root, board_dims):
        self.root = root
        self.rows, self.cols = board_dims
        self.first_click = True
        self.game_over = False
        self.timer_running = False
        self.elapsed_time = 0
        
        details = generateRandomBoard(self.rows, self.cols)
        self.board = makeGameboard(details[0])
        self.actualBoard = numberMineBoard(details[0])
        self.mineCount = details[1]
        self.flag_count = 0
        
        self.coordinates = makeCoordinates(self.board)
        self.vis = makeVisited(self.board)
        self.buttonsClear = set()
        self.flagged_buttons = set()
        
        self.root.title("Minesweeper")
        self.root.configure(bg=STYLE["bg_main"])
        
        self.create_widgets()
        self.update_mine_counter()

    def create_widgets(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=STYLE["header_bg"], bd=2, relief="solid")
        header_frame.pack(pady=10, padx=10, fill="x")

        self.mine_counter_var = tk.StringVar()
        mine_label = tk.Label(header_frame, textvariable=self.mine_counter_var, font=STYLE["font_header"], bg=STYLE["header_bg"], fg="red")
        mine_label.pack(side="left", padx=10)

        self.reset_button_var = tk.StringVar(value="Reset 😊")
        reset_button = tk.Button(header_frame, textvariable=self.reset_button_var, font=("Segoe UI Emoji", 16), command=self.reset_game, relief="raised", bd=2)
        reset_button.pack(side="left", expand=True, fill="x")

        self.timer_var = tk.StringVar(value="000")
        timer_label = tk.Label(header_frame, textvariable=self.timer_var, font=STYLE["font_header"], bg=STYLE["header_bg"], fg="red")
        timer_label.pack(side="right", padx=10)

        # Grid Frame
        grid_frame = tk.Frame(self.root, bg=STYLE["border_color"], bd=2, relief="solid")
        grid_frame.pack(pady=10, padx=10)

        self.buttons = []
        for i in range(self.rows):
            for j in range(self.cols):
                val = i * self.cols + j
                button = tk.Button(grid_frame, text="", width=2, height=1, font=STYLE["font_bold"], 
                                   bg=STYLE["bg_cell"], relief="raised", borderwidth=2)
                button.bind("<Button-1>", lambda e, v=val: self.handle_left_click(v))
                button.bind("<Button-3>", lambda e, v=val: self.handle_right_click(v))
                button.grid(row=i, column=j)
                self.buttons.append(button)
        
        # Footer Frame
        footer_frame = tk.Frame(self.root, bg=STYLE["bg_main"])
        footer_frame.pack(pady=5)
        main_menu_button = tk.Button(footer_frame, text="Main Menu", command=self.back_to_main_menu, font=STYLE["font_main"])
        main_menu_button.pack()

    def handle_left_click(self, value):
        if self.game_over or value in self.flagged_buttons:
            return
            
        if self.first_click:
            self.start_timer()
            self.first_click = False

        row, col = self.coordinates[value]
        
        if self.actualBoard[row][col] == "M":
            self.reveal_all_mines(clicked_mine_val=value)
            self.stop_timer()
            self.game_over = True
            self.reset_button_var.set("Reset 😵")
            self.root.after(100, lambda: self.show_end_message("You Lost!"))
        else:
            self.buttonsClear.clear()
            if self.actualBoard[row][col] != "0":
                self.board[row][col] = self.actualBoard[row][col]
            else:
                dfs(row, col, self.board, self.actualBoard, self.vis, self.buttonsClear)
            
            self.reveal_cleared_buttons()
            
            if checkSpaces(self.mineCount, self.flag_count, self.board):
                self.win_game()

    def handle_right_click(self, value):
        if self.game_over:
            return
            
        button = self.buttons[value]
        if button['state'] == tk.DISABLED:
            return

        if value not in self.flagged_buttons:
            button.config(text="🚩", fg="red")
            self.flagged_buttons.add(value)
            self.flag_count += 1
        else:
            button.config(text="", fg="black")
            self.flagged_buttons.remove(value)
            self.flag_count -= 1
        
        self.update_mine_counter()

    def reveal_cleared_buttons(self):
        for button_index in self.buttonsClear:
            self.reveal_button(button_index)
        # Handle the initial click if it wasn't a '0'
        if not self.buttonsClear:
            row, col = self.coordinates[self.last_clicked]
            self.reveal_button(self.last_clicked)

    def reveal_button(self, button_index):
        row, col = self.coordinates[button_index]
        label_text = self.actualBoard[row][col]
        button = self.buttons[button_index]
        
        if label_text != "0":
            button.config(text=label_text, fg=STYLE["num_colors"].get(label_text, "black"))
        
        button.config(bg=STYLE["bg_cell_rev"], relief="sunken", state=tk.DISABLED, disabledforeground=STYLE["num_colors"].get(label_text, "black"))

    def reveal_all_mines(self, clicked_mine_val):
        for i in range(self.rows * self.cols):
            row, col = self.coordinates[i]
            if self.actualBoard[row][col] == "M":
                if i in self.flagged_buttons:
                    self.buttons[i].config(text="💣", bg="green", relief="sunken", state=tk.DISABLED)
                else:
                    bg_color = "red" if i == clicked_mine_val else STYLE["bg_cell_rev"]
                    self.buttons[i].config(text="💣", bg=bg_color, relief="sunken", state=tk.DISABLED)
            elif i in self.flagged_buttons: # Incorrect flag
                 self.buttons[i].config(text="❌", fg="red", bg=STYLE["bg_cell_rev"], relief="sunken", state=tk.DISABLED)

    def win_game(self):
        self.game_over = True
        self.stop_timer()
        self.reset_button_var.set("YOU WIN 😎")
        for i in range(self.rows * self.cols):
            if i not in self.flagged_buttons:
                self.reveal_button(i)
        self.root.after(100, lambda: self.show_end_message("You Won!"))

    def show_end_message(self, message):
        response = messagebox.askyesno("Game Over", f"{message}\nDo you want to play again?")
        if response:
            self.reset_game()
        else:
            self.root.destroy()
            sys.exit()

    def update_mine_counter(self):
        remaining = self.mineCount - self.flag_count
        self.mine_counter_var.set(f"{remaining:03d}")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def stop_timer(self):
        self.timer_running = False

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time += 1
            self.timer_var.set(f"{self.elapsed_time:03d}")
            self.root.after(1000, self.update_timer)

    def reset_game(self):
        self.root.destroy()
        new_root = tk.Tk()
        MinesweeperGame(new_root, (self.rows, self.cols))
        new_root.mainloop()

    def back_to_main_menu(self):
        self.root.destroy()
        backToMainMenu()
        
    def handle_left_click(self, value):
        if self.game_over or value in self.flagged_buttons:
            return
            
        if self.first_click:
            self.start_timer()
            self.first_click = False

        self.last_clicked = value # Store the last clicked button
        row, col = self.coordinates[value]
        
        result = self.player_clicks(row, col) # Use helper
        
        if result == "Lost":
            self.reveal_all_mines(clicked_mine_val=value)
            self.stop_timer()
            self.game_over = True
            self.reset_button_var.set(" YOU LOST 😵")
            self.root.after(100, lambda: self.show_end_message("You Lost!"))
        else:
            self.reveal_cleared_buttons()
            if result == "Win":
                self.win_game()

    def player_clicks(self, crow, ccol):
        if self.actualBoard[crow][ccol] == "M":
            return "Lost"
            
        self.buttonsClear.clear()
        if self.actualBoard[crow][ccol] != "0":
            self.board[crow][ccol] = self.actualBoard[crow][ccol]
        else:
            dfs(crow, ccol, self.board, self.actualBoard, self.vis, self.buttonsClear)
            
        if checkSpaces(self.mineCount, self.flag_count, self.board):
            return "Win"
        return "Cont"

def makeCoordinates(board):
    coordinates = {}
    for i in range(len(board)):
        for j in range(len(board[0])):
            coordinates[i*len(board[0]) + j] = (i, j)
    return coordinates

def makeVisited(board):
    return [[0 for _ in range(len(board[0]))] for _ in range(len(board))]

def makeGameboard(board):
    return [['E' for _ in range(len(board[0]))] for _ in range(len(board))]

def backToMainMenu():
    def start_game(dims):
        menu_root.destroy()
        game_root = tk.Tk()
        MinesweeperGame(game_root, dims)
        game_root.mainloop()

    menu_root = tk.Tk()
    menu_root.title("Minesweeper")
    menu_root.configure(bg=STYLE["bg_main"])
    
    main_frame = tk.Frame(menu_root, bg=STYLE["bg_main"], padx=40, pady=30)
    main_frame.pack()

    title_label = tk.Label(main_frame, text="Minesweeper", font=(STYLE["font_bold"][0], 24), bg=STYLE["bg_main"])
    title_label.pack(pady=(0, 20))

    difficulty_frame = tk.Frame(main_frame, bg=STYLE["bg_main"])
    difficulty_frame.pack(pady=10)

    easy_button = tk.Button(difficulty_frame, text="Easy (6x15)", width=15, font=STYLE["font_bold"], command=lambda: start_game((6, 15)))
    easy_button.pack(pady=5)
    medium_button = tk.Button(difficulty_frame, text="Medium (10x25)", width=15, font=STYLE["font_bold"], command=lambda: start_game((10, 25)))
    medium_button.pack(pady=5)
    hard_button = tk.Button(difficulty_frame, text="Hard (14x35)", width=15, font=STYLE["font_bold"], command=lambda: start_game((14, 35)))
    hard_button.pack(pady=5)

    instructions = (
        "Instructions:\n"
        "Left-click a cell to reveal it.\n"
        "Right-click a cell to flag it as a mine.\n"
        "Clear all non-mine cells to win!"
    )
    instruction_label = tk.Label(main_frame, text=instructions, font=STYLE["font_main"], bg=STYLE["bg_main"], justify="left")
    instruction_label.pack(pady=(20, 0))
    
    menu_root.protocol("WM_DELETE_WINDOW", sys.exit)
    menu_root.mainloop()

if __name__ == "__main__":
    backToMainMenu()