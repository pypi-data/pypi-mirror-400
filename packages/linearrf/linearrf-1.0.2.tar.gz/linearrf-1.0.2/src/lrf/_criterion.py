import numpy as np


def mse(y_true: np.ndarray, y_pred: np.ndarray):
    return ((y_true - y_pred)**2).mean()


def rmse(y_true: np.ndarray, y_pred: np.ndarray):
    return np.sqrt(((y_true - y_pred)**2).mean())


def mae(y_true: np.ndarray, y_pred: np.ndarray):
    return (np.abs(y_true - y_pred)).mean()


def mape(y_true: np.ndarray, y_pred: np.ndarray):
    return np.abs((y_true - y_pred)/y_true).mean()


def neg_explained_variance(y_true: np.ndarray, y_pred: np.ndarray):
    return np.var(y_true - y_pred)/np.var(y_true) - 1


def neg_r2(y_true: np.ndarray, y_pred: np.ndarray):
    return -np.einsum('i->', (y_true - y_pred)**2)/np.einsum('i->', (y_true - y_true.mean())**2)


def wape(y_true: np.ndarray, y_pred: np.ndarray):
    return np.einsum('i->', np.abs(y_true - y_pred))/np.einsum('i->', np.abs(y_true))


def _confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, thresh: float = 0.5):
    mask_ones = y_pred >= thresh

    tmp = y_true[mask_ones] == 1
    tp = np.count_nonzero(tmp)
    fp = tmp.shape[0] - tp

    tmp = y_true[~mask_ones] == 1
    fn = np.count_nonzero(tmp)
    tn = tmp.shape[0] - fn

    return tn, fp, fn, tp


def _thresholds(y_pred: np.ndarray):
    if y_pred.shape[0] < 10_000:
        thresholds = np.unique(y_pred).tolist()
    else:
        step = 1 / 6180
        thresholds = np.arange(max(np.min(y_pred) - 2 * step, 0), min(np.max(y_pred) + 2 * step, 1), step).tolist()

    if np.min(y_pred) > 0:
        thresholds = [0] + thresholds

    if np.max(y_pred) < 1:
        thresholds = thresholds + [1]

    return thresholds


def hamming(y_true: np.ndarray, y_pred: np.ndarray):
    return (y_true != y_pred).mean()


def cross_entropy(y_true: np.ndarray, y_pred: np.ndarray, penalty: float = 0):
    if y_true.ndim == 1:
        y_true = y_true[:, np.newaxis]

    y_pred = np.clip(y_pred, 1e-12, 1 - 1e-12)
    return -(y_true*np.log(y_pred)+(1-y_true)*np.log(1-y_pred)).sum()/y_pred.shape[0] + penalty


def neg_mcc(y_true: np.ndarray, y_pred: np.ndarray):
    samples = y_true.shape[0]
    tn, fp, fn, tp = _confusion_matrix(y_true=y_true, y_pred=y_pred, thresh=0.5)
    cm = np.array([[tn, fp], [fn, tp]]).reshape(2, 2)

    c = np.einsum('ii', cm)
    t = np.einsum('ij->j', cm)
    p = np.einsum('ij->i', cm)

    dividend = (c*samples - t @ p)
    divisor = (np.sqrt(samples**2 - p @ p) * np.sqrt(samples**2 - t @ t))

    if divisor == 0:
        mcc = 0.0
    else:
        mcc = dividend / divisor

    return -mcc


def neg_roc_auc(y_true: np.ndarray, y_pred: np.ndarray):
    thresholds = _thresholds(y_pred=y_pred)

    positives = y_true.sum()
    negatives = y_true.shape[0] - positives

    fpr, tpr = [], []

    for thresh in thresholds:
        _, fp, _, tp = _confusion_matrix(y_true=y_true, y_pred=y_pred, thresh=thresh)

        tpr.append(tp / positives)
        fpr.append(fp / negatives)

    # integration is from right to left, therefore this is already the negative ROC AUC
    neg_auc = np.trapz(tpr, fpr)

    return neg_auc


def neg_pr_auc(y_true: np.ndarray, y_pred: np.ndarray):
    thresholds = _thresholds(y_pred=y_pred)

    precision, recall = [], []

    for thresh in thresholds:
        _, fp, fn, tp = _confusion_matrix(y_true=y_true, y_pred=y_pred, thresh=thresh)

        p = tp / (tp + fp) if (tp + fp) > 0 else 0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0

        precision.append(p)
        recall.append(r)

    # integration is from right to left, therefore this is already the negative PR AUC
    neg_auc = np.trapz(precision, recall)

    return neg_auc


def neg_auk(y_true: np.ndarray, y_pred: np.ndarray):
    NotImplementedError()


def neg_g_mean(y_true: np.ndarray, y_pred: np.ndarray):
    tn, fp, fn, tp = _confusion_matrix(y_true=y_true, y_pred=y_pred)

    return -(tp * tn / ((tp + fn) * (tn + fp)))


def neg_f1(y_true: np.ndarray, y_pred: np.ndarray):
    _, fp, fn, tp = _confusion_matrix(y_true=y_true, y_pred=y_pred)

    return -(tp/(tp + 0.5*(fp + fn)))
