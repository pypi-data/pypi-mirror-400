"""
Objective functions for PSO optimization in WRFO.
"""

import numpy as np
from typing import List, Dict, Any
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from .metrics import (
    weighted_sum, 
    calcule_div_w, 
    entropie_shannon,
    find_worst_weighted_trees,
    find_worst_weighted_trees_div
)


class ObjectiveFunction:
    """
    PSO objective function with prediction caching and adaptive weighting.
    
    This class maintains state across PSO iterations, caching predictions
    to avoid redundant computation and adaptively adjusting weights based
    on tree performance.
    """
    
    def __init__(self, trees: List, X_train: np.ndarray, X_test: np.ndarray,
                 y_train: np.ndarray, y_test: np.ndarray, divmat: np.ndarray,
                 unique_classes: np.ndarray, rf,
                 accuracy_weight: float = 0.6,
                 diversity_weight: float = 0.4,
                 entropy_weight: float = 0.1):
        """
        Initialize objective function.
        
        Parameters
        ----------
        trees : list
            List of decision tree estimators
        X_train : np.ndarray
            Training features (for optimization)
        X_test : np.ndarray
            Test features (for tree removal)
        y_train : np.ndarray
            Training labels
        y_test : np.ndarray
            Test labels
        divmat : np.ndarray
            Diversity matrix
        unique_classes : np.ndarray
            Unique class labels
        rf : RandomForestClassifier
            Original random forest (for root feature access)
        accuracy_weight : float, default=0.6
            Weight for accuracy component
        diversity_weight : float, default=0.4
            Weight for diversity component (actually becomes 1-diversity in objective)
        entropy_weight : float, default=0.1
            Weight for Shannon entropy component
        """
        self.trees = trees
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.divmat = divmat
        self.unique_classes = unique_classes
        self.rf = rf
        self.num_classes = len(unique_classes)
        
        self.accuracy_weight = accuracy_weight
        self.diversity_weight = diversity_weight
        self.entropy_weight = entropy_weight
        
        # Cache predictions
        self._cache_predictions()
        
        # Initialization flag
        self.initialized = False
    
    def _cache_predictions(self):
        """Pre-compute all predictions for efficiency."""
        self.train_predictions = np.column_stack([
            tree.predict(self.X_train) for tree in self.trees
        ])
        self.test_predictions = np.column_stack([
            tree.predict(self.X_test) for tree in self.trees
        ])
    
    def __call__(self, sol: np.ndarray) -> float:
        """
        Evaluate objective function for PSO.
        
        Parameters
        ----------
        sol : np.ndarray
            Candidate solution (tree weights)
            
        Returns
        -------
        float
            Negative objective value (PSO minimizes)
        """
        # Initialize with sparse weights on first call
        if not self.initialized:
            sol = np.zeros(len(self.trees))
            indices_to_set = np.random.choice(len(sol), min(100, len(sol)), 
                                             replace=False)
            sol[indices_to_set] = 1.0
            self.initialized = True
        
        weights = list(sol)
        
        # Handle all-zero weights
        if all(weight == 0.0 for weight in weights):
            return 100000
        
        # Adaptively remove worst-performing trees
        worst_tree_index = find_worst_weighted_trees(
            self.trees, weights, self.X_test, self.y_test
        )
        for indice in worst_tree_index:
            if indice is not None:
                sol[indice] = max(0.0, sol[indice] - 0.1)
                weights[indice] = max(0.0, weights[indice] - 0.1)
        
        # Remove trees with high diversity (outliers)
        worst_tree_index = find_worst_weighted_trees_div(
            self.trees, weights, self.divmat
        )
        for indice in worst_tree_index:
            if indice is not None:
                sol[indice] = max(0.0, sol[indice] - 0.1)
                weights[indice] = max(0.0, weights[indice] - 0.1)
        
        # Use cached predictions
        predicted_classes = weighted_sum(
            self.train_predictions, weights, self.num_classes
        )
        
        # Compute metrics
        confusion_mat = confusion_matrix(
            self.y_train, predicted_classes, labels=self.unique_classes
        )
        accuracy = np.sum(np.diag(confusion_mat)) / np.sum(confusion_mat)
        precision, recall, f1_score, support = precision_recall_fscore_support(
            self.y_train, predicted_classes
        )
        
        # Root feature diversity (Shannon entropy)
        root_feature_indices = [
            tree.tree_.feature[0] 
            for tree, value in zip(self.rf.estimators_, weights) 
            if value != 0.0
        ]
        
        if len(root_feature_indices) == 0:
            shan = 0
        else:
            shan = entropie_shannon(root_feature_indices)
        
        # Weighted F1 score
        pr = np.mean(f1_score)
        
        # Diversity measure
        kappa = calcule_div_w(weights, self.divmat)
        
        # Combined objective: maximize accuracy and entropy, minimize diversity
        objective = (
            self.accuracy_weight * pr + 
            self.diversity_weight * (1 - kappa) + 
            self.entropy_weight * shan
        )
        
        # Return negative (PSO minimizes)
        return -1.0 * objective
    
    def reset(self):
        """Reset initialization flag for a new optimization run."""
        self.initialized = False
