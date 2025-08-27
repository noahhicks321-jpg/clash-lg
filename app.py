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

import streamlit as st

# Initialize session state
if "game" not in st.session_state:
    st.session_state.game = GameState()
if "message" not in st.session_state:
    st.session_state.message = ""

game = st.session_state.game

# -----------------------------
# Sidebar: Upgrades
# -----------------------------
st.sidebar.title("Upgrades")
next_upgrade = None
for upg in UPGRADES:
    if upg.name not in game.upgrades_purchased:
        next_upgrade = upg
        break

if next_upgrade:
    st.sidebar.write(f"Next Upgrade: {next_upgrade.name} - Cost: ${next_upgrade.cost}")
    if st.sidebar.button("Buy Upgrade"):
        if game.money >= next_upgrade.cost:
            game.money -= next_upgrade.cost
            next_upgrade.apply(game)
            game.upgrades_purchased.append(next_upgrade.name)
            st.sidebar.success(f"Purchased {next_upgrade.name}!")
        else:
            st.sidebar.error("Not enough money!")

st.sidebar.write(f"Money Per Click: ${game.money_per_click:.2f}")
st.sidebar.write(f"Money Per Second: ${game.money_per_second:.2f}")

# -----------------------------
# Home Tab - Clicking
# -----------------------------
st.title("Clash Royale Case Clicker Simulator")

# Apply passive income
game.apply_passive_income()

st.write(f"💰 Money: ${game.money:.2f}")
st.write(f"🏆 Arena Level: {game.arena_level}")

if st.button("Click Chest!"):
    game.click()
    st.session_state.message = f"You earned ${game.money_per_click:.2f}!"

if st.session_state.message:
    st.info(st.session_state.message)

# Update arena
arena_msg = update_arena_progress(game)
if arena_msg:
    st.balloons()
    st.success(arena_msg)

# -----------------------------
# Store Tab - Available Chests
# -----------------------------
st.header("🏰 Chest Store")

chests = available_chests(game)

for chest in chests:
    st.subheader(f"{chest.name} - Cost: ${chest.cost}")
    st.write("Rarity Chances:")
    for r, pct in chest.rarity_weights.items():
        st.write(f"- {r}: {pct}%")
    if st.button(f"Open {chest.name}", key=chest.name):
        pulled_card, msg = chest.open(game)
        st.session_state.message = msg
        st.success(msg)

# -----------------------------
# Collection Tab
# -----------------------------
st.header("📦 Your Card Collection")

if game.owned_cards:
    for idx, card in enumerate(game.owned_cards):
        st.write(f"{card.rarity} {card.name} - Sell Value: ${card.base_value:.2f}")
        if st.button(f"Sell {card.name}", key=f"sell_{idx}"):
            sell_card(game, card)
            st.success(f"Sold {card.name} for ${card.base_value:.2f}")
else:
    st.write("You don't own any cards yet. Open some chests!")

# -----------------------------
# All-Time Stats Tab
# -----------------------------
st.header("📊 All-Time Stats")
st.write(f"Total Money Made: ${game.total_money_made:.2f}")
st.write(f"Total Money from Clicks: ${game.total_money_clicked:.2f}")
st.write(f"Total Clicks: {game.total_clicks}")
st.write(f"Total Chests Opened: {game.total_chests_opened}")
st.write(f"Total Cards Collected: {game.total_cards_collected}")
st.write(f"Total Cards Sold: {game.total_cards_sold}")

# -----------------------------
# Available Cards Tab
# -----------------------------
st.header("🃏 Available Cards")
available = available_cards(game)
for card in available:
    st.write(f"{card.rarity} {card.name} - Potential Sell Value: ${card.base_value:.2f}")

# -----------------------------
# Ranked System Tab
# -----------------------------
st.header("🎖️ Ranked System")
arena_rewards = {
    1: 0, 2: 500, 3: 1000, 4: 2000, 5: 4000, 6: 7000, 7: 10000, 8: 13000, 9: 20000, 10: 50000,
    11: 70000, 12: 90000, 13: 110000, 14: 125000, 15: 180000, 16: 225000, 17: 260000, 18: 290000,
    19: 350000, 20: 500000, 21: 700000, 22: 850000, 23: 900000, 24: 1000000, 25: 3000000
}

for arena in ARENAS:
    unlocked = "✅" if game.arena_level >= arena.level else "❌"
    reward = arena_rewards.get(arena.level, 0)
    st.write(f"Arena {arena.level}: {arena.name} - Unlock: ${arena.unlock_condition.get('money', 0)} - Reward: ${reward} {unlocked}")

# -----------------------------
# Save & Load Game
# -----------------------------
st.header("💾 Save / Load Game")

if st.button("Save Game"):
    game.save()
    st.success("Game saved successfully!")

if st.button("Load Game"):
    game.load()
    st.success("Game loaded successfully!")

# Auto-save on every interaction
game.save()

st.write("Your progress is automatically saved with every action.")

# -----------------------------
# Passive Income Display & Automation
# -----------------------------
st.sidebar.header("💸 Earnings")

# Apply passive income continuously
def update_passive_income():
    game.apply_passive_income()
    st.sidebar.write(f"Money Per Second: ${game.money_per_second:.2f}")
    st.sidebar.write(f"Money Per Click: ${game.money_per_click:.2f}")
    st.sidebar.write(f"Total Money: ${game.money:.2f}")

# Run passive income updater every 1 second (approx)
st_autorefresh = st.experimental_rerun
update_passive_income()

# -----------------------------
# Dynamic Chest Unlocks by Arena
# -----------------------------
st.header("🏰 Chest Store (Updated)")

