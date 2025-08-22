# ==========================
# File: clashlg.py
# Updated Clash Royale League backend
# Fully Pillow ≥10 compatible
# ==========================

import random
import os
import json
import datetime
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# --------------------------
# CONFIG
# --------------------------
SEASON_GAMES = 82
PLAYOFF_TEAMS = 32
MAX_BALANCE_CHANGE = 11
SAVE_FILE = "league_state.json"
LOGO_FOLDER = Path("logos")
LOGO_SIZE = (64,64)

CARD_NAMES = [
    "Knight","Archers","Goblins","Giant","P.E.K.K.A","Mini P.E.K.K.A","Hog Rider","Musketeer","Baby Dragon",
    "Prince","Witch","Valkyrie","Skeleton Army","Bomber","Hunter","Electro Wizard","Wizard","Ice Wizard","Mega Minion",
    "Inferno Dragon","Lumberjack","Bandit","Royal Ghost","Magic Archer","Dart Goblin","Firecracker","Archer Queen",
    "Golden Knight","Skeleton King","Monk","Phoenix","Miner","Mega Knight","Electro Dragon","Sparky","Cannon Cart",
    "Flying Machine","Battle Ram","Ram Rider","Royal Recruits","Royal Hogs","Elite Barbarians","Barbarians","Minions",
    "Minion Horde","Ice Spirit","Fire Spirit","Electro Spirit","Heal Spirit","Bats","Wall Breakers","Goblin Gang",
    "Guards","Dark Prince","Bowler","Executioner","Fisherman","Zappies","Rascals","Mother Witch","Royal Champion",
    "Mortar","X-Bow","Tesla","Cannon","Bomb Tower","Inferno Tower","Goblin Hut","Barbarian Hut","Furnace","Tombstone",
    "Elixir Golem","Golem","Ice Golem","Skeletons","Graveyard","Clone","Freeze","Lightning"
][:80]

# --------------------------
# CARD CLASS
# --------------------------
class Card:
    def __init__(self,name):
        self.name = name
        self.atk_dmg = random.randint(80,1200)
        self.atk_type = random.choice(["Ground Melee","Air Melee","Ground Ranged","Air Ranged"])
        self.atk_speed = round(random.uniform(1.0,3.0),2)
        self.card_speed = random.choice(["Very Slow","Slow","Medium","Fast","Very Fast"])
        self.range = random.randint(1,10)
        self.health = random.randint(900,2500)
        self.record = {"wins":0,"losses":0}
        self.streak = 0
        self.awards = []
        self.championships = 0
        self.placements = []
        self.logo_path = LOGO_FOLDER/f"{self.name}.png"
        self.generate_logo()

    def overall_rating(self):
        dmg = (self.atk_dmg / 1200)*100*0.19
        spd = (3.0-self.atk_speed)/2.0*100*0.11
        rng = (self.range/10)*100*0.07
        hp = (self.health/2500)*100*0.22
        type_val = 0.09*(100 if "Ranged" in self.atk_type else 70)
        speed_val = {"Very Slow":60,"Slow":70,"Medium":80,"Fast":90,"Very Fast":100}[self.card_speed]*0.16
        rng_factor = random.randint(60,100)*0.16
        return round(dmg+spd+rng+hp+type_val+speed_val+rng_factor)

    def grade(self):
        ovr = self.overall_rating()
        if ovr>=98: return "Meta"
        elif ovr>=95: return "A+"
        elif ovr>=90: return "A"
        elif ovr>=84: return "B"
        elif ovr>=77: return "C"
        elif ovr>=71: return "D"
        else: return "F"

    def generate_logo(self):
        if not LOGO_FOLDER.exists():
            LOGO_FOLDER.mkdir()
        if not self.logo_path.exists():
            img = Image.new("RGB",LOGO_SIZE,color=(random.randint(50,200),
                                                   random.randint(50,200),
                                                   random.randint(50,200)))
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf",12)
            except:
                font = ImageFont.load_default()
            text = self.name[:2].upper()

            # Pillow >=10 compatible method
            bbox = draw.textbbox((0,0), text, font=font)
            w, h = bbox[2]-bbox[0], bbox[3]-bbox[1]
            draw.text(((LOGO_SIZE[0]-w)/2,(LOGO_SIZE[1]-h)/2), text, font=font, fill="white")
            img.save(str(self.logo_path))

