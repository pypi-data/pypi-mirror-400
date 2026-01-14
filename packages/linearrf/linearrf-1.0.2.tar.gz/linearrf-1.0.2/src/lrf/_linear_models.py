import numpy as np

from lrf._bfgs import BFGS
from lrf._preprocessor import Preprocessor


class Regressor:
    def __init__(self, alpha: float = 2.0, preprocessing: str = None, fit_intercept: bool = True,
                 intercept_in_input: bool = False):
        """
        Linear least-squares with l2 regularization, also knows as Ridge Regression or Tikhonov regularization. This
        implementation supports several preprocessing methods, namely centering, normalizing and standardizing the
        data.

        Args:
            alpha : float, default=2.0
                Regularization strength, larger values imply stronger regularization.
                Must be a positive float. If alpha=0, there is no regularization and this implementation is equal to
                a linear regression using least-squares.

            preprocessing: str, default=None
                Specifies the method for data preprocessing. Can be either 'center', 'normalize', 'standardize' or
                None (default)

            fit_intercept: bool, default=True
                Whether to calculate the intercept.

            intercept_in_input: bool, default=False
                Whether there is an intercept column at index 0 in the data.
        """

        self.alpha = alpha
        self.preprocessing = preprocessing
        self.fit_intercept = fit_intercept
        self.intercept_in_input = intercept_in_input

        if self.preprocessing is not None:
            self.preprocessor = Preprocessor(method=self.preprocessing)
        
        self.coef_ = None

    def fit(self, x: np.ndarray, y: np.ndarray, initial_coefs: np.ndarray = None):
        """
        Fit linear regression model.

        Args:
            x: np.ndarray
                Training data, containing the feature values.

            y: np.ndarray
                Target values.

        Returns:
            self:
                Returns an instance of self.
        """

        assert self.alpha >= 0

        x = self._preprocessing(x, fit=True, intercept=self.intercept_in_input)

        if self.fit_intercept and not self.intercept_in_input:
            # insert a 1 as the intercept
            x = np.insert(x, 0, 1, axis=1)

        # ridge regression, by l2 regularization
        A = self.alpha * np.identity(x.shape[1])
        # we do not want to regularize the intercept
        A[0, 0] = 0

        # self.coef_ = np.dot(np.dot(np.linalg.pinv(np.dot(x.T, x) + A), x.T), y)
        self.coef_ = np.linalg.lstsq(np.dot(x.T, x) + A, np.dot(x.T, y), rcond=None)[0]

        return self

    def predict(self, x: np.ndarray):
        """
        Make a prediction using the linear regression model.

        Args:
            x: Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted values.
        """

        assert self.coef_ is not None, 'This linear model is not fitted yet. Call "fit" before using this model to ' \
                                       'make predictions'

        x = self._preprocessing(x, fit=False, intercept=self.intercept_in_input)

        if self.fit_intercept and not self.intercept_in_input:
            # insert a 1 as the intercept
            x = np.insert(x, 0, 1, axis=1)

        return np.dot(x, self.coef_)

    def _preprocessing(self, x: np.ndarray, fit: bool, intercept: bool):
        """
       Fit the preprocessor or transform the data according to a given method.

        Args:
            x: np.ndarray
                Samples to be processed or on which the processor should be fitted.

            fit: bool
                Whether to call the 'fit' method of the preprocessor or to call the 'transform' method.

            intercept: bool
                Whether there is an intercept column at index 0 of x.

        Returns:
            np.ndarray: Returns the data, which is transformed if fit=False.
        """

        if self.preprocessing is not None:
            if fit:
                self.preprocessor.fit(x)

            x = self.preprocessor.transform(x, intercept)

        return x


class Classifier:
    def __init__(self, n_iter: int = 100, tol: float = 10**(-6), C: float = 1,
                 preprocessing: str = None, fit_intercept: bool = True, intercept_in_input: bool = False):
        self.n_iter = n_iter
        self.tol = tol
        self.C = C
        self.preprocessing = preprocessing
        self.fit_intercept = fit_intercept
        self.intercept_in_input = intercept_in_input

        if self.preprocessing is not None:
            self.preprocessor = Preprocessor(method=self.preprocessing)

        self.coef_ = None

    def fit(self, x: np.ndarray, y: np.ndarray, initial_coefs: np.ndarray = None):
        """
        Fit linear classification model.

        Args:
            x: np.ndarray
                Training data, containing the feature values.

            y: np.ndarray
                Target classes.

        Returns:
            self:
                Returns an instance of self.
        """

        if np.unique(y).shape[0] > 2:
            raise ValueError('You can only use the internal linear classification model for binary classification.'
                             'For multi-class classification provide a suitable model to the "linear_model" parameter.')

        x = self._preprocessing(x, fit=True, intercept=self.intercept_in_input)

        if self.fit_intercept and not self.intercept_in_input:
            # insert a 1 as the intercept
            x = np.insert(x, 0, 1, axis=1)

        self._logistic_regression(x=x, y=y, initial_coefs=initial_coefs)

        return self

    def predict_proba(self, x: np.ndarray):
        """
        Make a prediction of the probability of each class using the linear classification model.

        Args:
            x: np.ndarray
                Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted probability of each class.
        """

        x = self._preprocessing(x, fit=False, intercept=self.intercept_in_input)

        if self.fit_intercept and not self.intercept_in_input:
            # insert a 1 as the intercept
            x = np.insert(x, 0, 1, axis=1)

        one_proba = self._sigmoid(np.dot(x, self.coef_))
        y_pred_proba = np.ones((x.shape[0], 2))

        y_pred_proba[:, 0] -= one_proba
        y_pred_proba[:, 1] = one_proba

        return y_pred_proba

    def predict(self, x: np.ndarray):
        """
        Predict the classes using the linear classification model.

        Args:
            x: np.ndarray
                Samples of the features to derive the prediction from.

        Returns:
            np.ndarray: Returns the predicted classes.
        """

        return np.argmax(self.predict_proba(x), axis=1)

    @staticmethod
    def _sigmoid(y: np.ndarray):
        """
        Sigmoid function to map input to values between 0 and 1 on the characteristic s-shaped curve (sigmoid curve).
        This is the probability for the positive class.

        Args:
            y: np.ndarray
                Input values, which will be mapped to values between 0 and 1.

        Returns:
            np.ndarray: Returns the probability for the positive class.
        """
        return np.exp(-np.logaddexp(0, -y))

    def _preprocessing(self, x: np.ndarray, fit: bool, intercept: bool):
        """
       Fit the preprocessor or transform the data according to a given method.

       Args:
           x: np.ndarray
               Samples to be processed or on which the processor should be fitted.

           fit: bool
               Whether to call the 'fit' method of the preprocessor or to call the 'transform' method.

       Returns:
           np.ndarray: Returns the data, which is transformed if fit=False.
       """

        if self.preprocessing is not None:
            if fit:
                self.preprocessor.fit(x)

            x = self.preprocessor.transform(x, intercept)

        return x

    def _logistic_regression(self, x: np.ndarray, y: np.ndarray, initial_coefs: np.ndarray):
        intercept = self.fit_intercept or self.intercept_in_input

        bfgs = BFGS(intercept=intercept)
        if initial_coefs is None:
            self.coef_ = bfgs.classification(x=x, y_true=y, coef_=np.zeros((x.shape[1], )), C=self.C)
        else:
            self.coef_ = bfgs.classification(x=x, y_true=y, coef_=initial_coefs, C=self.C)