def get_unlocked_chests(game: GameState):
    unlocked = []
    for arena in ARENAS:
        if game.arena_level >= arena.level:
            unlocked.extend(arena.chest_unlocks)
    # Add guaranteed Legendary/Champion cards if arena requirements met
    if game.arena_level >= 15 and "Guaranteed Legendary" not in unlocked:
        unlocked.append("Guaranteed Legendary")
    if game.arena_level >= 20 and "Guaranteed Champion" not in unlocked:
        unlocked.append("Guaranteed Champion")
    return [c for c in CHESTS if c.name in unlocked]

chests = get_unlocked_chests(game)

for chest in chests:
    st.subheader(f"{chest.name} - Cost: ${chest.cost}")
    st.write("Rarity Chances:")
    for r, pct in chest.rarity_weights.items():
        st.write(f"- {r}: {pct}%")
    if st.button(f"Open {chest.name}", key=f"store_{chest.name}"):
        pulled_card, msg = chest.open(game)
        st.session_state.message = msg
        st.success(msg)

# Handle special guaranteed chests
if game.arena_level >= 15:
    if st.button("Open Guaranteed Legendary", key="guar_legendary"):
        legendary_cards = [c for c in CARD_POOL if c.rarity == "Legendary"]
        pulled = random.choice(legendary_cards)
        game.owned_cards.append(pulled)
        game.total_cards_collected += 1
        st.success(f"🎉 You pulled a guaranteed Legendary card: {pulled.name}!")

if game.arena_level >= 20:
    if st.button("Open Guaranteed Champion", key="guar_champion"):
        champion_cards = [c for c in CARD_POOL if c.rarity == "Champion"]
        pulled = random.choice(champion_cards)
        game.owned_cards.append(pulled)
        game.total_cards_collected += 1
        st.success(f"🏆 You pulled a guaranteed Champion card: {pulled.name}!")

# -----------------------------
# Card Sell Values by Rarity
# -----------------------------
RARITY_SELL_RANGES = {
    "Common": (0.58, 8.76),
    "Rare": (8.77, 28.95),
    "Epic": (28.96, 89.54),
    "Legendary": (89.55, 487.88),
    "Champion": (487.89, 6788.43)
}

def get_random_card_value(rarity):
    """Return a randomized sell value for a card based on rarity."""
    min_val, max_val = RARITY_SELL_RANGES[rarity]
    # Weighted random: lower values more common
    value = random.triangular(min_val, max_val, min_val)
    return round(value, 2)

# Update CARD_POOL base values dynamically
for card in CARD_POOL:
    card.base_value = get_random_card_value(card.rarity)

# -----------------------------
# Collection Tab / Sell Cards
# -----------------------------
st.header("📦 Your Card Collection")

if game.owned_cards:
    for idx, card in enumerate(game.owned_cards):
        st.write(f"{card.rarity} {card.name} - Sell Value: ${card.base_value:.2f}")
        if st.button(f"Sell {card.name}", key=f"sell_{idx}"):
            game.money += card.base_value
            game.owned_cards.pop(idx)
            game.total_cards_sold += 1
            st.success(f"Sold {card.name} for ${card.base_value:.2f}")

else:
    st.write("You don't own any cards yet. Open some chests!")

# -----------------------------
# Update All-Time Stats
# -----------------------------
st.header("📊 All-Time Stats")
st.write(f"Total Money Made: ${game.total_money_made:.2f}")
st.write(f"Total Money from Clicks: ${game.total_money_clicked:.2f}")
st.write(f"Total Clicks: {game.total_clicks}")
st.write(f"Total Chests Opened: {game.total_chests_opened}")
st.write(f"Total Cards Collected: {game.total_cards_collected}")
st.write(f"Total Cards Sold: {game.total_cards_sold}")

# -----------------------------
# Ranked System / Arenas
# -----------------------------
st.header("🎖️ Ranked System")

# Arena rewards mapping
ARENA_REWARDS = {
    1: 0, 2: 500, 3: 1000, 4: 2000, 5: 4000, 6: 7000, 7: 10000, 8: 13000, 9: 20000, 10: 50000,
    11: 70000, 12: 90000, 13: 110000, 14: 125000, 15: 180000, 16: 225000, 17: 260000, 18: 290000,
    19: 350000, 20: 500000, 21: 700000, 22: 850000, 23: 900000, 24: 1000000, 25: 3000000
}

def check_arena_progression(game: GameState):
    msg = None
    for arena in ARENAS:
        if game.arena_level < arena.level:
            required_money = arena.unlock_condition.get("money", 0)
            if game.total_money_made >= required_money:
                game.arena_level = arena.level
                reward = ARENA_REWARDS.get(arena.level, 0)
                game.money += reward
                msg = f"🎉 You unlocked {arena.name}! You received ${reward} as arena reward."
                break
    return msg

# Check for arena unlock on each run
arena_message = check_arena_progression(game)
if arena_message:
    st.balloons()
    st.success(arena_message)

# Display all arenas and progress
st.subheader("Arena Progression")
for arena in ARENAS:
    unlocked = "✅" if game.arena_level >= arena.level else "❌"
    required_money = arena.unlock_condition.get("money", 0)
    reward = ARENA_REWARDS.get(arena.level, 0)
    st.write(f"Arena {arena.level}: {arena.name} | Unlock Req: ${required_money} | Reward: ${reward} {unlocked}")

# -----------------------------
# Save / Load Game
# -----------------------------
st.header("💾 Save / Load Game")

SAVE_FILE = "save.json"

