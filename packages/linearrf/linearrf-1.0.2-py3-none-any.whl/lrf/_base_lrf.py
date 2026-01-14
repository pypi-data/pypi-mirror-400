import copy
import datetime
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import List, Union

import numpy as np

from lrf._linear_models import Regressor, Classifier
from lrf._node import Node


class _LinearRandomForest:
    def __init__(self, linear_model: Union[Regressor, Classifier] = None, n_estimators: int = 100, max_depth: int = 5,
                 criterion: str = None, n_splits: int = 15, split_samples_to_features_ratio: float = 4.5,
                 leaf_samples_to_features_ratio: float = 2.0, min_abs_improvement: float = 5*10**(-4),
                 warm_start: bool = True, n_jobs: int = -1, random_state: int = None, verbose: bool = False,
                 classification: bool = False):
        self.linear_model = linear_model
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.criterion = criterion
        self.n_splits = n_splits
        self.split_samples_to_features_ratio = split_samples_to_features_ratio
        self.leaf_samples_to_features_ratio = leaf_samples_to_features_ratio
        self.min_abs_improvement = min_abs_improvement
        self.warm_start = warm_start
        self.n_jobs = n_jobs
        self.random_state = random_state
        self.verbose = verbose
        self.classification = classification

    def _init_more_attributes(self, y):
        if self.classification:
            self.classes_ = None

        self.forest = None
        self.min_samples_split = None
        self.min_samples_leaf = None

        if self.max_depth is None:
            self.max_depth = 10 ** 32

        if self.n_jobs == -1 or self.n_jobs == 0:
            self.n_jobs = cpu_count()
        else:
            self.n_jobs = min(self.n_jobs, cpu_count())

        if self.split_samples_to_features_ratio < self.leaf_samples_to_features_ratio * 2:
            self.split_samples_to_features_ratio = self.leaf_samples_to_features_ratio * 2

        self.min_samples_split = None
        self.min_samples_leaf = None

        self.total_data_points = y.shape[0]

    def fit(self, x: np.ndarray, y: np.ndarray):

        assert y.ndim == 1
        assert not np.all(y == y[0])

        self._init_more_attributes(y=y)

        if self.classification:
            self._check_targets_classification(y)

        random_state_list = np.random.default_rng(self.random_state).integers(2**63, size=self.n_estimators)

        self.min_samples_split = self.split_samples_to_features_ratio * x.shape[1]
        self.min_samples_leaf = self.leaf_samples_to_features_ratio * x.shape[1]

        forest = []

        # add intercept here and not inside linear model for performance reasons
        x = np.insert(x, 0, 1, axis=1)

        # parallel process combinations of chunks of the data
        with ProcessPoolExecutor(max_workers=self.n_jobs) as executor:
            if self.verbose:
                print('\nStart growing trees...')
                finished_tasks = 0
                start_time = time.time()

            results = [executor.submit(self._grow_tree, x=x, y=y, random_state=i) for i in random_state_list]

            # collect the results and print the progress
            for r in as_completed(results):
                # collecting results
                grown_tree = r.result()
                forest.append(grown_tree)

                # printing progress
                if self.verbose:
                    finished_tasks += 1
                    self._print_progress(frac=finished_tasks/self.n_estimators, start_time=start_time)

        self.forest = forest
        
        if self.verbose:
            elapsed_seconds = round(time.time() - start_time)
            print('Finished planting the forest in {}     '.format(str(datetime.timedelta(seconds=elapsed_seconds))))

    @staticmethod
    def _print_progress(frac: float, start_time: float):
        """
        Prints the progress of the parallel multiprocessing
        Args:
            frac (int): Fraction of tasks which are already finished

        """
        elapsed_seconds = round(time.time() - start_time)
        remaining_seconds = round(elapsed_seconds / frac - elapsed_seconds)
        print('LRF - Progress: {}%, [{}<{}]'.format(
            round(100 * frac, 2),
            str(datetime.timedelta(seconds=elapsed_seconds)),
            str(datetime.timedelta(seconds=remaining_seconds))
        ), end='\r')

    def _grow_tree(self, x: np.ndarray, y: np.ndarray, random_state: int):

        rng = np.random.default_rng(random_state)

        idx = rng.choice(np.arange(x.shape[0]), x.shape[0])
        x = x[idx]
        y = y[idx]

        tree = self._root_node(x=x, y=y)

        # split
        tree = self._split(node=tree, x=x, y=y, depth=0, rng=rng)

        return tree

    def _root_node(self, x: np.ndarray, y: np.ndarray):
        # initial linear model
        root_model = copy.deepcopy(self.linear_model)

        if isinstance(root_model, (Regressor, Classifier)):
            root_model.fit(x, y, None)
        else:
            root_model.fit(x, y)

        if self.criterion == 'cross_entropy':
            y_pred = root_model.predict_proba(x)
        elif (self.criterion == 'neg_roc_auc') or (self.criterion == 'neg_pr_auc'):
            y_pred = root_model.predict_proba(x)[:, 1]
        else:
            y_pred = root_model.predict(x)

        metric = self._calculate_metric(y_true=y, y_pred=y_pred)

        # create node object
        tree = Node(depth=0, metric=metric, model=root_model)

        return tree

    def _split(self, node: Node, x: np.ndarray, y: np.ndarray, depth: int, rng: np.random.Generator):
        if (depth == self.max_depth) or np.all(np.all(x == x[0, :], axis=1)) or (x.shape[0] < self.min_samples_split):
            return node
        else:
            split = self._find_best_split(x=x, y=y, last_metric=node.metric, old_coefs=node.model.coef_, rng=rng)

            if split.get('threshold') is not None:
                node.threshold = split['threshold']
                node.split_col_idx = split['column']

                left_node = Node(depth=depth + 1, model=split['model_left'], metric=split['metric_left'])
                left_node = self._split(node=left_node, x=split['x_left'], y=split['y_left'],
                                        depth=depth + 1, rng=rng)

                right_node = Node(depth=depth + 1, model=split['model_right'], metric=split['metric_right'])
                right_node = self._split(node=right_node, x=split['x_right'], y=split['y_right'],
                                         depth=depth + 1, rng=rng)

                node.left_node = left_node
                node.right_node = right_node
                node.model = None

            return node

    def _find_best_split(self, x: np.ndarray, y: np.ndarray,
                         last_metric: float, old_coefs: np.ndarray, rng: np.random.Generator):
        split = {}

        random_col_ids = rng.choice(np.arange(1, (x.shape[1])), int(round(np.sqrt(x.shape[1] - 1))), replace=False)

        for col in random_col_ids:
            split_candidates = self._split_values(x[:, col])

            for thresh in split_candidates:
                left_idx = x[:, col] <= thresh
                left_idx, right_idx = left_idx.nonzero()[0], (~left_idx).nonzero()[0]

                if x[:, col].max() == thresh:
                    continue

                x_left, y_left = x.take(left_idx, axis=0), y.take(left_idx, axis=0)
                x_right, y_right = x.take(right_idx, axis=0), y.take(right_idx, axis=0)

                if np.all(y_left == y_left[0]) or np.all(y_right == y_right[0]):
                    continue

                observations_left, observations_right = y_left.shape[0], y_right.shape[0]

                if (
                        observations_left < self.min_samples_leaf
                ) or (
                        observations_right < self.min_samples_leaf
                ):
                    continue

                # initialize models
                model_left, model_right = copy.deepcopy(self.linear_model), copy.deepcopy(self.linear_model)

                # fit models
                if self.warm_start and isinstance(model_left, (Regressor, Classifier)) and isinstance(
                        model_right, (Regressor, Classifier)):
                    model_left.fit(x_left, y_left, initial_coefs=old_coefs)
                    model_right.fit(x_right, y_right, initial_coefs=old_coefs)
                else:
                    model_left.fit(x_left, y_left, None)
                    model_right.fit(x_right, y_right, None)

                # get prediction for these nodes
                if self.criterion == 'cross_entropy':
                    y_pred_left = model_left.predict_proba(x_left)
                    y_pred_right = model_right.predict_proba(x_right)
                elif (self.criterion == 'neg_roc_auc') or (self.criterion == 'neg_pr_auc'):
                    y_pred_left = model_left.predict_proba(x_left)[:, 1]
                    y_pred_right = model_right.predict_proba(x_right)[:, 1]
                else:
                    y_pred_left = model_left.predict(x_left)
                    y_pred_right = model_right.predict(x_right)

                # get metrics for these nodes
                metric_left = self._calculate_metric(y_true=y_left, y_pred=y_pred_left)
                metric_right = self._calculate_metric(y_true=y_right, y_pred=y_pred_right)

                new_metric = ((metric_left * observations_left + metric_right * observations_right)
                              / (observations_left + observations_right))
                better_split = new_metric < (last_metric - self.min_abs_improvement)

                if better_split:
                    last_metric = new_metric

                    split = {'column': col,
                             'threshold': thresh,
                             'model_left': model_left,
                             'model_right': model_right,
                             'x_right': x_right,
                             'y_right': y_right,
                             'x_left': x_left,
                             'y_left': y_left,
                             'metric_left': metric_left,
                             'metric_right': metric_right}

        return split

    def _split_values(self, values: np.ndarray) -> List:
        unique_values = np.unique(values)
        if unique_values.shape[0] <= self.n_splits:
            split_values = unique_values.tolist()[:-1]
        else:
            percentiles = np.linspace(0, 100, self.n_splits + 1)
            split_values = np.unique(np.percentile(data, percentiles))

        return split_values

    def predict(self, x: np.ndarray):
        NotImplementedError()

    def _calculate_metric(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        NotImplementedError()

    def export_text(self, tree: int = None, column_names: List[str] = None, ndigits: int = 5):
        txt = ''
        if tree is None:
            for i, node in enumerate(self.forest):
                txt += 'Tree {}:\n'.format(i)
                txt += self._node_to_text(node=node, column_names=column_names, ndigits=ndigits)
                txt += '\n' + '\n'
        else:
            txt += 'Tree {}:\n'.format(tree)
            node = self.forest[tree]
            txt += self._node_to_text(node=node, column_names=column_names, ndigits=ndigits)

        return txt

    def _node_to_text(self, node: Node, column_names: List[str] = None, ndigits: int = 3):

        txt = ''.join(['|   ']*node.depth)
        txt += '|---'

        if node.model is None:
            if column_names is None:
                col = 'col_{}'.format(node.split_col_idx - 1)
            else:
                col = column_names[node.split_col_idx - 1]

            txt += ' '.join([col, '<', str(round(node.threshold, ndigits))])
            txt += '\n'

            txt += self._node_to_text(node=node.left_node, column_names=column_names, ndigits=ndigits)

            txt += ''.join(['|   '] * node.depth)
            txt += '|---'
            txt += ' '.join([col, '>=', str(round(node.threshold, ndigits))])
            txt += '\n'

            txt += self._node_to_text(node=node.right_node, column_names=column_names, ndigits=ndigits)

        else:
            intercept = node.model.coef_[0]
            weights = node.model.coef_[1:]
            weights = ['+' + str(round(w, ndigits)) if w > 0 else str(round(w, ndigits)) for w in weights]
            if column_names is None:
                cols = ['col_{}'.format(i) for i in range(len(weights))]
            else:
                cols = column_names

            weights_and_cols = ' '.join(['*'.join(p) for p in list(zip(weights, cols))])

            txt += ' '.join(['model: y =', str(round(intercept, ndigits)), weights_and_cols])

            txt += '\n'

        return txt

    def set_params(self, **parameters):
        for parameter, value in parameters.items():
            setattr(self, parameter, value)
        return self

    def _check_targets_classification(self, y: np.ndarray):
        self.classes_ = np.unique(y)
        assert issubclass(self.classes_.dtype.type, np.integer), 'Please convert targets to integer values'
