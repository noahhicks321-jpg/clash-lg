# app.py
"""
Clash Royale Clicker - Chunk #1 (Core Framework)
Paste this file as the first base. Later chunks will replace/extend this file.
"""

import streamlit as st
import time
import random
import pandas as pd

st.set_page_config(page_title="Clash Royale Clicker", page_icon="👑", layout="wide")

# -------------------------------
# ---- SESSION STATE SETUP -----
# -------------------------------
def init_session_state():
    ss = st.session_state
    # core currency / progression
    ss.setdefault("coins", 0.0)
    ss.setdefault("mpc", 1.0)           # money per click (base)
    ss.setdefault("mps", 0.0)           # money per second (passive)
    ss.setdefault("total_money", 0.0)   # all-time money earned (for arenas)
    ss.setdefault("total_clicks", 0)    # total clicks performed
    ss.setdefault("total_chests_opened", 0)
    ss.setdefault("total_cards_collected", 0)
    ss.setdefault("total_cards_sold", 0)
    ss.setdefault("last_update", time.time())
    ss.setdefault("inventory", [])      # list of dicts: {"Card","Rarity","Value","timestamp"}
    ss.setdefault("history", [])        # recent events strings
    ss.setdefault("arena", 1)
    ss.setdefault("arena_rewards_claimed", [])
    # placeholders for upgrades, chests (will be fleshed out in future chunks)
    ss.setdefault("upgrades_purchased", [])  # store upgrade ids in order purchased
    ss.setdefault("unlocked_chests", ["Wooden Chest"])  # chests available immediately
    ss.setdefault("available_cards_table", None)  # placeholder for later chunk when we add 120 cards

init_session_state()

# -------------------------------
# ---- CONFIG PLACEHOLDERS -----
# -------------------------------
# Chest definitions (partial, full definitions will be added in chunk #3)
CHESTS = {
    "Wooden Chest": {"price": 15, "odds": {"Common": 0.85, "Rare": 0.15}},
    "Silver Chest": {"price": 75, "odds": {"Common": 0.75, "Rare": 0.15, "Epic": 0.10}},
    "Gold Chest": {"price": 150, "odds": {"Common": 0.70, "Rare": 0.17, "Epic": 0.11, "Legendary": 0.02}},
    # More chests will be added in later chunks (Magical, King's, Legendary, Champion, Universal, Guaranteed etc.)
}

# Small example card pool for chunk #1 (we'll replace with the full 120 later)
CARD_POOL = {
    "Common": ["Knight", "Archers", "Bomber", "Skeletons"],
    "Rare": ["Musketeer", "Mini P.E.K.K.A", "Valkyrie"],
    "Epic": ["Baby Dragon", "Prince", "Witch"],
    "Legendary": ["Miner", "Lumberjack"],
    "Champion": ["Monk", "Golden Knight"],
}

# Sale value ranges per rarity (will be used to randomize values when pulling)
CARD_VALUE_RANGES = {
    "Common": (0.58, 8.76),
    "Rare": (8.77, 28.95),
    "Epic": (28.96, 89.54),
    "Legendary": (89.55, 487.88),
    "Champion": (487.89, 6788.43),
}

# Arena progression (partial sample; full list will be added later)
ARENAS = [
    {"arena": 1, "req": 0, "reward": 0},
    {"arena": 2, "req": 1_000, "reward": 500},
    {"arena": 3, "req": 7_000, "reward": 1_000},
    {"arena": 4, "req": 15_000, "reward": 2_000},
    # ... will continue up to Arena 25 in a later chunk
]

# -------------------------------
# ---- CORE GAME LOGIC -----
# -------------------------------
def now():
    return time.time()

def grant_passive_income():
    """
    Calculate passive income since last update and add it to coins and total_money.
    This gets called whenever the UI re-renders so we don't need a background thread.
    """
    ss = st.session_state
    current = now()
    elapsed = current - ss["last_update"]
    if elapsed <= 0:
        return 0.0
    earned = elapsed * ss["mps"]
    if earned > 0:
        ss["coins"] += earned
        ss["total_money"] += earned
    ss["last_update"] = current
    return earned

def perform_click():
    """Handle a user click: add mpc, track stats, record history."""
    ss = st.session_state
    ss["coins"] += ss["mpc"]
    ss["total_money"] += ss["mpc"]
    ss["total_clicks"] += 1
    evt = f"Clicked and earned {ss['mpc']}$ (Total clicks: {ss['total_clicks']})"
    ss["history"].insert(0, f"{time.strftime('%H:%M:%S')} - {evt}")
    # cap history
    ss["history"] = ss["history"][:500]