if st.button("Save Game"):
    game.save(SAVE_FILE)
    st.success("Game saved successfully!")

if st.button("Load Game"):
    game.load(SAVE_FILE)
    st.success("Game loaded successfully!")

# Auto-save on every interaction
game.save(SAVE_FILE)
st.write("Your progress is automatically saved with every action.")

# -----------------------------
# Advanced Chest System with Arena Unlocks
# -----------------------------
CHESTS = [
    Chest("Wooden Chest", 15, {"Common": 85, "Rare": 15, "Epic": 0, "Legendary": 0}),
    Chest("Silver Chest", 75, {"Common": 75, "Rare": 15, "Epic": 10, "Legendary": 0}),
    Chest("Golden Chest", 150, {"Common": 70, "Rare": 17, "Epic": 11, "Legendary": 2}),
    Chest("Magical Chest", 750, {"Common": 62, "Rare": 19, "Epic": 13, "Legendary": 4, "Champion": 2}),
    Chest("Kings Chest", 2700, {"Common": 51, "Rare": 22, "Epic": 15, "Legendary": 8, "Champion": 4}),
    Chest("Legendary Chest", 8500, {"Common": 40, "Rare": 27, "Epic": 18, "Legendary": 9, "Champion": 6}),
    Chest("Champion Chest", 15000, {"Common": 30, "Rare": 31, "Epic": 20, "Legendary": 11, "Champion": 8}),
    Chest("Universal Chest", 35000, {"Common": 20, "Rare": 33, "Epic": 24, "Legendary": 13, "Champion": 10}),
    Chest("Guaranteed Legendary", 0, {"Legendary": 100}),  # Unlocks at Arena 15
    Chest("Guaranteed Champion", 0, {"Champion": 100}),    # Unlocks at Arena 20
]

# Update function for filtering chests based on arena unlocks
def available_chests(game: GameState):
    unlocked = []
    for chest in CHESTS:
        if chest.name == "Wooden Chest" and game.arena_level >= 1:
            unlocked.append(chest)
        elif chest.name == "Silver Chest" and game.arena_level >= 2:
            unlocked.append(chest)
        elif chest.name == "Golden Chest" and game.arena_level >= 3:
            unlocked.append(chest)
        elif chest.name == "Magical Chest" and game.arena_level >= 5:
            unlocked.append(chest)
        elif chest.name == "Kings Chest" and game.arena_level >= 6:
            unlocked.append(chest)
        elif chest.name == "Legendary Chest" and game.arena_level >= 8:
            unlocked.append(chest)
        elif chest.name == "Champion Chest" and game.arena_level >= 9:
            unlocked.append(chest)
        elif chest.name == "Universal Chest" and game.arena_level >= 12:
            unlocked.append(chest)
        elif chest.name == "Guaranteed Legendary" and game.arena_level >= 15:
            unlocked.append(chest)
        elif chest.name == "Guaranteed Champion" and game.arena_level >= 20:
            unlocked.append(chest)
    return unlocked

import random

class Card:
    def __init__(self, name, rarity, base_value):
        self.name = name
        self.rarity = rarity
        self.base_value = base_value

def random_value(rarity):
    ranges = {
        "Common": (0.58, 8.76),
        "Rare": (8.77, 28.95),
        "Epic": (28.96, 89.54),
        "Legendary": (89.55, 487.88),
        "Champion": (487.89, 6788.43)
    }
    return round(random.uniform(*ranges[rarity]), 2)

