import random
import pandas as pd

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------
def generate_random_name():
    prefixes = ['Crimson', 'Shadow', 'Thunder', 'Blaze', 'Frost', 'Iron', 'Golden', 'Storm', 'Night', 'Silver']
    suffixes = ['Dragon', 'Knight', 'Wizard', 'Golem', 'Phoenix', 'Goblin', 'Ranger', 'Beast', 'Slayer', 'Giant']
    return f"{random.choice(prefixes)} {random.choice(suffixes)}"

def generate_team_color():
    colors = ['Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Teal', 'Pink']
    return random.choice(colors)

# ------------------------------
# CARD CLASS
# ------------------------------
class Card:
    def __init__(self):
        self.name = generate_random_name()
        self.stats = {
            'atk': random.randint(50,100),
            'defense': random.randint(50,100),
            'hit_speed': random.randint(50,100),
            'speed': random.randint(50,100)
        }
        self.ovr_power = self.calculate_ovr()
        self.grade = None
        self.trend = '▲'
        self.elixir_base = round(random.uniform(1,10),1)
        self.elixir_current = self.elixir_base
        self.contribution_pct = 0
        self.clutch_play = False
        self.awards = []
        self.contracts = []

    def calculate_ovr(self):
        return round(sum(self.stats.values()) / len(self.stats),1)

    def update_elixir(self):
        self.elixir_current = max(1, min(10, self.ovr_power/10 + random.uniform(-0.5,0.5)))

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
    def __init__(self):
        self.name = generate_random_name()
        self.color = generate_team_color()
        self.cards = [Card(), Card()]
        self.wins = 0
        self.losses = 0
        self.played_games = []
        self.streak = 0

# ------------------------------
# LEAGUE CLASS
# ------------------------------
class League:
    def __init__(self):
        self.teams = [Team() for _ in range(30)]
        self.history = {'champions': [], 'awards': []}

    # Simulate single game between first card of two teams
    def simulate_game(self, team1, team2):
        card1 = team1.cards[0]
        card2 = team2.cards[0]

        stat_factor = (card1.ovr_power - card2.ovr_power)/100 * 0.75
        rng_factor = random.uniform(-0.25,0.25)
        total = stat_factor + rng_factor

        # Clutch plays
        card1.clutch_play = random.random() < 0.02
        card2.clutch_play = random.random() < 0.02

        # Score calculation
        if total > 0:
            score1, score2 = 3, -2
            if card1.clutch_play: score1 +=5
            team1.wins +=1
            team2.losses +=1
        else:
            score1, score2 = -2,3
            if card2.clutch_play: score2 +=5
            team2.wins +=1
            team1.losses +=1

        # Winning streak bonus
        if team1.wins >=5: score1 += team1.wins -4
        if team2.wins >=5: score2 += team2.wins -4

        # Update contributions
        card1.contribution_pct += max(0, score1)
        card2.contribution_pct += max(0, score2)

        # Update elixir & grades
        card1.update_elixir(); card2.update_elixir()
        card1.assign_grade(); card2.assign_grade()

        # Record game
        team1.played_games.append((team2.name, score1, score2))
        team2.played_games.append((team1.name, score2, score1))

        return score1, score2

    # Simulate full season: 40 games per team
    def simulate_season(self):
        for _ in range(40):
            teams = self.teams.copy()
            random.shuffle(teams)
            for i in range(0,len(teams),2):
                self.simulate_game(teams[i], teams[i+1])

    # Season summary as DataFrame for Streamlit
    def season_summary_df(self):
        data = []
        for t in self.teams:
            for c in t.cards:
                data.append({
                    'Team': t.name,
                    'Color': t.color,
                    'Card': c.name,
                    'OVR': c.ovr_power,
                    'Grade': c.grade,
                    'Elixir': c.elixir_current,
                    'Contribution': c.contribution_pct,
                    'Clutch': c.clutch_play
                })
        return pd.DataFrame(data)

    # Standings as DataFrame
    def standings_df(self):
        data = []
        for t in self.teams:
            data.append({
                'Team': t.name,
                'Color': t.color,
                'Wins': t.wins,
                'Losses': t.losses
            })
        return pd.DataFrame(data)

    # Assign awards
    def assign_awards(self):
        all_cards = [c for t in self.teams for c in t.cards]
        top_contrib = max(all_cards, key=lambda x: x.contribution_pct)
        top_score = max(all_cards, key=lambda x: x.ovr_power)
        mvp = max(all_cards, key=lambda x: x.contribution_pct + x.ovr_power/10)
        self.history['awards'].append({
            'MVP': mvp.name,
            'Top Contribution': top_contrib.name,
            'Top Scorer': top_score.name
        })
