import streamlit as st
import pandas as pd
from clashlg import League
import random

# ------------------------------
# INITIALIZE LEAGUE
# ------------------------------
if 'league' not in st.session_state:
    st.session_state.league = League()

league = st.session_state.league

# ------------------------------
# STREAMLIT UI
# ------------------------------
st.set_page_config(layout="wide")
st.title("Clash Fantasy League")

tabs = ["Home", "Standings", "Card Stats", "Season Summary", "Top Meta Cards"]
tab = st.sidebar.radio("Tabs", tabs)

# ------------------------------
# HOME PAGE: Simulate Game / Season
# ------------------------------
if tab == "Home":
    st.header("Simulate Games & Seasons")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Single Game"):
            # Pick two random teams
            team1, team2 = random.sample(league.teams, 2)
            score1, score2 = league.simulate_game(team1, team2)
            st.success(f"{team1.name} vs {team2.name}")
            st.write(f"{team1.cards[0].name} Score: {score1}")
            st.write(f"{team2.cards[0].name} Score: {score2}")

    with col2:
        if st.button("Simulate Full Season"):
            league.simulate_season()
            league.assign_awards()
            st.success("Full Season Simulated and Awards Assigned!")

# ------------------------------
# STANDINGS
# ------------------------------
elif tab == "Standings":
    st.header("Team Standings")
    df = league.standings_df()
    st.dataframe(df.sort_values(by="Wins", ascending=False))

# ------------------------------
# CARD STATS
# ------------------------------
elif tab == "Card Stats":
    st.header("All Cards Stats")
    df = league.season_summary_df()
    st.dataframe(df.sort_values(by="OVR", ascending=False))

# ------------------------------
# SEASON SUMMARY
# ------------------------------
elif tab == "Season Summary":
    st.header("Season Summary & Awards")
    st.subheader("Standings")
    st.dataframe(league.standings_df().sort_values(by="Wins", ascending=False))

    st.subheader("Awards")
    if league.history['awards']:
        st.json(league.history['awards'][-1])
    else:
        st.write("No awards yet. Simulate a season to assign awards.")

# ------------------------------
# TOP META CARDS
# ------------------------------
elif tab == "Top Meta Cards":
    st.header("Top 10 Cards by OVR Power")
    all_cards = [c for t in league.teams for c in t.cards]
    top_cards = sorted(all_cards, key=lambda x: x.ovr_power, reverse=True)[:10]
    data = []
    for c in top_cards:
        data.append({
            'Card': c.name,
            'OVR': c.ovr_power,
            'Grade': c.grade,
            'Elixir': c.elixir_current,
            'Contribution': c.contribution_pct,
            'Clutch': c.clutch_play
        })
    st.dataframe(pd.DataFrame(data))