CARD_POOL = [
    # ---------- Commons (50 cards) ----------
    Card("Knight", "Common", random_value("Common")),
    Card("Archers", "Common", random_value("Common")),
    Card("Bomber", "Common", random_value("Common")),
    Card("Skeletons", "Common", random_value("Common")),
    Card("Fire Spirits", "Common", random_value("Common")),
    Card("Goblins", "Common", random_value("Common")),
    Card("Ice Spirit", "Common", random_value("Common")),
    Card("Zap", "Common", random_value("Common")),
    Card("Arrows", "Common", random_value("Common")),
    Card("Cannon", "Common", random_value("Common")),
    Card("Spear Goblins", "Common", random_value("Common")),
    Card("Bats", "Common", random_value("Common")),
    Card("Rascals", "Common", random_value("Common")),
    Card("Barbarians", "Common", random_value("Common")),
    Card("Firecracker", "Common", random_value("Common")),
    Card("Royal Delivery", "Common", random_value("Common")),
    Card("Skeleton Barrel", "Common", random_value("Common")),
    Card("Ice Golem", "Common", random_value("Common")),
    Card("Knight's Shield", "Common", random_value("Common")),
    Card("Dart Goblin", "Common", random_value("Common")),
    Card("Electro Spirit", "Common", random_value("Common")),
    Card("Goblin Cage", "Common", random_value("Common")),
    Card("Heal Spirit", "Common", random_value("Common")),
    Card("Wall Breakers", "Common", random_value("Common")),
    Card("Royal Ghost", "Common", random_value("Common")),
    Card("Magic Archer", "Common", random_value("Common")),
    Card("Ranged Goblins", "Common", random_value("Common")),
    Card("Battle Healer", "Common", random_value("Common")),
    Card("Skeleton King Minions", "Common", random_value("Common")),
    Card("Royal Hogs", "Common", random_value("Common")),
    Card("Fisherman", "Common", random_value("Common")),
    Card("Goblin Drill", "Common", random_value("Common")),
    Card("Fire Spirit Trio", "Common", random_value("Common")),
    Card("Barbarian Barrel", "Common", random_value("Common")),
    Card("Minerlings", "Common", random_value("Common")),
    Card("Sparky Skeleton", "Common", random_value("Common")),
    Card("Cursed Goblins", "Common", random_value("Common")),
    Card("Skeleton Parade", "Common", random_value("Common")),
    Card("Rage Spirits", "Common", random_value("Common")),
    Card("Goblin Gang", "Common", random_value("Common")),
    Card("Ice Spirits", "Common", random_value("Common")),
    Card("Zappies", "Common", random_value("Common")),
    Card("Elixir Golem", "Common", random_value("Common")),
    Card("Prince’s Shield", "Common", random_value("Common")),
    Card("Battle Ram", "Common", random_value("Common")),
    Card("Goblin Barrel Minions", "Common", random_value("Common")),
    Card("Royal Skeletons", "Common", random_value("Common")),
    Card("Spear Goblin Trio", "Common", random_value("Common")),
    Card("Ice Spirit Duo", "Common", random_value("Common")),

    # ---------- Rares (35 cards) ----------
    Card("Musketeer", "Rare", random_value("Rare")),
    Card("Mini P.E.K.K.A", "Rare", random_value("Rare")),
    Card("Hog Rider", "Rare", random_value("Rare")),
    Card("Fireball", "Rare", random_value("Rare")),
    Card("Valkyrie", "Rare", random_value("Rare")),
    Card("Inferno Tower", "Rare", random_value("Rare")),
    Card("Wizard", "Rare", random_value("Rare")),
    Card("Rocket", "Rare", random_value("Rare")),
    Card("Cannon Cart", "Rare", random_value("Rare")),
    Card("Tesla", "Rare", random_value("Rare")),
    Card("Knight Rider", "Rare", random_value("Rare")),
    Card("Bomb Tower", "Rare", random_value("Rare")),
    Card("Elixir Collector", "Rare", random_value("Rare")),
    Card("Flying Machine", "Rare", random_value("Rare")),
    Card("Hunter", "Rare", random_value("Rare")),
    Card("Barbarian Hut", "Rare", random_value("Rare")),
    Card("Royal Recruits", "Rare", random_value("Rare")),
    Card("Mortar", "Rare", random_value("Rare")),
    Card("Tesla Coil", "Rare", random_value("Rare")),
    Card("Goblin Hut", "Rare", random_value("Rare")),
    Card("Bomb Minion", "Rare", random_value("Rare")),
    Card("Zappies Tower", "Rare", random_value("Rare")),
    Card("Ice Wizard", "Rare", random_value("Rare")),
    Card("Flying Archer", "Rare", random_value("Rare")),
    Card("Spear Goblin Squad", "Rare", random_value("Rare")),
    Card("Ranged Wizard", "Rare", random_value("Rare")),
    Card("Royal Hogs Squad", "Rare", random_value("Rare")),
    Card("Battle Healer Squad", "Rare", random_value("Rare")),
    Card("Goblin Drill Team", "Rare", random_value("Rare")),
    Card("Magic Archer Squad", "Rare", random_value("Rare")),
    Card("Fisherman Squad", "Rare", random_value("Rare")),
    Card("Wall Breakers Squad", "Rare", random_value("Rare")),

    # ---------- Epics (20 cards) ----------
    Card("Baby Dragon", "Epic", random_value("Epic")),
    Card("Prince", "Epic", random_value("Epic")),
    Card("Witch", "Epic", random_value("Epic")),
    Card("Giant Skeleton", "Epic", random_value("Epic")),
    Card("Balloon", "Epic", random_value("Epic")),
    Card("Freeze", "Epic", random_value("Epic")),
    Card("Golem", "Epic", random_value("Epic")),
    Card("Skeleton Army", "Epic", random_value("Epic")),
    Card("Lightning", "Epic", random_value("Epic")),
    Card("Goblin Giant", "Epic", random_value("Epic")),
    Card("Royal Giant", "Epic", random_value("Epic")),
    Card("Prince Trio", "Epic", random_value("Epic")),
    Card("Executioner", "Epic", random_value("Epic")),
    Card("Night Witch", "Epic", random_value("Epic")),
    Card("Elixir Golem", "Epic", random_value("Epic")),
    Card("Dark Prince", "Epic", random_value("Epic")),
    Card("Magic Archer", "Epic", random_value("Epic")),
    Card("Electro Dragon", "Epic", random_value("Epic")),
    Card("Skeleton Dragons", "Epic", random_value("Epic")),

    # ---------- Legendaries (10 cards) ----------
    Card("Sparky", "Legendary", random_value("Legendary")),
    Card("Electro Wizard", "Legendary", random_value("Legendary")),
    Card("Mega Knight", "Legendary", random_value("Legendary")),
    Card("Miner", "Legendary", random_value("Legendary")),
    Card("Princess", "Legendary", random_value("Legendary")),
    Card("Log", "Legendary", random_value("Legendary")),
    Card("Lumberjack", "Legendary", random_value("Legendary")),
    Card("Magic Archer", "Legendary", random_value("Legendary")),
    Card("Graveyard", "Legendary", random_value("Legendary")),
    Card("Night Witch", "Legendary", random_value("Legendary")),

    # ---------- Champions (5 cards) ----------
    Card("Golden Knight", "Champion", random_value("Champion")),
    Card("Archer Queen", "Champion", random_value("Champion")),
    Card("Skeleton King", "Champion", random_value("Champion")),
    Card("Mighty Miner", "Champion", random_value("Champion")),
    Card("Royal Champion", "Champion", random_value("Champion")),
]

