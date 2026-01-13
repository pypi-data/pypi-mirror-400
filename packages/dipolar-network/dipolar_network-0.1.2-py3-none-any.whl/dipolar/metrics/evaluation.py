import numpy as np


def evaluate_accuracy(model, X, y):
    """
    Computes simple classification accuracy.

    Parameters
    ----------
    model : DipolarNetwork
        Any classifier implementing .predict(X)

    X : ndarray of shape (n_samples, n_features)
        Input samples.

    y : ndarray of shape (n_samples,)
        Ground truth class labels.

    Returns
    -------
    float
        Fraction of correctly classified samples.
    """
    preds = model.predict(X)
    return np.mean(preds == y)


def confusion_matrix(model, X, y):
    """
    Computes 2-class confusion matrix (0/1).
    Returns array: [[TN, FP],
                    [FN, TP]]
    """
    preds = model.predict(X)

    tn = np.sum((preds == 0) & (y == 0))
    fp = np.sum((preds == 1) & (y == 0))
    fn = np.sum((preds == 0) & (y == 1))
    tp = np.sum((preds == 1) & (y == 1))

    return np.array([[tn, fp],
                     [fn, tp]])
