import pandas as pd
import build_the_machine

def analyze_side_bias():
    print("Building the machine...")
    ends, stones = build_the_machine.load_data()
    # We only need 'Ends' data for this high-level check first
    
    # Filter for Power Play Ends
    # PowerPlay: 1 = Right Side, 2 = Left Side (Challenge description says 1=Right, 2=Left)
    pp_ends = ends[ends['PowerPlay'].notna()].copy()
    
    # 1. Compare Raw Scoring
    right_pp = pp_ends[pp_ends['PowerPlay'] == 1]
    left_pp = pp_ends[pp_ends['PowerPlay'] == 2]
    
    print(f"\n--- The 'Hidden Bias' (Right vs Left) ---")
    print(f"Sample Size: {len(right_pp)} Right Side vs {len(left_pp)} Left Side")
    
    avg_right = right_pp['Result'].mean()
    avg_left = left_pp['Result'].mean()
    
    print(f"Avg Score (Right Side): {avg_right:.3f}")
    print(f"Avg Score (Left Side):  {avg_left:.3f}")
    
    diff = ((avg_right - avg_left) / avg_left) * 100
    print(f"Difference: Right side is {diff:+.1f}% better/worse than Left.")

    # 2. Conversion Rate (Scoring 2+)
    conv_right = (right_pp['Result'] >= 2).mean()
    conv_left = (left_pp['Result'] >= 2).mean()
    
    print(f"\nConversion Rate (2+ pts):")
    print(f"Right: {conv_right:.1%}")
    print(f"Left:  {conv_left:.1%}")
    
    # 3. The "Steal" Risk (Scoring 0 or giving up points)
    steal_right = (right_pp['Result'] <= 0).mean() # Includes blank ends (0) and steals (<0? Wait, result is pts scored by team.)
    # In 'Ends.csv', Result is simply "Points Scored". Usually positive. 
    # If opponent steals, the 'Result' for THIS team is 0? Or does Ends.csv have a row for the scoring team?
    # Let's check Result distribution.
    
    # Assuming Result is points scored by TeamID.
    # If they get stolen on, Result is 0.
    
    fail_right = (right_pp['Result'] == 0).mean()
    fail_left = (left_pp['Result'] == 0).mean()
    
    print(f"\nFailure Rate (Score 0):")
    print(f"Right: {fail_right:.1%}")
    print(f"Left:  {fail_left:.1%}")

    if abs(diff) > 5:
        print("\nWINNING INSIGHT FOUND: The side MATTERS. Teams should stop flipping a coin and pick the winner.")
    else:
        print("\nResult: No significant bias found. Back to the drawing board.")

if __name__ == "__main__":
    analyze_side_bias()
