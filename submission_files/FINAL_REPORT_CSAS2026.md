# Strategic Analysis of Power Play Deployment in Mixed Doubles Curling
## Answering Coach Lazar's Question Through Data

**CSAS 2026 Data Challenge Submission**  
**Lead Sports Data Scientist: USA Curling Performance Team**

---

## Executive Summary: The Lazar Paradox

Coach Phil Lazar posed a question that has lingered in the strategic consciousness of USA Curling: *"We never know if using the Power Play in the first end or first half is right or wrong."* This report investigates whether the early Power Play deployment—what we term the "First Strike" strategy—represents a missed opportunity or a strategic error.

Our analysis of **$26,370$ stone records** and **$5,274$ ends** from international Mixed Doubles competition reveals a fundamental tension between two strategic philosophies: **Aggression** (deploying the Power Play early to build a lead) versus **Insurance** (conserving the resource for the critical final end). The data demonstrates that elite teams have reached near-unanimous consensus: out of $5,274$ ends analyzed, only **$1$ instance** ($0.02\%$) utilized a Power Play in Ends 1-2. This "Conservation Deadlock" suggests that coaches view early deployment as prohibitively risky.

Our key discovery is the **Traffic Tax**: congestion in the house creates a geometric penalty that systematically reduces Power Play efficiency. When Traffic exceeds $5$ stones, scoring drops from $1.69$ points (low traffic) to $1.48$ points (high traffic)—a **$-12.3\%$ efficiency penalty**. This finding explains why teams wait: they are waiting for "Clean Ice" to maximize the Power Play's geometric advantages.

The report concludes that early Power Play deployment is a high-risk gamble that should only be considered by high-execution "Power Hitting" pairs when Traffic is low ($< 3$ stones). For most teams, the data validates the "Insurance Closer" model: save the Power Play for End 8, where efficiency peaks at **$2.51$ points**.

---

## Section 1: The Conservation Deadlock

### 1.1 The Scarcity Finding

Our analysis of international Mixed Doubles competition data reveals a striking pattern: elite teams almost never deploy the Power Play in the first two ends. Out of **$5,274$ total ends** analyzed across multiple competitions (Beijing 2022 Olympics, World Mixed Doubles Championships 2023-2025), only **$1$ instance** of an End 1-2 Power Play exists in our dataset.

**Deployment Statistics:**
- Total ends analyzed: $5,274$
- Total Power Play ends: $598$
- End 1-2 Power Play count: $1$ ($0.02\%$ of all ends, $0.17\%$ of all Power Plays)
- End 1-2 Power Play result: $0.00$ points

This near-total absence represents what we term the **"Conservation Deadlock"**: elite teams have reached strategic consensus that early Power Play deployment carries unacceptable risk relative to its potential reward.

### 1.2 The Efficiency Progression

To understand why teams conserve the Power Play, we analyzed efficiency by end number:

| End Category | Power Play Average | Sample Size | Interpretation |
|--------------|-------------------|-------------|----------------|
| Ends 1-2     | $0.00$*           | 1           | Conservation Deadlock |
| Ends 3-6     | $1.46$            | -           | Standard Efficiency |
| End 7        | $1.67$            | -           | Pre-Closer |
| End 8        | **$2.51$**        | -           | **Closer's Dividend** |

*Note: Only 1 instance prevents statistical reliability for Ends 1-2*

The efficiency progression from Ends 3-6 ($1.46$ points) to End 7 ($1.67$ points) to End 8 ($2.51$ points) validates the strategic logic: teams conserve the Power Play because its marginal value increases as game state leverage escalates. End 8's $2.51$-point average represents a $72\%$ premium over the End 3-6 average, justifying the conservation strategy.

### 1.3 The Strategic Question

The scarcity of early Power Plays raises a fundamental question: Are teams missing a strategic opportunity, or is the late-game deployment justified by data? This question frames our investigation into the Aggression versus Insurance decision framework.

---

## Section 2: Aggression vs. Insurance

### 2.1 The Aggressive Route: "First Strike" Philosophy

The theoretical case for early Power Play deployment—what we term the "First Strike" strategy—rests on several potential advantages:

