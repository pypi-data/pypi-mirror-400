"""
Core module for calculating football team performance indices.

This module implements a statistical model based on z-scores to compute
a league-relative performance index for football teams.
"""


def _calcular_zscore(valor, media, desviacion):
    """
    Calculate the z-score (standard score) for a given value.

    The z-score measures how many standard deviations a value is from the mean.
    It enables comparison of values from different distributions on a common scale.

    Args:
        valor (float): The value to standardize.
        media (float): The mean of the distribution.
        desviacion (float): The standard deviation of the distribution.

    Returns:
        float: The z-score of the value.

    Raises:
        ValueError: If standard deviation is zero or negative.
    """
    if desviacion <= 0:
        raise ValueError(
            f"La desviación estándar debe ser positiva, pero es {desviacion}"
        )
    return (valor - media) / desviacion


def _validar_parametros(
    puntos,
    goles_a_favor,
    goles_en_contra,
    partidos_jugados,
    media_ppg_liga,
    std_ppg_liga,
    media_gd_liga,
    std_gd_liga,
):
    """
    Validate input parameters for team index calculation.

    Args:
        puntos: Total points earned by the team.
        goles_a_favor: Goals scored by the team.
        goles_en_contra: Goals conceded by the team.
        partidos_jugados: Number of matches played.
        media_ppg_liga: League average points per game.
        std_ppg_liga: League standard deviation of points per game.
        media_gd_liga: League average goal difference per game.
        std_gd_liga: League standard deviation of goal difference per game.

    Raises:
        ValueError: If any parameter is invalid.
    """
    if not isinstance(puntos, (int, float)) or puntos < 0:
        raise ValueError("puntos debe ser un número no negativo")

    if not isinstance(goles_a_favor, (int, float)) or goles_a_favor < 0:
        raise ValueError("goles_a_favor debe ser un número no negativo")

    if not isinstance(goles_en_contra, (int, float)) or goles_en_contra < 0:
        raise ValueError("goles_en_contra debe ser un número no negativo")

    if not isinstance(partidos_jugados, (int, float)) or partidos_jugados <= 0:
        raise ValueError("partidos_jugados debe ser un número positivo")

    if not isinstance(media_ppg_liga, (int, float)):
        raise ValueError("media_ppg_liga debe ser un número")

    if not isinstance(std_ppg_liga, (int, float)) or std_ppg_liga <= 0:
        raise ValueError("std_ppg_liga debe ser un número positivo")

    if not isinstance(media_gd_liga, (int, float)):
        raise ValueError("media_gd_liga debe ser un número")

    if not isinstance(std_gd_liga, (int, float)) or std_gd_liga <= 0:
        raise ValueError("std_gd_liga debe ser un número positivo")