def open_chest(chest_name):
    """Simplified chest open routine for chunk #1."""
    ss = st.session_state
    chest = CHESTS.get(chest_name)
    if not chest:
        st.error("Chest definition not found.")
        return
    price = chest["price"]
    if ss["coins"] < price:
        st.warning("Not enough coins to open that chest.")
        return

    ss["coins"] -= price
    ss["total_chests_opened"] += 1

    # Determine rarity by odds (odds must sum to <=1; remainder implicit Common fallback)
    roll = random.random()
    cum = 0.0
    picked_rarity = "Common"
    for rarity, odds in chest["odds"].items():
        cum += odds
        if roll <= cum:
            picked_rarity = rarity
            break

    card = random.choice(CARD_POOL.get(picked_rarity, ["Unknown Card"]))
    low, high = CARD_VALUE_RANGES[picked_rarity]
    value = round(random.uniform(low, high), 2)
    entry = {
        "Card": card,
        "Rarity": picked_rarity,
        "Value": value,
        "timestamp": time.time()
    }
    ss["inventory"].append(entry)
    ss["total_cards_collected"] += 1
    ss["history"].insert(0, f"{time.strftime('%H:%M:%S')} - Opened {chest_name}: {card} ({picked_rarity}) worth {value}$")
    ss["history"] = ss["history"][:500]
    st.success(f"Pulled {card} ({picked_rarity}) worth {value}$")

def check_arena_progression():
    """Check whether total_money reaches next arena requirements and award rewards once."""
    ss = st.session_state
    current_total = ss["total_money"]
    # find the highest arena unlocked by total_money
    unlocked = ss["arena"]
    for a in ARENAS:
        if current_total >= a["req"] and a["arena"] > unlocked:
            unlocked = a["arena"]

    if unlocked > ss["arena"]:
        # award each newly unlocked arena reward (if not already claimed)
        for a in ARENAS:
            if ss["arena"] < a["arena"] <= unlocked:
                if a["arena"] not in ss["arena_rewards_claimed"]:
                    ss["coins"] += a["reward"]
                    ss["arena_rewards_claimed"].append(a["arena"])
                    ss["history"].insert(0, f"{time.strftime('%H:%M:%S')} - Reached Arena {a['arena']}! Awarded {a['reward']}$")
        ss["arena"] = unlocked

# -------------------------------
# ---- UI: Layout & Tabs -----
# -------------------------------
# Update passive income as soon as the page loads / re-renders
earned = grant_passive_income()
check_arena_progression()

# Top header row (global metrics)
col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
with col1:
    st.title("🎯 Clash Royale Clicker")
    st.caption("Chunk #1 — Core framework. Paste the next chunks in order to expand the game.")
with col2:
    st.metric("Coins", f"{round(st.session_state['coins'], 2)}$")
with col3:
    st.metric("Money / Click", f"{round(st.session_state['mpc'], 2)}$")
with col4:
    st.metric("Money / Sec", f"{round(st.session_state['mps'], 2)}$")
with col5:
    st.metric("Arena", st.session_state["arena"])

# Main tabs
tabs = st.tabs(["🏠 Home", "🛒 Store", "📚 Collection", "🔎 Available Cards", "📜 All-time History", "🏆 Ranked System"])

# ---------------- Home Tab ----------------
with tabs[0]:
    st.header("Home — Click to earn")
    left, right = st.columns([3, 1])

    with left:
        # Large click button area
        st.markdown(
            "<div style='display:flex;align-items:center;justify-content:center;height:300px;border-radius:12px;"
            "background:linear-gradient(135deg,#fef3c7,#fde68a);'>"
            "<button style='font-size:28px;padding:26px 40px;border-radius:12px;border:none;cursor:pointer;'>"
            "CLICK HERE</button></div>",
            unsafe_allow_html=True,
        )
        # Because the above is decorative, provide a real button for click-handling
        if st.button("💥 Click! (Real)"):
            perform_click()

        st.write("Tip: Clicking the big decorative area doesn't trigger clicks in Streamlit; use the 'Click!' button above or we'll add a JS-based clicker in a later chunk.")

        # Quick stats
        st.write(
            f"**Total money earned:** {round(st.session_state['total_money'],2)}$\n\n"
            f"**Total clicks:** {st.session_state['total_clicks']}\n\n"
            f"**Total chests opened:** {st.session_state['total_chests_opened']}"
        )

    with right:
        st.subheader("Upgrades (placeholder)")
        st.info("Upgrades system will be supplied in Chunk #2. For now, you can see basic mpc/mps values above.")
        st.divider()
        st.subheader("Unlocked Chests")
        for c in st.session_state["unlocked_chests"]:
            st.write(f"- {c}")

