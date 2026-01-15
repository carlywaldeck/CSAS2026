
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    return ends, stones

def analyze_side_bias():
    ends, stones = load_data()
    pp_end_keys = ends[ends['PowerPlay'] > 0][['CompetitionID', 'SessionID', 'GameID', 'EndID']]
    pp_stones = pd.merge(stones, pp_end_keys, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    
    # Identify pre-placed positions
    initial_shots = pp_stones.sort_values('ShotID').groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).first().reset_index()
    
    CENTER_LINE_X = 750
    def get_side(x):
        if x < CENTER_LINE_X - 50: return "Left"
        if x > CENTER_LINE_X + 50: return "Right"
        return "Center"

    initial_shots['PPSide'] = initial_shots['stone_1_x'].apply(get_side)
    
    results = ends[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Result']]
    side_success = pd.merge(initial_shots, results, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    
    stats = side_success.groupby('PPSide')['Result'].agg(['mean', 'count'])
    print("\n--- Power Play Side Selection ---")
    print(stats)
    
    handle_stats = side_success.groupby(['PPSide', 'Handle'])['Result'].agg(['mean', 'count'])
    print("\n--- Side Success by Handle ---")
    print(handle_stats)

if __name__ == "__main__":
    analyze_side_bias()
