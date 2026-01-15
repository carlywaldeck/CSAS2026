# Strategic Optimization of the Mixed Doubles Power Play: A Leverage-Based Analytical Framework
### **CSAS 2026 Competitive Submission**
**Authors: [Group of Three Researchers]**

---

### **Abstract**
In the tactical landscape of Mixed Doubles Curling, the Power Play represents a singular, non-renewable strategic resource. Traditional deployment logic—informed by risk-aversion and convention—frequently treats the Power Play as a 9th-inning "Closer," reserved primarily for the final ends of a game to mitigate defeat or secure a narrow victory. Drawing from our group's collective background in the baseball industry, we identified this conventional wisdom as a strategic inefficiency rooted in a misunderstanding of leverage. We propose the **"First Strike" Framework**, an analytical approach that views the Power Play through the lens of high-leverage bullpen management. By situationalizing the Power Play as a **"Fireman"**—a potent resource deployed in early-game high-leverage windows (End 1 or 2)—teams can disrupt the technical rhythm of opponents and force a geometric mismatch that favors offensive volatility. Utilizing a robust dataset of 26,000+ stones, we developed a multi-layered decision engine powered by the **Power Play Readiness Score (PPRS)** and the **Chaos State Index (CSI)**. Our research demonstrates that for elite, high-execution squads (defined herein as "Chaos Agents"), weaponizing the Power Play early maximizes Expected Value (EV) and transforms the resource from a defensive safety net into a proactive strategic weapon.

---

### **1. Introduction: Convention vs. Leverage**
The strategic management of limited resources is the primary challenge of performance analytics across all modern sports. In professional baseball, the management of elite relief pitchers underwent a radical transformation in the early 21st century. The rigid adherence to the "Save" statistic—which mandated that the team's best reliever be saved for the final three outs—was challenged by a "leverage-first" model. Forward-thinking managers recognized that a game could be won or lost in the 5th or 6th inning if a high-leverage threat was left unchecked. This led to the rise of the **"Fireman"** (the high-leverage reliever) and the **"Opener"** (the strategic starter).

Our group, coming from the baseball industry, saw a direct and striking parallel in the Mixed Doubles Power Play. In curling, the Power Play is the ultimate "high-leverage reliever." Its most common usage is in End 8—the literal final inning. However, our attention was drawn to this problem during the **CSAS Zoom Information Session**, where the concept of unconventional Power Play timing—specifically its usage in the first end—was introduced as an unvalidated strategic maneuver. This sparked our interest: was the End 1 Power Play a tactical gimmick, or was it a valid application of leverage-based management that the curling world had yet to quantify?

We recognized a significant opportunity to conduct a deeper dive into this "first inning" usage. We approached the problem with the perspective that the Power Play is a team’s "Closer." Rather than assuming the Closer must always be saved for the final end, we utilized our bullpen analogy to investigate a **"Fireman" deployment**—using the team's most potent resource early to build a lead or disrupt the technical rhythm of an opponent. This paper details our methodology for validating the **"First Strike" Strategy** and the resulting decision-support framework that bridges the gap between descriptive data and prescriptive coaching.

---

### **2. Data Description and Pre-processing**
Our research is anchored in a comprehensive longitudinal dataset of professional Mixed Doubles Curling, provided for the 2026 CSAS challenge. 

#### **2.1 Dataset Composition**
- **Positional Data (N=26,300 stones)**: This core dataset provides discrete X and Y coordinates for every throw in professional competition. The integrity of this data is paramount, as it allows for the reconstruction of the "house geometry" at any point in an end.
- **Game Metadata (N=5,276 ends)**: This includes temporal and situational variables: competition ID, session ID, end number, hammer possession, and result.
- **Power Play Subset (N=598 ends)**: To train our specific models, we extracted 598 Power Play ends, representing a diverse cross-section of elite play, including matchups between technical technical teams (e.g., Team GBR) and aggressive offensive teams (e.g., Team USA).

#### **2.2 Standardization and Geometric Normalization**
Given that different venues and competitions may have variations in sheet measurement or recording, we standardized all stones to a global coordinate system. The ice was modeled as a corridor where $X=0$ represents the centerline and $Y=0$ represents the center of the house (the pin). We focused on the scoring area ($Y \in [0, 600]$) and the guard/hog line zone ($Y \in [1100, 3000]$). This normalization allowed our **Chaos State Index (CSI)** to remain accurate across disparate datasets, ensuring that "congestion" was measured with mathematical consistency regardless of the venue.

---

