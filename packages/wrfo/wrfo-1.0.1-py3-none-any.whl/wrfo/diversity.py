"""
Diversity computation functions for WRFO algorithm.
"""

import numpy as np
from typing import List
from joblib import Parallel, delayed
from tqdm.auto import tqdm
from .metrics import calculate_cohens_kappa


def kappa_score(model1, model2, X: np.ndarray, y: np.ndarray) -> float:
    """
    Compute normalized kappa score between two models.
    
    Parameters
    ----------
    model1 : estimator
        First model with predict() method
    model2 : estimator
        Second model with predict() method
    X : np.ndarray
        Features for prediction
    y : np.ndarray
        True labels (not used but kept for consistency)
        
    Returns
    -------
    float
        Normalized kappa score in range [0, 1]
    """
    y_pred1 = model1.predict(X)
    y_pred2 = model2.predict(X)
    kappa = calculate_cohens_kappa(y_pred1, y_pred2)
    
    if kappa is None:
        return 0.5
    
    return (kappa + 1) / 2


def compute_kappa_pair(i: int, j: int, trees: List, X_train: np.ndarray, 
                       y_train: np.ndarray) -> tuple:
    """
    Compute kappa score for a pair of trees.
    
    Parameters
    ----------
    i : int
        Index of first tree
    j : int
        Index of second tree
    trees : list
        List of decision tree estimators
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training labels
        
    Returns
    -------
    tuple
        (i, j, kappa_score)
    """
    distance = kappa_score(trees[i], trees[j], X_train, y_train)
    return i, j, distance


def compute_diversity_matrix_parallel(trees: List, X_train: np.ndarray, 
                                     y_train: np.ndarray, 
                                     n_jobs: int = -1,
                                     verbose: bool = True) -> np.ndarray:
    """
    Compute diversity matrix using parallel processing.
    
    The diversity matrix contains pairwise kappa-based diversity measures
    between all trees in the ensemble.
    
    Parameters
    ----------
    trees : list
        List of decision tree estimators
    X_train : np.ndarray
        Training features
    y_train : np.ndarray
        Training labels
    n_jobs : int, default=-1
        Number of parallel jobs (-1 uses all cores)
    verbose : bool, default=True
        Whether to show progress bar
        
    Returns
    -------
    np.ndarray
        Normalized diversity matrix, shape (n_trees, n_trees)
    """
    num_trees = len(trees)
    divmat = np.zeros((num_trees, num_trees))
    
    # Generate all pairs
    pairs = [(i, j) for i in range(num_trees) for j in range(i+1, num_trees)]
    
    # Parallel computation
    if verbose:
        results = Parallel(n_jobs=n_jobs, backend='threading')(
            delayed(compute_kappa_pair)(i, j, trees, X_train, y_train)
            for i, j in tqdm(pairs, desc="  Computing diversity matrix", leave=False)
        )
    else:
        results = Parallel(n_jobs=n_jobs, backend='threading')(
            delayed(compute_kappa_pair)(i, j, trees, X_train, y_train)
            for i, j in pairs
        )
    
    # Fill matrix (symmetric)
    for i, j, distance in results:
        divmat[i, j] = distance
        divmat[j, i] = distance
    
    # Normalize to [0, 1] range
    min_val = np.min(divmat)
    max_val = np.max(divmat)
    
    if max_val - min_val > 1e-10:
        divmat = (divmat - min_val) / (max_val - min_val)
    
    divmat = np.round(divmat, 3)
    
    return divmat
