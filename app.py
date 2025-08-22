# ==========================
# File: app.py
# Streamlit UI for Clash Royale League
# ==========================

import streamlit as st
import pandas as pd
from PIL import Image
from clashlg import ClashLeague, Card, LOGO_FOLDER, MAX_BALANCE_CHANGE, SEASON_GAMES

st.set_page_config(page_title="Clash Royale League",layout="wide")

# --------------------------
# INIT LEAGUE
# --------------------------
if "league" not in st.session_state:
    st.session_state.league = ClashLeague()
league = st.session_state.league

# --------------------------
# NAVIGATION
# --------------------------
tabs = ["Home","Card Stats","Standings","Card Info","Awards","Playoffs","League History","Records","Calendar","Balance Changes"]
page = st.sidebar.radio("Navigate", tabs)

# --------------------------
# HOME TAB
# --------------------------
if page=="Home":
    st.title(f"🏆 Clash Royale League - Season {league.season}")
    col1,col2 = st.columns([2,1])
    with col1:
        st.subheader("Simulate Games")
        if st.button("Sim 1 Game"): league.simulate_games(1)
        if st.button("Sim 5 Games"): league.simulate_games(5)
        if st.button("Sim 10 Games"): league.simulate_games(10)
        if st.button("Sim 40 Games"): league.simulate_games(40)
        if st.button("Sim Full Season"): league.simulate_games(len(league.cards)*41)
        if st.button("Save Game"): league.save()
        if st.button("Load Game"): league.load()

        st.subheader("Season Management")
        if st.button("Next Season / Rollover"):
            df = league.standings()
            for c in league.cards:
                placement=df[df["Name"]==c.name].index[0]+1
                c.placements.append(placement)
                c.record={"wins":0,"losses":0}
                c.streak=0
            league.calendar = league.generate_calendar()
            league.season+=1
            league.balance_changes_done=False
            st.success(f"Season rolled over to Season {league.season}!")

    with col2:
        st.subheader("🔥 Top 10 Cards")
        df = league.standings().head(10)
        for idx,row in df.iterrows():
            logo = Image.open(row["Logo"])
            st.image(logo,width=40,caption=f"{row['Name']} ({row['Grade']})")
            st.write(f"W:{row['W']}  L:{row['L']}  OVR:{row['OVR']}")

# --------------------------
# CARD STATS TAB
# --------------------------
elif page=="Card Stats":
    st.title("📊 Card Stats")
    df=league.standings()
    st.dataframe(df[["Name","W","L","Win%","OVR","Grade","Streak"]],use_container_width=True)

# --------------------------
# STANDINGS TAB
# --------------------------
elif page=="Standings":
    st.title("📈 Standings")
    df = league.standings()
    buff_nerf=[]
    last_changes = league.patch_notes.get("balance",[])
    for c in df["Name"]:
        entry = next((x for x in last_changes if x["name"]==c), None)
        if entry:
            total_change=sum(entry["diffs"].values())
            if total_change>0: buff_nerf.append("B")
            elif total_change<0: buff_nerf.append("N")
            else: buff_nerf.append("")
        else: buff_nerf.append("")
    df["B/N"]=buff_nerf
    st.dataframe(df[["Name","B/N","W","L","Win%","OVR","Grade","Streak"]],use_container_width=True)

# --------------------------
# CARD INFO TAB
# --------------------------
elif page=="Card Info":
    st.title("🔍 Card Info")
    card_name=st.selectbox("Select Card",[c.name for c in league.cards])
    card=next(c for c in league.cards if c.name==card_name)
    st.image(card.logo_path,width=80)
    st.write(f"**ATK DMG:** {card.atk_dmg}")
    st.write(f"**ATK TYPE:** {card.atk_type}")
    st.write(f"**ATK SPEED:** {card.atk_speed}")
    st.write(f"**CARD SPEED:** {card.card_speed}")
    st.write(f"**RANGE:** {card.range}")
    st.write(f"**HEALTH:** {card.health}")
    st.write(f"**Current Season Record:** {card.record}")
    st.write(f"**Championships:** {card.championships}")
    st.write(f"**Awards:** {card.awards}")
    st.write(f"**Previous Placements:** {card.placements}")

# --------------------------
# AWARDS TAB
# --------------------------
elif page=="Awards":
    st.title("🏅 Awards")
    if st.button("Assign Awards"):
        awards=league.assign_awards()
        st.success("Awards Assigned!")
        st.json(awards)
    if league.patch_notes.get("awards"):
        st.subheader("Last Season Awards")
        st.json(league.patch_notes["awards"])

# --------------------------
# PLAYOFFS TAB
# --------------------------
elif page=="Playoffs":
    st.title("🎯 Playoffs")
    if st.button("Run Playoffs"):
        champ,results=league.run_playoffs()
        st.success(f"Champion: {champ}")
        st.json(results)

# --------------------------
# LEAGUE HISTORY TAB
# --------------------------
elif page=="League History":
    st.title("📖 League History")
    st.json(league.history)

# --------------------------
# RECORDS TAB
# --------------------------
elif page=="Records":
    st.title("📜 Records")
    data=[]
    for c in league.cards:
        data.append({"Name":c.name,"Championships":c.championships,
                     "Wins":c.record["wins"],"Losses":c.record["losses"]})
    df=pd.DataFrame(data)
    st.dataframe(df.sort_values(by="Championships",ascending=False),use_container_width=True)

# --------------------------
# CALENDAR TAB
# --------------------------
elif page=="Calendar":
    st.title("📅 Calendar")
    df=pd.DataFrame(league.calendar)
    df["date"]=df["date"].astype(str)
    st.dataframe(df,use_container_width=True)

# --------------------------
# BALANCE CHANGES TAB
# --------------------------
elif page=="Balance Changes":
    st.title("⚖️ Balance Changes - Manual Patch")
    if league.balance_changes_done:
        st.warning("Balance changes already applied this season.")
    else:
        st.write(f"Select up to {MAX_BALANCE_CHANGE} cards to edit stats:")
        selected_cards=st.multiselect("Cards",[c.name for c in league.cards])
        edited_cards=[]
        for cname in selected_cards[:MAX_BALANCE_CHANGE]:
            card=next(c for c in league.cards if c.name==cname)
            with st.expander(f"{card.name}"):
                atk_dmg=st.slider("ATK DMG",50,1500,card.atk_dmg,key=f"dmg_{card.name}")
                health=st.slider("HEALTH",500,3000,card.health,key=f"hp_{card.name}")
                atk_speed=st.slider("ATK SPEED",0.5,3.0,float(card.atk_speed),0.1,key=f"spd_{card.name}")
                rng=st.slider("RANGE",1,10,card.range,key=f"rng_{card.name}")
                edited_cards.append({"name":card.name,"atk_dmg":atk_dmg,"health":health,"atk_speed":atk_speed,"range":rng})
        if st.button("Apply Changes") and edited_cards:
            changes=league.apply_balance_changes(edited_cards)
            st.success("Balance Changes Applied!")
            st.json(changes)