# -----------------------------
# Chest System with Champions
# -----------------------------
class Chest:
    def __init__(self, name, cost, rarity_weights):
        self.name = name
        self.cost = cost
        self.rarity_weights = rarity_weights  # Dict: {"Common": %, "Rare": %, "Epic": %, "Legendary": %, "Champion": %}

    def open(self, game: GameState):
        if game.money < self.cost:
            return None, "Not enough money!"
        game.money -= self.cost
        game.total_chests_opened += 1

        # Choose rarity
        rarity = random.choices(
            population=list(self.rarity_weights.keys()),
            weights=list(self.rarity_weights.values()),
            k=1
        )[0]

        # Filter cards by rarity
        candidates = [c for c in CARD_POOL if c.rarity == rarity]
        pulled = random.choice(candidates)

        # Add to collection
        game.owned_cards.append(pulled)
        game.total_cards_collected += 1

        return pulled, f"You pulled a {rarity} card: {pulled.name}!"


# Define chest types with Champion rarity
CHESTS = [
    Chest("Wooden Chest", 15, {"Common": 85, "Rare": 15, "Epic": 0, "Legendary": 0, "Champion": 0}),
    Chest("Silver Chest", 75, {"Common": 75, "Rare": 15, "Epic": 10, "Legendary": 0, "Champion": 0}),
    Chest("Gold Chest", 150, {"Common": 70, "Rare": 17, "Epic": 11, "Legendary": 2, "Champion": 0}),
    Chest("Magical Chest", 750, {"Common": 62, "Rare": 19, "Epic": 13, "Legendary": 4, "Champion": 2}),
    Chest("Kings Chest", 2700, {"Common": 51, "Rare": 22, "Epic": 15, "Legendary": 8, "Champion": 4}),
    Chest("Legendary Chest", 8500, {"Common": 40, "Rare": 27, "Epic": 18, "Legendary": 9, "Champion": 6}),
    Chest("Champion Chest", 15000, {"Common": 30, "Rare": 31, "Epic": 20, "Legendary": 11, "Champion": 8}),
    Chest("Universal Chest", 35000, {"Common": 20, "Rare": 33, "Epic": 24, "Legendary": 13, "Champion": 10}),
]

# -----------------------------
# Arena-Based Chest Display
# -----------------------------
st.header("🏰 Available Chests by Arena")
chests = available_chests(game)
for chest in chests:
    st.subheader(f"{chest.name} - Cost: ${chest.cost}")
    st.write("Rarity Chances:")
    for rarity, pct in chest.rarity_weights.items():
        st.write(f"- {rarity}: {pct}%")
    if st.button(f"Open {chest.name}", key=f"arena_{chest.name}"):
        pulled_card, msg = chest.open(game)
        st.session_state.message = msg
        st.success(msg)

# -----------------------------
# Auto-Updating Card Collection
# -----------------------------
st.header("📦 Card Collection (Sell Cards)")
if game.owned_cards:
    for idx, card in enumerate(game.owned_cards):
        st.write(f"{card.rarity} {card.name} - Sell Value: ${card.base_value:.2f}")
        if st.button(f"Sell {card.name}", key=f"collection_sell_{idx}"):
            game.money += card.base_value
            game.owned_cards.pop(idx)
            game.total_cards_sold += 1
            st.success(f"Sold {card.name} for ${card.base_value:.2f}")
else:
    st.write("You haven't opened any chests yet!")

# -----------------------------
# Helper Function: Display Stats Sidebar
# -----------------------------
def display_sidebar_stats(game: GameState):
    st.sidebar.header("💸 Game Stats")
    st.sidebar.write(f"Money: ${game.money:.2f}")
    st.sidebar.write(f"Money per Click: ${game.money_per_click:.2f}")
    st.sidebar.write(f"Money per Second: ${game.money_per_second:.2f}")
    st.sidebar.write(f"Total Clicks: {game.total_clicks}")
    st.sidebar.write(f"Total Chests Opened: {game.total_chests_opened}")
    st.sidebar.write(f"Total Cards Collected: {game.total_cards_collected}")
    st.sidebar.write(f"Total Cards Sold: {game.total_cards_sold}")
    st.sidebar.write(f"Arena Level: {game.arena_level}")

display_sidebar_stats(game)

# -----------------------------
# Auto-Save on Each Interaction
# -----------------------------
SAVE_FILE = "save.json"
game.save(SAVE_FILE)

# -----------------------------
# -----------------------------
# ADVANCED GAMEPLAY ENHANCEMENTS
# -----------------------------
# -----------------------------

import threading
import datetime

# -----------------------------
# Achievements System
# -----------------------------
ACHIEVEMENTS = [
    {"name": "First Click", "condition": lambda g: g.total_clicks >= 1, "reward": 50, "unlocked": False},
    {"name": "Chest Collector I", "condition": lambda g: g.total_chests_opened >= 10, "reward": 500, "unlocked": False},
    {"name": "Chest Collector II", "condition": lambda g: g.total_chests_opened >= 50, "reward": 5000, "unlocked": False},
    {"name": "Millionaire", "condition": lambda g: g.total_money_made >= 1_000_000, "reward": 100_000, "unlocked": False},
    {"name": "Card Hoarder I", "condition": lambda g: g.total_cards_collected >= 50, "reward": 2000, "unlocked": False},
    {"name": "Card Hoarder II", "condition": lambda g: g.total_cards_collected >= 200, "reward": 10_000, "unlocked": False},
]

def check_achievements(game: GameState):
    messages = []
    for ach in ACHIEVEMENTS:
        if not ach["unlocked"] and ach["condition"](game):
            ach["unlocked"] = True
            game.money += ach["reward"]
            messages.append(f"🏆 Achievement unlocked: {ach['name']}! Reward: ${ach['reward']}")
    return messages

