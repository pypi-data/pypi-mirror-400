# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""This module includes Learner dmls. The dmls inherit from the AbstractDML. The instance methods
could wrap the econml methods or any other packages. The call to Learner dmls are prefixed by learner_.
This reduces the possibility of shadowing function calls to the external packages. This module follows a similar
design to the classifiers, regressors, and other modules under model_manager package.
"""


import abc
import sys
import warnings
import logging

from econml.dml import LinearDML, DML, NonParamDML
from econml.inference import BootstrapInference
from sklearn.linear_model import RidgeCV, LassoCV
from sklearn.linear_model import SGDRegressor, HuberRegressor, LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.ensemble import ExtraTreesRegressor, BaggingRegressor
from sklearn.tree import DecisionTreeRegressor, ExtraTreeRegressor
from sklearn.neighbors import KNeighborsRegressor, RadiusNeighborsRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.svm import SVR
from sklearn.gaussian_process import GaussianProcessRegressor
from catboost import CatBoostRegressor


class AbstractDML:

    __metaclass__ = abc.ABCMeta

    def __init__(self):  # pragma: no cover
        self.mdl = None

    @staticmethod
    def learner_fit(X, y, t, models_dict, bootstrap_inference_params, **kwargs):  # pragma: no cover
        pass

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):  # pragma: no cover
        pass


class DMLHandler(AbstractDML):

    @abc.abstractmethod
    def __init__(self):
        super(AbstractDML, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, t, models_dict, bootstrap_inference_params, **kwargs):
        try:
            return getattr(sys.modules[__name__], models_dict["dml"]["type"]).learner_fit(X, y, t, models_dict, bootstrap_inference_params, **kwargs)
        except AttributeError:
            return StandardDMLs.learner_fit(X, y, t, models_dict, bootstrap_inference_params, **kwargs)

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        try:
            return getattr(sys.modules[__name__], mdl["type"]).learner_predict(X, mdl, carry_data, full_data, cols_to_carry)
        except AttributeError:
            return StandardDMLs.learner_predict(X, mdl, carry_data, full_data, cols_to_carry)


class StandardDMLs(AbstractDML):

    def __init__(self):
        super(AbstractDML, self).__init__()  # pragma: no cover

    @staticmethod
    def learner_fit(X, y, t, models_dict, bootstrap_inference_params, **kwargs):
        """Train a dml using the features (X) and the model_y target, and model_t target. Instantiation of the dml
        object (econml's dml) occurs here. The function return the trainer dml object

        :param X: the features for training
        :param y: the model_y target column
        :param t: the model_t target column
        :param models_dict: the full models_dict dictionary
        :param bootstrap_inference_params: the bootstrap inference params
        :param kwargs: other possible keyword arguments
        :return: the trained DML model object
        """
        bootstrap_inference = BootstrapInference(**bootstrap_inference_params)
        logging.info("Fitting a %s model...", models_dict["dml"]["type"])
        if "model_final" in models_dict["dml"]:
            model = getattr(sys.modules[__name__], models_dict["dml"]["type"])(model_y=models_dict["model_y"]["model"],
                                                                               model_t=models_dict["model_t"]["model"],
                                                                               model_final=getattr(sys.modules[__name__], models_dict["dml"]["model_final"]["type"])(**models_dict["dml"]["model_final"]["params"]),
                                                                               **models_dict["dml"]["params"])
        else:
            model = getattr(sys.modules[__name__], models_dict["dml"]["type"])(model_y=models_dict["model_y"]["model"],
                                                                               model_t=models_dict["model_t"]["model"],
                                                                               **models_dict["dml"]["params"])

        model.fit(y, t, X=X, inference=bootstrap_inference)
        logging.info(f"The score on training data is: {model.score(y, t, X=X)}")
        # if the log level is debug, we log all the attributes
        logging.debug(vars(model))
        return model

    @staticmethod
    def learner_predict(X, mdl, carry_data=True, full_data=None, cols_to_carry=None):
        """Make predictions using the trained model. In some situations, learner needs to save the predictions according to
        some identifiers (e.g. id_columns). In those situations, the functions also returns the data that the user has
        requested. This method is similar to other methods in classifiers, regressors, and other modules. It just calls
        the relevant methods for making predictions such as effect instead of predict.

        :param X: the features to use for making predictions (obviously this should match with the features used for training)
        :param mdl: an item in the Learner models_dict
        :param carry_data: a flag to identify if the some selected data must be returned.
        :param full_data: the data set that contains the full data set. The selection is performed on this data set.
        :param cols_to_carry: the cols to select from the full data and return (this is usually the id_cols)
        :return: The prediction or the prediction along the selected columns

        Note: The reason for passing the full data is that the feature matrix usually does not contain id information.
        """
        logging.info("Making predictions using the %s model...", mdl["type"])
        logging.info(f"Average treatment effect is {mdl['model'].ate(X)}")
        logging.info(f"Average treatment interval is {mdl['model'].ate_interval(X)}")
        if carry_data:
            if full_data is None:
                warnings.warn("carry_data was set true but no data was passed, will not return any data...", Warning)
            if cols_to_carry is None:
                warnings.warn("carry_data was set true but no cols_to_carry was passed, will not return any data...", Warning)
            if full_data is not None and cols_to_carry:
                effect = mdl["model"].effect(X)
                lower, upper = mdl["model"].effect_interval(X)
                return effect, lower, upper, full_data[cols_to_carry]
        effect = mdl["model"].effect(X)
        lower, upper = mdl["model"].effect_interval(X)
        return effect, lower, upper, None
