"""
UNO Card Game — Tkinter Implementation
Human vs up to 3 AI opponents
"""

import tkinter as tk
from tkinter import messagebox
import random

# ─────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────
COLORS = ["Red", "Green", "Blue", "Yellow"]
CARD_COLORS = {
    "Red":    "#e74c3c",
    "Green":  "#27ae60",
    "Blue":   "#2980b9",
    "Yellow": "#f1c40f",
    "Wild":   "#8e44ad",
}
TEXT_COLORS = {
    "Red": "white", "Green": "white",
    "Blue": "white", "Yellow": "#1a1a1a", "Wild": "white",
}
VALUES = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
          "Skip", "Reverse", "+2"]
WILD_CARDS = ["Wild", "+4"]


# ─────────────────────────────────────────
#  Card
# ─────────────────────────────────────────
class Card:
    def __init__(self, color, value):
        self.color = color   # "Red"|"Green"|"Blue"|"Yellow"|"Wild"
        self.value = value   # e.g. "5", "Skip", "Wild", "+4"

    def __repr__(self):
        return f"{self.color} {self.value}"

    def can_play_on(self, top: "Card", current_color: str) -> bool:
        if self.color == "Wild":
            return True
        if self.color == current_color:
            return True
        if self.value == top.value:
            return True
        return False


# ─────────────────────────────────────────
#  Deck
# ─────────────────────────────────────────
def build_deck() -> list:
    deck = []
    for color in COLORS:
        deck.append(Card(color, "0"))
        for value in VALUES[1:]:          # 1‑9, Skip, Reverse, Draw Two × 2
            deck.append(Card(color, value))
            deck.append(Card(color, value))
    for _ in range(4):
        deck.append(Card("Wild", "Wild"))
        deck.append(Card("Wild", "+4"))
    random.shuffle(deck)
    return deck


# ─────────────────────────────────────────
#  Player
# ─────────────────────────────────────────
class Player:
    def __init__(self, name: str, is_human: bool = False):
        self.name = name
        self.is_human = is_human
        self.hand: list[Card] = []

    def draw(self, deck: list, n: int = 1):
        for _ in range(n):
            if deck:
                self.hand.append(deck.pop())

    def playable_cards(self, top: Card, current_color: str) -> list[Card]:
        return [c for c in self.hand if c.can_play_on(top, current_color)]

    # Simple AI: prefer color match, then value match, then wild last
    def ai_choose(self, top: Card, current_color: str) -> Card | None:
        playable = self.playable_cards(top, current_color)
        if not playable:
            return None
        color_match = [c for c in playable if c.color == current_color and c.color != "Wild"]
        value_match = [c for c in playable if c.value == top.value and c.color != "Wild"]
        specials   = [c for c in playable if c.value in ("Skip", "Reverse", "+2", "+4")]
        wilds      = [c for c in playable if c.color == "Wild"]
        for group in (specials, color_match, value_match, wilds):
            if group:
                return random.choice(group)
        return playable[0]

    # AI picks the color it has the most of
    def ai_choose_color(self) -> str:
        counts = {c: 0 for c in COLORS}
        for card in self.hand:
            if card.color in counts:
                counts[card.color] += 1
        return max(counts, key=counts.get)


