# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential
import sys
import logging

from learner.data_worker.data_loader import get_value

class DMLConfiguration:
    """Parse all input variables specific to the dml engine.
    """

    def __init__(self, json_config, engine):
        self._json_config = json_config
        self._engine = engine
        self.discrete_treatment = self.get_discrete_treatment()
        self.bootstrap_inference_params = self.get_bootstrap_inference_params()
        self.standard_scaler_activate = get_value(self._json_config, True, "dml", "standard_scaler_params", "activate")
        self.pca_activate = get_value(self._json_config, True, "dml", "pca_params", "activate")
        self.pca_n_components = get_value(self._json_config, 50, "dml", "pca_params", "n_components")

    def get_discrete_treatment(self):
        try:
            models_dict_value = self._json_config["model"]["models_dict"]["dml"]["params"]["discrete_treatment"]
        except KeyError:
            models_dict_value = False

        try:
            value = self._json_config["dml"]["discrete_treatment"]
        except KeyError:
            value = False

        if self._engine == "DML" and value != models_dict_value:
            logging.critical("The value of discrete_treatment in the dml section and models_dict section are "
                             "not consistent. It's best to explicitly set both of them. Please update your "
                             "configuration file and try again. Exiting...")
            sys.exit(1)
        return value

    def get_bootstrap_inference_params(self):
        try:
            return self._json_config["dml"]["bootstrap_inference_params"]
        except KeyError:
            return {"n_bootstrap_samples": 50, "n_jobs": -1}