# -----------------------------
# Click Multiplier System
# -----------------------------
class ClickBoost:
    def __init__(self):
        self.active = False
        self.multiplier = 1.0
        self.end_time = None

    def activate(self, multiplier, duration_seconds):
        self.active = True
        self.multiplier = multiplier
        self.end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration_seconds)

    def update(self):
        if self.active and datetime.datetime.now() >= self.end_time:
            self.active = False
            self.multiplier = 1.0

click_boost = ClickBoost()

def boosted_click(game: GameState):
    click_boost.update()
    game.click()
    earned = game.money_per_click * click_boost.multiplier
    game.money += earned - game.money_per_click  # Add extra from multiplier
    game.total_money_made += earned - game.money_per_click
    return earned

# -----------------------------
# Event Chests System
# -----------------------------
EVENT_CHESTS = [
    Chest("Halloween Chest", 2000, {"Common": 30, "Rare": 30, "Epic": 25, "Legendary": 10, "Champion": 5}),
    Chest("Christmas Chest", 3000, {"Common": 20, "Rare": 25, "Epic": 30, "Legendary": 15, "Champion": 10}),
]

def available_event_chests():
    today = datetime.datetime.now()
    chests = []
    if today.month == 10:
        chests.append(EVENT_CHESTS[0])
    if today.month == 12:
        chests.append(EVENT_CHESTS[1])
    return chests

# -----------------------------
# Passive Income Auto-Thread
# -----------------------------
def passive_income_thread(game: GameState, interval=1):
    while True:
        game.apply_passive_income()
        messages = check_achievements(game)
        for msg in messages:
            st.session_state.message = msg
        time.sleep(interval)

# Run passive income in separate thread
threading.Thread(target=passive_income_thread, args=(game,), daemon=True).start()

# -----------------------------
# Timed Boosts Display & Activation
# -----------------------------
st.sidebar.header("⚡ Temporary Boosts")
if click_boost.active:
    remaining = (click_boost.end_time - datetime.datetime.now()).seconds
    st.sidebar.success(f"Click Boost Active! x{click_boost.multiplier} ({remaining}s left)")
else:
    if st.sidebar.button("Activate 2x Click Boost (30s) - $5000"):
        if game.money >= 5000:
            game.money -= 5000
            click_boost.activate(2.0, 30)
            st.sidebar.success("Click Boost Activated!")
        else:
            st.sidebar.error("Not enough money!")

# -----------------------------
# Auto-Refresh Stats Sidebar
# -----------------------------
def display_dynamic_sidebar(game: GameState):
    st.sidebar.header("💰 Player Stats")
    st.sidebar.write(f"Money: ${game.money:.2f}")
    st.sidebar.write(f"Money per Click: ${game.money_per_click:.2f} x{click_boost.multiplier}")
    st.sidebar.write(f"Money per Second: ${game.money_per_second:.2f}")
    st.sidebar.write(f"Total Clicks: {game.total_clicks}")
    st.sidebar.write(f"Total Chests Opened: {game.total_chests_opened}")
    st.sidebar.write(f"Total Cards Collected: {game.total_cards_collected}")
    st.sidebar.write(f"Total Cards Sold: {game.total_cards_sold}")
    st.sidebar.write(f"Arena Level: {game.arena_level}")

display_dynamic_sidebar(game)

# -----------------------------
# Event Chest Store Tab
# -----------------------------
st.header("🎉 Event Chests")
event_chests = available_event_chests()
if event_chests:
    for chest in event_chests:
        st.subheader(f"{chest.name} - Cost: ${chest.cost}")
        st.write("Rarity Chances:")
        for rarity, pct in chest.rarity_weights.items():
            st.write(f"- {rarity}: {pct}%")
        if st.button(f"Open {chest.name}", key=f"event_{chest.name}"):
            pulled_card, msg = chest.open(game)
            st.session_state.message = msg
            st.success(msg)
else:
    st.write("No special event chests available currently.")

# -----------------------------
# Boosted Click Button
# -----------------------------
st.header("💥 Click Chest!")
if st.button("Click Chest!"):
    earned = boosted_click(game)
    st.session_state.message = f"You earned ${earned:.2f}!"

if st.session_state.message:
    st.info(st.session_state.message)

# -----------------------------
# Timed Auto-Save
# -----------------------------
def autosave_loop(game: GameState, interval=15):
    while True:
        game.save(SAVE_FILE)
        time.sleep(interval)

threading.Thread(target=autosave_loop, args=(game,), daemon=True).start()

# -----------------------------
# Daily Login Reward
# -----------------------------
if "last_daily" not in st.session_state:
    st.session_state.last_daily = None

today = datetime.datetime.today().date()
if st.session_state.last_daily != today:
    st.session_state.last_daily = today
    reward = 100 + random.randint(0, 200)
    game.money += reward
    st.success(f"🎁 Daily Login Reward: ${reward}")

# -----------------------------
# Notification Area
# -----------------------------
st.sidebar.header("📣 Notifications")
if st.session_state.message:
    st.sidebar.info(st.session_state.message)

# -----------------------------
# Arena Unlock Rewards
# -----------------------------
arena_msg = check_arena_progression(game)
if arena_msg:
    st.balloons()
    st.success(arena_msg)

# -----------------------------
# Mega Stats Dashboard (Charts)
# -----------------------------
st.header("📊 Money Over Time")
import pandas as pd
import matplotlib.pyplot as plt

if "money_history" not in st.session_state:
    st.session_state.money_history = []

