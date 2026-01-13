# TeamIndexScore

A professional Python package for calculating an explainable performance index for football teams based on league statistics.

## Overview

**TeamIndexScore** provides a statistical model to evaluate football team performance relative to league averages. The index combines two key metrics using standardized scores (z-scores):

- **Points Per Game (PPG)**: Measures competitive efficiency
- **Goal Difference Per Game (GD_pg)**: Measures net scoring performance

The model uses z-scores to standardize metrics, enabling meaningful comparisons across different leagues and seasons. A z-score of 0 represents league-average performance, positive values indicate above-average performance, and negative values indicate below-average performance.

## Formula

### Core Calculation
```
TEAM_INDEX_RAW = 0.55 × z_PPG + 0.45 × z_GD_pg
```
Where:
- `PPG = points / matches_played`
- `GD_pg = (goals_for - goals_against) / matches_played`
- `z_x = (x - league_mean_x) / league_std_x`

### Normalized Index (1-10 Scale)
When `normalize_by_ppg=True`, the raw index is transformed using a sigmoid function and scaled to a 1-10 range:

```
TEAM_INDEX = 1 + 9 × sigmoid(TEAM_INDEX_RAW) × min(PPG / 3, 1.0)
```

This approach ensures:
- **Differentiation**: Teams with different performances receive distinct scores
- **Intuitive Scale**: Scores range from 1 (lowest) to 10 (highest)
- **Competitive Context**: PPG acts as a scaling factor, rewarding consistent point accumulation

The weights (55% PPG, 45% GD) reflect that points are the ultimate measure of success in football, while goal difference provides important context about the quality of those results.

## Installation

```bash
pip install TeamIndexScore
```

## Requirements

- Python >= 3.9
- No external dependencies (pure Python)

## Basic Usage

```python
from teamindexscore import calcular_indice_equipo

# Calculate index for a team
index = calcular_indice_equipo(
    puntos=45,                    # Total points earned
    goles_a_favor=60,             # Goals scored
    goles_en_contra=25,           # Goals conceded
    partidos_jugados=20,          # Matches played
    media_ppg_liga=1.5,           # League average PPG
    std_ppg_liga=0.4,             # League std dev of PPG
    media_gd_liga=0.0,            # League average GD per game
    std_gd_liga=0.8               # League std dev of GD per game
)

print(f"Team Index: {index}")  # Output: 2.47
```

## Advanced Features

### Detailed Breakdown

Get detailed metrics for analysis:

```python
index, breakdown = calcular_indice_equipo(
    puntos=45,
    goles_a_favor=60,
    goles_en_contra=25,
    partidos_jugados=20,
    media_ppg_liga=1.5,
    std_ppg_liga=0.4,
    media_gd_liga=0.0,
    std_gd_liga=0.8,
    return_breakdown=True
)

print(f"PPG: {breakdown['ppg']}")
print(f"z-score PPG: {breakdown['z_ppg']}")
print(f"GD per game: {breakdown['gd_pg']}")
print(f"z-score GD: {breakdown['z_gd_pg']}")
```

### Competitive Normalization

Apply competitive ceiling normalization based on actual points earned:

```python
index = calcular_indice_equipo(
    puntos=45,
    goles_a_favor=60,
    goles_en_contra=25,
    partidos_jugados=20,
    media_ppg_liga=1.5,
    std_ppg_liga=0.4,
    media_gd_liga=0.0,
    std_gd_liga=0.8,
    normalize_by_ppg=True  # Apply competitive normalization
)
```

When `normalize_by_ppg=True`, the index is scaled using a sigmoid function and adjusted by the team's competitive ceiling (PPG/3), ensuring that:
- The index ranges from 1 to 10 for intuitive interpretation
- Teams with higher PPG receive proportionally higher scores
- Even small performance differences are meaningfully reflected
- The relationship between teams' performances is preserved

### Example: Comparing Teams

```python
# Team A: 30 points in 15 matches (2.0 PPG)
index_a = calcular_indice_equipo(
    puntos=30, goles_a_favor=35, goles_en_contra=25,
    partidos_jugados=15, media_ppg_liga=1.5, std_ppg_liga=0.3,
    media_gd_liga=0.2, std_gd_liga=0.5, normalize_by_ppg=True
)

# Team B: 43 points in 15 matches (2.87 PPG)
index_b = calcular_indice_equipo(
    puntos=43, goles_a_favor=48, goles_en_contra=25,
    partidos_jugados=15, media_ppg_liga=1.5, std_ppg_liga=0.3,
    media_gd_liga=0.2, std_gd_liga=0.5, normalize_by_ppg=True
)

print(f"Team A Index: {index_a:.2f}")  # e.g., 6.24
print(f"Team B Index: {index_b:.2f}")  # e.g., 8.91
```

### Custom Weights

Adjust the importance of PPG vs GD:

```python
index = calcular_indice_equipo(
    puntos=45,
    goles_a_favor=60,
    goles_en_contra=25,
    partidos_jugados=20,
    media_ppg_liga=1.5,
    std_ppg_liga=0.4,
    media_gd_liga=0.0,
    std_gd_liga=0.8,
    peso_ppg=0.6,  # 60% weight to PPG
    peso_gd=0.4    # 40% weight to GD
)
```

## Interpretation

### With Normalization (normalize_by_ppg=True)
- **9-10**: Exceptional performance (top tier)
- **7-8.9**: Strong performance (elite)
- **5-6.9**: Above average (good)
- **3-4.9**: Average performance
- **1-2.9**: Below average (needs improvement)

### Without Normalization (normalize_by_ppg=False)
- **> 0**: Above-average performance
- **= 0**: League-average performance
- **< 0**: Below-average performance
- **Typical range**: -3 to +3

## Limitations

- Requires accurate league statistics (mean and standard deviation)
- Does not account for strength of schedule or opponent quality
- Small sample sizes (few matches) may produce unstable estimates
- Index is relative to the specific league and cannot be compared across leagues without additional normalization

## Use Cases

- **Performance Analysis**: Evaluate team performance relative to league standards
- **Scouting**: Compare teams across different leagues using standardized metrics
- **Academic Research**: Reproducible and explainable performance measurement
- **Sports Analytics**: Data-driven insights for coaching and management decisions

## License

MIT License - See LICENSE file for details.

## Author

Alvaro Lopez Molina (alopezmolina4@gmail.com)

## Contributing

This is an academic project. For questions or suggestions, please contact the author.
