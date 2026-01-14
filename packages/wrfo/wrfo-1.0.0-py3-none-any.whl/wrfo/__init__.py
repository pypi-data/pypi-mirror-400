"""
WRFO: Weighted Random Forest Optimization
==========================================

A Random Forest ensemble optimization algorithm that uses Particle Swarm 
Optimization (PSO) to find optimal tree weights based on diversity and 
performance metrics.

Main classes:
    WRFOClassifier: Main classifier implementing the WRFO algorithm

Main functions:
    compute_diversity_matrix: Compute pairwise diversity matrix for trees
"""

from .optimizer import WRFOClassifier
from .diversity import compute_diversity_matrix_parallel as compute_diversity_matrix

__version__ = "1.0.0"
__all__ = ["WRFOClassifier", "compute_diversity_matrix"]