st.session_state.money_history.append({"time": datetime.datetime.now(), "money": game.money})
history_df = pd.DataFrame(st.session_state.money_history)
fig, ax = plt.subplots()
ax.plot(history_df["time"], history_df["money"], color="gold")
ax.set_xlabel("Time")
ax.set_ylabel("Money")
ax.set_title("Money Growth Over Time")
st.pyplot(fig)

# -----------------------------
# -----------------------------
# ADVANCED UPGRADE TREE & CARD MECHANICS
# -----------------------------
# -----------------------------

# -----------------------------
# Upgrade Tree Nodes
# -----------------------------
class UpgradeNode:
    def __init__(self, name, cost, effect_type, effect_value, dependencies=[]):
        self.name = name
        self.cost = cost
        self.effect_type = effect_type  # "click" or "passive" or "card"
        self.effect_value = effect_value
        self.dependencies = dependencies
        self.unlocked = False

    def can_unlock(self, game: GameState):
        return all(dep in game.upgrades_purchased for dep in self.dependencies)

    def apply(self, game: GameState):
        if self.effect_type == "click":
            game.money_per_click += self.effect_value
        elif self.effect_type == "passive":
            game.money_per_second += self.effect_value
        elif self.effect_type == "card":
            # Apply card bonus
            for card in game.owned_cards:
                if card.rarity == "Champion":
                    card.base_value += self.effect_value
        self.unlocked = True
        game.upgrades_purchased.append(self.name)

# Example upgrade tree
UPGRADE_TREE = [
    UpgradeNode("Click Mastery I", 5000, "click", 2.0),
    UpgradeNode("Passive Mastery I", 7000, "passive", 5.0),
    UpgradeNode("Champion Empower I", 15000, "card", 50, dependencies=["Click Mastery I"]),
    UpgradeNode("Click Mastery II", 25000, "click", 5.0, dependencies=["Click Mastery I"]),
    UpgradeNode("Passive Mastery II", 30000, "passive", 10.0, dependencies=["Passive Mastery I"]),
    UpgradeNode("Champion Empower II", 50000, "card", 150, dependencies=["Champion Empower I"]),
]

def display_upgrade_tree(game: GameState):
    st.header("🌳 Upgrade Tree")
    for node in UPGRADE_TREE:
        status = "✅ Unlocked" if node.name in game.upgrades_purchased else "🔒 Locked"
        can_unlock = node.can_unlock(game) and node.name not in game.upgrades_purchased
        st.write(f"{node.name} - Cost: ${node.cost} | Effect: {node.effect_type} +{node.effect_value} | Status: {status}")
        if can_unlock:
            if st.button(f"Unlock {node.name}", key=f"upgrade_{node.name}"):
                if game.money >= node.cost:
                    game.money -= node.cost
                    node.apply(game)
                    st.success(f"Unlocked {node.name}!")
                else:
                    st.error("Not enough money!")

display_upgrade_tree(game)

# -----------------------------
# Champion Cards Active Abilities
# -----------------------------
class ChampionCardAbility:
    def __init__(self, card_name, ability_desc, cooldown_seconds, effect_func):
        self.card_name = card_name
        self.ability_desc = ability_desc
        self.cooldown_seconds = cooldown_seconds
        self.effect_func = effect_func
        self.last_used = datetime.datetime.min

    def can_use(self):
        return (datetime.datetime.now() - self.last_used).total_seconds() >= self.cooldown_seconds

    def use(self, game: GameState):
        if self.can_use():
            self.effect_func(game)
            self.last_used = datetime.datetime.now()
            return True
        return False

# Example champion abilities
def golden_knight_ability(game: GameState):
    game.money += 1000
    st.success("⚡ Golden Knight ability activated! +$1000")

def archer_queen_ability(game: GameState):
    game.money_per_click *= 2
    st.success("🎯 Archer Queen ability activated! Clicks x2 for 30s")
    click_boost.activate(2, 30)

CHAMPION_ABILITIES = [
    ChampionCardAbility("Golden Knight", "Instant $1000", 300, golden_knight_ability),
    ChampionCardAbility("Archer Queen", "Double Click Power 30s", 600, archer_queen_ability),
]

st.header("⚔️ Champion Abilities")
for ability in CHAMPION_ABILITIES:
    card_owned = any(c.name == ability.card_name for c in game.owned_cards)
    if card_owned:
        status = "✅ Ready" if ability.can_use() else "⏳ Cooldown"
        st.write(f"{ability.card_name}: {ability.ability_desc} | Status: {status}")
        if st.button(f"Use {ability.card_name}", key=f"ability_{ability.card_name}"):
            if ability.use(game):
                st.success(f"Used {ability.card_name} ability!")
            else:
                st.warning("Ability is on cooldown!")

# -----------------------------
# Card Fusion / Upgrade System
# -----------------------------
st.header("🛠️ Card Fusion")
def fuse_cards(game: GameState, card1: Card, card2: Card):
    if card1.rarity != card2.rarity:
        st.error("Cards must be same rarity to fuse!")
        return
    # Increase base value of first card by second card value * 1.5
    bonus = card2.base_value * 1.5
    card1.base_value += bonus
    game.owned_cards.remove(card2)
    st.success(f"Fused {card2.name} into {card1.name}! +${bonus:.2f} value")

if len(game.owned_cards) >= 2:
    card1_idx = st.selectbox("Select first card to fuse", range(len(game.owned_cards)))
    card2_idx = st.selectbox("Select second card to fuse", [i for i in range(len(game.owned_cards)) if i != card1_idx])
    if st.button("Fuse Cards"):
        fuse_cards(game, game.owned_cards[card1_idx], game.owned_cards[card2_idx])
