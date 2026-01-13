import pandas as pd
import os

DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def debug_ids():
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv")) # Load all to search
    
    # Check ShotIDs for Game 1, End 1 vs End 2
    game1 = stones[(stones['CompetitionID']==0) & (stones['SessionID']==1) & (stones['GameID']==1)]
    
    print("\nShotIDs for Game 1, End 1:")
    print(game1[game1['EndID']==1]['ShotID'].sort_values().values)
    
    print("\nShotIDs for Game 1, End 2:")
    print(game1[game1['EndID']==2]['ShotID'].sort_values().values)
    
    # Also check if gbr_pp_ends keys are present in stones
    # Create manual key
    key = "0_1_1_1" # Comp 0, Sess 1, Game 1, End 1
    
    # Is this key in stones?
    # We saw stones for 0,1,1,1 in the head check.


if __name__ == "__main__":
    debug_ids()