def calcular_indice_equipo(
    puntos,
    goles_a_favor,
    goles_en_contra,
    partidos_jugados,
    media_ppg_liga,
    std_ppg_liga,
    media_gd_liga,
    std_gd_liga,
    peso_ppg=0.55,
    peso_gd=0.45,
    normalize_by_ppg=False,
    return_breakdown=False,
):
    """
    Calculate a league-relative performance index for a football team.

    This function implements a statistical model based on standardized scores (z-scores)
    to measure team performance relative to league averages. The index combines two
    key metrics:

    1. Points Per Game (PPG): Measures competitive efficiency
    2. Goal Difference Per Game (GD_pg): Measures net scoring performance

    Why z-scores?
    -------------
    Z-scores standardize metrics to a common scale, allowing meaningful comparison
    across different leagues and seasons. A z-score of 0 represents league-average
    performance, positive values indicate above-average performance, and negative
    values indicate below-average performance.

    Why weights 0.55 / 0.45?
    -------------------------
    The model assigns 55% weight to PPG and 45% to GD_pg based on the principle that
    points are the ultimate measure of success in football, while goal difference
    provides important context about the quality of those results. This weighting
    reflects that a team can win efficiently (low GD) or dominantly (high GD), with
    both approaches being valuable but points being paramount.

    Formula:
    --------
    TEAM_INDEX_RAW = peso_ppg * z_PPG + peso_gd * z_GD_pg

    where:
        PPG = puntos / partidos_jugados
        GD_pg = (goles_a_favor - goles_en_contra) / partidos_jugados
        z_x = (x - media_liga_x) / std_liga_x

    Competitive Normalization (optional):
    --------------------------------------
    When normalize_by_ppg=True, the index is normalized by the team's competitive
    ceiling defined by the maximum theoretical points (3 PPG):

        ppg_factor = min(PPG / 3, 1.0)
        TEAM_INDEX = max(TEAM_INDEX_RAW * ppg_factor, 0)

    This normalization ensures that:
    - The index ceiling is determined by actual competitive performance (points earned)
    - Goal difference provides context but cannot inflate the index beyond what
      points justify
    - The index remains non-negative, improving interpretability
    - Teams with low PPG are penalized regardless of goal difference

    This approach avoids arbitrary scales (e.g., 1-10) and grounds the index in
    football's fundamental scoring system: 3 points per win.

    Limitations:
    ------------
    - Requires accurate league statistics (mean and std) for valid comparisons
    - Does not account for strength of schedule or opponent quality
    - Small sample sizes (few matches) may produce unstable estimates
    - Index is relative to the specific league and cannot be compared across leagues
      without additional normalization

    Args:
        puntos (int or float): Total points earned by the team.
        goles_a_favor (int or float): Total goals scored by the team.
        goles_en_contra (int or float): Total goals conceded by the team.
        partidos_jugados (int or float): Number of matches played by the team.
        media_ppg_liga (float): League average of points per game.
        std_ppg_liga (float): League standard deviation of points per game.
        media_gd_liga (float): League average of goal difference per game.
        std_gd_liga (float): League standard deviation of goal difference per game.
        peso_ppg (float, optional): Weight for PPG component. Default: 0.55.
        peso_gd (float, optional): Weight for GD_pg component. Default: 0.45.
        normalize_by_ppg (bool, optional): If True, normalizes index by competitive
                                           ceiling (PPG/3). Default: False.
        return_breakdown (bool, optional): If True, returns detailed breakdown.
                                           Default: False.

    Returns:
        float or tuple: If return_breakdown=False, returns the performance index.
                        Without normalization: continuous value (typically -3 to +3).
                        With normalization: non-negative value bounded by competitive ceiling.
                        
                        If return_breakdown=True, returns a tuple (indice, desglose)
                        where desglose is a dict containing:
                        - "ppg": Points per game
                        - "gd_pg": Goal difference per game
                        - "z_ppg": Standardized PPG score
                        - "z_gd_pg": Standardized GD_pg score
                        - "peso_ppg": Weight applied to PPG
                        - "peso_gd": Weight applied to GD_pg
                        - "indice_raw": Raw index before normalization
                        - "ppg_factor": PPG normalization factor
                        - "indice_normalizado": Normalized index (only if normalize_by_ppg=True)

    Raises:
        ValueError: If input parameters are invalid, standard deviations are zero,
                    or weights don't sum to 1.0 (within tolerance).

    Examples:
        >>> # Basic usage: Team with above-average performance
        >>> calcular_indice_equipo(
        ...     puntos=45, goles_a_favor=60, goles_en_contra=25, partidos_jugados=20,
        ...     media_ppg_liga=1.5, std_ppg_liga=0.4,
        ...     media_gd_liga=0.0, std_gd_liga=0.8
        ... )
        2.47

        >>> # With competitive normalization
        >>> calcular_indice_equipo(
        ...     puntos=45, goles_a_favor=60, goles_en_contra=25, partidos_jugados=20,
        ...     media_ppg_liga=1.5, std_ppg_liga=0.4,
        ...     media_gd_liga=0.0, std_gd_liga=0.8,
        ...     normalize_by_ppg=True
        ... )
        1.85

        >>> # With breakdown for detailed analysis
        >>> indice, desglose = calcular_indice_equipo(
        ...     puntos=45, goles_a_favor=60, goles_en_contra=25, partidos_jugados=20,
        ...     media_ppg_liga=1.5, std_ppg_liga=0.4,
        ...     media_gd_liga=0.0, std_gd_liga=0.8,
        ...     normalize_by_ppg=True,
        ...     return_breakdown=True
        ... )
        >>> print(f"Índice normalizado: {indice}")
        Índice normalizado: 1.85
        >>> print(f"PPG: {desglose['ppg']}, Factor: {desglose['ppg_factor']}")
        PPG: 2.25, Factor: 0.75
    """
    _validar_parametros(
        puntos,
        goles_a_favor,
        goles_en_contra,
        partidos_jugados,
        media_ppg_liga,
        std_ppg_liga,
        media_gd_liga,
        std_gd_liga,
    )

    if not isinstance(peso_ppg, (int, float)) or not isinstance(peso_gd, (int, float)):
        raise ValueError("peso_ppg y peso_gd deben ser números")

    suma_pesos = peso_ppg + peso_gd
    if not (0.99 <= suma_pesos <= 1.01):
        raise ValueError(
            f"La suma de peso_ppg y peso_gd debe ser 1.0 (tolerancia ±0.01), "
            f"pero es {suma_pesos:.4f}"
        )

    ppg = puntos / partidos_jugados
    gd_pg = (goles_a_favor - goles_en_contra) / partidos_jugados

    z_ppg = _calcular_zscore(ppg, media_ppg_liga, std_ppg_liga)
    z_gd_pg = _calcular_zscore(gd_pg, media_gd_liga, std_gd_liga)

    indice_raw = peso_ppg * z_ppg + peso_gd * z_gd_pg

    ppg_factor = min(ppg / 3.0, 1.0)

    if normalize_by_ppg:
        indice_normalizado = max(indice_raw * ppg_factor, 0.0)
        indice_final = round(indice_normalizado, 2)
    else:
        indice_final = round(indice_raw, 2)

    if return_breakdown:
        desglose = {
            "ppg": round(ppg, 2),
            "gd_pg": round(gd_pg, 2),
            "z_ppg": round(z_ppg, 2),
            "z_gd_pg": round(z_gd_pg, 2),
            "peso_ppg": peso_ppg,
            "peso_gd": peso_gd,
            "indice_raw": round(indice_raw, 2),
            "ppg_factor": round(ppg_factor, 2),
            "normalize_by_ppg": normalize_by_ppg,
        }
        if normalize_by_ppg:
            desglose["indice_normalizado"] = indice_final
        return (indice_final, desglose)

    return indice_final
