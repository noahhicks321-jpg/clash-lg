import random
import json
import os
import datetime
import pandas as pd

# ==========================================================
# CONFIGURATION
# ==========================================================
SEASON_GAMES = 82
PLAYOFF_TEAMS = 32
SAVE_FILE = "clash_league_save.json"

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
]
CARD_NAMES = CARD_NAMES[:80]  # cap at 80

# ==========================================================
# CARD GENERATION
# ==========================================================
def generate_card(name):
    return {
        "name": name,
        "atk_dmg": random.randint(80, 1200),
        "atk_type": random.choice(["Ground Melee","Air Melee","Ground Ranged","Air Ranged"]),
        "atk_speed": round(random.uniform(1.0, 3.0), 2),
        "card_speed": random.choice(["Very Slow","Slow","Medium","Fast","Very Fast"]),
        "range": random.randint(1, 10),
        "health": random.randint(900, 2500),
        "record": {"wins": 0, "losses": 0},
        "history": [],
        "championships": 0,
        "streak": 0,
        "logo": "🛡️",
        "awards": [],
        "placements": []
    }

def overall_rating(card):
    dmg = (card["atk_dmg"] / 1200) * 100 * 0.19
    spd = (3.0 - card["atk_speed"]) / 2.0 * 100 * 0.11
    rng = (card["range"] / 10) * 100 * 0.07
    hp = (card["health"] / 2500) * 100 * 0.22
    type_val = 0.09 * (100 if "Ranged" in card["atk_type"] else 70)
    speed_val = {"Very Slow":60,"Slow":70,"Medium":80,"Fast":90,"Very Fast":100}[card["card_speed"]] * 0.16
    rng_factor = random.randint(60, 100) * 0.16
    return round(dmg+spd+rng+hp+type_val+speed_val+rng_factor)

def letter_grade(ovr):
    if ovr >= 98: return "Meta"
    elif ovr >= 95: return "A+"
    elif ovr >= 90: return "A"
    elif ovr >= 84: return "B"
    elif ovr >= 77: return "C"
    elif ovr >= 71: return "D"
    else: return "F"

# ==========================================================
# LEAGUE ENGINE
# ==========================================================
class ClashLeague:
    def __init__(self):
        self.season = 1
        self.cards = [generate_card(name) for name in CARD_NAMES]
        self.history = []
        self.calendar = self.generate_calendar()
        self.playoff_bracket = None
        self.awards = {}

    def generate_calendar(self):
        start_date = datetime.date(2025, 7, 9)
        games = []
        for i in range(SEASON_GAMES):
            date = start_date + datetime.timedelta(days=i*2)
            games.append({"game": i+1, "date": date, "played": False})
        return games

    # ==============================
    # SIMULATION
    # ==============================
    def simulate_game(self):
        c1, c2 = random.sample(self.cards, 2)
        ovr1, ovr2 = overall_rating(c1), overall_rating(c2)
        if ovr1 == ovr2:
            winner = random.choice([c1, c2])
        else:
            winner = c1 if ovr1 > ovr2 else c2
        loser = c2 if winner == c1 else c1

        winner["record"]["wins"] += 1
        loser["record"]["losses"] += 1
        winner["streak"] = max(1, winner["streak"]+1)
        loser["streak"] = min(-1, loser["streak"]-1)
        return winner, loser

    def simulate_games(self, n=1):
        results = []
        for _ in range(n):
            results.append(self.simulate_game())
        return results

    def simulate_full_season(self):
        games = SEASON_GAMES * (len(self.cards)//2)
        self.simulate_games(games)

    # ==============================
    # STANDINGS
    # ==============================
    def standings(self):
        standings = []
        for card in self.cards:
            w, l = card["record"]["wins"], card["record"]["losses"]
            ovr = overall_rating(card)
            standings.append({
                "Name": card["name"],
                "W": w,
                "L": l,
                "Win%": round(w / (w+l+0.001), 3),
                "OVR": ovr,
                "Grade": letter_grade(ovr),
                "Streak": card["streak"],
                "Logo": card["logo"]
            })
        df = pd.DataFrame(standings).sort_values(by=["W","OVR"], ascending=False)
        return df.reset_index(drop=True)

    # ==============================
    # PLAYOFFS
    # ==============================
    def run_playoffs(self):
        df = self.standings().head(PLAYOFF_TEAMS)
        teams = df["Name"].tolist()
        bracket = teams
        round_names = ["Round of 32","Round of 16","Quarterfinals","Semifinals","Finals"]
        series_wins = {"Round of 32":1,"Round of 16":1,"Quarterfinals":2,"Semifinals":2,"Finals":3}
        results = {}

        for rnd in round_names:
            winners = []
            rnd_results = []
            for i in range(0, len(bracket), 2):
                t1, t2 = bracket[i], bracket[i+1]
                c1 = next(c for c in self.cards if c["name"] == t1)
                c2 = next(c for c in self.cards if c["name"] == t2)
                needed = series_wins[rnd]
                s1 = s2 = 0
                while s1 < needed and s2 < needed:
                    w, l = self.simulate_game()
                    if w["name"] == c1["name"]: s1+=1
                    if w["name"] == c2["name"]: s2+=1
                winner = c1 if s1 > s2 else c2
                winners.append(winner["name"])
                rnd_results.append({"match": f"{t1} vs {t2}", "winner": winner["name"]})
            results[rnd] = rnd_results
            bracket = winners
        champion = bracket[0]
        champ_card = next(c for c in self.cards if c["name"] == champion)
        champ_card["championships"] += 1
        self.history.append({"season": self.season, "champion": champion, "playoffs": results})
        return champion, results

    # ==============================
    # AWARDS
    # ==============================
    def assign_awards(self):
        df = self.standings()
        mvp = df.iloc[0]["Name"]
        # most improved (compare last placement)
        improvements = []
        for c in self.cards:
            if len(c["placements"]) > 0:
                improvements.append((c["name"], c["placements"][-1]-df[df["Name"]==c["name"]].index[0]))
        most_improved = max(improvements, key=lambda x: x[1])[0] if improvements else mvp
        self.awards = {"MVP": mvp, "Most Improved": most_improved}
        for award, winner in self.awards.items():
            card = next(c for c in self.cards if c["name"] == winner)
            card["awards"].append({"season": self.season, "award": award})

    # ==============================
    # BALANCE CHANGES
    # ==============================
    def balance_changes(self):
        # randomly buff or nerf up to 11 cards
        buffed, nerfed = [], []
        for _ in range(11):
            card = random.choice(self.cards)
            if random.random() > 0.5:
                card["atk_dmg"] = int(card["atk_dmg"]*1.1)
                card["health"] = int(card["health"]*1.1)
                buffed.append(card["name"])
            else:
                card["atk_dmg"] = int(card["atk_dmg"]*0.9)
                card["health"] = int(card["health"]*0.9)
                nerfed.append(card["name"])
        return buffed, nerfed

    # ==============================
    # SAVE / LOAD
    # ==============================
    def save(self):
        data = {
            "season": self.season,
            "cards": self.cards,
            "history": self.history,
            "calendar": self.calendar
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)

    def load(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE) as f:
                data = json.load(f)
            self.season = data["season"]
            self.cards = data["cards"]
            self.history = data["history"]
            self.calendar = data["calendar"]
