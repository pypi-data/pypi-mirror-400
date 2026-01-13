"""
TeamIndexScore: A professional Python package for football team performance analysis.

This package provides tools to calculate an explainable performance index (0-100)
for football teams based on league statistics including position, points, goals,
and matches played.
"""

__version__ = "0.2.0"

from teamindexscore.core import calcular_indice_equipo

__all__ = ["calcular_indice_equipo", "__version__"]
