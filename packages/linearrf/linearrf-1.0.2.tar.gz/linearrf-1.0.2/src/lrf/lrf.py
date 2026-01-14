from typing import List, Any

import numpy as np

from lrf._base_lrf import _LinearRandomForest
from lrf._linear_models import Regressor, Classifier
from lrf._criterion import (mse, rmse, mae, mape, wape, neg_explained_variance, neg_r2,
                            hamming, cross_entropy, neg_mcc, neg_roc_auc, neg_pr_auc)
from lrf._node import Node


class LRFRegressor(_LinearRandomForest):
    def __init__(self, linear_model: Any = None, alpha: float = 2.0, preprocessing: str = None,
                 n_estimators: int = 100, max_depth: int = 5, n_splits: int = 15,
                 split_samples_to_features_ratio: float = 4.5, min_abs_improvement: float = 1 * 10 ** (-4),
                 leaf_samples_to_features_ratio: float = 2.0, criterion: str = 'mse',
                 n_jobs: int = -1, random_state: int = None, verbose: bool = False):

        self.alpha = alpha
        self.preprocessing = preprocessing
        self._estimator_type = 'regressor'

        if linear_model is None:
            linear_model = Regressor(alpha=self.alpha, preprocessing=self.preprocessing, intercept_in_input=True)
        else:
            assert hasattr(linear_model, 'fit')
            assert hasattr(linear_model, 'predict')

        super().__init__(linear_model=linear_model,
                         n_estimators=n_estimators, max_depth=max_depth, criterion=criterion,
                         n_splits=n_splits, split_samples_to_features_ratio=split_samples_to_features_ratio,
                         leaf_samples_to_features_ratio=leaf_samples_to_features_ratio,
                         min_abs_improvement=min_abs_improvement,
                         n_jobs=n_jobs, random_state=random_state, verbose=verbose)

    def predict(self, x: np.ndarray):
        # add intercept here and not inside linear model for performance reasons
        x = np.insert(x, 0, 1, axis=1)

        # add columns with row index for sorting after multiprocessing
        x = np.insert(x, 0, np.arange(x.shape[0]), axis=1)

        results = [self._predict_tree(node=node, x=x, results=[]) for node in self.forest]

        results = [np.vstack(i) for i in results]
        results = np.array([i[np.argsort(i[:, 0])][:, 1:] for i in results])
        results = results.mean(axis=0).flatten()
        return results

    def _predict_tree(self, node: Node, x: np.ndarray, results: List):
        if node.model is None:
            if x.shape[0] > 0:
                left_indices = x[:, node.split_col_idx + 1] < node.threshold
                right_indices = ~left_indices

                results = self._predict_tree(node.left_node, x[left_indices], results)
                results = self._predict_tree(node.right_node, x[right_indices], results)
        else:
            if x.shape[0] > 0:
                node_results = node.model.predict(x[:, 1:])
                node_results = np.insert(node_results[:, np.newaxis], 0, x[:, 0], axis=1)

                results.extend(node_results)

        return results

    def _calculate_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        if self.criterion == 'mse':
            val = mse(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'rmse':
            val = rmse(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'mae':
            val = mae(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'mape':
            val = mape(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'wape':
            val = wape(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'neg_explained_variance':
            val = neg_explained_variance(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'neg_r2':
            val = neg_r2(y_true=y_true, y_pred=y_pred)
        else:
            print(' Metric "{}" is not implemented, MSE is used instead.'.format(self.criterion))
            val = mse(y_true=y_true, y_pred=y_pred)

        return val

    def get_params(self, deep: bool = True):
        return {'linear_model': self.linear_model, 'alpha': self.alpha, 'preprocessing': self.preprocessing,
                'n_estimators': self.n_estimators, 'max_depth': self.max_depth, 'n_splits': self.n_splits,
                'split_samples_to_features_ratio': self.split_samples_to_features_ratio,
                'leaf_samples_to_features_ratio': self.leaf_samples_to_features_ratio, 'criterion': self.criterion,
                'n_jobs': self.n_jobs, 'random_state': self.random_state, 'verbose': self.verbose}

    def score(self, X: np.ndarray, y: np.ndarray):
        y_pred = self.predict(X)
        return -neg_r2(y_true=y, y_pred=y_pred)


class LRFClassifier(_LinearRandomForest):
    def __init__(self, linear_model: Any = None, C: float = 1.0, n_estimators: int = 100, max_depth: int = 5,
                 n_splits: int = 15,  split_samples_to_features_ratio: float = 4.5,
                 leaf_samples_to_features_ratio: float = 2.0, criterion: str = 'neg_mcc',
                 min_abs_improvement: float = 5*10**(-4), n_jobs: int = -1, random_state: int = None,
                 verbose: bool = False, preprocessing: str = 'standardize', warm_start: bool = True):

        self.C = C
        self.preprocessing = preprocessing
        self._estimator_type = 'classifier'

        if linear_model is None:
            linear_model = Classifier(C=self.C, preprocessing=self.preprocessing, intercept_in_input=True)
        else:
            assert hasattr(linear_model, 'fit')
            assert hasattr(linear_model, 'predict')
            assert hasattr(linear_model, 'predict_proba')

        super().__init__(linear_model=linear_model,
                         n_estimators=n_estimators, max_depth=max_depth, criterion=criterion,
                         n_splits=n_splits, min_abs_improvement=min_abs_improvement,
                         split_samples_to_features_ratio=split_samples_to_features_ratio, random_state=random_state,
                         leaf_samples_to_features_ratio=leaf_samples_to_features_ratio, n_jobs=n_jobs, verbose=verbose,
                         classification=True, warm_start=warm_start)

    def predict(self, x: np.ndarray):
        """
        Predict the classes using the linear random forest.

        Args:
            x: Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted classes.
        """

        return np.argmax(self.predict_proba(x=x), axis=1)

    def predict_proba(self, x: np.ndarray):
        """
        Make a prediction of the probability of each class using the linear random forest.

        Args:
            x: Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted probability of each class.
        """

        # add intercept here and not inside linear model for performance reasons
        x = np.insert(x, 0, 1, axis=1)

        # add columns with row index for sorting after multiprocessing
        x = np.insert(x, 0, np.arange(x.shape[0]), axis=1)

        results = [self._predict_proba_tree(node=node, x=x, results=[]) for node in self.forest]

        c = results[0][0].shape[0]

        results = [np.concatenate(i).reshape((-1, c)) for i in results]
        results = np.array([i[np.argsort(i[:, 0])][:, 1:] for i in results])
        results = results.mean(axis=0)
        return results

    def _predict_proba_tree(self, node: Node, x: np.ndarray, results: List):
        """
        Make a prediction of the probability of each class using one given tree of the linear random forest.

        Args:
            x: Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted probability of each class.
        """

        if node.model is None:
            if x.shape[0] > 0:
                left_indices = x[:, node.split_col_idx + 1] < node.threshold
                right_indices = ~left_indices

                results = self._predict_proba_tree(node.left_node, x[left_indices], results)
                results = self._predict_proba_tree(node.right_node, x[right_indices], results)
        else:
            if x.shape[0] > 0:
                node_results = node.model.predict_proba(x[:, 1:])
                n, m = node_results.shape
                res = np.empty((n, m + 1))
                res[:, 0] = x[:, 0]
                res[:, 1:] = node_results

                results.extend(res)

        return results

    def _calculate_metric(self, y_true: np.ndarray, y_pred: np.ndarray):
        if self.criterion == 'neg_mcc':
            val = neg_mcc(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'neg_pr_auc':
            val = neg_pr_auc(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'hamming':
            val = hamming(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'cross_entropy':
            val = cross_entropy(y_true=y_true, y_pred=y_pred)
        elif self.criterion == 'neg_roc_auc':
            val = neg_roc_auc(y_true=y_true, y_pred=y_pred)
        else:
            print(' Metric "{}" is not implemented, the negative Matthews Correlation Coefficient is used '
                  'instead.'.format(self.criterion))
            val = neg_mcc(y_true=y_true, y_pred=y_pred)

        return val

    def get_params(self, deep=True):
        return {'linear_model': self.linear_model, 'C': self.C, 'preprocessing': self.preprocessing,
                'n_estimators': self.n_estimators, 'max_depth': self.max_depth, 'n_splits': self.n_splits,
                'split_samples_to_features_ratio': self.split_samples_to_features_ratio,
                'leaf_samples_to_features_ratio': self.leaf_samples_to_features_ratio, 'criterion': self.criterion,
                'n_jobs': self.n_jobs, 'random_state': self.random_state, 'verbose': self.verbose}

    def score(self, X: np.ndarray, y: np.ndarray):
        y_pred = self.predict(X)
        return np.count_nonzero(y == y_pred)/y.shape[0]
