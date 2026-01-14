"""
Main WRFO Classifier implementation.
"""

import numpy as np
from typing import Optional, Union
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from pyswarm import pso
import warnings

from .diversity import compute_diversity_matrix_parallel
from .metrics import weighted_sum, calcule_div_w, entropie_shannon
from .objective import ObjectiveFunction


class WRFOClassifier(BaseEstimator, ClassifierMixin):
    """
    Weighted Random Forest Optimization Classifier.
    
    This classifier trains a Random Forest and then uses Particle Swarm 
    Optimization (PSO) to find optimal weights for each tree based on a
    multi-objective function combining accuracy, diversity, and entropy.
    
    Parameters
    ----------
    n_estimators : int, default=100
        Number of trees in the random forest
    
    swarm_size : int, default=10
        Number of particles in PSO swarm
    
    max_iter : int, default=10
        Maximum number of PSO iterations
    
    accuracy_weight : float, default=0.6
        Weight for accuracy component in objective function
    
    diversity_weight : float, default=0.4
        Weight for diversity component in objective function
    
    entropy_weight : float, default=0.1
        Weight for Shannon entropy component in objective function
    
    val_split : float, default=0.2
        Proportion of training data to use for validation during PSO
    
    random_state : int or None, default=None
        Random state for reproducibility
    
    n_jobs : int, default=-1
        Number of parallel jobs for Random Forest and diversity computation
    
    verbose : bool, default=True
        Whether to print progress information
    
    Attributes
    ----------
    rf_ : RandomForestClassifier
        The trained random forest
    
    weights_ : np.ndarray
        Optimized weights for each tree
    
    classes_ : np.ndarray
        Class labels
    
    divmat_ : np.ndarray
        Diversity matrix between trees
    
    n_features_in_ : int
        Number of features seen during fit
    
    Examples
    --------
    >>> from wrfo import WRFOClassifier
    >>> from sklearn.datasets import load_iris
    >>> from sklearn.model_selection import train_test_split
    >>> X, y = load_iris(return_X_y=True)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    >>> clf = WRFOClassifier(n_estimators=50, random_state=42)
    >>> clf.fit(X_train, y_train)
    >>> y_pred = clf.predict(X_test)
    >>> print(f"Accuracy: {clf.score(X_test, y_test):.3f}")
    """
    
    def __init__(self, 
                 n_estimators: int = 100,
                 swarm_size: int = 10,
                 max_iter: int = 10,
                 accuracy_weight: float = 0.6,
                 diversity_weight: float = 0.4,
                 entropy_weight: float = 0.1,
                 val_split: float = 0.2,
                 random_state: Optional[int] = None,
                 n_jobs: int = -1,
                 verbose: bool = True):
        self.n_estimators = n_estimators
        self.swarm_size = swarm_size
        self.max_iter = max_iter
        self.accuracy_weight = accuracy_weight
        self.diversity_weight = diversity_weight
        self.entropy_weight = entropy_weight
        self.val_split = val_split
        self.random_state = random_state
        self.n_jobs = n_jobs
        self.verbose = verbose
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'WRFOClassifier':
        """
        Fit the WRFO classifier.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Training data
        y : np.ndarray, shape (n_samples,)
            Target values
            
        Returns
        -------
        self : WRFOClassifier
            Fitted classifier
        """
        # Validate input
        X, y = check_X_y(X, y)
        self.classes_ = unique_labels(y)
        self.n_features_in_ = X.shape[1]
        
        # Split for PSO optimization
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=self.val_split, random_state=self.random_state,
            stratify=y
        )
        
        if self.verbose:
            print(f"Training WRFO with {self.n_estimators} trees...")
            print(f"  Train: {X_train.shape[0]} samples | Validation: {X_val.shape[0]} samples")
        
        # Train Random Forest
        if self.verbose:
            print("  [1/3] Training Random Forest...")
        
        self.rf_ = RandomForestClassifier(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=self.n_jobs
        )
        self.rf_.fit(X_train, y_train)
        
        # Baseline performance
        if self.verbose:
            y_pred = self.rf_.predict(X_val)
            rf_score = accuracy_score(y_val, y_pred)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_val, y_pred, average='weighted'
            )
            root_features = [tree.tree_.feature[0] for tree in self.rf_.estimators_]
            shan = entropie_shannon(root_features)
            print(f"    RF Baseline: Acc={rf_score:.4f} | Prec={precision:.4f} | "
                  f"Rec={recall:.4f} | F1={f1:.4f} | Shannon={shan:.4f}")
        
        # Compute diversity matrix
        if self.verbose:
            print("  [2/3] Computing diversity matrix...")
        
        self.divmat_ = compute_diversity_matrix_parallel(
            self.rf_.estimators_, X_train, y_train, 
            n_jobs=self.n_jobs, verbose=self.verbose
        )
        
        if self.verbose:
            uniform_weights = np.ones(self.n_estimators)
            kappa = calcule_div_w(uniform_weights, self.divmat_)
            print(f"    Diversity (uniform weights): {kappa:.4f}")
        
        # PSO Optimization
        if self.verbose:
            print("  [3/3] Optimizing weights with PSO...")
        
        # Create objective function
        obj_func = ObjectiveFunction(
            trees=self.rf_.estimators_,
            X_train=X_train,
            X_test=X_val,
            y_train=y_train,
            y_test=y_val,
            divmat=self.divmat_,
            unique_classes=self.classes_,
            rf=self.rf_,
            accuracy_weight=self.accuracy_weight,
            diversity_weight=self.diversity_weight,
            entropy_weight=self.entropy_weight
        )
        
        # Run PSO
        lb = np.zeros(self.n_estimators)
        ub = np.ones(self.n_estimators)
        
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore')
            self.weights_, fopt = pso(
                obj_func, lb, ub,
                swarmsize=self.swarm_size,
                maxiter=self.max_iter
            )
        
        if self.verbose:
            num_selected = np.sum(self.weights_ > 0.0)
            print(f"    PSO converged: {num_selected}/{self.n_estimators} trees selected")
            
            # Evaluate optimized ensemble on validation set
            val_predictions = np.column_stack([
                tree.predict(X_val) for tree in self.rf_.estimators_
            ])
            y_pred_wrfo = weighted_sum(val_predictions, self.weights_, len(self.classes_))
            wrfo_score = accuracy_score(y_val, y_pred_wrfo)
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_val, y_pred_wrfo, average='weighted'
            )
            kappa = calcule_div_w(self.weights_, self.divmat_)
            root_features = [
                tree.tree_.feature[0] 
                for tree, w in zip(self.rf_.estimators_, self.weights_) 
                if w > 0.0
            ]
            shan = entropie_shannon(root_features) if root_features else 0
            
            print(f"    WRFO Results: Acc={wrfo_score:.4f} | Prec={precision:.4f} | "
                  f"Rec={recall:.4f} | F1={f1:.4f} | Kappa={kappa:.4f} | Shannon={shan:.4f}")
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Samples
            
        Returns
        -------
        y_pred : np.ndarray, shape (n_samples,)
            Predicted class labels
        """
        check_is_fitted(self, ['rf_', 'weights_', 'classes_'])
        X = check_array(X)
        
        # Get predictions from all trees
        predictions = np.column_stack([
            tree.predict(X) for tree in self.rf_.estimators_
        ])
        
        # Weighted voting
        y_pred = weighted_sum(predictions, self.weights_, len(self.classes_))
        
        return y_pred
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities (not yet implemented for weighted ensemble).
        
        For now, this returns the standard Random Forest probabilities.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Samples
            
        Returns
        -------
        proba : np.ndarray, shape (n_samples, n_classes)
            Class probabilities
        """
        check_is_fitted(self, ['rf_'])
        return self.rf_.predict_proba(X)
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """
        Return accuracy score.
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            Test samples
        y : np.ndarray, shape (n_samples,)
            True labels
            
        Returns
        -------
        score : float
            Accuracy score
        """
        y_pred = self.predict(X)
        return accuracy_score(y, y_pred)
    
    def get_params(self, deep: bool = True) -> dict:
        """Get parameters for this estimator."""
        return {
            'n_estimators': self.n_estimators,
            'swarm_size': self.swarm_size,
            'max_iter': self.max_iter,
            'accuracy_weight': self.accuracy_weight,
            'diversity_weight': self.diversity_weight,
            'entropy_weight': self.entropy_weight,
            'val_split': self.val_split,
            'random_state': self.random_state,
            'n_jobs': self.n_jobs,
            'verbose': self.verbose
        }
    
    def set_params(self, **params) -> 'WRFOClassifier':
        """Set parameters for this estimator."""
        for key, value in params.items():
            setattr(self, key, value)
        return self
