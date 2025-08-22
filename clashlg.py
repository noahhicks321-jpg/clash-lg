# clashlg.py
import random
import pickle
from datetime import datetime, timedelta

# ------------------------------
# UTILITY FUNCTIONS
# ------------------------------
def generate_unique_names(prefix_list, used_names, count):
    names = []
    while len(names) < count:
        name = random.choice(prefix_list) + " " + random.choice(prefix_list)
        if name not in used_names:
            names.append(name)
            used_names.add(name)
    return names

def generate_logo():
    # Simple unicode logos
    logos = ["🔥","💎","⚡","🌟","🛡️","🏹","⚔️","🎯","🌀","🌈","🏆","🦄","🐉","🦅","🐺","🦁"]
    return random.choice(logos)

# ------------------------------
# CARD CLASS
# ------------------------------
class Card:
    def __init__(self, name):
        self.name = name
        self.icon = generate_logo()
        # Stats 0-100
        self.attack = round(random.uniform(40,100),1)
        self.defense = round(random.uniform(40,100),1)
        self.hit_speed = round(random.uniform(40,100),1)
        self.speed = round(random.uniform(40,100),1)
        # Derived stats
        self.ovr_power = round((self.attack*0.3 + self.defense*0.3 + self.hit_speed*0.2 + self.speed*0.2),1)
        self.grade = self.assign_grade()
        self.contribution_pct_value = 50.0
        self.clutch_pct_value = round(random.uniform(0,5),1)  # Starting clutch chance
        self.elixir_current = round(max(1,min(10,self.ovr_power/10)),1)
        self.dominance = 0.0
        # Score stats
        self.wins = 0
        self.losses = 0
        self.clutch_plays = 0
        self.damage_dealt = 0
        self.defensive_plays = 0
        # Contract history
        self.contracts = []

    def assign_grade(self):
        if self.ovr_power >= 90: return 'A+'
        elif self.ovr_power >= 80: return 'A'
        elif self.ovr_power >= 70: return 'B'
        elif self.ovr_power >= 60: return 'C'
        else: return 'D'

    def update_stats_post_game(self, won, damage, defense, clutch=False):
        if won: self.wins +=1
        else: self.losses +=1
        self.damage_dealt += damage
        self.defensive_plays += defense
        if clutch:
            self.clutch_plays +=1
        # Update OVR slightly with performance
        perf = (damage + defense + (clutch*50))/300*10
        self.ovr_power = round(min(100,max(1,self.ovr_power + perf)),1)
        self.grade = self.assign_grade()
        self.elixir_current = round(max(1,min(10,self.ovr_power/10)),1)

    def clutch_pct(self):
        return round(min(100, self.clutch_plays*2),1)

# ------------------------------
# TEAM CLASS
# ------------------------------
class Team:
    def __init__(self, name):
        self.name = name
        self.logo = generate_logo()
        self.cards = []
        self.wins = 0
        self.losses = 0
        self.streak = ""
        self.played_games = []

    def add_card(self, card):
        self.cards.append(card)

    def update_streak(self):
        streak = 0
        last_result = None
        for game in self.played_games:
            result = game[1] > game[2]
            if last_result == result:
                streak +=1
            else:
                streak = 1
            last_result = result
        self.streak = f"{'W' if last_result else 'L'}{streak}" if self.played_games else "N/A"

# ------------------------------
# LEAGUE CLASS
# ------------------------------
class League:
    def __init__(self):
        self.teams = []
        self.cards = []
        self.season = 1
        self.history = []
        self.playoffs = []

    def create_teams_and_cards(self):
        used_names = set()
        prefixes = ["Red","Blue","Green","Golden","Silver","Shadow","Dragon","Knight","Phoenix","Storm","Thunder","Frost","Iron","Wild","Fire","Dark"]
        team_names = generate_unique_names(prefixes, used_names, 30)
        card_names = generate_unique_names(prefixes, used_names, 80)
        # Create cards
        self.cards = [Card(name) for name in card_names]
        # Assign 2 cards per team
        for i in range(30):
            team = Team(team_names[i])
            team.add_card(self.cards[i*2])
            team.add_card(self.cards[i*2+1])
            self.teams.append(team)

    def assign_contributions(self):
        for t in self.teams:
            total_ovr = sum([c.ovr_power for c in t.cards])
            for c in t.cards:
                c.contribution_pct_value = round(c.ovr_power / total_ovr * 100,1) if total_ovr>0 else 50

    def simulate_game(self, team1, team2):
        score1 = sum([c.ovr_power for c in team1.cards])*0.75 + random.uniform(0,50)
        score2 = sum([c.ovr_power for c in team2.cards])*0.75 + random.uniform(0,50)
        # Clutch
        for c in team1.cards + team2.cards:
            clutch = random.random()<0.02
            c.update_stats_post_game(score1>score2 if c in team1.cards else score2>score1,
                                     damage=random.randint(50,200),
                                     defense=random.randint(20,100),
                                     clutch=clutch)
        # Update team results
        if score1>score2: team1.wins+=1; team2.losses+=1
        else: team2.wins+=1; team1.losses+=1
        team1.played_games.append((team2.name, score1, score2))
        team2.played_games.append((team1.name, score2, score1))
        team1.update_streak()
        team2.update_streak()
        self.assign_contributions()
        return score1, score2

    def simulate_full_season(self):
        for _ in range(40):
            for i in range(0,len(self.teams),2):
                self.simulate_game(self.teams[i], self.teams[i+1])

    def calculate_dominance(self):
        top_ovr = max([c.ovr_power for c in self.cards])
        for c in self.cards:
            c.dominance = round(c.ovr_power/top_ovr*100,1)

    def top_meta_cards(self, top_n=10):
        self.calculate_dominance()
        return sorted(self.cards, key=lambda x: x.ovr_power, reverse=True)[:top_n]

    # ------------------------------
    # SAVE / LOAD LEAGUE
    # ------------------------------
    def save_league(self, filename="league_save.pkl"):
        with open(filename,"wb") as f:
            pickle.dump(self,f)

    @staticmethod
    def load_league(filename="league_save.pkl"):
        with open(filename,"rb") as f:
            return pickle.load(f)

# ------------------------------
# INITIALIZE LEAGUE
# ------------------------------
league = League()
league.create_teams_and_cards()
league.assign_contributions()
league.calculate_dominance()
