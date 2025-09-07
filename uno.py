import tkinter as tk
from tkinter import messagebox
import random

COLORS = ["Red", "Green", "Yellow", "Blue"]
VALUES = [str(n) for n in range(0, 10)] + ["Skip", "Reverse", "Draw Two"]
SPECIALS = ["Wild", "Wild Draw Four"]
BG_COLOR = "#283747"
FONT_NAME = "Arial Rounded MT Bold"
CARD_WIDTH = 100
CARD_HEIGHT = 150
CARD_CORNER_RADIUS = 10


def generate_deck():
    """Generates and shuffles a standard 108-card UNO deck."""
    deck = []
    for color in COLORS:
        deck.append((color, "0"))
        for v in VALUES[1:]:
            deck.extend([(color, v)] * 2)
    for _ in range(4):
        deck.append(("Black", "Wild"))
        deck.append(("Black", "Wild Draw Four"))
    random.shuffle(deck)
    return deck

def card_str(card):
    """Returns a string representation of a card."""
    color, value = card
    if color == "Black": return value
    if value == "Skip": value = "🚫"
    if value == "Reverse": value = "🔄"
    if value == "Draw Two": value = "+2"
    if value == "Wild": return "Wild"
    if value == "Wild Draw Four": return "+4"
    return f"{value}"


class CardWidget(tk.Canvas):
    """A custom widget to display a single UNO card."""
    def __init__(self, parent, card_tuple, command=None):
        self.card = card_tuple
        self.command = command
        super().__init__(parent, width=CARD_WIDTH, height=CARD_HEIGHT, bg=BG_COLOR, bd=0, highlightthickness=0)
        self._create_rounded_rectangle(0, 0, CARD_WIDTH, CARD_HEIGHT, radius=CARD_CORNER_RADIUS, fill=self._get_card_color())
        self._draw_card_text()
        if self.command:
            self.bind("<Button-1>", self._on_click)
            self.bind("<Enter>", self._on_enter)
            self.bind("<Leave>", self._on_leave)

    def _create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius, x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2, x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius, x1, y1+radius, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def _get_card_color(self):
        color_map = {"Red": "#c72a18", "Green": "#4a942a", "Yellow": "#e5d325", "Blue": "#1769aa", "Black": "#262626"}
        return color_map.get(self.card[0], "#FFFFFF")

    def _draw_card_text(self):
        text = card_str(self.card)
        text_color = "white" if self.card[0] != "Yellow" else "black"
        if self.card[0] == "Black":
            self.create_oval(25, 30, 75, 60, fill="#c72a18", width=0)
            self.create_oval(25, 90, 75, 120, fill="#4a942a", width=0)
            self.create_oval(5, 60, 55, 90, fill="#1769aa", width=0)
            self.create_oval(45, 60, 95, 90, fill="#e5d325", width=0)
            if self.card[1] == "Wild Draw Four":
                 self.create_text(CARD_WIDTH/2, CARD_HEIGHT/2, text="+4", font=(FONT_NAME, 30, "bold"), fill="white")
        else:
            font_size = 40 if len(text) <= 2 else 22
            self.create_text(CARD_WIDTH/2, CARD_HEIGHT/2, text=text, font=(FONT_NAME, font_size, "bold"), fill=text_color)
            self.create_text(15, 20, text=text.replace('+2','+').replace('+4','+'), font=(FONT_NAME, 14, "bold"), fill=text_color)

    def _on_click(self, event): self.command()
    def _on_enter(self, event): self.config(highlightbackground="white", highlightthickness=3)
    def _on_leave(self, event): self.config(highlightthickness=0)


class UnoGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UNO with Stricter Stacking")
        self.configure(bg=BG_COLOR, padx=20, pady=20)
        self.deck, self.discard, self.hands = [], [], [[], []]
        self.current, self.direction = 0, 1
        self.awaiting_color_choice = False
        self.draw_stack, self.stacking_card_value = 0, None
        self.selected_card_indices = []
        self.info_var = tk.StringVar(value="Welcome to UNO!")
        self.bot_label_var = tk.StringVar()
        self.create_widgets()
        self.start_game()

    def create_widgets(self):
        bot_frame = tk.Frame(self, bg=BG_COLOR)
        bot_frame.pack(pady=10)
        tk.Label(bot_frame, text="Bot's Hand:", font=(FONT_NAME, 16), bg=BG_COLOR, fg="white").pack(side="left", padx=5)
        self.bot_card_count = tk.Label(bot_frame, text="7", font=(FONT_NAME, 16, "bold"), bg=BG_COLOR, fg="white")
        self.bot_card_count.pack(side="left")
        tk.Label(self, textvariable=self.bot_label_var, font=("Arial", 12, "italic"), bg=BG_COLOR, fg="#f0f0f0").pack()

        center_frame = tk.Frame(self, bg=BG_COLOR)
        center_frame.pack(pady=20)
        self.draw_pile_canvas = CardWidget(center_frame, ("Black", "UNO"), command=self.draw_card)
        self.draw_pile_canvas.pack(side="left", padx=15)
        self.discard_pile_canvas = tk.Canvas(center_frame, width=CARD_WIDTH, height=CARD_HEIGHT, bg=BG_COLOR, highlightthickness=0)
        self.discard_pile_canvas.pack(side="left", padx=15)

        tk.Label(self, textvariable=self.info_var, font=("Arial", 14), bg=BG_COLOR, fg="#f5f5f5").pack(pady=5)
        
        player_area_frame = tk.Frame(self, bg=BG_COLOR)
        player_area_frame.pack(pady=10)
        tk.Label(player_area_frame, text="Your Hand:", font=(FONT_NAME, 16), bg=BG_COLOR, fg="white").pack()
        self.cards_frame = tk.Frame(player_area_frame, bg=BG_COLOR)
        self.cards_frame.pack()

        self.color_choice_frame = tk.Frame(self, bg=BG_COLOR)
        
        self.turn_in_btn = tk.Button(self, text="Play Selected Cards", font=(FONT_NAME, 14, "bold"), 
                                     command=self.play_selected_cards, state="disabled",
                                     bg="#4a942a", fg="white", activebackground="#6dc24b")
        self.turn_in_btn.pack(pady=10)
        
        controls_frame = tk.Frame(self, bg=BG_COLOR)
        controls_frame.pack(pady=15, side="bottom")
        tk.Button(controls_frame, text="Restart Game", font=("Arial", 11), command=self.start_game).pack(side="left", padx=10)
        self.peek_btn = tk.Button(controls_frame, text="Peek Opponent's Cards", font=("Arial", 11), command=self.peek_bot_hand)
        self.peek_btn.pack(side="left", padx=10)

    def start_game(self):
        self.deck = generate_deck()
        self.discard = []
        self.hands = [[self.deck.pop() for _ in range(7)], [self.deck.pop() for _ in range(7)]]
        while True:
            first = self.deck.pop()
            if first[0] != "Black" and first[1] not in ("Skip", "Reverse", "Draw Two"):
                self.discard.append(first); break
            self.deck.insert(0, first)
        self.current, self.direction = 0, 1
        self.awaiting_color_choice = False
        self.draw_stack, self.stacking_card_value = 0, None
        self.selected_card_indices = []
        self.info_var.set("Your turn! Select cards and click 'Play'.")
        self.bot_label_var.set("")
        self.hide_color_choice()
        self.update_all()

    def update_all(self):
        self.discard_pile_canvas.delete("all")
        if self.discard: CardWidget(self.discard_pile_canvas, self.discard[-1]).place(x=0, y=0)
        for widget in self.cards_frame.winfo_children(): widget.destroy()

        for idx, card in enumerate(self.hands[0]):
            card_widget = CardWidget(self.cards_frame, card, command=lambda i=idx: self.toggle_selection(i))
            pady_config = (0, 20) if idx in self.selected_card_indices else 5
            card_widget.pack(side="left", padx=5, pady=pady_config)

        self.bot_card_count.config(text=str(len(self.hands[1])))
        self.peek_btn.config(state="normal" if self.current == 0 and not self.awaiting_color_choice else "disabled")
        self.turn_in_btn.config(state="normal" if self.selected_card_indices and self.current == 0 else "disabled")
        self.update_idletasks()

    def toggle_selection(self, idx):
        if idx in self.selected_card_indices:
            self.selected_card_indices.remove(idx)
        else:
            self.selected_card_indices.append(idx)
        self.update_all()

    def play_selected_cards(self):
        if self.current != 0 or not self.selected_card_indices: return

        indices_in_play_order = sorted(self.selected_card_indices, key=self.selected_card_indices.index)
        selected_cards = [self.hands[0][i] for i in indices_in_play_order]
        first_card, first_value = selected_cards[0], selected_cards[0][1]
        
        if not self.is_playable(first_card, self.discard[-1], self.hands[0]):
            self.info_var.set("Invalid move! The first card can't be played."); self.selected_card_indices.clear(); self.update_all(); return
        if not all(card[1] == first_value for card in selected_cards[1:]):
            self.info_var.set("Invalid stack! All selected cards must have the same number or power."); self.selected_card_indices.clear(); self.update_all(); return

        if first_card[0] == "Black":
            self.awaiting_color_choice = True; self.info_var.set("Choose a color for your Wild card."); self.show_color_choice(); return

        self.execute_play(indices_in_play_order)

    def execute_play(self, indices, chosen_color=None):
        indices.sort(reverse=True)
        played_cards = [self.hands[0].pop(idx) for idx in indices]
        played_cards.reverse()
        
        if chosen_color:
            self.discard.append((chosen_color, played_cards[0][1]))
            if len(played_cards) > 1: self.discard.extend(played_cards[1:])
        else:
            self.discard.extend(played_cards)

        self.selected_card_indices.clear()
        if self.check_win(0): messagebox.showinfo("Game Over", "You win!"); self.start_game(); return

        for card in played_cards[:-1]:
            if card[1] == 'Draw Two': self.draw_stack += 2
            elif card[1] == 'Wild Draw Four': self.draw_stack += 4
            if card[1] in ["Draw Two", "Wild Draw Four"]: self.stacking_card_value = card[1]

        self.handle_card_effect(self.discard[-1])
        self.update_all()
        if self.current == 1: self.after(1000, self.bot_move)

    def draw_card(self):
        if self.awaiting_color_choice or self.current != 0: return
        if self.draw_stack > 0:
            self.info_var.set(f"You draw {self.draw_stack} cards. Bot's turn.")
            self.draw_cards(0, self.draw_stack); self.draw_stack, self.stacking_card_value = 0, None
            self.current = 1; self.update_all(); self.after(1000, self.bot_move)
            return

        if any(self.is_playable(c, self.discard[-1], self.hands[0]) for c in self.hands[0]):
            self.info_var.set("You have a playable card! You must play it."); return
        if not self.deck: self.reshuffle()
        self.hands[0].append(self.deck.pop())
        self.info_var.set("You drew a card. Bot's turn!"); self.current = 1
        self.update_all(); self.after(1000, self.bot_move)

    def bot_move(self):
        if self.current != 1: return
        self.peek_btn.config(state="disabled")
        if self.draw_stack > 0:
            stack_opts = [i for i, c in enumerate(self.hands[1]) if c[1] == self.stacking_card_value]
            if stack_opts:
                play_indices = stack_opts; play_indices.sort(reverse=True)
                self.bot_label_var.set(f"Bot stacked {len(play_indices)} card(s)!")
                played_cards = [self.hands[1].pop(i) for i in play_indices]
                self.discard.extend(played_cards)
                for card in played_cards[:-1]:
                    if card[1] == 'Draw Two': self.draw_stack += 2
                    elif card[1] == 'Wild Draw Four': self.draw_stack += 4
                self.handle_card_effect(self.discard[-1])
            else:
                self.bot_label_var.set(f"Bot draws {self.draw_stack} cards.")
                self.draw_cards(1, self.draw_stack)
                self.draw_stack, self.stacking_card_value = 0, None; self.current = 0
                self.info_var.set("Your turn!")
            self.update_all(); return

        playable = [(i, c) for i, c in enumerate(self.hands[1]) if self.is_playable(c, self.discard[-1], self.hands[1])]
        if playable:
            idx, card_to_play = random.choice(playable)
            if card_to_play[0] == "Black":
                color = self.bot_choose_color()
                self.bot_label_var.set(f"Bot played a Wild and chose {color}")
                self.discard.append((color, self.hands[1].pop(idx)[1]))
            else:
                self.bot_label_var.set(f"Bot played {card_to_play[0]} {card_to_play[1]}")
                self.discard.append(self.hands[1].pop(idx))

            if self.check_win(1): messagebox.showinfo("Game Over", "Bot wins!"); self.start_game(); return
            
            self.handle_card_effect(self.discard[-1])
            self.update_all()

            # --- MODIFIED: Handle consecutive bot turns after playing a card ---
            # If the bot played a Skip/Reverse, it's still its turn. Schedule another move.
            if self.current == 1 and not self.check_win(1):
                self.after(1000, self.bot_move)
        else:
            if not self.deck: self.reshuffle()
            self.hands[1].append(self.deck.pop())
            self.bot_label_var.set("Bot drew a card."); self.current = 0
            self.info_var.set("Your turn!")
            self.update_all()

    def choose_color(self, color):
        if not self.awaiting_color_choice: return
        self.awaiting_color_choice = False; self.hide_color_choice()
        self.info_var.set(f"You chose {color}. Bot's turn.")
        indices_in_play_order = sorted(self.selected_card_indices, key=self.selected_card_indices.index)
        self.execute_play(indices_in_play_order, chosen_color=color)

    def handle_card_effect(self, card):
        color, value = card; next_player = (self.current + self.direction) % 2
        if value == "Draw Two":
            self.draw_stack += 2; self.stacking_card_value = "Draw Two"
            self.info_var.set(f"Stack is at +{self.draw_stack}! Next player must play a +2 or draw.")
            self.current = next_player
        elif value == "Wild Draw Four":
            self.draw_stack += 4; self.stacking_card_value = "Wild Draw Four"
            self.info_var.set(f"Stack is at +{self.draw_stack}! Next player must play a +4 or draw.")
            self.current = next_player
        elif value == "Skip": self.current = (self.current + self.direction * 2) % 2
        elif value == "Reverse": self.current = (self.current + self.direction * 2) % 2
        else: self.current = next_player
        
        if value not in ["Draw Two", "Wild Draw Four"]: 
            # This message is now set more carefully to avoid overwriting skip/reverse messages
            turn_msg = "Bot's turn." if self.current == 1 else "Your turn! Select cards and click 'Play'."
            if value == "Skip":
                turn_msg = "Your turn was skipped!" if self.current == 1 else "Bot's turn was skipped!"
            if value == "Reverse":
                turn_msg = "Your turn was skipped!" if self.current == 1 else "Bot's turn was skipped!"
            self.info_var.set(turn_msg)

    def is_playable(self, card, top, hand=None):
        if self.draw_stack > 0 and self.stacking_card_value:
            return card[1] == self.stacking_card_value
        if card[0] == top[0] or card[1] == top[1]: return True
        if card[1] == "Wild": return True
        if card[1] == "Wild Draw Four":
            return not any(c[0] == top[0] for c in hand) if hand else True
        return False

    def show_color_choice(self):
        self.color_choice_frame.pack(pady=10); self.turn_in_btn.pack_forget()
        for color in COLORS: tk.Button(self.color_choice_frame, bg=CardWidget(self, (color, ""))._get_card_color(), width=10, height=3, command=lambda c=color: self.choose_color(c)).pack(side="left", padx=5)
    def hide_color_choice(self):
        for widget in self.color_choice_frame.winfo_children(): widget.destroy()
        self.color_choice_frame.pack_forget(); self.turn_in_btn.pack(pady=10)
    def reshuffle(self): self.deck, self.discard = self.discard[:-1], [self.discard[-1]]; random.shuffle(self.deck)
    def check_win(self, player): return len(self.hands[player]) == 0
    def draw_cards(self, player, count):
        for _ in range(count):
            if not self.deck: self.reshuffle()
            self.hands[player].append(self.deck.pop())
    def bot_choose_color(self):
        counts = {c: sum(1 for card in self.hands[1] if card[0] == c) for c in COLORS}
        return max(counts, key=counts.get) if any(counts.values()) else random.choice(COLORS)
    def peek_bot_hand(self):
        self.peek_btn.config(state="disabled"); p = tk.Toplevel(self); p.title("Bot's Hand (Closes in 5s)"); p.config(bg=BG_COLOR, padx=15, pady=15); p.transient(self); p.grab_set()
        for card in self.hands[1]: CardWidget(p, card).pack(side="left", padx=5)
        p.after(5000, lambda: self.close_peek_window(p))
    def close_peek_window(self, window): window.destroy(); self.peek_btn.config(state="normal" if self.current == 0 else "disabled")

if __name__ == "__main__":
    UnoGame().mainloop()