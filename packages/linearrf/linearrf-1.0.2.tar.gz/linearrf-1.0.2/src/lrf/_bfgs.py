import numpy as np

from lrf._criterion import cross_entropy


class BFGS:
    def __init__(self, n_iter: int = 100, tol: float = 10**(-4), intercept: bool = True):
        self.n_iter = n_iter
        self.tol = tol
        self.intercept = intercept

    def classification(self, x: np.ndarray, y_true: np.ndarray, coef_: np.ndarray, C: float = 1.0):
        y_true = y_true[:, np.newaxis]

        coef_ = coef_[:, np.newaxis]
        new_grad = self._grad_cross_entropy_logistic(y_true=y_true, x=x, coef_=coef_, C=C,
                                                     y_pred=self._sigmoid(x@coef_))

        H_inv = np.eye(coef_.shape[0]) / 0.2

        alpha = 1
        for _ in range(self.n_iter):

            grad = new_grad

            direction = -H_inv @ grad

            alpha, new_grad = self._line_search(x=x, y=y_true, coef_=coef_, direction=direction,
                                                grad=grad, C=C, alpha=alpha)

            if alpha is None:
                break

            s = alpha * direction

            change_mask = coef_ != 0
            change = np.abs(s[change_mask] / coef_[change_mask]) if np.count_nonzero(change_mask) > 0 else 1

            coef_ += s

            if (np.max(change) <= self.tol) or np.all(new_grad == 0):
                break
            else:
                grad_diff = new_grad - grad

                st_grad_diff = s.T @ grad_diff

                A = ((st_grad_diff + grad_diff.T @ H_inv @ grad_diff) * (s @ s.T)) / (st_grad_diff**2)

                B = (H_inv @ grad_diff @ s.T + s @ grad_diff.T @ H_inv) / st_grad_diff

                H_inv += A - B

        return coef_.flatten()

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

    def _grad_cross_entropy_logistic(self, y_true: np.ndarray, x: np.ndarray, y_pred: np.ndarray,
                                     coef_: np.ndarray, C: float):

        weights = coef_.copy()
        if self.intercept:
            weights[0] = 0

        norm = np.linalg.norm(weights)
        if norm != 0.0:
            penalty = np.einsum('ij->', weights) / (C * norm)
        else:
            penalty = 0

        grad = x.T @ (y_pred - y_true) + penalty
        norm = np.linalg.norm(grad)
        if norm == 0:
            grad = np.zeros(grad.shape)
        else:
            grad /= norm
        return grad

    def _armijo(self, y: np.ndarray, y_pred: np.ndarray, coef_: np.ndarray, alpha: float, C: float,
                c1: float, grad_dir: float, cross_entropy_value: float):

        penalty = self.get_penalty(coef=coef_, C=C)

        left_armijo = cross_entropy(y_true=y, y_pred=y_pred, penalty=penalty)
        right_armijo = cross_entropy_value + c1 * alpha * grad_dir

        armijo = left_armijo <= right_armijo

        return armijo

    def _wolfe(self, x: np.ndarray, y: np.ndarray, coef_: np.ndarray, alpha: float, C: float,
               direction: np.ndarray, c1: float, c2: float, grad_dir: float, cross_entropy_value: float,
               x_coef: np.ndarray, x_direction: np.ndarray):

        y_pred = self._sigmoid(x_coef + alpha*x_direction)

        armijo = self._armijo(y=y, coef_=coef_, alpha=alpha, c1=c1, grad_dir=grad_dir,
                              cross_entropy_value=cross_entropy_value, C=C, y_pred=y_pred)

        if armijo:
            grad = self._grad_cross_entropy_logistic(y_true=y, x=x, coef_=coef_ + alpha * direction, C=C, y_pred=y_pred)
            left_curvature = (direction.T @ grad).item()
            right_curvature = c2 * grad_dir

            # since wolfe conditions are armijo and weak/strong curvature, the curvature directly implies weak or
            # strong wolfe since armijo is given to be True at this point
            weak_wolfe = left_curvature >= right_curvature
            strong_wolfe = np.abs(left_curvature) <= np.abs(right_curvature)
        else:
            weak_wolfe, strong_wolfe = False, False
            grad = None

        return weak_wolfe, strong_wolfe, grad

    def _line_search(self, x: np.ndarray, y: np.ndarray, coef_: np.ndarray,
                     direction: np.ndarray, grad: np.ndarray, C: float,
                     c1: float = 10 ** (-4), c2: float = 0.9,
                     alpha_upper: float = 2.0, alpha_lower: float = 10**-10, alpha: float = 1.0,
                     n_iter: int = 10):

        grad_dir = (direction.T @ grad).item()
        x_coef = x @ coef_
        x_direction = x @ direction

        penalty = self.get_penalty(coef=coef_, C=C)

        cross_entropy_value = cross_entropy(y_true=y, y_pred=self._sigmoid(x_coef), penalty=penalty)

        weak_wolfe_value, grad_value = 0, 0
        for _ in range(n_iter):
            weak_wolfe, strong_wolfe, grad = self._wolfe(x=x, y=y, coef_=coef_, alpha=alpha, direction=direction, c1=c1,
                                                         c2=c2, grad_dir=grad_dir,
                                                         cross_entropy_value=cross_entropy_value,
                                                         C=C, x_coef=x_coef, x_direction=x_direction)

            if strong_wolfe:
                break
            else:
                if weak_wolfe and alpha > weak_wolfe_value:
                    weak_wolfe_value = alpha
                    grad_value = grad

                    alpha_lower = alpha
                else:
                    alpha_upper = alpha

                alpha = (alpha_lower + alpha_upper) / 2
        else:
            if weak_wolfe_value != 0:
                alpha = weak_wolfe_value
                grad = grad_value
            else:
                alpha, grad = None, None

        return alpha, grad

    def get_penalty(self, coef: np.ndarray, C: float):
        if self.intercept:
            penalty = np.linalg.norm(coef[1:]) / C
        else:
            penalty = np.linalg.norm(coef) / C

        return penalty
