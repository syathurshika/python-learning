"""
🎯  Guess the Number Game
   Try to guess the secret number within limited attempts.
   Features: difficulty levels, hints, scoring, leaderboard.
"""

import random
import datetime

SEPARATOR = "=" * 50

# In-memory leaderboard
leaderboard = []

DIFFICULTIES = {
    "1": {"name": "Easy",   "range": (1, 50),   "attempts": 10},
    "2": {"name": "Medium", "range": (1, 100),  "attempts": 7},
    "3": {"name": "Hard",   "range": (1, 200),  "attempts": 5},
}


# ─────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────

def print_banner():
    print(f"\n{SEPARATOR}")
    print("        🎯  GUESS THE NUMBER  🎯")
    print(SEPARATOR)


def print_section(title):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")


def progress_bar(attempts_left, max_attempts):
    filled = int((attempts_left / max_attempts) * 20)
    bar = "█" * filled + "░" * (20 - filled)
    return f"  [{bar}] {attempts_left}/{max_attempts} attempts left"


# ─────────────────────────────────────────
#  Hint system
# ─────────────────────────────────────────

def get_hint(secret, guess, low, high):
    diff = abs(secret - guess)
    span = high - low

    if diff == 0:
        return "🎉 Exact match!"
    elif diff <= span * 0.05:
        direction = "higher" if secret > guess else "lower"
        return f"🔥 Burning hot! Go {direction}."
    elif diff <= span * 0.15:
        direction = "higher" if secret > guess else "lower"
        return f"♨️  Very warm! Try {direction}."
    elif diff <= span * 0.30:
        direction = "higher" if secret > guess else "lower"
        return f"😐 Getting warmer. Go {direction}."
    elif diff <= span * 0.50:
        direction = "higher" if secret > guess else "lower"
        return f"❄️  Cold. Try {direction}."
    else:
        direction = "higher" if secret > guess else "lower"
        return f"🧊 Freezing! Way {direction}."


# ─────────────────────────────────────────
#  Score calculator
# ─────────────────────────────────────────

def calculate_score(attempts_used, max_attempts, difficulty_name):
    base = {"Easy": 100, "Medium": 200, "Hard": 350}[difficulty_name]
    efficiency = (max_attempts - attempts_used + 1) / max_attempts
    return int(base * efficiency)


# ─────────────────────────────────────────
#  Difficulty selector
# ─────────────────────────────────────────

def choose_difficulty():
    print_section("SELECT DIFFICULTY")
    for key, d in DIFFICULTIES.items():
        lo, hi = d["range"]
        print(f"  [{key}] {d['name']:<8}  Range: {lo}–{hi}   Attempts: {d['attempts']}")
    print()
    while True:
        choice = input("  Your choice (1/2/3): ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("  ❌  Enter 1, 2, or 3.")


# ─────────────────────────────────────────
#  Leaderboard
# ─────────────────────────────────────────

def update_leaderboard(name, score, difficulty, attempts):
    leaderboard.append({
        "name"      : name,
        "score"     : score,
        "difficulty": difficulty,
        "attempts"  : attempts,
        "date"      : datetime.date.today().strftime("%Y-%m-%d"),
    })
    leaderboard.sort(key=lambda x: x["score"], reverse=True)


def show_leaderboard():
    print_section("🏆  LEADERBOARD  (Top 10)")
    if not leaderboard:
        print("  No scores yet. Play a game first!")
        return
    print(f"\n  {'#':<4} {'Name':<16} {'Score':<8} {'Difficulty':<10} {'Attempts':<9} {'Date'}")
    print(f"  {'─'*60}")
    for i, entry in enumerate(leaderboard[:10], 1):
        medal = ["🥇","🥈","🥉"][i-1] if i <= 3 else f" {i}."
        print(f"  {medal:<4} {entry['name']:<16} {entry['score']:<8} "
              f"{entry['difficulty']:<10} {entry['attempts']:<9} {entry['date']}")


# ─────────────────────────────────────────
#  Core game loop
# ─────────────────────────────────────────

def play_game(player_name):
    diff   = choose_difficulty()
    low, high      = diff["range"]
    max_attempts   = diff["attempts"]
    difficulty_name = diff["name"]
    secret         = random.randint(low, high)
    attempts_used  = 0
    history        = []

    print(f"\n  🎮  {difficulty_name} mode — Guess a number between {low} and {high}.")
    print(f"  You have {max_attempts} attempts. Good luck, {player_name}!\n")

    while attempts_used < max_attempts:
        remaining = max_attempts - attempts_used
        print(progress_bar(remaining, max_attempts))

        if history:
            print(f"  Previous guesses: {', '.join(map(str, history))}")

        raw = input(f"\n  Your guess [{low}–{high}]: ").strip()

        if not raw.isdigit():
            print("  ⚠️  Please enter a valid number.")
            continue

        guess = int(raw)
        if guess < low or guess > high:
            print(f"  ⚠️  Out of range! Enter a number between {low} and {high}.")
            continue

        attempts_used += 1
        history.append(guess)
        hint = get_hint(secret, guess, low, high)
        print(f"  {hint}")

        if guess == secret:
            score = calculate_score(attempts_used, max_attempts, difficulty_name)
            print(f"\n{'─'*50}")
            print(f"  🎉  Correct! The number was {secret}.")
            print(f"  📊  Attempts used : {attempts_used}/{max_attempts}")
            print(f"  ⭐  Score         : {score} pts")
            print(f"{'─'*50}")
            update_leaderboard(player_name, score, difficulty_name, attempts_used)
            return True

    print(f"\n  💀  Out of attempts! The number was {secret}.")
    print(f"  Better luck next time, {player_name}!")
    return False


# ─────────────────────────────────────────
#  Main menu
# ─────────────────────────────────────────

def main():
    print_banner()
    player_name = input("  Enter your name: ").strip() or "Player"

    while True:
        print_section("MAIN MENU")
        print("  [1] Play Game")
        print("  [2] View Leaderboard")
        print("  [0] Quit")
        choice = input("\n  Select: ").strip()

        if choice == "1":
            play_game(player_name)
            show_leaderboard()
        elif choice == "2":
            show_leaderboard()
        elif choice == "0":
            print(f"\n  Thanks for playing, {player_name}! 👋\n")
            break
        else:
            print("  ❌  Invalid choice.")


if __name__ == "__main__":
    main()