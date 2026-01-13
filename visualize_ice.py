import pandas as pd
import matplotlib.pyplot as plt
import build_the_machine

def draw_rink(ax):
    """Draws a realistic Curling Sheet House."""
    # Dimensions based on Challenge Data
    # Width: ~1500 units (~15ft) -> Scale: ~100 units = 1ft
    CENTER_X = 750
    TEE_Y = 800         # Center of House
    BACK_Y = 200        # Back Line
    HOG_Y = 2900        # Hog Line
    
    # 1. The Ice Surface (Background)
    ax.set_facecolor('#F0F8FF') # AliceBlue - looks icy!
    
    # 2. Main Lines
    # Center Line (Vertical)
    ax.axvline(x=CENTER_X, color='black', alpha=0.3, linestyle='-')
    
    # Tee Line (Horizontal through button)
    ax.axhline(y=TEE_Y, color='black', alpha=0.3, linestyle='-')
    
    # Back Line 
    ax.axhline(y=BACK_Y, color='black', alpha=1.0, linewidth=2, label="Back Line")
    
    # Hog Line (Far away)
    ax.axhline(y=HOG_Y, color='#A52A2A', alpha=0.7, linewidth=4, label="Hog Line") 
    # (Brown/Red is common for Hog Lines)

    # 3. The House (Rings)
    # Radii: 12ft (~600), 8ft (~400), 4ft (~200), Button
    # Colors: Blue (Outer), White (8ft), Red (4ft), White (Button)
    
    # 12ft Ring (Blue)
    c12 = plt.Circle((CENTER_X, TEE_Y), 600, color='#003366', fill=True, alpha=0.2)
    c12_outline = plt.Circle((CENTER_X, TEE_Y), 600, color='#003366', fill=False, linewidth=2)
    ax.add_artist(c12)
    ax.add_artist(c12_outline)
    
    # 8ft Ring (White)
    c8 = plt.Circle((CENTER_X, TEE_Y), 400, color='white', fill=True)
    c8_outline = plt.Circle((CENTER_X, TEE_Y), 400, color='black', fill=False, linewidth=1)
    ax.add_artist(c8)
    ax.add_artist(c8_outline)
    
    # 4ft Ring (Red)
    c4 = plt.Circle((CENTER_X, TEE_Y), 200, color='#CC0000', fill=True)
    ax.add_artist(c4)
    
    # Button (White)
    btn = plt.Circle((CENTER_X, TEE_Y), 50, color='white', fill=True)
    ax.add_artist(btn)

def visualize():
    print("Building realistic visualization...")
    ends, stones = build_the_machine.load_data()
    df = build_the_machine.create_master_dataframe(ends, stones)
    
    # Filter for Setup Phase (Shots 1-4)
    df['ShotRank'] = df.groupby('EndKey')['ShotID'].rank(method='first').astype(int)
    setup = df[df['ShotRank'] <= 4].copy()
    
    # Split outcomes
    winners = setup[setup['Result'] >= 3] # Big Score
    losers = setup[setup['Result'] <= 1]  # Low Score/Steal
    
    # Sample outcomes
    winners = winners.sample(n=min(300, len(winners)), random_state=42)
    losers = losers.sample(n=min(300, len(losers)), random_state=42)
    
    # Setup Figure
    fig, axes = plt.subplots(1, 2, figsize=(14, 10))
    
    # Plot 1: Losing Ends
    draw_rink(axes[0])
    axes[0].scatter(losers['stone_1_x'], losers['stone_1_y'], color='black', s=40, alpha=0.6, edgecolors='grey')
    axes[0].set_title("BAD ENDS (Score <= 1)\nNotice the clutter in the center!", fontsize=14, color='darkred')
    axes[0].set_xlim(0, 1500)
    axes[0].set_ylim(0, 3200) # Show a bit past Hog Line
    axes[0].set_aspect('equal') # Crucial for circles to look like circles!
    
    # Plot 2: Winning Ends
    draw_rink(axes[1])
    axes[1].scatter(winners['stone_1_x'], winners['stone_1_y'], color='#00FF00', s=40, alpha=0.6, edgecolors='darkgreen')
    axes[1].set_title("WINNING ENDS (Score 3+)\nNotice the wide open lanes!", fontsize=14, color='darkgreen')
    axes[1].set_xlim(0, 1500)
    axes[1].set_ylim(0, 3200)
    axes[1].set_aspect('equal')
    
    plt.tight_layout()
    plt.savefig("ice_visual_realistic.png", dpi=150)
    print("Saved 'ice_visual_realistic.png'")

if __name__ == "__main__":
    visualize()