# ─────────────────────────────────────────
#  Game Logic
# ─────────────────────────────────────────
class UnoGame:
    def __init__(self, num_opponents: int = 2):
        self.num_opponents = num_opponents
        self.reset()

    def reset(self):
        self.deck = build_deck()
        self.discard: list[Card] = []
        self.players: list[Player] = [Player("You", is_human=True)]
        for i in range(1, self.num_opponents + 1):
            self.players.append(Player(f"AI {i}"))

        # Deal 7 cards each
        for p in self.players:
            p.draw(self.deck, 7)

        # Flip first card (re-draw if it's a Wild)
        first = self.deck.pop()
        while first.color == "Wild":
            self.deck.insert(0, first)
            first = self.deck.pop()
        self.discard.append(first)

        self.current_color = first.color
        self.turn_index = 0
        self.direction = 1        # 1 = clockwise, -1 = counter
        self.game_over = False
        self.winner: Player | None = None

    @property
    def top_card(self) -> Card:
        return self.discard[-1]

    @property
    def current_player(self) -> Player:
        return self.players[self.turn_index]

    def next_turn(self):
        self.turn_index = (self.turn_index + self.direction) % len(self.players)

    def _replenish_deck(self):
        if len(self.deck) < 2:
            top = self.discard.pop()
            self.deck = self.discard[:]
            self.discard = [top]
            random.shuffle(self.deck)

    def draw_card(self, player: Player, n: int = 1):
        self._replenish_deck()
        player.draw(self.deck, n)

    def play_card(self, player: Player, card: Card, chosen_color: str | None = None) -> str:
        """Play a card. Returns a status message."""
        player.hand.remove(card)
        self.discard.append(card)

        # Resolve color
        if card.color == "Wild":
            self.current_color = chosen_color or "Red"
        else:
            self.current_color = card.color

        msg = f"{player.name} played {card}"

        # Check win
        if not player.hand:
            self.game_over = True
            self.winner = player
            return msg

        # Apply effect, then advance turn
        skip_next = False
        if card.value == "Reverse":
            if len(self.players) == 2:
                skip_next = True          # Acts like Skip in 2-player
            else:
                self.direction *= -1
        elif card.value == "Skip":
            skip_next = True
        elif card.value == "+2":
            self.next_turn()
            next_p = self.current_player
            self.draw_card(next_p, 2)
            msg += f" → {next_p.name} draws 2 & is skipped"
            skip_next = False             # already advanced
            self.next_turn()
            return msg
        elif card.value == "+4":
            self.next_turn()
            next_p = self.current_player
            self.draw_card(next_p, 4)
            msg += f" → {next_p.name} draws 4 & is skipped"
            skip_next = False
            self.next_turn()
            return msg

        self.next_turn()
        if skip_next:
            msg += f" → {self.current_player.name} is skipped"
            self.next_turn()

        return msg


