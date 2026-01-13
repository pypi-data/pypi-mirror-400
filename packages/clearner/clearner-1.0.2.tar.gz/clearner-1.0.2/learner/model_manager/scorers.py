# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module implements all scoring functions that are not readily available"""

import math
from sklearn.metrics import mean_squared_error
from scipy.stats import spearmanr


def root_mean_squared_error(*args, **kwargs):
    """Because root_mean_squared_error is not readily available but mean_squared_error is, we compute mean_squared_error
    and return the squared root to get root_mean_squared_error.

    :param args: the positional arguments, these are y_true and y_pred
    :param kwargs: the keywords arguments if there are any
    :return: the root mean squared error
    """
    return math.sqrt(mean_squared_error(args[0], args[1], **kwargs))


def spearman_r(*args, **kwargs):
    """Because scipy implementation of Spearman correlation coefficient returns both correlation coefficient and
    p-value, we need to re-implement it here to only return the correlation coefficient.

    :param args: the positional arguments, these are y_true and y_pred
    :param kwargs: the keywords arguments if there are any
    :return: the Spearman correlation coefficient
    """
    spearman_corr, _ = spearmanr(args[0], args[1], **kwargs)
    return spearman_corr
