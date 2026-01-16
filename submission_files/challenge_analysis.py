"""
CSAS 2026 Curling Data Challenge
Power Play Strategy Analysis

Analyzes when teams should deploy Power Plays in Mixed Doubles Curling.
Calculates metrics like Traffic, execution scores, and deployment patterns.

Author: [Your Name]
Date: 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Constants from the challenge description
BUTTON_X = 750
BUTTON_Y = 800
HOUSE_RADIUS = 600
CENTER_CORRIDOR = 200
SENTINEL = 4095  # stone knocked off
NOT_THROWN = 0

# Data directory
DATA_DIR = "/Users/tsobazy/Desktop/curling/CSAS2026"


def load_data():
    """Load the CSV files."""
    stones_path = os.path.join(DATA_DIR, "Stones.csv")
    ends_path = os.path.join(DATA_DIR, "Ends.csv")
    stones = pd.read_csv(stones_path)
    ends = pd.read_csv(ends_path)
    return stones, ends


def distance_to_button(x, y):
    """Calculate distance from stone to button using distance formula."""
    dx = x - BUTTON_X
    dy = y - BUTTON_Y
    return np.sqrt(dx*dx + dy*dy)


def calculate_traffic(stones):
    """
    Calculate Traffic metric - number of stones in the house.
    Traffic is like congestion - more stones = harder to score.
    """
    print("\n" + "="*70)
    print("1. TRAFFIC CALCULATION")
    print("="*70)
    
    # Make copy so we don't mess up original
    df = stones.copy()
    traffic_list = []
    
    # Loop through each shot
    for i in range(len(df)):
        row = df.iloc[i]
        count = 0
        
        # Check all 12 stone positions
        for stone_num in range(1, 13):
            x_col = 'stone_' + str(stone_num) + '_x'
            y_col = 'stone_' + str(stone_num) + '_y'
            
            x = row[x_col]
            y = row[y_col]
            
            # Skip if not valid
            if pd.isna(x) or pd.isna(y):
                continue
            if x == NOT_THROWN or y == NOT_THROWN:
                continue
            if x == SENTINEL or y == SENTINEL:
                continue
            
            # Check if in house
            dist = distance_to_button(x, y)
            if dist <= HOUSE_RADIUS:
                count += 1
        
        traffic_list.append(count)
    
    df['Traffic'] = traffic_list
    
    # Print stats
    print(f"\nTotal shots: {len(df):,}")
    print(f"Average Traffic: {df['Traffic'].mean():.2f}")
    print(f"Max Traffic: {df['Traffic'].max()}")
    
    # Stats by end
    print("\nTraffic by End:")
    end_stats = df.groupby('EndID')['Traffic'].agg(['mean', 'max'])
    print(end_stats.round(2))
    
    return df


def calculate_pprs(stones, ends):
    """
    Power Play Readiness Score - measures center congestion in early ends.
    Only calculated for ends 1-2.
    """
    print("\n" + "="*70)
    print("2. POWER PLAY READINESS SCORE")
    print("="*70)
    
    # Filter to ends 1-2
    early = stones[stones['EndID'].isin([1, 2])].copy()
    pprs_list = []
    
    for i in range(len(early)):
        row = early.iloc[i]
        center_count = 0
        
        for stone_num in range(1, 13):
            x_col = 'stone_' + str(stone_num) + '_x'
            y_col = 'stone_' + str(stone_num) + '_y'
            
            x = row[x_col]
            y = row[y_col]
            
            if pd.isna(x) or pd.isna(y):
                continue
            if x == NOT_THROWN or y == NOT_THROWN:
                continue
            if x == SENTINEL or y == SENTINEL:
                continue
            
            # Center corridor: |X - 750| < 200
            if abs(x - BUTTON_X) < CENTER_CORRIDOR:
                center_count += 1
        
        pprs_list.append(center_count)
    
    early['PPRS'] = pprs_list
    
    print(f"\nShots in Ends 1-2: {len(early):,}")
    print(f"Average PPRS: {early['PPRS'].mean():.2f}")
    print(f"Max PPRS: {early['PPRS'].max()}")
    
    return early


def analyze_deployment(ends):
    """Analyze when Power Plays are deployed and how effective they are."""
    print("\n" + "="*70)
    print("3. POWER PLAY DEPLOYMENT ANALYSIS")
    print("="*70)
    
    # Get Power Play ends
    pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] > 0)].copy()
    
    print(f"\nTotal Power Plays: {len(pp)}")
    print(f"Average Points: {pp['Result'].mean():.2f}")
    
    # Big End rate
    big_ends = (pp['Result'] >= 3).sum()
    big_end_rate = (big_ends / len(pp)) * 100
    print(f"Big End Rate (3+ pts): {big_end_rate:.1f}%")
    
    # By end number
    print("\n" + "-" * 70)
    print("By End Number:")
    print("-" * 70)
    
    end_grouped = pp.groupby('EndID').agg({
        'Result': ['count', 'mean']
    })
    end_grouped.columns = ['Count', 'AvgPoints']
    end_grouped['Pct'] = (end_grouped['Count'] / len(pp) * 100).round(1)
    print(end_grouped)
    
    # Categorize
    def get_category(end_id):
        if end_id <= 2:
            return 'Early'
        elif end_id >= 7:
            return 'Late'
        else:
            return 'Middle'
    
    pp['Category'] = pp['EndID'].apply(get_category)
    
    # Stats by category
    cat_stats = pp.groupby('Category')['Result'].agg(['mean', 'count'])
    big_end_by_cat = pp.groupby('Category').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    )
    
    print("\n" + "-" * 70)
    print("By Category:")
    print("-" * 70)
    print("\nAverage Points:")
    print(cat_stats['mean'])
    print("\nCount:")
    print(cat_stats['count'])
    print("\nBig End Rate:")
    print(big_end_by_cat.round(2))
    
    # Early PP analysis (key finding)
    early_pp = pp[pp['Category'] == 'Early']
    print("\n" + "-" * 70)
    print("Early Power Plays (Ends 1-2):")
    print("-" * 70)
    print(f"Count: {len(early_pp)}")
    if len(early_pp) > 0:
        print(f"Average: {early_pp['Result'].mean():.2f}")
        print(f"Percentage: {len(early_pp)/len(pp)*100:.2f}%")
    else:
        print("None found")
    
    return pp


def analyze_shot_types(stones):
    """Compare execution scores for Draws vs Wicks."""
    print("\n" + "="*70)
    print("4. SHOT ACCURACY - Draws vs Wicks")
    print("="*70)
    
    # Filter to each shot type
    draws = stones[stones['Task'] == 0]
    wicks = stones[stones['Task'] == 4]
    
    draw_avg = draws['Points'].mean()
    wick_avg = wicks['Points'].mean()
    
    print(f"\nDraws (Task 0):")
    print(f"  Count: {len(draws):,}")
    print(f"  Avg Score: {draw_avg:.2f}/4.0")
    print(f"  Std Dev: {draws['Points'].std():.2f}")
    
    print(f"\nWicks (Task 4):")
    print(f"  Count: {len(wicks):,}")
    print(f"  Avg Score: {wick_avg:.2f}/4.0")
    print(f"  Std Dev: {wicks['Points'].std():.2f}")
    
    if len(draws) > 0 and len(wicks) > 0:
        diff = draw_avg - wick_avg
        pct = (diff / wick_avg) * 100
        print(f"\nDifference: {diff:+.2f} points ({pct:+.1f}%)")
        print(f"Execution Gap: Draws are {pct:.1f}% better")
    
    return draws, wicks


def analyze_traffic_effect(stones_with_traffic, ends):
    """
    Analyze how Traffic affects Power Play scoring.
    This is the Traffic Tax finding.
    """
    print("\n" + "="*70)
    print("5. TRAFFIC IMPACT ON POWER PLAYS")
    print("="*70)
    
    # Merge to get results
    merged = pd.merge(
        stones_with_traffic,
        ends[['CompetitionID', 'SessionID', 'GameID', 'EndID', 'Result', 'PowerPlay']],
        on=['CompetitionID', 'SessionID', 'GameID', 'EndID'],
        how='inner'
    )
    
    # Only Power Play ends
    pp_stones = merged[merged['PowerPlay'].notna() & (merged['PowerPlay'] > 0)].copy()
    
    # Categorize Traffic
    def categorize_traffic(t):
        if t <= 2:
            return 'Low (0-2)'
        elif t <= 4:
            return 'Medium (3-4)'
        else:
            return 'High (5+)'
    
    pp_stones['TrafficCat'] = pp_stones['Traffic'].apply(categorize_traffic)
    
    # Stats by Traffic level
    traffic_stats = pp_stones.groupby('TrafficCat')['Result'].agg(['mean', 'count'])
    big_end_by_traffic = pp_stones.groupby('TrafficCat').apply(
        lambda x: (x['Result'] >= 3).sum() / len(x) * 100
    )
    
    print(f"\nTotal PP shots: {len(pp_stones):,}")
    print("\nAverage Points by Traffic:")
    print(traffic_stats['mean'].round(2))
    print("\nCount by Traffic:")
    print(traffic_stats['count'])
    print("\nBig End Rate by Traffic:")
    print(big_end_by_traffic.round(2))
    
    # Calculate Traffic Tax
    low = pp_stones[pp_stones['TrafficCat'] == 'Low (0-2)']
    high = pp_stones[pp_stones['TrafficCat'] == 'High (5+)']
    
    if len(low) > 0 and len(high) > 0:
        low_avg = low['Result'].mean()
        high_avg = high['Result'].mean()
        tax = ((high_avg - low_avg) / low_avg) * 100
        
        print(f"\n" + "-" * 70)
        print(f"TRAFFIC TAX:")
        print(f"Low Traffic: {low_avg:.2f} points")
        print(f"High Traffic: {high_avg:.2f} points")
        print(f"Tax: {tax:+.1f}%")
        
        if tax < 0:
            print(f"\nFinding: High traffic reduces efficiency by {abs(tax):.1f}%")
    
    return pp_stones


def compare_teams(ends, stones):
    """Compare GBR vs Italy Power Play performance."""
    print("\n" + "="*70)
    print("6. TEAM COMPARISON: GBR vs Italy")
    print("="*70)
    
    # Try to load teams
    try:
        teams = pd.read_csv(os.path.join(DATA_DIR, "Teams.csv"))
    except:
        print("Couldn't load Teams.csv")
        return None
    
    # Find team IDs
    gbr_ids = teams[teams['NOC'] == 'GBR']['TeamID'].unique().tolist()
    ita_ids = teams[teams['NOC'] == 'ITA']['TeamID'].unique().tolist()
    
    if len(gbr_ids) == 0 or len(ita_ids) == 0:
        print("GBR or Italy teams not found")
        return None
    
    print(f"\nGBR teams: {len(gbr_ids)}")
    print(f"Italy teams: {len(ita_ids)}")
    
    # Get Power Play ends
    pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] > 0)].copy()
    
    gbr_pp = pp[pp['TeamID'].isin(gbr_ids)]
    ita_pp = pp[pp['TeamID'].isin(ita_ids)]
    
    print("\n" + "-" * 70)
    print("Performance Comparison:")
    print("-" * 70)
    
    # GBR stats
    if len(gbr_pp) > 0:
        gbr_avg = gbr_pp['Result'].mean()
        gbr_big = (gbr_pp['Result'] >= 3).sum() / len(gbr_pp) * 100
        gbr_std = gbr_pp['Result'].std()
        print(f"\nGBR:")
        print(f"  Sample: {len(gbr_pp)}")
        print(f"  Avg Points: {gbr_avg:.2f}")
        print(f"  Big End Rate: {gbr_big:.1f}%")
        print(f"  Std Dev: {gbr_std:.2f}")
    else:
        gbr_avg = 0
        gbr_big = 0
        gbr_std = 0
        print("\nGBR: No data")
    
    # Italy stats
    if len(ita_pp) > 0:
        ita_avg = ita_pp['Result'].mean()
        ita_big = (ita_pp['Result'] >= 3).sum() / len(ita_pp) * 100
        ita_std = ita_pp['Result'].std()
        print(f"\nItaly:")
        print(f"  Sample: {len(ita_pp)}")
        print(f"  Avg Points: {ita_avg:.2f}")
        print(f"  Big End Rate: {ita_big:.1f}%")
        print(f"  Std Dev: {ita_std:.2f}")
    else:
        ita_avg = 0
        ita_big = 0
        ita_std = 0
        print("\nItaly: No data")
    
    return {
        'gbr_avg': gbr_avg,
        'ita_avg': ita_avg,
        'gbr_std': gbr_std,
        'ita_std': ita_std
    }


def make_plot(ends):
    """Create bar chart of Power Play effectiveness by end."""
    print("\n" + "="*70)
    print("7. VISUALIZATION")
    print("="*70)
    
    # Get Power Play ends
    pp = ends[ends['PowerPlay'].notna() & (ends['PowerPlay'] > 0)].copy()
    
    # Group by end
    by_end = pp.groupby('EndID').agg({
        'Result': ['mean', 'count', 'std']
    }).reset_index()
    by_end.columns = ['EndID', 'AvgPoints', 'Count', 'StdDev']
    
    # Make plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(by_end['EndID'], by_end['AvgPoints'], 
                  yerr=by_end['StdDev'].fillna(0),
                  capsize=5, alpha=0.7, color='steelblue', edgecolor='black')
    
    ax.set_xlabel('End Number', fontsize=12, fontweight='bold')
    ax.set_ylabel('Average Points Scored', fontsize=12, fontweight='bold')
    ax.set_title('Power Play Effectiveness by End Number', fontsize=14, fontweight='bold')
    ax.set_xticks(range(1, 9))
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add count labels
    for i in range(len(by_end)):
        end = by_end.iloc[i]
        ax.text(end['EndID'], end['AvgPoints'] + end['StdDev'] + 0.05,
                f'n={int(end["Count"])}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    # Save
    out_path = os.path.join(DATA_DIR, 'power_play_by_end.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"\nSaved to: {out_path}")
    plt.close()


def main():
    """Main function to run all analyses."""
    print("="*70)
    print("CSAS 2026 CURLING ANALYSIS")
    print("Power Play Strategy Analysis")
    print("="*70)
    
    # Load data
    print("\nLoading data...")
    stones, ends = load_data()
    print(f"Loaded {len(stones):,} shots and {len(ends):,} ends")
    
    # Run analyses
    stones_traffic = calculate_traffic(stones)
    early_pprs = calculate_pprs(stones, ends)
    pp_deployment = analyze_deployment(ends)
    draws, wicks = analyze_shot_types(stones)
    traffic_analysis = analyze_traffic_effect(stones_traffic, ends)
    team_comp = compare_teams(ends, stones)
    make_plot(ends)
    
    # Summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70)
    print("\nKey Findings:")
    print(f"  Avg Traffic: {stones_traffic['Traffic'].mean():.2f}")
    print(f"  Total Power Plays: {len(pp_deployment)}")
    print(f"  Draw accuracy: {draws['Points'].mean():.2f}/4.0")
    print(f"  Wick accuracy: {wicks['Points'].mean():.2f}/4.0")
    
    gap = draws['Points'].mean() - wicks['Points'].mean()
    gap_pct = (gap / wicks['Points'].mean()) * 100
    print(f"  Execution Gap: {gap:.2f} points ({gap_pct:.1f}%)")


if __name__ == "__main__":
    main()