# --------------------------
# LEAGUE CLASS
# --------------------------
class ClashLeague:
    def __init__(self):
        self.season = 1
        self.cards = [Card(name) for name in CARD_NAMES]
        self.history = []
        self.calendar = self.generate_calendar()
        self.playoff_bracket = None
        self.patch_notes = {}
        self.balance_changes_done = False

    def generate_calendar(self):
        start_date = datetime.date(2025,7,9)
        games=[]
        for i in range(SEASON_GAMES):
            date = start_date + datetime.timedelta(days=i*2)
            games.append({"game":i+1,"date":date,"played":False})
        return games

    def simulate_game(self):
        c1,c2 = random.sample(self.cards,2)
        ovr1,ovr2 = c1.overall_rating(),c2.overall_rating()
        winner = c1 if ovr1>=ovr2 else c2
        loser = c2 if winner==c1 else c1
        winner.record["wins"]+=1
        loser.record["losses"]+=1
        winner.streak = max(1,winner.streak+1)
        loser.streak = min(-1,loser.streak-1)
        return winner,loser

    def simulate_games(self,n=1):
        results=[]
        for _ in range(n):
            results.append(self.simulate_game())
        return results

    def standings(self):
        data=[]
        for c in self.cards:
            w,l=c.record["wins"],c.record["losses"]
            data.append({"Name":c.name,"W":w,"L":l,"Win%":round(w/(w+l+0.001),3),
                         "OVR":c.overall_rating(),"Grade":c.grade(),
                         "Streak":c.streak,"Logo":str(c.logo_path)})
        df=pd.DataFrame(data)
        return df.sort_values(by=["W","OVR"],ascending=False).reset_index(drop=True)

    def run_playoffs(self):
        df = self.standings().head(PLAYOFF_TEAMS)
        teams = df["Name"].tolist()
        round_names = ["Round of 32","Round of 16","Quarterfinals","Semifinals","Finals"]
        series_wins = {"Round of 32":1,"Round of 16":1,"Quarterfinals":2,"Semifinals":2,"Finals":3}
        results={}
        bracket = teams
        for rnd in round_names:
            winners=[]
            rnd_results=[]
            for i in range(0,len(bracket),2):
                t1,t2 = bracket[i],bracket[i+1]
                c1=next(c for c in self.cards if c.name==t1)
                c2=next(c for c in self.cards if c.name==t2)
                needed = series_wins[rnd]
                s1=s2=0
                while s1<needed and s2<needed:
                    w,l=self.simulate_game()
                    if w.name==c1.name: s1+=1
                    if w.name==c2.name: s2+=1
                winner=c1 if s1>s2 else c2
                winners.append(winner.name)
                rnd_results.append({"match":f"{t1} vs {t2}","winner":winner.name})
            results[rnd]=rnd_results
            bracket=winners
        champion=bracket[0]
        champ_card=next(c for c in self.cards if c.name==champion)
        champ_card.championships+=1
        self.history.append({"season":self.season,"champion":champion,"playoffs":results})
        return champion,results

    def assign_awards(self):
        df=self.standings()
        mvp=df.iloc[0]["Name"]
        improvements=[]
        for c in self.cards:
            if len(c.placements)>0:
                improvements.append((c.name,c.placements[-1]-df[df["Name"]==c.name].index[0]))
        most_improved=max(improvements,key=lambda x:x[1])[0] if improvements else mvp
        awards={"MVP":mvp,"Most Improved":most_improved}
        for award,winner in awards.items():
            card=next(c for c in self.cards if c.name==winner)
            card.awards.append({"season":self.season,"award":award})
        self.patch_notes["awards"]=awards
        return awards

    def apply_balance_changes(self,changes):
        applied=[]
        for c in changes[:MAX_BALANCE_CHANGE]:
            card=next(card for card in self.cards if card.name==c["name"])
            diffs={}
            for stat in ["atk_dmg","health","range","atk_speed"]:
                old=getattr(card,stat)
                setattr(card,stat,c[stat])
                diffs[stat]=getattr(card,stat)-old
            applied.append({"name":card.name,"diffs":diffs})
        self.balance_changes_done=True
        self.patch_notes["balance"]=applied
        return applied

    def save(self):
        data={"season":self.season,"cards":[c.__dict__ for c in self.cards],
              "history":self.history,"calendar":self.calendar,"patch_notes":self.patch_notes,
              "balance_changes_done":self.balance_changes_done}
        with open(SAVE_FILE,"w") as f:
            json.dump(data,f)

    def load(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE) as f:
                data=json.load(f)
            self.season=data["season"]
            self.calendar=data["calendar"]
            self.history=data["history"]
            self.patch_notes=data.get("patch_notes",{})
            self.balance_changes_done=data.get("balance_changes_done",False)
            self.cards=[]
            for cdata in data["cards"]:
                c=Card(cdata["name"])
                for attr in ["atk_dmg","atk_type","atk_speed","card_speed","range","health","record",
                             "streak","awards","championships","placements","logo_path"]:
                    setattr(c,attr,cdata[attr])
                self.cards.append(c)