else:
    st.write("Need at least 2 cards to fuse.")

# -----------------------------
# Chest Animation Simulation
# -----------------------------
st.header("🎁 Chest Animation")
selected_chest = st.selectbox("Select chest to open", available_chests(game))
if st.button("Animate Chest"):
    st.info(f"Opening {selected_chest.name}...")
    for i in range(5):
        st.write(f"Shuffling... {'.'*i}")
        time.sleep(0.3)
    pulled_card, msg = selected_chest.open(game)
    st.success(f"✨ Chest Opened! You got {pulled_card.rarity} {pulled_card.name}")

# -----------------------------
# Leaderboard (Simulated)
# -----------------------------
st.header("🏆 Leaderboard (Top 10 Richest Players)")
if "leaderboard" not in st.session_state:
    # Simulate leaderboard
    st.session_state.leaderboard = [{"name": f"Player{i}", "money": random.randint(1000, 1_000_000)} for i in range(1, 11)]
    # Include current player
    st.session_state.leaderboard.append({"name": "You", "money": game.money})
    st.session_state.leaderboard = sorted(st.session_state.leaderboard, key=lambda x: x["money"], reverse=True)[:10]

for idx, entry in enumerate(st.session_state.leaderboard):
    highlight = " (You)" if entry["name"] == "You" else ""
    st.write(f"{idx+1}. {entry['name']}: ${entry['money']:.2f}{highlight}")

# -----------------------------
# Daily & Weekly Challenges
# -----------------------------
st.header("🎯 Challenges")
if "challenges" not in st.session_state:
    st.session_state.challenges = [
        {"desc": "Open 5 chests today", "completed": False, "reward": 500},
        {"desc": "Earn $10,000 in clicks", "completed": False, "reward": 1000},
        {"desc": "Collect 10 new cards", "completed": False, "reward": 750},
    ]

for chal in st.session_state.challenges:
    if not chal["completed"]:
        if chal["desc"] == "Open 5 chests today" and game.total_chests_opened >= 5:
            chal["completed"] = True
            game.money += chal["reward"]
            st.success(f"Challenge Completed: {chal['desc']}! Reward: ${chal['reward']}")
        elif chal["desc"] == "Earn $10,000 in clicks" and game.total_money_clicked >= 10_000:
            chal["completed"] = True
            game.money += chal["reward"]
            st.success(f"Challenge Completed: {chal['desc']}! Reward: ${chal['reward']}")
        elif chal["desc"] == "Collect 10 new cards" and game.total_cards_collected >= 10:
            chal["completed"] = True
            game.money += chal["reward"]
            st.success(f"Challenge Completed: {chal['desc']}! Reward: ${chal['reward']}")
    status = "✅ Completed" if chal["completed"] else "❌ In Progress"
    st.write(f"{chal['desc']} | Status: {status} | Reward: ${chal['reward']}")

# -----------------------------
# Extra Visual Feedback
# -----------------------------
st.balloons() if random.random() < 0.01 else None  # Random occasional balloons for fun

# -----------------------------
# ADVANCED UPGRADE TREE & CARD MECHANICS (Continuation)
# -----------------------------

# Apply card bonuses for specific upgrades
class CardBonusUpgrade(UpgradeNode):
    def apply(self, game: GameState):
        for card in game.owned_cards:
            if card.rarity == "Champion":
                card.base_value += self.effect_value
        game.upgrades_purchased.append(self.name)
        self.unlocked = True

# Example Upgrade Tree
UPGRADE_TREE = [
    UpgradeNode("Click Master I", 5000, "click", 5),
    UpgradeNode("Passive Gold I", 10000, "passive", 10),
    CardBonusUpgrade("Champion Boost I", 15000, "card", 50, dependencies=["Click Master I"]),
    UpgradeNode("Click Master II", 25000, "click", 15, dependencies=["Click Master I"]),
    CardBonusUpgrade("Champion Boost II", 40000, "card", 100, dependencies=["Champion Boost I"]),
]

# Display Upgrade Tree in Sidebar
st.sidebar.header("🌳 Upgrade Tree")
for node in UPGRADE_TREE:
    status = "✅ Purchased" if node.name in game.upgrades_purchased else "🔒 Locked"
    can_unlock = node.can_unlock(game) and node.name not in game.upgrades_purchased
    st.sidebar.write(f"{node.name} - Cost: ${node.cost} - {status}")
    if can_unlock:
        if st.sidebar.button(f"Unlock {node.name}", key=f"tree_{node.name}"):
            if game.money >= node.cost:
                game.money -= node.cost
                node.apply(game)
                st.sidebar.success(f"Unlocked {node.name}!")
            else:
                st.sidebar.error("Not enough money to unlock!")

# -----------------------------
# Champion Card Enhancement Display
# -----------------------------
st.header("🏆 Champion Card Bonuses")
champion_cards = [c for c in game.owned_cards if c.rarity == "Champion"]
if champion_cards:
    for card in champion_cards:
        st.write(f"{card.name} - Boosted Sell Value: ${card.base_value:.2f}")
else:
    st.write("No Champion cards owned yet. Unlock upgrades to enhance them!")

# -----------------------------
# Card Synergy Effects (Optional)
# -----------------------------
# Example: Having multiple Champions increases passive income
def apply_champion_synergy(game: GameState):
    champions = [c for c in game.owned_cards if c.rarity == "Champion"]
    bonus_per_champion = 0.5  # extra money per second
    game.money_per_second += len(champions) * bonus_per_champion

apply_champion_synergy(game)

