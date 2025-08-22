import streamlit as st
import pandas as pd
import random
from clashlg import League

# ------------------------------
# INITIALIZE LEAGUE
# ------------------------------
if 'league' not in st.session_state:
    st.session_state.league = League()

league = st.session_state.league

st.set_page_config(layout="wide")
st.title("⚔️ Clash Fantasy League Dashboard")

# ------------------------------
# NAVIGATION TABS
# ------------------------------
tabs = ["🏠 Home", "📊 Standings", "🃏 Card Info", "🏟️ Team Info", "🔥 Top Meta Cards", "📜 Season Summary"]
tab = st.sidebar.radio("Navigation", tabs)

# ------------------------------
# HOME: SIMULATION
# ------------------------------
if tab == "🏠 Home":
    st.header("Simulate Games & Seasons")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Single Game"):
            team1, team2 = random.sample(league.teams, 2)
            score1, score2 = league.simulate_game(team1, team2)
            st.success(f"{team1.logo} {team1.name} vs {team2.logo} {team2.name}")
            st.write(f"{team1.cards[0].icon} {team1.cards[0].name} Score: {score1}")
            st.write(f"{team2.cards[0].icon} {team2.cards[0].name} Score: {score2}")

    with col2:
        if st.button("Simulate Full Season"):
            league.simulate_full_season()
            league.assign_awards()
            st.success("🏆 Full Season Simulated & Awards Assigned!")

# ------------------------------
# STANDINGS
# ------------------------------
elif tab == "📊 Standings":
    st.header("Team Standings")
    df = league.standings_df().sort_values(by="Wins", ascending=False)
    st.dataframe(df.style.set_properties(**{'text-align':'center'}))

# ------------------------------
# CARD INFO
# ------------------------------
elif tab == "🃏 Card Info":
    st.header("All Card Stats")
    df = league.cards_df().sort_values(by="OVR", ascending=False)
    st.dataframe(df.style.format({'OVR': '{:.1f}', 'Elixir': '{:.1f}'}).set_properties(**{'text-align':'center'}))

# ------------------------------
# TEAM INFO
# ------------------------------
elif tab == "🏟️ Team Info":
    st.header("Team Profiles & Card Details")
    df = league.team_info_df()
    st.dataframe(df.style.format({'OVR': '{:.1f}', 'Elixir': '{:.1f}'}).set_properties(**{'text-align':'center'}))

# ------------------------------
# TOP META CARDS
# ------------------------------
elif tab == "🔥 Top Meta Cards":
    st.header("Top 10 Cards by OVR Power")
    top_cards = league.top_meta_cards()
    data = []
    for c in top_cards:
        data.append({
            'Card Icon': c.icon,
            'Card': c.name,
            'OVR': c.ovr_power,
            'Grade': c.grade,
            'Elixir': c.elixir_current,
            'Contribution': c.contribution_pct,
            'Clutch': c.clutch_play
        })
    df_top = pd.DataFrame(data)
    st.dataframe(df_top.style.format({'OVR':'{:.1f}','Elixir':'{:.1f}'}).set_properties(**{'text-align':'center'}))

# ------------------------------
# SEASON SUMMARY
# ------------------------------
elif tab == "📜 Season Summary":
    st.header("Season Summary & Awards")
    st.subheader("Standings")
    st.dataframe(league.standings_df().sort_values(by="Wins", ascending=False))
    
    st.subheader("Top Awards")
    if league.history['awards']:
        st.json(league.history['awards'][-1])
    else:
        st.write("No awards yet. Simulate a season to assign awards.")
