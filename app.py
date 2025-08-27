import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from collections import defaultdict
from streamlit_autorefresh import st_autorefresh

# -------------------- AUTOREFRESH --------------------
st_autorefresh(interval=1000, key="refresh")

# -------------------- SESSION STATE INIT --------------------
if 'coins' not in st.session_state: st.session_state.coins = 0
if 'xp' not in st.session_state: st.session_state.xp = 0
if 'level' not in st.session_state: st.session_state.level = 1
if 'inventory' not in st.session_state: st.session_state.inventory = defaultdict(int)
if 'chests' not in st.session_state: st.session_state.chests = []
if 'last_passive' not in st.session_state: st.session_state.last_passive = datetime.now()
if 'cards' not in st.session_state:
    st.session_state.cards = [
        {"name":"Knight","atk":50,"hp":200,"rarity":"Common"},
        {"name":"Archer","atk":40,"hp":100,"rarity":"Common"},
        {"name":"Baby Dragon","atk":60,"hp":150,"rarity":"Rare"},
        {"name":"Wizard","atk":80,"hp":120,"rarity":"Rare"},
        {"name":"P.E.K.K.A","atk":150,"hp":500,"rarity":"Epic"},
        {"name":"Giant","atk":100,"hp":400,"rarity":"Rare"},
        {"name":"Mini P.E.K.K.A","atk":120,"hp":250,"rarity":"Rare"},
        {"name":"Hog Rider","atk":110,"hp":220,"rarity":"Epic"},
        {"name":"Valkyrie","atk":70,"hp":300,"rarity":"Rare"},
        {"name":"Musketeer","atk":90,"hp":180,"rarity":"Rare"},
        {"name":"Bomber","atk":60,"hp":100,"rarity":"Common"},
        {"name":"Skeleton Army","atk":10,"hp":30,"rarity":"Common"},
        {"name":"Prince","atk":130,"hp":200,"rarity":"Epic"},
        {"name":"Dark Prince","atk":120,"hp":250,"rarity":"Epic"},
        {"name":"Spear Goblins","atk":30,"hp":60,"rarity":"Common"},
        {"name":"Goblin Barrel","atk":80,"hp":50,"rarity":"Epic"},
        {"name":"Witch","atk":50,"hp":150,"rarity":"Epic"},
        {"name":"Ice Wizard","atk":40,"hp":120,"rarity":"Epic"},
        {"name":"Electro Wizard","atk":50,"hp":130,"rarity":"Legendary"},
        {"name":"Golden Knight","atk":140,"hp":350,"rarity":"Legendary"},
        {"name":"Mega Minion","atk":100,"hp":150,"rarity":"Rare"},
        {"name":"Inferno Dragon","atk":200,"hp":220,"rarity":"Epic"},
        {"name":"Skeleton","atk":20,"hp":30,"rarity":"Common"},
        {"name":"Fire Spirits","atk":80,"hp":50,"rarity":"Common"},
        {"name":"Cannon","atk":50,"hp":300,"rarity":"Common"},
        {"name":"Tesla","atk":60,"hp":320,"rarity":"Rare"},
        {"name":"Bomb Tower","atk":70,"hp":400,"rarity":"Rare"},
        {"name":"Goblin Gang","atk":30,"hp":70,"rarity":"Common"},
        {"name":"Minions","atk":60,"hp":80,"rarity":"Common"},
        {"name":"Minion Horde","atk":40,"hp":30,"rarity":"Rare"}
    ]

# -------------------- UTILITY FUNCTIONS --------------------
def gain_passive():
    now = datetime.now()
    elapsed = (now - st.session_state.last_passive).total_seconds()
    if elapsed >= 1:
        st.session_state.coins += int(elapsed * st.session_state.level)
        st.session_state.xp += int(elapsed * 2)
        st.session_state.last_passive = now
        check_levelup()

def check_levelup():
    threshold = st.session_state.level * 100
    if st.session_state.xp >= threshold:
        st.session_state.level += 1
        st.session_state.xp -= threshold
        st.success(f"Level Up! Now Level {st.session_state.level}")

def add_chest(name, timer_seconds):
    st.session_state.chests.append({
        "name": name,
        "ready_time": datetime.now() + timedelta(seconds=timer_seconds),
        "opened": False
    })

def open_chest(chest):
    coins = random.randint(50,200) * st.session_state.level
    card = random.choice(st.session_state.cards)
    st.session_state.inventory[card['name']] += 1
    chest['opened'] = True
    st.session_state.coins += coins
    st.success(f"Opened {chest['name']}! +{coins} coins, gained {card['name']} card")

def ready_chests():
    return [c for c in st.session_state.chests if not c['opened'] and datetime.now() >= c['ready_time']]

def click_for_coins():
    gain = 10 * st.session_state.level
    st.session_state.coins += gain
    st.session_state.xp += 5
    st.success(f"Gained {gain} coins and 5 XP!")
    check_levelup()

def daily_reward():
    coins_reward = random.randint(100,500) * st.session_state.level
    st.session_state.coins += coins_reward
    st.success(f"Daily Reward! +{coins_reward} coins")

# -------------------- PASSIVE INCOME --------------------
gain_passive()

# -------------------- SIDEBAR --------------------
st.sidebar.header("Player Stats")
st.sidebar.write(f"Level: {st.session_state.level}")
st.sidebar.write(f"XP: {st.session_state.xp}/{st.session_state.level*100}")
st.sidebar.write(f"Coins: {st.session_state.coins}")

st.sidebar.header("Inventory")
for card, count in st.session_state.inventory.items():
    st.sidebar.write(f"{card}: {count}")

st.sidebar.header("Add Chests")
if st.sidebar.button("Silver Chest"):
    add_chest("Silver Chest", 10)
if st.sidebar.button("Gold Chest"):
    add_chest("Gold Chest", 20)
if st.sidebar.button("Epic Chest"):
    add_chest("Epic Chest", 40)
if st.sidebar.button("Legendary Chest"):
    add_chest("Legendary Chest", 60)

st.sidebar.header("Events")
if st.sidebar.button("Daily Reward"):
    daily_reward()

# -------------------- MAIN AREA --------------------
st.title("Clash Royale Case Clicker 🏰")

st.header("Cards")
st.dataframe(pd.DataFrame(st.session_state.cards))

st.header("Clicker")
if st.button("Click for Coins"):
    click_for_coins()

st.header("Chests Ready")
for chest in ready_chests():
    if st.button(f"Open {chest['name']}"):
        open_chest(chest)

st.header("Stats Charts")
stats_df = pd.DataFrame({
    "Metric":["Coins","XP","Level"],
    "Value":[st.session_state.coins, st.session_state.xp, st.session_state.level]
})
st.bar_chart(stats_df.set_index("Metric"))

inventory_df = pd.DataFrame({
    "Card": list(st.session_state.inventory.keys()),
    "Count": list(st.session_state.inventory.values())
})
if not inventory_df.empty:
    st.bar_chart(inventory_df.set_index("Card"))

st.write("Progress auto-refreshes every second! All coins, XP, and chest timers update in real-time.")
