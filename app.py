# -------------------- CORE GAME DATA --------------------

# Card rarities & value ranges
RARITY_VALUES = {
    "Common": (0.58, 8.76),
    "Rare": (8.77, 28.95),
    "Epic": (28.96, 89.54),
    "Legendary": (89.55, 487.88),
    "Champion": (487.89, 6788.43),
}

# Chest definitions
CHESTS = {
    "Wooden Chest": {
        "price": 15,
        "arena_req": 1,
        "chances": {"Common": 0.85, "Rare": 0.15}
    },
    "Silver Chest": {
        "price": 75,
        "arena_req": 2,
        "chances": {"Common": 0.75, "Rare": 0.15, "Epic": 0.10}
    },
    "Golden Chest": {
        "price": 150,
        "arena_req": 3,
        "chances": {"Common": 0.70, "Rare": 0.17, "Epic": 0.11, "Legendary": 0.02}
    },
    "Magical Chest": {
        "price": 750,
        "arena_req": 5,
        "chances": {"Common": 0.62, "Rare": 0.19, "Epic": 0.13, "Legendary": 0.04, "Champion": 0.02}
    },
    "Kings Chest": {
        "price": 2700,
        "arena_req": 6,
        "chances": {"Common": 0.51, "Rare": 0.22, "Epic": 0.15, "Legendary": 0.08, "Champion": 0.04}
    },
    "Legendary Chest": {
        "price": 8500,
        "arena_req": 8,
        "chances": {"Common": 0.40, "Rare": 0.27, "Epic": 0.18, "Legendary": 0.09, "Champion": 0.06}
    },
    "Champion Chest": {
        "price": 15000,
        "arena_req": 9,
        "chances": {"Common": 0.30, "Rare": 0.31, "Epic": 0.20, "Legendary": 0.11, "Champion": 0.08}
    },
    "Universal Chest": {
        "price": 35000,
        "arena_req": 12,
        "chances": {"Common": 0.20, "Rare": 0.33, "Epic": 0.24, "Legendary": 0.13, "Champion": 0.10}
    },
    "Guaranteed Legendary": {
        "price": None,  # one-time arena reward
        "arena_req": 15,
        "guaranteed": "Legendary"
    },
    "Guaranteed Champion": {
        "price": None,
        "arena_req": 20,
        "guaranteed": "Champion"
    }
}

# Upgrades (alternate between auto-clickers and MPC)
UPGRADES = [
    {"name": "Auto Clicker I", "type": "auto", "value": 0.5, "cost": 20},
    {"name": "MPC I", "type": "mpc", "value": 2, "cost": 1000},
    {"name": "Auto Clicker II", "type": "auto", "value": 1.5, "cost": 500},
    {"name": "MPC II", "type": "mpc", "value": 6, "cost": 5000},
    {"name": "Auto Clicker III", "type": "auto", "value": 5, "cost": 2500},
    {"name": "MPC III", "type": "mpc", "value": 9.5, "cost": 12500},
    {"name": "Gold Clicker I", "type": "auto", "value": 7, "cost": 8000},
    {"name": "MPC IV", "type": "mpc", "value": 15, "cost": 25000},
    {"name": "Gold Clicker II", "type": "auto", "value": 9.5, "cost": 20000},
    {"name": "MPC V", "type": "mpc", "value": 25, "cost": 65000},
    {"name": "Master Clicker I", "type": "auto", "value": 12, "cost": 50000},
    {"name": "MPC Master", "type": "mpc", "value": 50, "cost": 120000},
    {"name": "Master Clicker II", "type": "auto", "value": 15, "cost": 150000},
]

# Arena progression (requirements + rewards)
ARENAS = [
    {"arena": 1, "req": 0, "reward": 0},
    {"arena": 2, "req": 1000, "reward": 500},
    {"arena": 3, "req": 7000, "reward": 1000},
    {"arena": 4, "req": 15000, "reward": 2000},
    {"arena": 5, "req": 30000, "reward": 4000},
    {"arena": 6, "req": 50000, "reward": 7000},
    {"arena": 7, "req": 75000, "reward": 10000},
    {"arena": 8, "req": 110000, "reward": 13000},
    {"arena": 9, "req": 150000, "reward": 20000},
    {"arena": 10, "req": 200000, "reward": 50000},
    {"arena": 11, "req": 275000, "reward": 70000},
    {"arena": 12, "req": 400000, "reward": 90000},
    {"arena": 13, "req": 550000, "reward": 110000},
    {"arena": 14, "req": 750000, "reward": 125000},
    {"arena": 15, "req": 1000000, "reward": 180000},
    {"arena": 16, "req": 1300000, "reward": 225000},
    {"arena": 17, "req": 1700000, "reward": 260000},
    {"arena": 18, "req": 2200000, "reward": 290000},
    {"arena": 19, "req": 2800000, "reward": 350000},
    {"arena": 20, "req": 3500000, "reward": 500000},
    {"arena": 21, "req": 4300000, "reward": 700000},
    {"arena": 22, "req": 5200000, "reward": 850000},
    {"arena": 23, "req": 6200000, "reward": 900000},
    {"arena": 24, "req": 7300000, "reward": 1000000},
    {"arena": 25, "req": 10000000, "reward": 3000000},
]

# -------------------- BASE STATE --------------------
game_state = {
    "money": 0,
    "mpc": 1,  # money per click
    "mps": 0,  # money per second
    "upgrades_owned": [],
    "cards_owned": {},  # {"Card Name": {"rarity": "Epic", "value": 120.5, "count": 1}}
    "arena": 1,
    "total_money_made": 0,
    "total_clicked": 0,
    "total_chests_opened": 0,
    "total_cards_collected": 0,
    "total_cards_sold": 0,
}
