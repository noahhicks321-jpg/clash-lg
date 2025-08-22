# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from clashlg import league, Card, Team, League

st.set_page_config(page_title="Clash Fantasy League", layout="wide")

# ------------------------------
# SAVE / LOAD LEAGUE
# ------------------------------
def save_league():
    league.save_league("league_save.pkl")
    st.success("League saved!")

def load_league():
    global league
    league = League.load_league("league_save.pkl")
    st.success("League loaded!")

# ------------------------------
# HOMEPAGE TAB
# ------------------------------
st.title("Clash Fantasy League")

tabs = st.tabs(["Homepage", "Standings", "Card Info", "Team Info", "Season Summary"])

with tabs[0]:
    st.header("Top 10 Cards This Season")
    top_cards = league.top_meta_cards()
    card_data = []
    for c in top_cards:
        card_data.append({
            "Logo": c.icon,
            "Name": c.name,
            "OVR": c.ovr_power,
            "Grade": c.grade,
            "Contribution %": c.contribution_pct_value,
            "Clutch %": c.clutch_pct(),
            "Elixir": c.elixir_current,
            "Dominance": c.dominance
        })
    df_cards = pd.DataFrame(card_data)
    st.table(df_cards)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simulate Single Game"):
            t1 = league.teams[0]; t2 = league.teams[1]
            s1,s2 = league.simulate_game(t1,t2)
            st.info(f"Game Result: {t1.name} {s1:.1f} - {s2:.1f} {t2.name}")
    with col2:
        if st.button("Simulate Full Season"):
            league.simulate_full_season()
            st.success("Full season simulated!")

# ------------------------------
# STANDINGS TAB
# ------------------------------
with tabs[1]:
    st.header("Team Standings")
    standings_data = []
    for t in league.teams:
        standings_data.append({
            "Logo": t.logo,
            "Team": t.name,
            "Wins": t.wins,
            "Losses": t.losses,
            "Streak": t.streak,
            "Strategy": t.strategy
        })
    df_standings = pd.DataFrame(standings_data)
    st.table(df_standings)

# ------------------------------
# CARD INFO TAB
# ------------------------------
with tabs[2]:
    st.header("All Card Stats")
    all_cards_data = []
    for c in league.cards:
        all_cards_data.append({
            "Logo": c.icon,
            "Name": c.name,
            "OVR": c.ovr_power,
            "Grade": c.grade,
            "Attack": c.attack,
            "Defense": c.defense,
            "Hit Speed": c.hit_speed,
            "Speed": c.speed,
            "Contribution %": c.contribution_pct_value,
            "Clutch %": c.clutch_pct(),
            "Elixir": c.elixir_current,
            "Dominance": c.dominance
        })
    df_all_cards = pd.DataFrame(all_cards_data)
    st.dataframe(df_all_cards, use_container_width=True)

# ------------------------------
# TEAM INFO TAB
# ------------------------------
with tabs[3]:
    st.header("Team Info")
    for t in league.teams:
        with st.expander(f"{t.logo} {t.name}"):
            team_data = []
            for c in t.cards:
                team_data.append({
                    "Card Logo": c.icon,
                    "Name": c.name,
                    "OVR": c.ovr_power,
                    "Grade": c.grade,
                    "Contribution %": c.contribution_pct_value,
                    "Clutch %": c.clutch_pct(),
                    "Elixir": c.elixir_current,
                    "Dominance": c.dominance
                })
            df_team = pd.DataFrame(team_data)
            st.table(df_team)
            # Show recent game highlights
            st.write("Recent Game Highlights:")
            for c in t.cards:
                for h in c.history[-3:]:
                    st.write(f"{c.name}: {'Win' if h['won'] else 'Loss'}, Damage: {h['damage']}, Defense: {h['defense']}, Clutch: {h['clutch']}")

# ------------------------------
# SEASON SUMMARY TAB
# ------------------------------
with tabs[4]:
    st.header("Season Summary & Awards")
    if league.history:
        st.write(f"Season {league.season} Champion: {league.history[-1]['champion']}")
    else:
        st.write("No champion yet. Simulate season first.")
    st.write("Hall of Fame:")
    for champ in league.hall_of_fame:
        st.write(f"{champ.name} ({champ.cards[0].icon}{champ.cards[1].icon})")

    # Patch notes editing
    st.subheader("Patch Notes / Meta Adjustments")
    patch_text = st.text_area("Edit Card Stats / Meta", height=150, value="Adjust OVR, Attack, Defense, etc.")
    if st.button("Apply Patch Notes"):
        st.success("Patch notes applied! (Logic to apply stats changes to cards goes here)")

# ------------------------------
# SAVE / LOAD LEAGUE
# ------------------------------
st.sidebar.header("League Management")
if st.sidebar.button("Save League"):
    save_league()
if st.sidebar.button("Load League"):
    load_league()
