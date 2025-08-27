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

    # -----------------------------
# Card System
# -----------------------------
class Card:
    def __init__(self, name, rarity, base_value):
        self.name = name
        self.rarity = rarity  # Common, Rare, Epic, Legendary
        self.base_value = base_value

    def __repr__(self):
        return f"{self.rarity} {self.name} (Value: {self.base_value})"


# Define card pool
CARD_POOL = [
    Card("Knight", "Common", 5),
    Card("Archers", "Common", 5),
    Card("Bomber", "Common", 6),
    Card("Musketeer", "Rare", 20),
    Card("Mini P.E.K.K.A", "Rare", 25),
    Card("Hog Rider", "Rare", 30),
    Card("Baby Dragon", "Epic", 100),
    Card("Prince", "Epic", 120),
    Card("Witch", "Epic", 140),
    Card("Sparky", "Legendary", 500),
    Card("Electro Wizard", "Legendary", 600),
    Card("Mega Knight", "Legendary", 750),
]


# -----------------------------
# Chest System
# -----------------------------
class Chest:
    def __init__(self, name, cost, rarity_weights):
        self.name = name
        self.cost = cost
        self.rarity_weights = rarity_weights  # Dict: {"Common": %, "Rare": %, "Epic": %, "Legendary": %}

    def open(self, game: GameState):
        if game.money < self.cost:
            return None, "Not enough money!"
        game.money -= self.cost
        game.total_chests_opened += 1

        rarity = random.choices(
            population=list(self.rarity_weights.keys()),
            weights=list(self.rarity_weights.values()),
            k=1
        )[0]

        # Get random card of that rarity
        candidates = [c for c in CARD_POOL if c.rarity == rarity]
        pulled = random.choice(candidates)

        # Add to collection
        game.owned_cards.append(pulled)
        game.total_cards_collected += 1

        return pulled, f"You pulled a {rarity} card: {pulled.name}!"


# Define chest types
CHESTS = [
    Chest("Wooden Chest", 50, {"Common": 80, "Rare": 15, "Epic": 5, "Legendary": 0}),
    Chest("Silver Chest", 200, {"Common": 65, "Rare": 25, "Epic": 8, "Legendary": 2}),
    Chest("Gold Chest", 1000, {"Common": 45, "Rare": 35, "Epic": 15, "Legendary": 5}),
    Chest("Magical Chest", 5000, {"Common": 30, "Rare": 40, "Epic": 20, "Legendary": 10}),
    Chest("Legendary Chest", 20000, {"Common": 0, "Rare": 0, "Epic": 40, "Legendary": 60}),
]


# -----------------------------
# Selling Cards
# -----------------------------
def sell_card(game: GameState, card: Card):
    game.money += card.base_value
    game.owned_cards.remove(card)
    game.total_cards_sold += 1


    print(f"Money: {game.money:.2f}")
    print(f"MPC: {game.money_per_click}")
    print(f"MPS: {game.money_per_second}")
    print(f"Upgrades bought: {game.upgrades_purchased}")

# -----------------------------
# Arena System
# -----------------------------
class Arena:
    def __init__(self, level, name, unlock_condition, chest_unlocks, card_unlocks):
        self.level = level
        self.name = name
        self.unlock_condition = unlock_condition  # money OR stat requirement
        self.chest_unlocks = chest_unlocks  # which chest types become available
        self.card_unlocks = card_unlocks    # which cards enter the pool


# Define Arenas
ARENAS = [
    Arena(1, "Training Camp", {"money": 0}, ["Wooden Chest"], ["Knight", "Archers", "Bomber"]),
    Arena(2, "Goblin Stadium", {"money": 500}, ["Silver Chest"], ["Musketeer", "Mini P.E.K.K.A"]),
    Arena(3, "Bone Pit", {"money": 2000}, ["Gold Chest"], ["Hog Rider", "Baby Dragon"]),
    Arena(4, "P.E.K.K.A’s Playhouse", {"money": 10000}, ["Magical Chest"], ["Prince", "Witch"]),
    Arena(5, "Legendary Arena", {"money": 50000}, ["Legendary Chest"], ["Sparky", "Electro Wizard", "Mega Knight"]),
]


# -----------------------------
# Check Arena Unlocks
# -----------------------------
def update_arena_progress(game: GameState):
    for arena in ARENAS:
        if game.arena_level < arena.level:
            cond = arena.unlock_condition
            if "money" in cond and game.total_money_made >= cond["money"]:
                game.arena_level = arena.level
                return f"🎉 You unlocked {arena.name}!"
    return None


# -----------------------------
# Filter Available Chests/Cards
# -----------------------------
def available_chests(game: GameState):
    unlocked = []
    for arena in ARENAS:
        if game.arena_level >= arena.level:
            unlocked.extend(arena.chest_unlocks)
    return [c for c in CHESTS if c.name in unlocked]


def available_cards(game: GameState):
    unlocked = []
    for arena in ARENAS:
        if game.arena_level >= arena.level:
            unlocked.extend(arena.card_unlocks)
    return [c for c in CARD_POOL if c.name in unlocked]