# ---------------- Store Tab ----------------
with tabs[1]:
    st.header("Store — Chests")
    st.write("Open chests to get cards. Chest definitions and full odds will be expanded in Chunk #3.")
    store_cols = st.columns(2)
    i = 0
    for chest_name, chest in CHESTS.items():
        with store_cols[i % 2]:
            st.subheader(f"{chest_name} — {chest['price']}$")
            # show odds succinctly
            odds_text = ", ".join([f"{r}: {int(od*100)}%" for r, od in chest["odds"].items()])
            st.write(f"Odds — {odds_text}")
            if st.button(f"Open {chest_name} ({chest['price']}$)", key=f"open_{chest_name}"):
                open_chest(chest_name)
        i += 1

# ---------------- Collection Tab ----------------
with tabs[2]:
    st.header("Collection — Cards you own")
    inv = st.session_state["inventory"]
    if not inv:
        st.info("You don't have any cards yet. Open chests in the Store.")
    else:
        df = pd.DataFrame(inv)
        # format timestamp nicely if present
        if "timestamp" in df.columns:
            df["Pulled At"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%Y-%m-%d %H:%M:%S")
            df = df.drop(columns=["timestamp"])
            cols = ["Card", "Rarity", "Value", "Pulled At"]
        else:
            cols = ["Card", "Rarity", "Value"]
        st.dataframe(df[cols], use_container_width=True)

        st.markdown("**Sell functionality will be added in Chunk #4.**")

# ---------------- Available Cards Tab ----------------
with tabs[3]:
    st.header("Available Cards (Preview)")
    st.write("This tab will display every obtainable card (120) with sell prices and rarities in Chunk #4.")
    st.write("For now: small sample pool shown below.")
    sample = []
    for rarity, cards in CARD_POOL.items():
        for c in cards:
            low, high = CARD_VALUE_RANGES[rarity]
            sample.append({"Card": c, "Rarity": rarity, "Sell Value Range": f"{low}$ - {high}$"})
    st.table(pd.DataFrame(sample))

# ---------------- All-time History Tab ----------------
with tabs[4]:
    st.header("All-time History")
    st.write("Recent actions (most recent first). This will expand with more stats in Chunk #7.")
    if st.session_state["history"]:
        for h in st.session_state["history"][:200]:
            st.write(h)
    else:
        st.info("No history yet. Play to generate events!")

# ---------------- Ranked System Tab ----------------
with tabs[5]:
    st.header("Ranked System (Arenas)")
    st.write("Arena progression is based on **Total money made**. When you reach a new arena you'll be awarded a cash reward (claimed automatically).")
    st.write(f"Current Arena: **{st.session_state['arena']}**")
    st.write(f"Total Money Made: **{round(st.session_state['total_money'],2)}$**")
    st.divider()
    st.subheader("Arena Requirements (sample)")
    st.dataframe(pd.DataFrame(ARENAS), use_container_width=True)

# ---------------- Footer Controls ----------------
st.sidebar.header("Quick Controls")
if st.sidebar.button("⏱️ Force passive income tick"):
    # call the passive income function and rerun so user sees change
    grant_passive_income()
    st.experimental_rerun()

if st.sidebar.button("🔄 Reset Progress (debug)"):
    confirm = st.sidebar.checkbox("Confirm reset")
    if confirm:
        # reset relevant session_state keys to initial defaults
        st.session_state.update({
            "coins": 0.0,
            "mpc": 1.0,
            "mps": 0.0,
            "total_money": 0.0,
            "total_clicks": 0,
            "total_chests_opened": 0,
            "total_cards_collected": 0,
            "total_cards_sold": 0,
            "last_update": time.time(),
            "inventory": [],
            "history": [],
            "arena": 1,
            "arena_rewards_claimed": [],
            "upgrades_purchased": [],
            "unlocked_chests": ["Wooden Chest"],
        })
        st.success("Progress reset. Page will reload.")
        st.experimental_rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("**Developer notes:** Paste the next chunk (Upgrades system) to add the full ordered upgrade tree. Subsequent chunks will add the full chest list, 120 cards, save/load, sell mechanics, arena reward list to Arena 25, guaranteed chests, and more.")
