
import pandas as pd
import numpy as np
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

TASK_MAP = {
    0: "Draw", 1: "Front", 2: "Guard", 3: "Raise", 4: "Wick", 5: "Freeze",
    6: "Take-out", 7: "Hit and Roll", 8: "Clearing", 9: "Double Take-out",
    10: "Promotion Take-out", 11: "Through"
}

def load_data():
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    return ends, stones

def analyze_sequences():
    ends, stones = load_data()
    
    # Filter for PP ends only
    pp_ends = ends[ends['PowerPlay'] > 0].copy()
    pp_keys = pp_ends[['CompetitionID', 'SessionID', 'GameID', 'EndID']]
    
    # Merge with stones
    pp_stones = pd.merge(stones, pp_keys, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    
    # Sort and take first 3 shots of each end
    pp_stones = pp_stones.sort_values(['CompetitionID', 'SessionID', 'GameID', 'EndID', 'ShotID'])
    first_3 = pp_stones.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).head(3).copy()
    
    # Map task names
    first_3['TaskName'] = first_3['Task'].map(TASK_MAP).fillna("Other")
    
    # Pivot to get sequences per end
    # We want a string like "Task1 -> Task2 -> Task3"
    sequences = first_3.groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID'])['TaskName'].apply(lambda x: " -> ".join(x)).reset_index()
    
    # Count failure modes (shots with points = 0)
    failures = first_3[first_3['Points'] == 0].groupby(['CompetitionID', 'SessionID', 'GameID', 'EndID']).size().reset_index(name='FailCount')
    
    # Merge with end results
    final_df = pd.merge(sequences, pp_ends[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Result']], on=['CompetitionID', 'SessionID', 'GameID', 'EndID'])
    final_df = pd.merge(final_df, failures, on=['CompetitionID', 'SessionID', 'GameID', 'EndID'], how='left').fillna(0)
    
    # Group by sequence
    seq_stats = final_df.groupby('TaskName')['Result'].agg(['mean', 'count']).rename(columns={'mean': 'AvgResult'})
    
    # Probabilities
    def prob_score(x, score):
        return (x >= score).mean() * 100

    seq_probs = final_df.groupby('TaskName')['Result'].apply(lambda x: pd.Series({
        'P(0)': (x == 0).mean() * 100,
        'P(1)': (x == 1).mean() * 100,
        'P(2)': (x == 2).mean() * 100,
        'P(3+)': (x >= 3).mean() * 100
    })).unstack()
    
    # Combine stats
    full_stats = pd.concat([seq_stats, seq_probs], axis=1)
    
    print("\n--- Power Play Opening Script Analysis (Shots 1-3) ---")
    # Top 10 most common scripts
    top_scripts = full_stats.sort_values('count', ascending=False).head(10)
    print(top_scripts.to_string())
    
    # Failure analysis
    fail_stats = final_df.groupby('TaskName')['FailCount'].mean().sort_values(ascending=False).head(10)
    print("\n--- Avg Failures (Points=0) in First 3 Shots by Script ---")
    print(fail_stats)

if __name__ == "__main__":
    analyze_sequences()
