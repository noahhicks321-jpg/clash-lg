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
# HOME TAB: SIMULATION
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
# STANDINGS TAB
# ------------------------------
elif tab == "📊 Standings":
    st.header("Team Standings")
    df = league.standings_df().sort_values(by="Wins", ascending=False)
    st.dataframe(df.style.set_properties(**{'text-align':'center'}))

# ------------------------------
# CARD INFO TAB
# ------------------------------
elif tab == "🃏 Card Info":
    st.header("All Card Stats")
    df = league.cards_df().sort_values(by="OVR", ascending=False)
    
    for i, row in df.iterrows():
        with st.expander(f"{row['Card Icon']} {row['Card']} ({row['Grade']})"):
            st.markdown(f"**Team:** {row['Team Logo']} {row['Team']} ({row['Color']})")
            st.write(f"**Attack:** {row['Attack']}")
            st.write(f"**Defense:** {row['Defense']}")
            st.write(f"**Hit Speed:** {row['Hit Speed']}")
            st.write(f"**Speed:** {row['Speed']}")
            st.write(f"**OVR Power:** {row['OVR']}")
            st.write(f"**Elixir Cost:** {row['Elixir']}")
            st.write(f"**Contribution %:** {row['Contribution %']}%")
            st.write(f"**Clutch %:** {row['Clutch %']}%")
            st.write(f"**Contracts:** {row.get('Contracts', 'N/A')}")
    
# ------------------------------
# TEAM INFO TAB
# ------------------------------
elif tab == "🏟️ Team Info":
    st.header("Team Profiles & Card Details")
    df = league.team_info_df()
    for team_name in df['Team'].unique():
        tdf = df[df['Team']==team_name]
        st.subheader(f"{tdf.iloc[0]['Team Logo']} {team_name} ({tdf.iloc[0]['Color']})")
        st.table(tdf[['Card Icon','Card','OVR','Grade','Elixir','Contribution %','Clutch %']].style.format({'OVR':'{:.1f}','Elixir':'{:.1f}'}))

# ------------------------------
# TOP META CARDS TAB
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
            'Contribution %': c.contribution_pct(),
            'Clutch %': c.clutch_pct()
        })
    df_top = pd.DataFrame(data)
    st.dataframe(df_top.style.format({'OVR':'{:.1f}','Elixir':'{:.1f}'}).set_properties(**{'text-align':'center'}))

# ------------------------------
# SEASON SUMMARY TAB
# ------------------------------
elif tab == "📜 Season Summary":
    st.header("Season Summary & Awards")
    
    st.subheader("Team Standings")
    st.dataframe(league.standings_df().sort_values(by="Wins", ascending=False))
    
    st.subheader("Top Awards")
    if league.history['awards']:
        st.json(league.history['awards'][-1])
    else:
        st.write("No awards yet. Simulate a season to assign awards.")
    
    st.subheader("Top Meta Cards")
    top_cards = league.top_meta_cards()
    data = []
    for c in top_cards:
        data.append({
            'Card Icon': c.icon,
            'Card': c.name,
            'OVR': c.ovr_power,
            'Grade': c.grade,
            'Elixir': c.elixir_current,
            'Contribution %': c.contribution_pct(),
            'Clutch %': c.clutch_pct()
        })
    df_top = pd.DataFrame(data)
    st.dataframe(df_top.style.format({'OVR':'{:.1f}','Elixir':'{:.1f}'}).set_properties(**{'text-align':'center'}))

# ------------------------------
# ENHANCED STYLING AND DYNAMIC ELIXIR
# ------------------------------
def grade_color(grade):
    if grade in ['A+', 'A']: return 'green'
    elif grade == 'B': return 'blue'
    elif grade == 'C': return 'orange'
    else: return 'red'

def trend_arrow(trend):
    if trend == '▲': return '🟢▲'
    elif trend == '▼': return '🔴▼'
    return trend

def format_cards_table(df):
    df_formatted = df.copy()
    df_formatted['Grade'] = df_formatted.apply(lambda x: f"{trend_arrow(getattr(x,'trend','▲'))} <span style='color:{grade_color(x['Grade'])}'>{x['Grade']}</span>", axis=1)
    df_formatted['Card Display'] = df_formatted['Card Icon'] + ' ' + df_formatted['Card']
    df_formatted['Team Display'] = df_formatted['Team Logo'] + ' ' + df_formatted['Team']
    df_formatted['Elixir'] = df_formatted['OVR'].apply(lambda ovr: round(max(1, min(10, ovr/10)),1))  # Dynamic elixir based on OVR
    return df_formatted[['Team Display','Card Display','OVR','Grade','Elixir','Contribution %','Clutch %']]

# Example Usage in CARD INFO tab:
if tab == "🃏 Card Info":
    st.header("All Card Stats - Enhanced Display")
    df = league.cards_df().sort_values(by="OVR", ascending=False)
    df_formatted = format_cards_table(df)
    st.write("**Click to view card details:**")
    for idx, row in df_formatted.iterrows():
        with st.expander(f"{row['Card Display']} ({row['Grade']})"):
            st.markdown(f"**Team:** {row['Team Display']}")
            st.write(f"**OVR Power:** {row['OVR']}")
            st.write(f"**Elixir Cost:** {row['Elixir']}")
            st.write(f"**Contribution %:** {row['Contribution %']}%")
            st.write(f"**Clutch %:** {row['Clutch %']}%")
