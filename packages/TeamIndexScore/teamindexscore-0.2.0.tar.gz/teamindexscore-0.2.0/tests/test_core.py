import pytest
from teamindexscore.core import calcular_indice_equipo


def test_equipo_por_encima_de_media_obtiene_indice_positivo():
    """Test that a team performing above league average gets a positive index."""
    indice = calcular_indice_equipo(
        puntos=50,
        goles_a_favor=60,
        goles_en_contra=20,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
    )
    assert indice > 0, f"Expected positive index, got {indice}"


def test_equipo_por_debajo_de_media_obtiene_indice_negativo():
    """Test that a team performing below league average gets a negative index."""
    indice = calcular_indice_equipo(
        puntos=15,
        goles_a_favor=20,
        goles_en_contra=40,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
    )
    assert indice < 0, f"Expected negative index, got {indice}"


def test_equipo_promedio_obtiene_indice_cercano_a_cero():
    """Test that a team with average performance gets an index close to zero."""
    indice = calcular_indice_equipo(
        puntos=30,
        goles_a_favor=35,
        goles_en_contra=35,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
    )
    assert abs(indice) < 0.1, f"Expected index close to 0, got {indice}"


def test_return_breakdown_devuelve_tupla_con_dict():
    """Test that return_breakdown=True returns a tuple with float and dict."""
    resultado = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        return_breakdown=True,
    )

    assert isinstance(resultado, tuple), "Expected tuple when return_breakdown=True"
    assert len(resultado) == 2, "Expected tuple of length 2"

    indice, desglose = resultado

    assert isinstance(indice, float), f"Expected float for index, got {type(indice)}"
    assert isinstance(desglose, dict), f"Expected dict for breakdown, got {type(desglose)}"

    claves_minimas = {"ppg", "gd_pg", "z_ppg", "z_gd_pg", "peso_ppg", "peso_gd"}
    claves_obtenidas = set(desglose.keys())
    assert claves_minimas.issubset(claves_obtenidas), (
        f"Expected at least keys {claves_minimas}, got {claves_obtenidas}"
    )


def test_error_cuando_std_ppg_liga_es_cero():
    """Test that ValueError is raised when std_ppg_liga is zero."""
    with pytest.raises(ValueError, match="std_ppg_liga debe ser un número positivo"):
        calcular_indice_equipo(
            puntos=30,
            goles_a_favor=35,
            goles_en_contra=35,
            partidos_jugados=20,
            media_ppg_liga=1.5,
            std_ppg_liga=0.0,
            media_gd_liga=0.0,
            std_gd_liga=1.0,
        )


def test_error_cuando_std_gd_liga_es_cero():
    """Test that ValueError is raised when std_gd_liga is zero."""
    with pytest.raises(ValueError, match="std_gd_liga debe ser un número positivo"):
        calcular_indice_equipo(
            puntos=30,
            goles_a_favor=35,
            goles_en_contra=35,
            partidos_jugados=20,
            media_ppg_liga=1.5,
            std_ppg_liga=0.5,
            media_gd_liga=0.0,
            std_gd_liga=0.0,
        )


def test_error_cuando_pesos_no_suman_uno():
    """Test that ValueError is raised when weights don't sum to 1.0."""
    with pytest.raises(ValueError, match="suma de peso_ppg y peso_gd debe ser 1.0"):
        calcular_indice_equipo(
            puntos=30,
            goles_a_favor=35,
            goles_en_contra=35,
            partidos_jugados=20,
            media_ppg_liga=1.5,
            std_ppg_liga=0.5,
            media_gd_liga=0.0,
            std_gd_liga=1.0,
            peso_ppg=0.6,
            peso_gd=0.5,
        )


def test_pesos_personalizados_validos():
    """Test that custom weights work correctly when they sum to 1.0."""
    indice = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        peso_ppg=0.7,
        peso_gd=0.3,
    )
    assert isinstance(indice, float), "Expected float result with custom weights"


def test_validacion_puntos_negativos():
    """Test that ValueError is raised when points are negative."""
    with pytest.raises(ValueError, match="puntos debe ser un número no negativo"):
        calcular_indice_equipo(
            puntos=-10,
            goles_a_favor=35,
            goles_en_contra=35,
            partidos_jugados=20,
            media_ppg_liga=1.5,
            std_ppg_liga=0.5,
            media_gd_liga=0.0,
            std_gd_liga=1.0,
        )


def test_validacion_partidos_jugados_cero():
    """Test that ValueError is raised when partidos_jugados is zero."""
    with pytest.raises(ValueError, match="partidos_jugados debe ser un número positivo"):
        calcular_indice_equipo(
            puntos=30,
            goles_a_favor=35,
            goles_en_contra=35,
            partidos_jugados=0,
            media_ppg_liga=1.5,
            std_ppg_liga=0.5,
            media_gd_liga=0.0,
            std_gd_liga=1.0,
        )


def test_normalize_by_ppg_no_devuelve_negativo():
    """Test that normalize_by_ppg=True ensures non-negative index for poor teams."""
    indice = calcular_indice_equipo(
        puntos=10,
        goles_a_favor=15,
        goles_en_contra=40,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        normalize_by_ppg=True,
    )
    assert indice >= 0, f"Expected non-negative index with normalization, got {indice}"


def test_breakdown_indica_si_normaliza():
    """Test that breakdown correctly indicates whether normalization is active."""
    _, desglose_sin_norm = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        return_breakdown=True,
        normalize_by_ppg=False,
    )
    assert desglose_sin_norm["normalize_by_ppg"] is False, (
        "Expected normalize_by_ppg=False in breakdown"
    )

    _, desglose_con_norm = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        return_breakdown=True,
        normalize_by_ppg=True,
    )
    assert desglose_con_norm["normalize_by_ppg"] is True, (
        "Expected normalize_by_ppg=True in breakdown"
    )


def test_indice_normalizado_solo_aparece_cuando_corresponde():
    """Test that indice_normalizado only appears in breakdown when normalize_by_ppg=True."""
    _, desglose_sin_norm = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        return_breakdown=True,
        normalize_by_ppg=False,
    )
    assert "indice_normalizado" not in desglose_sin_norm, (
        "indice_normalizado should not be present when normalize_by_ppg=False"
    )

    _, desglose_con_norm = calcular_indice_equipo(
        puntos=40,
        goles_a_favor=50,
        goles_en_contra=30,
        partidos_jugados=20,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        return_breakdown=True,
        normalize_by_ppg=True,
    )
    assert "indice_normalizado" in desglose_con_norm, (
        "indice_normalizado should be present when normalize_by_ppg=True"
    )


def test_ppg_factor_maximo_cuando_ppg_es_tres():
    """Test that ppg_factor is 1.0 when team has perfect PPG (3 points per game)."""
    _, desglose = calcular_indice_equipo(
        puntos=39,
        goles_a_favor=50,
        goles_en_contra=20,
        partidos_jugados=13,
        media_ppg_liga=1.5,
        std_ppg_liga=0.5,
        media_gd_liga=0.0,
        std_gd_liga=1.0,
        normalize_by_ppg=True,
        return_breakdown=True,
    )
    assert desglose["ppg_factor"] == 1.0, (
        f"Expected ppg_factor=1.0 when PPG=3, got {desglose['ppg_factor']}"
    )
