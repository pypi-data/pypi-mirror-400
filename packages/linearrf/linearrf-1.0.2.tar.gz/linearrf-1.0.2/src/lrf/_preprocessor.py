import numpy as np


class Preprocessor:
    def __init__(self, method: str):
        """
        Preprocessor for data transformation by a given method.

        Args:
            method: str
                Specifies the transformation method, which could be 'center', 'normalize' or 'standardize'.
        """

        assert method in ['center', 'normalize', 'standardize'],\
            'The scaling method should be "center", "normalize" or "standardize".'

        self.method = method

        self.mean = None
        self.min = None
        self.max = None
        self.std = None

    def fit(self, x: np.ndarray):
        """
        Compute the values which are needed for the given preprocessing method.

        Args:
            x: np.ndarray
                The data used to compute the values which are needed for the given preprocessing method.

        Returns:
            self: Returns an instance of self.
        """

        if self.method == 'center':
            self.mean = x.mean(axis=0)
        elif self.method == 'normalize':
            self.min = x.min(axis=0)
            self.max = x.max(axis=0)

            # if the difference between min and max is 0, this would raise an error. In this case, do not preprocess
            # the data.
            diff = self.max - self.min
            diff_zero = diff == 0
            self.min[diff_zero] = 0
            self.max[diff_zero] = 1
        elif self.method == 'standardize':
            self.mean = x.mean(axis=0)
            self.std = x.std(axis=0)

            # if the standard deviation is 0, this would raise an error. In this case, do not preprocess the data.
            zero_std = self.std == 0
            self.mean[zero_std] = 0
            self.std[zero_std] = 1

        return self

    def transform(self, x: np.ndarray, intercept: bool):
        """
        Transform the data according to the given method.

        Args:
            x: np.ndarray
                The data which will be transformed.

            intercept: bool
                Whether there is an intercept column at index 0 of x.

        Returns:
            np.ndarray: Returns the transformed data.
        """
        if self.method == 'center':
            return self._center(x, intercept)
        elif self.method == 'normalize':
            return self._normalize(x, intercept)
        elif self.method == 'standardize':
            return self._standardize(x, intercept)

    def _center(self, x: np.ndarray, intercept: bool):
        """
        Center the data.

        Args:
            x: np.ndarray
                The data which will be centered.

            intercept: bool
                Whether there is an intercept column at index 0 of x.

        Returns:
            np.ndarray: Returns the centered data.
        """
        x -= self.mean

        if intercept:
            if x.ndim == 2:
                x[:, 0] = 1
            else:
                x[0] = 1

        return x

    def _normalize(self, x: np.ndarray, intercept: bool):
        """
        Normalize the data.

        Args:
            x: np.ndarray
                The data which will be normalized.

            intercept: bool
                Whether there is an intercept column at index 0 of x.

        Returns:
            np.ndarray: Returns the normalized data.
        """

        x = (x - self.min)/(self.max - self.min)

        if intercept:
            if x.ndim == 2:
                x[:, 0] = 1
            else:
                x[0] = 1

        return x

    def _standardize(self, x: np.ndarray, intercept: bool):
        """
        Standardize the data.

        Args:
            x: np.ndarray
                The data which will be standardized.

            intercept: bool
                Whether there is an intercept column at index 0 of x.

        Returns:
            np.ndarray: Returns the standardized data.
        """

        x = (x - self.mean) / self.std

        if intercept:
            if x.ndim == 2:
                x[:, 0] = 1
            else:
                x[0] = 1

        return x
