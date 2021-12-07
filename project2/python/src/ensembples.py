import numpy as np
from scipy.optimize import minimize_scalar
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor


class RandomForestMSE:
    def __init__(
        self, n_estimators, max_depth=None, feature_subsample_size=None, 
        object_subsample_size=None, random_seed=None,
        **trees_parameters
    ):
        """
        n_estimators : int
            The number of trees in the forest.
        max_depth : int
            The maximum depth of the tree. If None then there is no limits.
        feature_subsample_size : float
            The size of feature set for each tree. If None then use one-third of all features.
        """

        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.feature_subsample_size = feature_subsample_size
        self.object_subsample_size = object_subsample_size
        self.trees_parameters = trees_parameters 
        self.estimators = []
        self.indices = []
        np.random.seed(random_seed)

    
    def _sample_indices(self, maximum, size):
        return np.random.choice(maximum, size, replace=True)

    def fit(self, X, y, X_val=None, y_val=None):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        y : numpy ndarray
            Array of size n_objects
        X_val : numpy ndarray
            Array of size n_val_objects, n_features
        y_val : numpy ndarray
            Array of size n_val_objects
        """
        
        if self.feature_subsample_size is None:
            self.feature_subsample_size = X.shape[1] // 3
        
        if self.object_subsample_size is None:
            if self.n_estimators != 1:
                self.object_subsample_size = int(1.5 * X.shape[0] // self.n_estimators) 
            else:
                self.object_subsample_size = X.shape[0]
        
        for _ in range(self.n_estimators):
            est = DecisionTreeRegressor(
                max_depth=self.max_depth,
                **self.trees_parameters)

            obj_ind = self._sample_indices(X.shape[1], self.feature_subsample_size)
            X_train, y_train = X[obj_ind], y[obj_ind]

            feat_ind = self._sample_indices(X.shape[1], self.feature_subsample_size)
            est.fit(X_train[:, feat_ind], y_train)
            self.indices.append(feat_ind)
            self.estimators.append(est)

        return self


    def predict(self, X):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        Returns
        -------
        y : numpy ndarray
            Array of size n_objects
        """

        predictions = np.zeros(X.shape[0], dtype=float)

        for feat, est in zip(self.indices, self.estimators):
            predictions += est.predict(X[:, feat])
        
        return predictions / self.n_estimators


class GradientBoostingMSE:
    def __init__(
        self, n_estimators, learning_rate=0.1, max_depth=5, 
        feature_subsample_size=None, object_subsample_size=None, random_seed=None,
        **trees_parameters
    ):
        """
        n_estimators : int
            The number of trees in the forest.
        learning_rate : float
            Use alpha * learning_rate instead of alpha
        max_depth : int
            The maximum depth of the tree. If None then there is no limits.
        feature_subsample_size : float
            The size of feature set for each tree. If None then use one-third of all features.
        """

        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.feature_subsample_size = feature_subsample_size
        self.object_subsample_size = object_subsample_size
        self.trees_parameters = trees_parameters
        self.indices = []
        self.estimators = []
        self.weights = []
        np.random.seed(random_seed)

    def _sample_indices(self, maximum, size):
        return np.random.choice(maximum, size, replace=True)
    
    def fit(self, X, y, X_val=None, y_val=None):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        y : numpy ndarray
            Array of size n_objects
        """

        self.estimators = []
        self.indices = []
        self.weights = []

        if self.feature_subsample_size is None:
            self.feature_subsample_size = X.shape[1] // 3
        
        if self.object_subsample_size is None:
            if self.n_estimators != 1:
                self.object_subsample_size = int(1.5 * X.shape[0] // self.n_estimators) 
            else:
                self.object_subsample_size = X.shape[0]

        a_y = np.zeros(y.shape[0], dtype=float)
        
        for _ in range(self.n_estimators):
            est = DecisionTreeRegressor(
                max_depth=self.max_depth,
                **self.trees_parameters)

            obj_ind = self._sample_indices(X.shape[1], self.feature_subsample_size)
            X_train, y_train = X[obj_ind], y[obj_ind]

            feat_ind = self._sample_indices(X.shape[1], self.feature_subsample_size)

            est.fit(X_train[:, feat_ind], 2 * (a_y[obj_ind] - y_train) / y_train.shape[0])

            self.indices.append(feat_ind)
            self.estimators.append(est)

            pred = est.predict(X[:, feat_ind])
            weight = minimize_scalar(lambda x: np.mean((y - a_y - x * pred)**2)).x

            self.weights.append(weight)
            a_y += self.learning_rate * weight * pred


        return self


    def predict(self, X):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        Returns
        -------
        y : numpy ndarray
            Array of size n_objects
        """

        predictions = np.zeros(X.shape[0], dtype=float)

        for feat, est, weight in zip(self.indices, self.estimators, self.weights):
            predictions += self.learning_rate * weight * est.predict(X[:, feat]) 
        
        return predictions
