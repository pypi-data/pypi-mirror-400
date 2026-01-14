"""
Metrics and utility functions for WRFO algorithm.
"""

import math
import numpy as np
from collections import Counter
from typing import List, Union


def weighted_sum(predictions: np.ndarray, weights: Union[List[float], np.ndarray], 
                 num_classes: int) -> np.ndarray:
    """
    Perform weighted voting across multiple predictions.
    
    Parameters
    ----------
    predictions : np.ndarray
        Predictions from multiple models, shape (n_samples, n_models)
    weights : list or np.ndarray
        Weight for each model
    num_classes : int
        Number of classes in the classification problem
        
    Returns
    -------
    np.ndarray
        Final predictions based on weighted voting
    """
    weights_arr = np.array(weights)
    n_samples = predictions.shape[0]
    class_instances = np.zeros(n_samples, dtype=int)
    
    for i in range(n_samples):
        weighted_sums = np.bincount(
            predictions[i].astype(int), 
            weights=weights_arr, 
            minlength=num_classes
        )
        class_instances[i] = np.argmax(weighted_sums)
    
    return class_instances


def calcule_div_w(weights: Union[List[float], np.ndarray], 
                  divmat: np.ndarray) -> float:
    """
    Calculate weighted diversity measure.
    
    Parameters
    ----------
    weights : list or np.ndarray
        Weights for each tree
    divmat : np.ndarray
        Diversity matrix (pairwise diversity between trees)
        
    Returns
    -------
    float
        Weighted diversity score
    """
    weights_arr = np.array(weights) if isinstance(weights, list) else weights
    divmat2 = divmat * weights_arr[:, np.newaxis]
    np.fill_diagonal(divmat2, np.nan)
    mean_values = np.nanmean(divmat2, axis=1)
    count_nonzero = np.count_nonzero(mean_values)
    
    if count_nonzero == 0:
        return 0
    
    return np.sum(mean_values) / count_nonzero


def entropie_shannon(liste: List) -> float:
    """
    Calculate normalized Shannon entropy.
    
    Parameters
    ----------
    liste : list
        List of values (e.g., feature indices)
        
    Returns
    -------
    float
        Normalized Shannon entropy (between 0 and 1)
    """
    compteur = Counter(liste)
    total = len(liste)
    entropie = -sum((freq / total) * math.log(freq / total, 2) 
                    for freq in compteur.values())
    entropie_max = math.log(len(set(liste)), 2)
    
    if entropie_max == 0:
        return 0
    
    entropie_normalisee = entropie / entropie_max
    return entropie_normalisee


def calculate_cohens_kappa(Ti: np.ndarray, Tj: np.ndarray) -> float:
    """
    Calculate Cohen's Kappa between two sets of predictions.
    
    Parameters
    ----------
    Ti : np.ndarray
        Predictions from first model
    Tj : np.ndarray
        Predictions from second model
        
    Returns
    -------
    float
        Cohen's Kappa score, or None if undefined
    """
    observed_agreement = np.mean(Ti == Tj)
    unique_labels = np.unique(np.concatenate((Ti, Tj)))
    n = len(unique_labels)
    total_instances = len(Ti)
    
    random_agreement = np.sum(
        np.sum(np.equal.outer(
            np.histogram(Ti, bins=n, range=(0, n))[0],
            np.histogram(Tj, bins=n, range=(0, n))[0]
        ))
    ) / (total_instances ** 2)
    
    if (1 - random_agreement) != 0:
        kappa = (observed_agreement - random_agreement) / (1 - random_agreement)
        return kappa
    else:
        return None


def find_worst_weighted_trees(tree_list: List, weight_list: List[float], 
                              X_test: np.ndarray, y_test: np.ndarray) -> List[int]:
    """
    Find indices of trees performing below average.
    
    Parameters
    ----------
    tree_list : list
        List of decision tree estimators
    weight_list : list
        Current weights for each tree
    X_test : np.ndarray
        Test features
    y_test : np.ndarray
        Test labels
        
    Returns
    -------
    list
        Indices of below-average trees
    """
    accuracies = []
    for i, tree in enumerate(tree_list):
        if weight_list[i] > 0.0:
            accuracy = tree.score(X_test, y_test)
            accuracies.append((i, accuracy))
    
    if not accuracies:
        return []
    
    average_accuracy = sum(accuracy for _, accuracy in accuracies) / len(accuracies)
    indices = [i for i, accuracy in accuracies if accuracy < average_accuracy]
    return indices


def find_worst_weighted_trees_div(tree_list: List, weight_list: List[float], 
                                  divmat: np.ndarray) -> List[int]:
    """
    Find indices of trees with high diversity (potential outliers).
    
    Parameters
    ----------
    tree_list : list
        List of decision tree estimators
    weight_list : list
        Current weights for each tree
    divmat : np.ndarray
        Diversity matrix
        
    Returns
    -------
    list
        Indices of high-diversity trees
    """
    diversities = []
    for i, tree in enumerate(tree_list):
        if weight_list[i] > 0.0:
            diversity = np.mean(divmat[i])
            diversities.append((i, diversity))
    
    if not diversities:
        return []
    
    std = np.std([d for _, d in diversities])
    average_diversity = np.mean([diversity for _, diversity in diversities])
    indices = [i for i, diversity in diversities 
               if diversity > (average_diversity + (std / 4))]
    return indices
