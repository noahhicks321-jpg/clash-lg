import random
import pandas as pd

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def generate_unique_name(used_names, prefixes, suffixes):
    while True:
        name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
        if name not in used_names:
            used_names.add(name)
            return name

def generate_team_color():
    colors = ['Red','Blue','Green','Yellow','Purple','Orange','Teal','Pink','Brown','Cyan','Magenta']
    return random.choice(colors)

def generate_team_logo():
    logos = ['🔥','⚡','🛡️','🗡️','🐉','🦅','🦄','🐺','🦁','👑','🧿','🌪️']
    return random.choice(logos)

def generate_card_icon():
    icons = ['⚔️','🏹','🪄','🛡️','💥','🧿','🔥','🧱','🌪️','🦴','🩸','⚡']
    return random.choice(icons)

# ------------------------------
# CARD CLASS
# ------------------------------
class Card:
    def __init__(self, used_names):
        prefixes = ['Crimson','Shadow','Thunder','Blaze','Frost','Iron','Golden','Storm','Night','Silver','Emerald','Obsidian']
        suffixes = ['Dragon','Knight','Wizard','Golem','Phoenix','Goblin','Ranger','Beast','Slayer','Giant','Sentinel','Warden']
        self.name = generate_unique_name(used_names, prefixes, suffixes)
        self.icon = generate_card_icon()
        self.stats = {
            'atk': random.randint(50,100),
            'defense': random.randint(50,100),
            'hit_speed': random.randint(50,100),
            'speed': random.randint(50,100)
        }
        self.ovr_power = round(sum(self.stats.values())/len(self.stats),1)
        self.grade = None
        self.trend = '▲'
        self.elixir_base = round(random.uniform(1,10),1)
        self.elixir_current = self.elixir_base
        self.contribution = 0
        self.clutch_chance = 0
        self.games_played = 0
        self.awards = []
        self.contracts = []

    def update_after_game(self, points, clutch_occurred):
        self.contribution += points
        self.games_played += 1
        if clutch_occurred:
            self.clutch_chance += 1
        self.update_elixir()
        self.assign_grade()
        self.ovr_power = round(sum(self.stats.values())/len(self.stats),1)

    def contribution_pct(self):
        if self.games_played == 0: return 0
        return round((self.contribution / (self.games_played * 10))*100,1)  # assuming 10 max pts per game

    def clutch_pct(self):
        if self.games_played == 0: return 0
        return round((self.clutch_chance / self.games_played)*100,1)

    def update_elixir(self):
        self.elixir_current = round(max(1, min(10, self.ovr_power/10 + random.uniform(-0.5,0.5))),1)

    def assign_grade(self):
        ovr = self.ovr_power
        if ovr >= 90: self.grade = 'A+'
        elif ovr >= 80: self.grade = 'A'
        elif ovr >= 70: self.grade = 'B'
        elif ovr >= 60: self.grade = 'C'
        else: self.grade = 'D'

# ------------------------------
# TEAM CLASS
# ------------------------------
class Team:
    used_names = set()
    def __init__(self):
        prefixes = ['Crimson','Shadow','Thunder','Blaze','Frost','Iron','Golden','Storm','Night','Silver','Emerald','Obsidian']
        suffixes = ['Titans','Legends','Guardians','Rangers','Warriors','Knights','Sentinels','Beasts','Slayers','Giants','Wardens','Phoenix']
        self.name = generate_unique_name(Team.used_names, prefixes, suffixes)
        self.color = generate_team_color()
        self.logo = generate_team_logo()
        self.cards = [Card(Team.used_names), Card(Team.used_names)]
        self.wins = 0
        self.losses = 0
        self.played_games = []

# ------------------------------
# LEAGUE CLASS
# ------------------------------
class League:
    def __init__(self):
        self.teams = [Team() for _ in range(30)]
        self.history = {'champions': [], 'awards': []}

    def simulate_game(self, team1, team2):
        card1 = team1.cards[0]
        card2 = team2.cards[0]

        stat_factor = (card1.ovr_power - card2.ovr_power)/100 * 0.75
        rng_factor = random.uniform(-0.25,0.25)
        total = stat_factor + rng_factor

        card1_clutch = random.random() < 0.02
        card2_clutch = random.random() < 0.02

        if total > 0:
            score1, score2 = 3, -2
            if card1_clutch: score1 +=5
            team1.wins +=1
            team2.losses +=1
        else:
            score1, score2 = -2,3
            if card2_clutch: score2 +=5
            team2.wins +=1
            team1.losses +=1

        if team1.wins >=5: score1 += team1.wins -4
        if team2.wins >=5: score2 += team2.wins -4

        card1.update_after_game(score1, card1_clutch)
        card2.update_after_game(score2, card2_clutch)

        team1.played_games.append((team2.name, score1, score2))
        team2.played_games.append((team1.name, score2, score1))

        return score1, score2

    def simulate_full_season(self):
        for _ in range(40):
            teams = self.teams.copy()
            random.shuffle(teams)
            for i in range(0,len(teams),2):
                self.simulate_game(teams[i], teams[i+1])

    # ------------------------------
    # DATAFRAMES
    # ------------------------------
    def standings_df(self):
        data = []
        for t in self.teams:
            data.append({
                'Logo': t.logo,
                'Team': t.name,
                'Color': t.color,
                'Wins': t.wins,
                'Losses': t.losses
            })
        return pd.DataFrame(data)

    def cards_df(self):
        data = []
        for t in self.teams:
            for c in t.cards:
                data.append({
                    'Team Logo': t.logo,
                    'Team': t.name,
                    'Color': t.color,
                    'Card Icon': c.icon,
                    'Card': c.name,
                    'Attack': c.stats['atk'],
                    'Defense': c.stats['defense'],
                    'Hit Speed': c.stats['hit_speed'],
                    'Speed': c.stats['speed'],
                    'OVR': c.ovr_power,
                    'Grade': c.grade,
                    'Elixir': c.elixir_current,
                    'Contribution %': c.contribution_pct(),
                    'Clutch %': c.clutch_pct()
                })
        return pd.DataFrame(data)

    def team_info_df(self):
        data = []
        for t in self.teams:
            for c in t.cards:
                data.append({
                    'Team Logo': t.logo,
                    'Team': t.name,
                    'Color': t.color,
                    'Card Icon': c.icon,
                    'Card': c.name,
                    'OVR': c.ovr_power,
                    'Grade': c.grade,
                    'Elixir': c.elixir_current,
                    'Contribution %': c.contribution_pct(),
                    'Clutch %': c.clutch_pct()
                })
        return pd.DataFrame(data)

    # ------------------------------
    # AWARDS
    # ------------------------------
    def assign_awards(self):
        all_cards = [c for t in self.teams for c in t.cards]
        top_contrib = max(all_cards, key=lambda x: x.contribution_pct())
        top_score = max(all_cards, key=lambda x: x.ovr_power)
        mvp = max(all_cards, key=lambda x: x.contribution_pct() + x.ovr_power/10)
        self.history['awards'].append({
            'MVP': mvp.name,
            'Top Contribution': top_contrib.name,
            'Top Scorer': top_score.name
        })

    def top_meta_cards(self, n=10):
        all_cards = [c for t in self.teams for c in t.cards]
        return sorted(all_cards, key=lambda x: x.ovr_power, reverse=True)[:n]