### **3. Methods: The Analytical Pipeline**
To transform 26,000 stones into a tactical manual, we implemented a three-stage analytical workflow.

#### **3.1 High-Leverage Modeling (XGBoost)**
We utilized **XGBoost (Extreme Gradient Boosting)** to model Expected Value (EV) by end and score-state. This decision was driven by the algorithm's ability to handle the non-linear relationship between the temporal constraints of a game (the end number) and the quantitative pressure of the scoreboard. Our model implemented a tree-based ensemble with a learning rate of 0.05 and a depth of 6, specifically tuned to capture the inflection points where a minor lead necessitates a defensive "pivot" versus an aggressive "strike."
- **The Finding**: The model identified that while the *absolute* win probability of a Power Play is highest late in the game, the *relative* leverage—the ability to permanently shift the game's trajectory—is highest in Ends 1 and 2. This statistically validated our "Fireman" perspective: using the closer early isn't a waste; it's a leverage play. The feature importance analysis revealed that "Current House Congestion" and "End Number" were the two most significant drivers of the "Strike Opportunity" signal.

#### **3.2 Feature Engineering: PPRS and CSI**
To move the strategy from "the lab" to "the bench," we needed metrics that a coach could assess in real-time. This required a transformation of raw coordinate data into indexed scores that reflect strategic utility.
- **Power Play Readiness Score (PPRS)**: This 0-100 metric assesses whether the center of the ice is "ready" for a Power Play. It calculates the density of stones in the "Center corridor" ($|X| < 200$). Every stone found in this region during End 1-2 reduces the PPRS by 15 points, representing the increased difficulty of accessing the wing-guard. Additionally, we awarded a +20 point bonus for "Guard Depth"—if the current guards were positioned deep (near the hog line), the lateral lane clearance for the Power Play draw was significantly maximized, which our model correlated with a 0.22 EV increase.
- **Chaos State Index (CSI)**: This metric was designed to quantify the complexity of the end. By counting centerline stones, identifying blocking guards, and noting house occupancy, the CSI provides a single number that describes the "clutter" level of the game. We implemented a weighted system where stones in the "Top 4" of the house carried a 1.5x multiplier in congestion value, as these are the primary drivers of "freeze-heavy" high-variance scoring ends.

#### **3.3 Shot-3 State Bucket Analysis and Prescriptive ROI**
The third stone of a Power Play is the literal "fork in the road." After three shots, the geometry of the end is largely established. We bucketed every Power Play in our sample by their Shot-3 state:
1.  **Clean**: < 1 stone in center, 0 in house.
2.  **Moderate**: 2-3 stones in center, 1 in house.
3.  **Heavy**: 4+ stones in center, multiple in house. 
We calculated the **Expected Value (EV)** of the outcome based on the call for Shot 4. Using **Laplace Smoothing ($\alpha=1$)**, we ensured that our probabilities remained robust even in lower-sample "Ultra Chaos" buckets. This allowed us to generate a prescriptive table: if the state is Moderate, a **Draw** yields an 1.65 EV, while a **Raise** drops to 1.15 due to high failure variance.

---

### **4. Results: Validating the "First Strike"**

#### **4.1 Statistical ROI of Early Deployment**
Our validation revealed that an End 1 Power Play—contingent on favorable ice geometry (**PPRS ≥ 65**)—generates a significant scoring premium. Most teams achieve a 1-point "standard" Power Play. However, when the First Strike is executed correctly, the frequency of **Big Ends (3+ points)** increases by over 40% compared to standard End 1 play. In baseball terms, this is the equivalent of a "first-inning grand slam" that forces the technical opponent to spend the rest of the game in an uncomfortably aggressive posture.

#### **4.2 The "Draw Under Guard" Failure Rate**
One of the most actionable results of our data dive was the quantification of the "Draw Under Guard" pitfall. In Mixed Doubles, players often attempt to draw behind the corner guard created by the Power Play. Our analysis of the **Stones.csv** dataset showed a **12.3% total failure rate** (stones resulting in 0 points) for this specific shot when attempted in "Moderate" congestion. 
- **The Implication**: This provided a data-based mandate for the **Tick Shot**. We found that replacing a risky "Draw Under Guard" with a "Tick" (Task 4: Wick) in Shot 3/4 increased the overall EV of the end by +0.18 points—a massive margin in professional play.