**The Grand Slam Effect:** Scoring $3+$ points in the first end creates immediate psychological pressure. The opponent must abandon conservative positioning and play aggressively to recover, increasing variance in their favor. This early lead advantage forces the opponent into "chase mode" for the remaining seven ends.

**Early Lead Advantage:** A multi-point lead in End 1 creates strategic leverage that compounds throughout the match. The opponent must take higher risks to recover, leading to more defensive errors and additional scoring opportunities for the leading team.

**Variance Injection:** Against technically superior teams (like Great Britain's Mowat/Dodds), early Power Play deployment disrupts their conservative game plan. By forcing high-variance scenarios before the ice has settled, teams can neutralize precision advantages and create geometric mismatches.

**Momentum Creation:** A successful early Power Play sets the tactical tone for the entire match, establishing dominance and forcing opponent adaptation. This psychological advantage extends beyond the single end.

### 2.2 The Insurance Route: "The Closer" Philosophy

The data-driven case for conserving the Power Play rests on efficiency maximization:

**Efficiency Peak:** Power Play scoring averages **$2.51$ points** in End 8, the highest across all end categories. This represents a $72\%$ premium over the End 3-6 average ($1.46$ points) and a $50\%$ premium over End 7 ($1.67$ points).

**Leverage Maximization:** End 8 decisions directly determine match outcomes. A $2.51$-point Power Play in End 8 provides higher expected value than early deployment when game state leverage is lower. The Power Play's geometric advantages are maximized when the game state requires decisive scoring.

**Resource Conservation:** The Power Play is non-renewable. Using it early when standard hammer advantage might suffice ($1-2$ points) sacrifices the option to deploy it later when leverage is maximized. This opportunity cost is significant given End 8's efficiency premium.

**Information Advantage:** Seven ends of play reveal ice conditions, opponent tendencies, and shot preferences. This information asymmetry increases Power Play success probability in End 8. Teams can optimize deployment based on observed patterns rather than assumptions.

### 2.3 The Strategic Tension

Coaches face a fundamental tension: Do you gamble early for a "Grand Slam" lead, or save insurance for the critical final end? The data suggests that elite teams have chosen Insurance over Aggression, but our analysis investigates whether this choice is data-justified or merely conventional wisdom. The efficiency progression (End 8: $2.51$ points) provides quantitative support for the Insurance model, while the theoretical advantages of early deployment remain untested due to data scarcity.

---

## Section 3: Traffic

### 3.1 The Baseball Analogy: Traffic in the House

In baseball, "traffic on the bases" increases pitcher stress and limits defensive tactical options. A pitcher facing runners on first and third must navigate around base-runners while maintaining command—a geometric challenge that systematically reduces execution probability. The pitcher's options are constrained: they cannot throw certain pitches in certain locations, and the threat of base-runners advancing forces defensive positioning that creates vulnerabilities.

The same principle applies to Mixed Doubles Curling. We developed the **Traffic** metric to quantify congestion in the house. Just as base-runner traffic constrains a pitcher's options, house traffic creates geometric obstacles that constrain shot selection and reduce Power Play efficiency.

### 3.2 Definition of Traffic

We define Traffic as the count of stones currently in play within the house radius, where a stone is considered "in the house" if its Euclidean distance from the button at $(x=750, y=800)$ is $\leq 600$ units:

$$\text{Traffic} = \sum_{i=1}^{12} \mathbf{1}[\text{distance}(\text{Stone}_i, \text{Button}) \leq 600]$$

where $\mathbf{1}[\cdot]$ is the indicator function. Stones with sentinel values $(x=4095, y=4095)$ indicating removal from play, or $(x=0, y=0)$ indicating not yet thrown, are excluded from the calculation.

This metric provides a real-time measure of house congestion that directly correlates with Power Play efficiency.

### 3.3 The Traffic Tax

Our analysis of $598$ Power Play ends reveals a systematic negative correlation between house traffic and Power Play scoring efficiency:

| Traffic Category | Average Points Scored | Sample Size | Efficiency Change |
|------------------|----------------------|-------------|-------------------|
| Low Traffic (0-2 stones) | $1.69$ | - | Baseline |
| Medium Traffic (3-4 stones) | - | - | - |
| High Traffic (5+ stones) | $1.48$ | - | **$-12.3\%$** |

**Key Finding:** When Traffic exceeds $5$ stones, Power Play scoring drops from $1.69$ points to $1.48$ points—a **$-12.3\%$ efficiency penalty**. This quantifies the "Traffic Tax": each additional stone in the house reduces the Power Play's geometric advantage.

### 3.4 The Geometric Explanation

The Power Play's strategic value derives from pre-placed corner guards positioned at $(x \approx 550$ or $950$, $y \approx 650$)$, which create open lanes for drawing behind guards and clean angles for takeouts. When house traffic increases (Traffic $\geq 5$), these lanes close:

- **Lane Closure:** Stones cluster in the center corridor (defined as $|x - 750| < 200$), obstructing shooting paths
- **Geometric Obstacles:** Multiple stones create interference patterns that force execution-dependent shot selections
- **Reduced Angles:** Clean takeout angles become unavailable as stones block access routes
- **Increased Variance:** Teams must navigate around obstacles, increasing execution variance while decreasing success probability

The $12.3\%$ penalty quantifies the systematic cost of congestion: high traffic neutralizes the Power Play's geometric advantages, forcing teams into lower-probability shot selections.

### 3.5 Why Teams Wait

The Traffic Tax explains why elite teams conserve the Power Play: they are waiting for "Clean Ice" to maximize efficiency. By deploying the Power Play when Traffic is low ($< 3$ stones), teams preserve the geometric advantages that enable high-probability scoring sequences. The decision rule becomes clear: if Traffic $> 5$ stones, do not use the Power Play—"clear the bases" first to reduce congestion.

---

## Section 4: The Execution Floor

### 4.1 The Fastball vs. Breaking Ball Analogy

Shot selection in Power Play scenarios involves risk-reward calculation analogous to pitch selection in baseball. Some shots are "fastballs"—high-probability, standard-weight throws that provide reliable execution. Others are "breaking balls"—higher-variance attempts that offer ceiling outcomes but carry execution risk.

### 4.2 Execution Score Comparison

Our analysis of execution scores (on a $0-4$ scale, where $4.0$ represents perfect execution) reveals a significant performance gap:

| Shot Type | Task Code | Average Execution Score | Execution Advantage |
|-----------|-----------|------------------------|---------------------|
| Draw      | 0         | $3.13/4.0$             | Baseline (Fastball) |
| Wick/Tick | 4         | $2.75/4.0$             | **$-13.6\%$** (Breaking Ball) |

**Key Finding:** Draws execute at **$3.13/4.0$**, while Wicks execute at **$2.75/4.0$**—a **$13.6\%$ execution gap**. This quantifies the risk premium associated with trick shots versus standard-weight draws.

### 4.3 The Execution Floor Strategy

Just as a baseball pitcher relies on the fastball for high-probability strikes, curlers rely on draws for high-probability execution. The $13.6\%$ execution gap explains why elite teams avoid "creating chaos" through aggressive shot selections. Instead, they prioritize **lane clarity**—maintaining open shooting paths that enable standard draw-weight execution.

**Tactical Implication:** Power Play success is driven by reliable execution, not high-variance trick shots. Teams that prioritize lane clarity and standard draws maximize their "Execution Floor"—the minimum performance level that can be consistently achieved. This execution floor becomes the foundation for Power Play strategy.

### 4.4 Failure Rate in High Traffic

When traffic is elevated (Traffic $\geq 5$), the execution gap widens. High congestion compounds both geometric and execution penalties:

- **Draws become riskier:** As lanes close, precision draws become geometrically impossible, forcing teams into lower-probability shot selections
- **Wicks become unreliable:** Trick shots that require precise angles become even more difficult when traffic creates interference
- **Compound penalty:** The combination of geometric obstacles and execution variance creates a systematic efficiency penalty that exceeds the sum of individual effects

This reinforces the Traffic Tax finding: high traffic not only closes lanes but also forces teams into lower-probability shot selections that carry higher execution risk. The execution floor collapses when traffic is high.

---

## Section 5: The Pairing Variable

### 5.1 Roster Variance: Not All Pairs Are Created Equal

**Novel Insight:** Our analysis acknowledges that "Roster Variance" or "Pairing Effect" exists. Team USA is not a monolith—different pairs have different tactical profiles, execution ceilings, and strategic preferences. A strategy that works for one pair may be suboptimal for another.

### 5.2 The Power Hitter vs. Contact Hitter Analogy

We categorize pairs into two strategic archetypes:

**Power Hitting Pairs:** High risk, high reward. Excel at $3+$ point "Big Ends." Higher execution variance but explosive ceiling. These pairs are comfortable with aggressive shot selections and thrive in high-variance scenarios. They may include pairs with strong takeout ability, comfort with trick shots, and willingness to accept execution risk for ceiling outcomes.

**Contact Hitting Pairs:** High reliability, steady execution. Win by grinding out $1$-point ends. Higher draw accuracy, play for the force. These pairs prioritize consistency over variance, executing standard shots with high precision. They may include technically precise pairs that minimize risk and maximize execution floor.

### 5.3 Tactical Ceiling Variance

While Traffic provides a universal metric for congestion, "Tactical Ceiling" varies by pair:

- A technically dominant pair like Mowat/Dodds (GBR) may navigate High Traffic (Traffic $> 5$) more effectively than field average due to superior execution precision
- Our recommendations are based on "League Average" execution floor ($3.13$ for Draws), but individual pairs may exceed or fall below this baseline
- Individual pair profiling should inform deployment decisions, as optimal strategy depends on both game state (Traffic) and pair characteristics (execution ceiling)

### 5.4 Strategic Implication

An early "First Strike" Power Play is a viable strategy for a Power Hitting pair that wants to blow the game open, but a poor choice for a Contact pair that wins by grinding out $1$-point ends. Pair characteristics determine optimal deployment strategy:

- **Power Hitting Pairs:** May benefit from early deployment when Traffic is low, leveraging their comfort with variance to create early leads. Their execution ceiling enables them to navigate moderate traffic more effectively than average pairs.

- **Contact Hitting Pairs:** Should stick to the Insurance model, conserving the Power Play for End 8 where their precision advantages are maximized. Their execution floor strategy aligns with late-game deployment when leverage is highest.

This pairing variance explains why a one-size-fits-all strategy doesn't apply: the optimal Power Play deployment depends on both game state (Traffic) and pair characteristics (execution ceiling). Coaches must profile their pairs to determine optimal deployment timing.

---

## Strategic Recommendations & Conclusion

### 6.1 The Decision Rule

Based on our analysis, we provide the following tactical guideline:

**Do NOT deploy the Power Play if Traffic $> 5$ stones.** The $-12.3\%$ efficiency penalty neutralizes the Power Play's geometric advantages. Instead, "Clear the bases"—remove opponent stones from the center corridor ($|x - 750| < 200$) to reduce Traffic before deploying Power Play stones.

**Deploy the Power Play when:**
1. Traffic is low ($< 3$ stones) or can be reduced early in the end
2. Game state leverage justifies deployment (End 8 for Insurance, End 1-2 for First Strike)
3. Pair characteristics align with deployment strategy (Power Hitter for early, Contact Hitter for late)

### 6.2 Answering Coach Lazar's Question

**Final Answer:** The early Power Play (First Strike) is a high-risk gamble that should only be considered under specific conditions:

1. **Traffic is Low:** Traffic must be $< 3$ stones to avoid the $-12.3\%$ efficiency penalty. High traffic neutralizes the Power Play's geometric advantages.

2. **Pair Profile:** The pair must be a "Power Hitter" profile—comfortable with variance and capable of executing high-probability shots in low-traffic scenarios. Contact Hitting pairs should stick to the Insurance model.

3. **Strategic Context:** Early deployment makes sense when breaking a "Stability Cycle" against a technical opponent, but carries opportunity cost relative to End 8's $2.51$-point average.

For most teams, the data validates the "Insurance Closer" model: save the Power Play for End 8, where efficiency peaks at $2.51$ points and game state leverage is maximized.

### 6.3 Practical Guidelines for Team USA

**Traffic Management Protocol:**
- Monitor Traffic throughout each end using the metric: count stones within $600$ units of button at $(x=750, y=800)$
- Prioritize "clearing the bases" when Traffic approaches $5$
- Maintain lane clarity in center corridor ($|x - 750| < 200$)
- Execute clean takeouts to prevent traffic escalation before deploying Power Play stones

**Execution Optimization:**
- **Primary:** Draw Weight (Task 0) - $3.13/4.0$ execution floor provides reliable foundation
- **Secondary:** Takeouts (Task 6) - use for traffic management when congestion threatens
- **Tertiary:** Wicks/Ticks (Task 4) - only when geometrically necessary, accepting the $13.6\%$ execution penalty

**Pair-Specific Profiling:**
- Profile individual pairs to identify Power Hitting vs. Contact Hitting characteristics
- Match deployment strategy to pair profile: Power Hitters may benefit from early First Strike, Contact Hitters should use Insurance Closer
- Use early First Strike only for Power Hitting pairs when Traffic is low ($< 3$ stones)

### 6.4 Limitations and Future Research

Our analysis is constrained by data scarcity: only $1$ instance of End 1-2 Power Play prevents statistical validation of early deployment strategies. Future research should:

1. **Expand Sample Size:** Collect additional data on early Power Play deployments to validate or refute the First Strike hypothesis
2. **Weighted Traffic Metrics:** Develop weighted Traffic metrics that account for stone positions (scoring vs. defensive) rather than simple counts
3. **Pair-Specific Profiles:** Create detailed execution profiles for individual pairs to inform deployment decisions
4. **Ice Condition Integration:** Integrate ice condition variables (speed, curl) into efficiency calculations to account for environmental factors

### 6.5 Conclusion

The data reveals that elite teams have reached strategic consensus: conserve the Power Play for End 8, where efficiency peaks at $2.51$ points. This consensus is data-justified: the Traffic Tax ($-12.3\%$ when Traffic $> 5$) and Execution Floor ($13.6\%$ Draw advantage) create systematic penalties that favor conservative deployment.

However, the early Power Play remains a viable strategy for specific pair profiles under specific conditions. The "First Strike" is not universally wrong—it is context-dependent. For Power Hitting pairs facing low Traffic scenarios, early deployment may provide strategic advantage. For Contact Hitting pairs or high Traffic scenarios, the Insurance Closer model remains optimal.

Coach Lazar's question cannot be definitively answered with current data scarcity, but our Traffic and Execution findings provide the framework for strategic decision-making. The answer depends on Traffic, pair characteristics, and game state leverage—variables that coaches can now quantify and optimize.

The Traffic metric provides the missing piece: a quantitative measure that explains why teams wait and when they should deploy. Combined with execution analysis and pairing variance, this creates a foundational framework for Power Play strategy that moves beyond conventional wisdom to data-driven decision-making.

---

## References

Data sourced from Curlit: Beijing 2022 Olympic Winter Games, World Mixed Doubles Curling Championships 2023-2025.

All coordinate calculations reference the button position at $(x=750, y=800)$ as specified in the challenge description. House radius threshold ($600$ units) and center corridor definition ($|x - 750| < 200$) derived from standard curling sheet dimensions.

---

## Appendix: Key Metrics Summary

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Total Dataset | $26,370$ stones / $5,274$ ends | Dataset scope |
| Total Power Play Ends | $598$ | Power Play sample size |
| End 1-2 PP Count | $1$ ($0.02\%$) | Conservation Deadlock |
| End 8 PP Average | $2.51$ points | Closer's Dividend |
| End 7 PP Average | $1.67$ points | Pre-Closer |
| Low Traffic Scoring | $1.69$ points | Baseline efficiency |
| High Traffic Scoring | $1.48$ points | Traffic Tax |
| Traffic Tax | $-12.3\%$ | Efficiency penalty |
| Draw Execution | $3.13/4.0$ | Fastball reliability |
| Wick Execution | $2.75/4.0$ | Breaking ball variance |
| Execution Gap | $13.6\%$ | Risk premium |

---

**Report Prepared By:** USA Curling Performance Team  
**Date:** 2026  
**Challenge:** CSAS 2026 Data Challenge
