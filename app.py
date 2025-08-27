import random
import json
import time

# -----------------------------
# Core Game State
# -----------------------------
class GameState:
    def __init__(self):
        self.money = 0.0
        self.money_per_click = 1.0
        self.money_per_second = 0.0

        # Stats
        self.total_money_made = 0.0
        self.total_clicks = 0
        self.total_chests_opened = 0
        self.total_cards_collected = 0
        self.total_cards_sold = 0
        self.total_money_clicked = 0.0

        # Progression
        self.arena_level = 1
        self.owned_cards = []
        self.upgrades_purchased = []

        # Passive income tracking
        self.last_tick = time.time()

    def click(self):
        """Handle user clicking on chest space"""
        self.money += self.money_per_click
        self.total_money_made += self.money_per_click
        self.total_money_clicked += self.money_per_click
        self.total_clicks += 1

    def apply_passive_income(self):
        """Handle money per second"""
        now = time.time()
        elapsed = now - self.last_tick
        self.last_tick = now
        earned = elapsed * self.money_per_second
        self.money += earned
        self.total_money_made += earned

    def save(self, filename="save.json"):
        with open(filename, "w") as f:
            json.dump(self.__dict__, f, default=str, indent=2)

    def load(self, filename="save.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                self.__dict__.update(data)
        except FileNotFoundError:
            print("No save file found, starting fresh.")

# -----------------------------
# Upgrade System
# -----------------------------
class Upgrade:
    def __init__(self, name, cost, effect_type, effect_value):
        self.name = name
        self.cost = cost
        self.effect_type = effect_type  # "click" or "passive"
        self.effect_value = effect_value

    def apply(self, game: GameState):
        if self.effect_type == "click":
            game.money_per_click += self.effect_value
        elif self.effect_type == "passive":
            game.money_per_second += self.effect_value

# Predefined upgrade path
UPGRADES = [
    Upgrade("Auto Clicker I", 20, "passive", 0.5),
    Upgrade("MPC I", 1000, "click", 2),
    Upgrade("Auto Clicker II", 500, "passive", 1.5),
    Upgrade("MPC II", 5000, "click", 6),
    Upgrade("Auto Clicker III", 2500, "passive", 5),
    Upgrade("MPC III", 12500, "click", 9.5),
    Upgrade("Gold Clicker I", 8000, "passive", 7),
    Upgrade("MPC IV", 25000, "click", 15),
    Upgrade("Gold Clicker II", 20000, "passive", 9.5),
    Upgrade("MPC V", 65000, "click", 25),
    Upgrade("Master Clicker I", 50000, "passive", 12),
    Upgrade("MPC Master", 120000, "click", 50),
    Upgrade("Master Clicker II", 150000, "passive", 15),
]

# -----------------------------
# Example of Usage
# -----------------------------
if __name__ == "__main__":
    game = GameState()

    # Simulate a few clicks
    for _ in range(10):
        game.click()

    # Buy first upgrade if possible
    if game.money >= UPGRADES[0].cost:
        game.money -= UPGRADES[0].cost
        UPGRADES[0].apply(game)
        game.upgrades_purchased.append(UPGRADES[0].name)

    print(f"Money: {game.money:.2f}")
    print(f"MPC: {game.money_per_click}")
    print(f"MPS: {game.money_per_second}")
    print(f"Upgrades bought: {game.upgrades_purchased}")