#### **4.3 International Execution Benchmarking**
We performed a "Causal Decomposition" of the world's top teams. Our research found that:
- **Team GBR (Mowat)**: Exhibits high technical consistency but is penalized by an **11% Raise Mix**. Their propensity to call high-risk "Raises" (Task 3) often derails their Power Play efficiency.
- **Team ITA (Retornaz)**: Achieves high scores through volume drawing but lacks the "Chaos ROI" of more aggressive teams.
- **Elite Offensive Profile (USA)**: These teams act as **"Chaos Agents."** Their Big End (3+) probability actually **increases** as the house gets messier (High CSI). This validated our conclusion that these teams should *never* save their Power Play; they should use it to create the chaos that favors them.

---

### **5. Discussion: The Philosophy of Chaos**

#### **5.1 Inertia vs. Innovation: The Zoom Session Catalyst**
The CSAS Zoom Information Session raised a provocative question: *What is the data-backed validity of the End 1 Power Play?* Tradition suggests that calling a Power Play in the first end is a desperate measure, usually indicative of a team that has already lost control. However, our research demonstrates that this is a misconception of strategic "inertia." Most teams avoid the early Power Play not because it is suboptimal, but because they are psychologically anchored to saving the resource for a "Closer" role. 

By deploying the Power Play as a **Fireman** in End 1, a team breaks the conventional "pace of play." Our study suggests that the technical team's win probability drops significantly when faced with an unexpected End 1 Power Play, as they are forced to abandon their "Stability Mode" before the ice has even settled. This tactical shock creates a "Variance Dividend" that the offensive team can cash in early to dictate the remainder of the eight ends.

#### **5.2 The Two Tactical Modes: Stability vs. Strike**
Our framework moves the Power Play from a defensive insurance policy to an **"Offensive Selective Tool."** By viewing the Power Play through the Fireman analogy, we recognize that its value isn’t just in the points it scores, but in the **performance mode it forces upon the ice.**
1.  **Technical Mode (Stability)**: Traditionally used when leading by 3+. The goal is to eliminate variance, simplify the geometry, and score a clean 1 or 2 points.
2.  **Scoring Mode (First Strike)**: Used early to weaponize variance. 

Our research concludes that world-class "Technical Giants" attempt to play the Power Play as a game of order. But for the **Chaos Agent**, the Power Play is a way to force the technical team into a "muddle" they are ill-equipped to manage. This approach strategically "closes" the game in the first two ends by establishing a technical gap that forces the opponent to chase—leading to more defensive errors and higher scoring opportunities for the lead team. We found that teams utilizing the "First Strike" doctrine successfully built a 2+ point lead in 42% of analyzed cases, transitioning them into a dominant "Stability Mode" for the remainder of the match.

---

### **6. Suggestions for Further Study: The Next Frontier**

#### **6.1 Handle Rotation and "Hot Turn" Bias**
Our preliminary data identified a "Hot Turn" edge—specifically on the right side of the sheet (Handle 0). We suggest a deeper dive into biomechanical data to see if this bias is venue-specific or a fundamental human-performance metric that should be integrated into the PPRS weights.

#### **6.2 Dynamic Ice Modeling**
Olympic ice is not static. As the pebble breaks down, the "ready" state for a First Strike changes. Integrating real-time path data to adjust the PPRS throughout a 10-session tournament would provide the level of precision required for a gold-medal campaign.

#### **6.3 Opponent-Specific "Antidotes"**
While we built "Opponent Recipes" (e.g., *Early Tick against GBR*), future research could build a **Counter-PPRS**. This would allow a defending team to identify the exact center-guard position that lowers the offensive team's EV to the minimum, neutralizing the "Fireman" before he can take the mound.

---

### **7. Conclusion: From Data to Gold**
The **"First Strike" Analytical Framework** demonstrates that the Mixed Doubles Power Play is a resource of extreme leverage that the professional world has historically under-utilized. By shifting our perspective from the conservative "Closer" model to the aggressive **"Fireman" model**, we have validated that an early Power Play is not a risk—it is a strategic weapon.

Through the engineering of the **PPRS**, **CSI**, and **Shot-3 EV Calculator**, we have converted 26,000 stones into a definitive tactical doctrine. Our research proves that for elite, high-execution squads, managing chaos is statistically superior to avoiding it. By weaponizing the Power Play in End 1, teams can dictate the game's geometry, disrupt technical rhythm, and secure a competitive edge that remains robust across any venue. In the 2026 Olympic stage, the team that treats their Power Play as a Fireman—deploying it with mathematical precision in the hottest moments of the game—will be the team that stands atop the podium.

---
**Version 1.0 Submission | CSAS 2026**
**Group: [Research Team Name]**
**Date: January 2026**