# ─────────────────────────────────────────
#  GUI
# ─────────────────────────────────────────
class UnoApp(tk.Tk):
    CARD_W, CARD_H = 70, 100
    AI_CARD_W, AI_CARD_H = 40, 60

    def __init__(self):
        super().__init__()
        self.title("🃏 UNO")
        self.resizable(False, False)
        self.configure(bg="#1a6b3c")

        # Ask number of opponents
        self.num_opponents = self._ask_opponents()
        self.game = UnoGame(self.num_opponents)
        self._selected_card: Card | None = None
        self._card_buttons: dict[Card, tk.Button] = {}

        self._build_ui()
        self._refresh()

    # ── startup dialog ──────────────────────────────
    def _ask_opponents(self) -> int:
        dlg = tk.Toplevel(self)
        dlg.title("UNO Setup")
        dlg.resizable(False, False)
        dlg.configure(bg="#1a6b3c")
        dlg.grab_set()
        tk.Label(dlg, text="Number of AI opponents:", bg="#1a6b3c",
                 fg="white", font=("Arial", 13, "bold")).pack(pady=(20, 8))
        var = tk.IntVar(value=2)
        for n in (1, 2, 3):
            tk.Radiobutton(dlg, text=str(n), variable=var, value=n,
                           bg="#1a6b3c", fg="white", selectcolor="#145a32",
                           font=("Arial", 12)).pack()
        result = [2]

        def confirm():
            result[0] = var.get()
            dlg.destroy()

        tk.Button(dlg, text="Start Game", command=confirm,
                  bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
                  relief="flat", padx=12, pady=6).pack(pady=16)
        self.wait_window(dlg)
        return result[0]

    # ── layout ──────────────────────────────────────
    def _build_ui(self):
        # Top bar
        self.top_frame = tk.Frame(self, bg="#145a32", pady=6)
        self.top_frame.pack(fill="x")
        self.status_lbl = tk.Label(self.top_frame, text="", bg="#145a32",
                                   fg="white", font=("Arial", 11, "bold"))
        self.status_lbl.pack(side="left", padx=12)
        tk.Button(self.top_frame, text="New Game", command=self._new_game,
                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold"),
                  relief="flat", padx=8).pack(side="right", padx=8)

        # AI hands (top)
        self.ai_frame = tk.Frame(self, bg="#1a6b3c")
        self.ai_frame.pack(fill="x", padx=10, pady=6)
        self.ai_labels: list[tk.Label] = []
        self.ai_hand_frames: list[tk.Frame] = []
        for i in range(self.num_opponents):
            col = tk.Frame(self.ai_frame, bg="#1a6b3c")
            col.pack(side="left", padx=16)
            lbl = tk.Label(col, text="", bg="#1a6b3c", fg="white",
                           font=("Arial", 10, "bold"))
            lbl.pack()
            hf = tk.Frame(col, bg="#1a6b3c")
            hf.pack()
            self.ai_labels.append(lbl)
            self.ai_hand_frames.append(hf)

        # Centre: discard + deck + color swatch
        centre = tk.Frame(self, bg="#1a6b3c")
        centre.pack(pady=10)

        self.discard_canvas = tk.Canvas(centre, width=self.CARD_W + 20,
                                        height=self.CARD_H + 20, bg="#1a6b3c",
                                        highlightthickness=0)
        self.discard_canvas.pack(side="left", padx=20)

        self.color_swatch = tk.Canvas(centre, width=36, height=36,
                                      bg="#1a6b3c", highlightthickness=0)
        self.color_swatch.pack(side="left", padx=4)

        deck_btn = tk.Button(centre, text="Draw\nCard", width=6,
                             command=self._human_draw,
                             bg="#2c3e50", fg="white",
                             font=("Arial", 11, "bold"), relief="raised",
                             pady=14)
        deck_btn.pack(side="left", padx=20)
        self.deck_btn = deck_btn

        # Log
        log_frame = tk.Frame(self, bg="#1a6b3c")
        log_frame.pack(fill="x", padx=12)
        self.log_text = tk.Text(log_frame, height=4, bg="#0d3b22", fg="#a8d8a8",
                                font=("Consolas", 9), state="disabled",
                                relief="flat", bd=0, wrap="word")
        self.log_text.pack(fill="x")

        # Human hand
        tk.Label(self, text="Your Hand", bg="#1a6b3c", fg="#a8d8a8",
                 font=("Arial", 10, "italic")).pack(pady=(8, 2))
        self.hand_frame = tk.Frame(self, bg="#1a6b3c")
        self.hand_frame.pack(pady=4, padx=10)

        # Play button
        self.play_btn = tk.Button(self, text="Play Selected Card",
                                  command=self._human_play,
                                  bg="#27ae60", fg="white",
                                  font=("Arial", 12, "bold"),
                                  relief="flat", padx=16, pady=6)
        self.play_btn.pack(pady=8)

    # ── drawing helpers ─────────────────────────────
    def _draw_card_canvas(self, canvas: tk.Canvas, card: Card,
                          x: int, y: int, w: int, h: int,
                          color_override: str | None = None):
        bg = CARD_COLORS.get(color_override or card.color, "#8e44ad")
        fg = TEXT_COLORS.get(color_override or card.color, "white")
        r = 8
        canvas.create_rectangle(x + r, y, x + w - r, y + h, fill=bg, outline="")
        canvas.create_rectangle(x, y + r, x + w, y + h - r, fill=bg, outline="")
        canvas.create_arc(x, y, x + 2*r, y + 2*r, start=90, extent=90, fill=bg, outline="")
        canvas.create_arc(x + w - 2*r, y, x + w, y + 2*r, start=0, extent=90, fill=bg, outline="")
        canvas.create_arc(x, y + h - 2*r, x + 2*r, y + h, start=180, extent=90, fill=bg, outline="")
        canvas.create_arc(x + w - 2*r, y + h - 2*r, x + w, y + h, start=270, extent=90, fill=bg, outline="")
        # white border
        canvas.create_oval(x + 6, y + 6, x + w - 6, y + h - 6,
                            outline="white", width=2)
        label = card.value if card.value not in ("Wild", "Wild Draw Four") else \
                ("W" if card.value == "Wild" else "W+4")
        canvas.create_text(x + w // 2, y + h // 2, text=label,
                            fill=fg, font=("Arial", max(9, w // 6), "bold"))

    def _make_card_button(self, parent: tk.Frame, card: Card) -> tk.Button:
        bg = CARD_COLORS.get(card.color, "#8e44ad")
        fg = TEXT_COLORS.get(card.color, "white")
        label = card.value
        if card.value == "Wild Draw Four":
            label = "W+4"
        elif card.value == "Wild":
            label = "Wild"
        btn = tk.Button(parent, text=label, bg=bg, fg=fg, width=5, height=3,
                        font=("Arial", 9, "bold"), relief="raised", bd=3,
                        command=lambda c=card: self._select_card(c))
        return btn

    # ── refresh UI ──────────────────────────────────
    def _refresh(self):
        g = self.game
        is_human_turn = g.current_player.is_human and not g.game_over

        # Status
        if g.game_over:
            self.status_lbl.config(
                text=f"🎉 {g.winner.name} wins!" if g.winner else "Game over")
        else:
            self.status_lbl.config(
                text=f"Turn: {g.current_player.name}  |  "
                     f"Color: {g.current_color}  |  "
                     f"Deck: {len(g.deck)} cards")

        # Discard pile
        self.discard_canvas.delete("all")
        self._draw_card_canvas(self.discard_canvas, g.top_card, 10, 10,
                               self.CARD_W, self.CARD_H,
                               color_override=g.current_color
                               if g.top_card.color == "Wild" else None)

        # Color swatch
        self.color_swatch.delete("all")
        swatch_bg = CARD_COLORS.get(g.current_color, "#555")
        self.color_swatch.create_oval(2, 2, 34, 34, fill=swatch_bg, outline="white", width=2)

        # AI hands
        for i, p in enumerate(g.players[1:]):
            self.ai_labels[i].config(
                text=f"{p.name}  ({len(p.hand)} cards)"
                     + (" ◄" if g.players.index(p) == g.turn_index else ""))
            for w in self.ai_hand_frames[i].winfo_children():
                w.destroy()
            cols = min(len(p.hand), 16)
            for j, _ in enumerate(p.hand[:cols]):
                c = tk.Canvas(self.ai_hand_frames[i],
                              width=self.AI_CARD_W, height=self.AI_CARD_H,
                              bg="#1a6b3c", highlightthickness=0)
                c.pack(side="left", padx=1)
                c.create_rectangle(4, 4, self.AI_CARD_W - 4,
                                   self.AI_CARD_H - 4,
                                   fill="#2c3e50", outline="white", width=2)
                c.create_text(self.AI_CARD_W // 2, self.AI_CARD_H // 2,
                              text="UNO", fill="#a8d8a8",
                              font=("Arial", 7, "bold"))
            if len(p.hand) > cols:
                tk.Label(self.ai_hand_frames[i],
                         text=f"+{len(p.hand)-cols}",
                         bg="#1a6b3c", fg="white",
                         font=("Arial", 9)).pack(side="left")

        # Human hand
        for w in self.hand_frame.winfo_children():
            w.destroy()
        self._card_buttons.clear()
        human = g.players[0]
        playable = set(id(c) for c in human.playable_cards(g.top_card, g.current_color))
        for card in human.hand:
            btn = self._make_card_button(self.hand_frame, card)
            if id(card) not in playable or not is_human_turn:
                btn.config(state="disabled", relief="flat")
            if card is self._selected_card:
                btn.config(relief="sunken", bd=4, highlightbackground="white")
            btn.pack(side="left", padx=2, pady=2)
            self._card_buttons[card] = btn

        self.play_btn.config(state="normal" if (is_human_turn and self._selected_card) else "disabled")
        self.deck_btn.config(state="normal" if is_human_turn else "disabled")

        # Trigger AI if not human's turn
        if not g.current_player.is_human and not g.game_over:
            self.after(900, self._ai_turn)

    def _select_card(self, card: Card):
        if card is self._selected_card:
            self._selected_card = None
        else:
            self._selected_card = card
        self._refresh()

    # ── actions ─────────────────────────────────────
    def _human_play(self):
        card = self._selected_card
        if card is None:
            return
        g = self.game
        human = g.players[0]
        if not card.can_play_on(g.top_card, g.current_color):
            self._log("That card can't be played right now.")
            return

        chosen_color = None
        if card.color == "Wild":
            chosen_color = self._pick_color()
            if chosen_color is None:
                return  # user cancelled

        self._selected_card = None
        msg = g.play_card(human, card, chosen_color)
        self._log(msg)
        if g.game_over:
            self._refresh()
            messagebox.showinfo("UNO!", f"🎉 {g.winner.name} wins!")
        else:
            self._refresh()

    def _human_draw(self):
        g = self.game
        human = g.players[0]
        if g.current_player is not human:
            return
        g.draw_card(human, 1)
        self._log(f"You drew a card.")
        self._selected_card = None
        # If now playable, let player choose to play; else end turn
        if not human.playable_cards(g.top_card, g.current_color):
            g.next_turn()
            self._log("No playable card — turn skipped.")
        self._refresh()

    def _ai_turn(self):
        g = self.game
        ai = g.current_player
        if ai.is_human or g.game_over:
            return
        card = ai.ai_choose(g.top_card, g.current_color)
        if card is None:
            g.draw_card(ai, 1)
            self._log(f"{ai.name} draws a card.")
            card = ai.ai_choose(g.top_card, g.current_color)
            if card is None:
                self._log(f"{ai.name} has no playable card — skipped.")
                g.next_turn()
                self._refresh()
                return

        chosen_color = ai.ai_choose_color() if card.color == "Wild" else None
        msg = g.play_card(ai, card, chosen_color)
        if chosen_color:
            msg += f" (chose {chosen_color})"
        if len(ai.hand) == 1:
            msg += " — UNO! 🔔"
        self._log(msg)

        if g.game_over:
            self._refresh()
            messagebox.showinfo("UNO!", f"🤖 {g.winner.name} wins!")
        else:
            self._refresh()

    def _log(self, msg: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _pick_color(self) -> str | None:
        dlg = tk.Toplevel(self)
        dlg.title("Choose Color")
        dlg.resizable(False, False)
        dlg.configure(bg="#1a1a1a")
        dlg.grab_set()
        tk.Label(dlg, text="Pick a color:", bg="#1a1a1a", fg="white",
                 font=("Arial", 13, "bold")).pack(pady=(16, 8))
        result = [None]
        btn_frame = tk.Frame(dlg, bg="#1a1a1a")
        btn_frame.pack(padx=20, pady=10)
        for color in COLORS:
            def choose(c=color):
                result[0] = c
                dlg.destroy()
            tk.Button(btn_frame, text=color, bg=CARD_COLORS[color],
                      fg=TEXT_COLORS[color], font=("Arial", 12, "bold"),
                      width=9, pady=8, relief="flat",
                      command=choose).pack(side="left", padx=4)
        self.wait_window(dlg)
        return result[0]

    def _new_game(self):
        self.game.reset()
        self._selected_card = None
        for w in self.hand_frame.winfo_children():
            w.destroy()
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self._refresh()


# ─────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────
if __name__ == "__main__":
    app = UnoApp()
    app.mainloop()