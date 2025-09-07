import tkinter as tk
from tkinter import messagebox
import copy
import random

def pattern(r,c): return (3*(r%3)+r//3+c)%9
def shuffle(s): return random.sample(s,len(s)) 

base = 3
side = base*base

def generate_board():
    rBase = range(base) 
    rows  = [g*base + r for g in shuffle(rBase) for r in shuffle(rBase)] 
    cols  = [g*base + c for g in shuffle(rBase) for c in shuffle(rBase)]
    nums  = shuffle(range(1,base*base+1))
    board = [[nums[pattern(r,c)] for c in cols] for r in rows]
    return board

def remove_numbers(board, empties=40):
    board = copy.deepcopy(board)
    squares = side*side
    empties = min(empties, squares)
    for p in random.sample(range(squares), empties):
        board[p//side][p%side] = 0
    return board

class Sudoku(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sudoku")
        self.geometry("600x700")
        self.resizable(False, False)

        self.hint_limit = 5
        self.hints_used = 0

        self.base_board = generate_board()
        self.puzzle = remove_numbers(self.base_board, empties=40)
        self.current_board = copy.deepcopy(self.puzzle)

        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.create_widgets()
        self.draw_board()

    # ADDED: Validation function to allow only single digits (1-9)
    def _validate_input(self, P):
        """
        Validates the input to allow only empty strings or single digits from 1 to 9.
        P: The value of the entry if the edit is allowed.
        """
        # Allow deletion (resulting in an empty string)
        if P == "":
            return True
        
        # Check if the input is a single digit and not '0'
        if len(P) == 1 and P.isdigit() and P != '0':
            return True
            
        # Reject any other input
        return False

    def create_widgets(self):
        # MODIFIED: Added validation to the Entry widgets
        vcmd = (self.register(self._validate_input), '%P') # Register the validation function

        frame = tk.Frame(self)
        frame.pack(pady=20)
        for i in range(9):
            for j in range(9):
                # Apply the validation command to each Entry widget
                e = tk.Entry(frame, width=2, font=("Arial", 24), justify='center',
                             validate="key", validatecommand=vcmd)
                e.grid(row=i, column=j, padx=(2 if j%3==0 else 0), pady=(2 if i%3==0 else 0))
                self.entries[i][j] = e

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        self.hint_btn = tk.Button(btn_frame, text=f"Hint ({self.hint_limit - self.hints_used} left)", command=self.give_hint)
        self.hint_btn.grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Check Solution", command=self.check_solution).grid(row=0, column=1, padx=10)
        tk.Button(btn_frame, text="Reset", command=self.reset_puzzle).grid(row=0, column=2, padx=10)

    def draw_board(self):
        for i in range(9):
            for j in range(9):
                e = self.entries[i][j]
                e.delete(0, tk.END)
                if self.puzzle[i][j] != 0:
                    e.insert(0, str(self.puzzle[i][j]))
                    e.config(state='disabled', disabledforeground='black', fg='black')
                else:
                    e.config(state='normal', fg='black')
        self.update_hint_button()

    def give_hint(self):
        if self.hints_used >= self.hint_limit:
            self.hint_btn.config(state='disabled')
            return
        # Fill a random empty or incorrect cell with the correct value
        empties = [(i, j) for i in range(9) for j in range(9)
                   if self.entries[i][j].get() == '' or self.entries[i][j].get() != str(self.base_board[i][j])]
        if not empties:
            messagebox.showinfo("Hint", "No empty or incorrect cells to hint!")
            return
        i, j = random.choice(empties)
        self.entries[i][j].delete(0, tk.END)
        self.entries[i][j].insert(0, str(self.base_board[i][j]))
        self.entries[i][j].config(fg='blue')
        self.hints_used += 1
        self.update_hint_button()

    def update_hint_button(self):
        hints_left = self.hint_limit - self.hints_used
        self.hint_btn.config(text=f"Hint ({hints_left} left)")
        if hints_left <= 0:
            self.hint_btn.config(state='disabled')
        else:
            self.hint_btn.config(state='normal')

    def check_solution(self):
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if val == '' or not val.isdigit() or int(val) != self.base_board[i][j]:
                    messagebox.showerror("Incorrect", "Sorry, the solution is not correct yet!")
                    return
        messagebox.showinfo("Congratulations", "You solved the Sudoku!")

    def reset_puzzle(self):
        self.hint_limit = 5
        self.hints_used = 0
        self.base_board = generate_board()
        self.puzzle = remove_numbers(self.base_board, empties=40)
        self.current_board = copy.deepcopy(self.puzzle)
        self.draw_board()

if __name__ == "__main__":
    game = Sudoku()
    game.mainloop()