import streamlit as st
import pandas as pd
import random
import time
import json
from datetime import datetime, timedelta
import os

# -------------------- INITIAL DATA --------------------
CARD_POOL = [
    {"Name": "Knight", "AtkDmg": 50, "AtkSpd": 1.2, "Range": 1, "Rarity": "Common"},
    {"Name": "Archer", "AtkDmg": 35, "AtkSpd": 1.5, "Range": 5, "Rarity": "Common"},
    {"Name": "Baby Dragon", "AtkDmg": 70, "AtkSpd": 1.0, "Range": 3, "Rarity": "Rare"},
    {"Name": "Wizard", "AtkDmg": 90, "AtkSpd": 1.3, "Range": 4, "Rarity": "Epic"},
    {"Name": "P.E.K.K.A", "AtkDmg": 300, "AtkSpd": 0.8, "Range": 1, "Rarity": "Epic"},
    {"Name": "Giant", "AtkDmg": 200, "AtkSpd": 0.9, "Range": 1, "Rarity": "Rare"},
    {"Name": "Mini P.E.K.K.A", "AtkDmg": 150, "AtkSpd": 1.0, "Range": 1, "Rarity": "Rare"},
    {"Name": "Hog Rider", "AtkDmg": 180, "AtkSpd": 1.2, "Range": 1, "Rarity": "Epic"},
    {"Name": "Valkyrie", "AtkDmg": 130, "AtkSpd": 1.0, "Range": 1, "Rarity": "Rare"},
    {"Name": "Musketeer", "AtkDmg": 120, "AtkSpd": 1.3, "Range": 4, "Rarity": "Rare"}
]

UPGRADES = {
    "click": 1,
    "passive": 0,
    "multiplier": 1.0
}

ACHIEVEMENTS = []
PLAYER_STATS = {
    "gold": 0,
    "clicks": 0,
    "cards_collected": [],
    "chests_opened": 0
}
CHESTS = []
ARENAS = ["Training Camp", "Goblin Arena", "Bone Pit", "Barbarian Bowl"]
CURRENT_ARENA = 0

SAVE_FILE = "clash_clicker_save.json"

# -------------------- UTILITY FUNCTIONS --------------------

def save_game():
    data = {
        "player_stats": PLAYER_STATS,
        "upgrades": UPGRADES,
        "achievements": ACHIEVEMENTS,
        "chests": CHESTS,
        "current_arena": CURRENT_ARENA
    }
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load_game():
    global PLAYER_STATS, UPGRADES, ACHIEVEMENTS, CHESTS, CURRENT_ARENA
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            PLAYER_STATS = data.get("player_stats", PLAYER_STATS)
            UPGRADES = data.get("upgrades", UPGRADES)
            ACHIEVEMENTS = data.get("achievements", ACHIEVEMENTS)
            CHESTS = data.get("chests", CHESTS)
            CURRENT_ARENA = data.get("current_arena", CURRENT_ARENA)


def gain_gold(amount):
    PLAYER_STATS["gold"] += int(amount * UPGRADES["multiplier"])


def collect_card():
    card = random.choice(CARD_POOL)
    PLAYER_STATS["cards_collected"].append(card)
    return card


def open_chest():
    chest_content = []
    num_cards = random.randint(1, 3)
    for _ in range(num_cards):
        chest_content.append(collect_card())
    gold_reward = random.randint(50, 200)
    gain_gold(gold_reward)
    PLAYER_STATS["chests_opened"] += 1
    CHESTS.append({"cards": chest_content, "gold": gold_reward, "time": str(datetime.now())})
    return chest_content, gold_reward

# -------------------- STREAMLIT UI --------------------

st.set_page_config(page_title="Clash Clicker", layout="wide")
load_game()

st.title("⚔️ Clash Clicker")

menu = st.sidebar.selectbox("Menu", ["Main", "Cards", "Chests", "Upgrades", "Achievements", "Stats"])

if menu == "Main":
    st.header("🏰 Main Arena")
    st.subheader(f"Current Arena: {ARENAS[CURRENT_ARENA]}")

    if st.button("Click for Gold!"):
        gain_gold(1 + UPGRADES["click"])
        PLAYER_STATS["clicks"] += 1
        st.success(f"You gained {int(1 + UPGRADES['click']*UPGRADES['multiplier'])} gold!")

    if st.button("Open a Chest"):
        cards, gold = open_chest()
        st.success(f"Chest opened! Gold: {gold}, Cards: {[c['Name'] for c in cards]}")

elif menu == "Cards":
    st.header("🃏 Cards Collection")
    df_cards = pd.DataFrame(PLAYER_STATS["cards_collected"])
    if not df_cards.empty:
        st.dataframe(df_cards)
    else:
        st.info("No cards collected yet.")

elif menu == "Chests":
    st.header("🎁 Chest History")
    if CHESTS:
        for idx, chest in enumerate(CHESTS):
            st.write(f"Chest {idx+1}: Gold {chest['gold']}, Cards {[c['Name'] for c in chest['cards']]}, Time {chest['time']}")
    else:
        st.info("No chests opened yet.")

elif menu == "Upgrades":
    st.header("⚡ Upgrades")
    click_upgrade = st.number_input("Click Upgrade", min_value=UPGRADES['click'], step=1)
    passive_upgrade = st.number_input("Passive Upgrade", min_value=UPGRADES['passive'], step=1)
    multiplier_upgrade = st.number_input("Multiplier", min_value=float(UPGRADES['multiplier']), step=0.1, format="%.1f")

    if st.button("Apply Upgrades"):
        UPGRADES['click'] = click_upgrade
        UPGRADES['passive'] = passive_upgrade
        UPGRADES['multiplier'] = multiplier_upgrade
        st.success("Upgrades applied!")

elif menu == "Achievements":
    st.header("🏆 Achievements")
    if ACHIEVEMENTS:
        for a in ACHIEVEMENTS:
            st.write(f"{a}")
    else:
        st.info("No achievements unlocked yet.")

elif menu == "Stats":
    st.header("📊 Player Stats")
    st.write(f"Gold: {PLAYER_STATS['gold']}")
    st.write(f"Clicks: {PLAYER_STATS['clicks']}")
    st.write(f"Cards Collected: {len(PLAYER_STATS['cards_collected'])}")
    st.write(f"Chests Opened: {PLAYER_STATS['chests_opened']}")

st.sidebar.markdown("---")
if st.sidebar.button("Save Game"):
    save_game()
    st.sidebar.success("Game saved!")
