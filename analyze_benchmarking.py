
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    teams = pd.read_csv(os.path.join(DATA_DIR, "Teams.csv"))
    games = pd.read_csv(os.path.join(DATA_DIR, "Games.csv"))
    return ends, stones, teams, games

def analyze_benchmarking():
    ends, stones, teams, games = load_data()
    
    # Target NOCs
    targets = ['USA', 'GBR', 'ITA', 'CAN']
    
    # Map TeamID to NOC
    team_map = teams.set_index('TeamID')['NOC'].to_dict()
    
    # Identify PP ends
    pp_ends = ends[ends['PowerPlay'] > 0].copy()
    pp_ends['NOC'] = pp_ends['TeamID'].map(team_map)
    
    # Filter for target groups
    target_ends = pp_ends[pp_ends['NOC'].isin(targets)].copy()
    
    # 1. Scoring Distribution
    def score_dist(x):
        return pd.Series({
            'AvgPoints': x.mean(),
            'P(0)': (x == 0).mean() * 100,
            'P(1)': (x == 1).mean() * 100,
            'P(2+)': (x >= 2).mean() * 100,
            'P(3+)': (x >= 3).mean() * 100
        })

    scores = target_ends.groupby('NOC')['Result'].apply(score_dist).unstack()
    
    # 2. Timing Distribution
    def timing_dist(x):
        return pd.Series({
            'Early (1-2)': (x <= 2).mean() * 100,
            'Mid (3-6)': ((x >= 3) & (x <= 6)).mean() * 100,
            'Late (7-8)': (x >= 7).mean() * 100
        })

    timing = target_ends.groupby('NOC')['EndID'].apply(timing_dist).unstack()
    
    # 3. Execution Quality (Points avg for first 3 shots)
    pp_keys = target_ends[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'NOC']]
    pp_stones = pd.merge(stones, pp_keys, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    first_3 = pp_stones.sort_values(['CompetitionID', 'SessionID', 'GameID', 'EndID', 'ShotID']).groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).head(3)
    
    execution = first_3.groupby('NOC')['Points'].mean().rename('ExecutionPts')
    
    # Combine Dashboard
    dashboard = pd.concat([scores, timing, execution], axis=1)
    
    print("\n--- International Power Play Benchmarking Dashboard ---")
    print(dashboard.to_string())
    
    # Task Mix
    TASK_MAP = {0: "Draw", 1: "Front", 2: "Guard", 3: "Raise", 4: "Wick", 5: "Freeze", 6: "Take-out"}
    pp_stones['TaskName'] = pp_stones['Task'].map(TASK_MAP).fillna("Other")
    task_mix = pp_stones.groupby(['NOC', 'TaskName']).size().unstack(fill_value=0)
    task_mix_pct = task_mix.div(task_mix.sum(axis=1), axis=0) * 100
    
    print("\n--- Task Mix Percentage (%) ---")
    print(task_mix_pct.to_string())

if __name__ == "__main__":
    analyze_benchmarking()
