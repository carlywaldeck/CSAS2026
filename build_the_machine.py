import pandas as pd
import os

# --- STEP 1: SETUP ---
DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"

def load_data():
    """Loads the necessary CSV files."""
    print("Loading data...")
    # TODO: Load 'Ends.csv' and 'Stones.csv' into pandas DataFrames
    # ends = pd.read_csv(...)
    # stones = pd.read_csv(...)
    
    # Placeholder return (Replace these with real dataframes when you write the code above)
    ends = pd.read_csv(os.path.join(DATA_DIR, "Ends.csv"))
    stones = pd.read_csv(os.path.join(DATA_DIR, "Stones.csv"))
    return ends, stones

def create_master_dataframe(ends, stones):
    """
    Merges Stones with Ends so every stone has a 'Result' (Score).
    """
    print("Merging data...")
    
    # --- EXPLANATION ---
    # We are creating a "Barcode" for every end. 
    # By gluing the IDs together (Comp_Sess_Game_End), we get a unique string like "0_1_1_1".
    # This lets us verify that Stone X belongs exactly to End Y.
    
    # 1. Create the Key for Stones
    stones['EndKey'] = (
        stones['CompetitionID'].astype(str) + "_" + 
        stones['SessionID'].astype(str) + "_" + 
        stones['GameID'].astype(str) + "_" + 
        stones['EndID'].astype(str)
    )
    
    # 2. Create the Key for Ends
    ends['EndKey'] = (
        ends['CompetitionID'].astype(str) + "_" + 
        ends['SessionID'].astype(str) + "_" + 
        ends['GameID'].astype(str) + "_" + 
        ends['EndID'].astype(str)
    )
    
    # 3. Merge them!
    # We take the Stones (our base) and attach the 'Result' and 'PowerPlay' info from Ends.
    # on='EndKey' tells pandas to match rows where the Barcodes are identical.
    master_df = pd.merge(
        stones, 
        ends[['EndKey', 'Result', 'PowerPlay']], # Only take what we need
        on='EndKey', 
        how='left'
    )
    
    return master_df

if __name__ == "__main__":
    ends_df, stones_df = load_data()
    master_df = create_master_dataframe(ends_df, stones_df)
    
    if not master_df.empty:
        print("\nSuccess! Here is the Master Dataframe:")
        print(master_df.head())
        print(f"Total Rows: {len(master_df)}")
    else:
        print("\nMaster Dataframe is empty. Fill in the TODOs to build the machine!")
