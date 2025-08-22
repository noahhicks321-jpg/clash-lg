import streamlit as st
import pandas as pd
from clashlg import ClashLeague

st.set_page_config(page_title="Clash Royale League", layout="wide")
if "league" not in st.session_state:
    st.session_state.league = ClashLeague()

league = st.session_state.league

# ==========================================================
# NAVIGATION
# ==========================================================
tabs = ["Home","Card Stats","Standings","Card Info","Awards","Playoffs","League History","Records","Calendar"]
page = st.sidebar.radio("Navigate", tabs)

# ==========================================================
# HOME
# ==========================================================
if page == "Home":
    st.title(f"🏆 Clash Royale League - Season {league.season}")
    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("Simulate Games")
        if st.button("Sim 1 Game"): league.simulate_games(1)
        if st.button("Sim 5 Games"): league.simulate_games(5)
        if st.button("Sim 10 Games"): league.simulate_games(10)
        if st.button("Sim 40 Games"): league.simulate_games(40)
        if st.button("Sim Full Season"): league.simulate_full_season()

        if st.button("Save Game"): league.save()
        if st.button("Load Game"): league.load()

    with col2:
        st.subheader("🔥 Top 10 Cards")
        df = league.standings().head(10)
        st.table(df[["Logo","Name","W","L","Grade","OVR"]])

# ==========================================================
# CARD STATS
# ==========================================================
elif page == "Card Stats":
    st.title("📊 Card Stats")
    df = league.standings()
    st.dataframe(df, use_container_width=True)

# ==========================================================
# STANDINGS
# ==========================================================
elif page == "Standings":
    st.title("📈 Standings")
    df = league.standings()
    st.dataframe(df, use_container_width=True)

# ==========================================================
# CARD INFO
# ==========================================================
elif page == "Card Info":
    st.title("🔍 Card Info")
    card_name = st.selectbox("Select Card", [c["name"] for c in league.cards])
    card = next(c for c in league.cards if c["name"] == card_name)
    st.json(card)

# ==========================================================
# AWARDS
# ==========================================================
elif page == "Awards":
    st.title("🏅 Awards")
    if st.button("Assign Awards"):
        league.assign_awards()
    st.json(league.awards)

# ==========================================================
# PLAYOFFS
# ==========================================================
elif page == "Playoffs":
    st.title("🎯 Playoffs")
    if st.button("Run Playoffs"):
        champ, results = league.run_playoffs()
        st.success(f"Champion: {champ}")
        st.json(results)

# ==========================================================
# LEAGUE HISTORY
# ==========================================================
elif page == "League History":
    st.title("📖 League History")
    st.json(league.history)

# ==========================================================
# RECORDS
# ==========================================================
elif page == "Records":
    st.title("📜 Records")
    champs = {}
    for c in league.cards:
        champs[c["name"]] = c["championships"]
    rec_df = pd.DataFrame.from_dict(champs, orient="index", columns=["Championships"]).sort_values(by="Championships", ascending=False)
    st.dataframe(rec_df)

# ==========================================================
# CALENDAR
# ==========================================================
elif page == "Calendar":
    st.title("📅 Calendar")
    df = pd.DataFrame(league.calendar)
    st.dataframe(df, use_container_width=True)
