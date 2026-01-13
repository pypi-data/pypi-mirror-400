# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import sys
import os
import warnings
import logging

import torch

from learner.data_worker.data_loader import get_value
from learner.configuration.supported_items import SUPPORTED_MODELS, SUPPORTED_INPUT_TYPES, SUPPORTED_ENGINES_FOR_LEARNING_RATE_PARAMS


class ModelsConfiguration:
    """Parse all input variables related to the model section. The type of each model and the
    hyperprameters are defined here."""

    def __init__(self, json_config, sep_timetag, output, data, engine, segmenter, dml):
        self._json_config = json_config
        self.sep_timetag = sep_timetag
        self._output = output
        self._data = data
        self._engine = engine
        self._segmenter = segmenter
        self._dml = dml
        self.device = self.get_device()
        self.num_models = get_value(self._json_config, 1, "model", "num_models")
        self.train_models = self.get_train_models()

        self.cv_activate = self.get_cv_activate()
        self.cv_kfold_params = self.get_cv_kfold_params()
        self.cv_options = self.get_cv_options()

        self.calibration_activate = self.get_calibration_activate()
        self.calibration_cv_params = self.get_calibration_cv_params()

        self.gs_activate = self.get_gs_activate()
        self.gs_kfold_params = self.get_gs_kfold_params()
        self.gs_options = get_value(self._json_config, {}, "model", "grid_search_params", "options")

        self.lr_activate = self.get_lr_activate()
        self.lr_start_lr = get_value(self._json_config, 1e-7, "model", "learning_rate_params", "start_lr")
        self.lr_end_lr = get_value(self._json_config, 10, "model", "learning_rate_params", "end_lr")
        self.lr_num_it = get_value(self._json_config, 100, "model", "learning_rate_params", "num_it")
        self.lr_stop_div = get_value(self._json_config, True, "model", "learning_rate_params", "stop_div")

        self.save_models = self.get_save_models()
        self.models_dict = self.get_models_dict()
        # set nrows_score to None. As soon as the engine gets instantiated, the value will be set to 0
        # I don't set it here to avoid confusions
        self.nrows_score = None

        self.version_activate = get_value(self._json_config, False, "model", "version_params", "activate")
        self.version_column_name = get_value(self._json_config, "version", "model", "version_params", "column_name")
        self.version_version_name = self.get_version_version_name()

    def get_device(self):
        try:
            device = self._json_config["model"]["device"]
            if device == "cuda" and not torch.cuda.is_available():
                warnings.warn("device was set to cuda but it looks like no gpu is available. Setting the device to "
                              "cpu", UserWarning)
                return "cpu"
            return device
        except KeyError:
            if torch.cuda.is_available():
                return 'cuda'
            return 'cpu'

    def get_train_models(self):
        try:
            train_models = self._json_config["model"]["train_models"]
            if train_models:
                if self._data.train_location:
                    if ("folder" in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.exists(self._data.train_location)) or\
                       ("folder" not in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.isfile(self._data.train_location)):
                        logging.error("train_models was set to true, but the location value is not valid. "
                                      "Exiting...")
                        sys.exit(1)
                elif not self._data.train_query_activate and "query" in SUPPORTED_INPUT_TYPES[self._engine]:
                    logging.error("train_models was set to true. However, no location or query was provided. Exiting...")
                    sys.exit(1)
            return train_models
        except KeyError:
            if self._data.train_location:
                if ("folder" in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.exists(self._data.train_location)) or\
                   ("folder" not in SUPPORTED_INPUT_TYPES[self._engine] and not os.path.isfile(self._data.train_location)):
                    logging.error("train_models defaults to true, but the location value is not valid.")
                    sys.exit(1)
            elif not self._data.train_query_activate and "query" in SUPPORTED_INPUT_TYPES[self._engine]:
                logging.error("train_models defaults to true, but neither location nor query were provided. Exiting...")
                sys.exit(1)
            return True

    def get_cv_activate(self):
        try:
            return self._json_config["model"]["cross_val_params"]["activate"]
        except KeyError:
            logging.info("Not using cross_validation...")
            return False

    def get_cv_kfold_params(self):
        try:
            return self._json_config["model"]["cross_val_params"]["kfold_params"]
        except KeyError:
            if self.cv_activate:
                warnings.warn("Cross validation was requested but k was not set, using default values: "
                              "{\"n_splits\": 3, \"shuffle\": false, \"random_state\": 42}", UserWarning)
            return {"n_splits": 3, "shuffle": False, "random_state": 42}

    def get_cv_options(self):
        # TODO: see if we should do something here depending on the input
        try:
            return self._json_config["model"]["cross_val_params"]["options"]
        except KeyError:
            return {}

    def get_calibration_activate(self):
        try:
            activate = self._json_config["model"]["calibration_params"]["activate"]
            if activate and self._engine != "Classifier":
                logging.critical("Calibration is only supported for the Classifier engine. Please update the "
                                 "configuration file and try again. Exiting...")
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_calibration_cv_params(self):
        try:
            return self._json_config["model"]["calibration_params"]["cv_params"]
        except KeyError:
            if self.calibration_activate:
                warnings.warn("Calibration was requested but cv params was not set, using default values: "
                              "{\"method\": \"sigmoid\", \"cv\": 5, \"n_jobs\": 1, \"ensemble\": true}", UserWarning)
                return {"method": "sigmoid", "cv": 5, "ensemble": True, "n_jobs": 1}
            return {}

    def get_gs_kfold_params(self):
        try:
            return self._json_config["model"]["grid_search_params"]["kfold_params"]
        except KeyError:
            if self.cv_activate:
                warnings.warn("Grid Search was requested but kfold_params was not set, using default values: "
                              "{\"n_splits\": 3, \"shuffle\": false, \"random_state\": 42}", UserWarning)
            return {"n_splits": 3, "shuffle": False, "random_state": 42}

    def get_lr_activate(self):
        try:
            activate = self._json_config["model"]["learning_rate_params"]["activate"]
            if activate and not self.train_models:
                logging.critical("learning_rate_params was activated but train_models was set to false. This feature "
                                 "is only valid when training the models. Please update the configuration file and "
                                 "try again. Exiting...")
                sys.exit(1)
            if activate and self._engine not in SUPPORTED_ENGINES_FOR_LEARNING_RATE_PARAMS:
                logging.critical("learning_rate_params was activated but it is not supported for the {engine} engine. "
                                 "The supported engines are {supported_engines}. Please update your configuration "
                                 "file. Exiting...".format(engine=self._engine,
                                                           supported_engines=SUPPORTED_ENGINES_FOR_LEARNING_RATE_PARAMS))
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_save_models(self):
        try:
            return self._json_config["model"]["save_models"]
        except KeyError:
            logging.info("Not saving any models")
            return False

    def get_gs_activate(self):
        try:
            activate = self._json_config["model"]["grid_search_params"]["activate"]
            if self.cv_activate and activate:
                logging.error("Both do_cross_val and do_grid_search are set to true. Please set one of them to "
                              "false. Exiting..")
                sys.exit(1)
            return activate
        except KeyError:
            return False

    def get_models_dict(self):
        # if we are not training the models, we don't care about models_dict
        if not self.train_models:
            return {}

        def validate_mdl(mdl, engine, display_engine=None):
            if display_engine is None:
                display_engine = engine
            try:
                if mdl["type"] not in SUPPORTED_MODELS[engine]:
                    logging.error("The model %s is not supported for %s engine. The supported models, "
                                  "in alphabetical order, are %s, Exiting...",
                                  mdl["type"], display_engine, sorted(SUPPORTED_MODELS[engine]))
                    sys.exit(1)
            except KeyError:
                if mdl["type"] not in SUPPORTED_MODELS["Classifier"]:
                    logging.error("The model %s is not supported. The supported models, "
                                  "in alphabetical order, are %s, Exiting...",
                                  mdl["type"], sorted(SUPPORTED_MODELS.values()))
                    sys.exit(1)

            if mdl["type"].startswith("Calibrated") and self.calibration_activate is False:
                logging.critical("A calibrated classifier was requested but calibration_params was not activated. "
                                 "Please updated the configuration file and try again. Exiting...")
                sys.exit(1)

            mdl["path"] = directory_path

        try:
            models_dict = self._json_config["model"]["models_dict"]
            self.validate_dml(models_dict)
            if self.num_models != len(models_dict):
                logging.error("Expected %i models but got %i. Exiting...", self.num_models, len(models_dict))
                sys.exit(1)
            for tag, mdls in models_dict.items():
                directory_path = self._output.path + self._output.name + "_" + tag + str(self.sep_timetag) + "/"
                # if a dictionary is passed, no need to loop
                if isinstance(mdls, dict):
                    if self._engine == "DML":
                        if tag == "model_y":
                            validate_mdl(mdls, "Regressor")
                        elif tag == "model_t":
                            if self._dml.discrete_treatment is False:
                                validate_mdl(mdls, "Regressor")
                            else:
                                validate_mdl(mdls, "Classifier")
                        else:
                            validate_mdl(mdls, "DML", "DML")
                    else:
                        validate_mdl(mdls, self._engine)
                # loop through each item to validate
                elif isinstance(mdls, list):
                    if not self._segmenter.activate:
                        logging.critical(f"""
                            Segmenter was not activated but the parameters for {tag} was provided in a list format.
                            Please turn on segmener or provide a dictionary. Exiting...
                        """)
                        sys.exit(1)

                    for mdl in mdls:
                        validate_mdl(mdl, self._engine)

                if not os.path.exists(directory_path) and self.train_models:  # pragma: no cover
                    os.makedirs(directory_path)
            return models_dict
        except KeyError:
            if self.train_models:
                logging.error("models_dict must be defined with train_models set to true...")
                sys.exit(1)
            return {}

    def validate_dml(self, models_dict):
        if self._engine != "DML":
            return
        if self._engine == "DML" and self.num_models != 3:
            logging.critical("When using the DML engine, num_models should be 3, and two items must be "
                             "defined in the models_dict field. Please update your configuration file and try "
                             "again. Exiting...")
            sys.exit(1)

        valid_keys = ["dml", "model_t", "model_y"]
        provided_key = sorted(list(models_dict.keys()))
        if provided_key != valid_keys:
            logging.critical(f"When using the DML engine, the keys in the models_dict field must be {valid_keys}. "
                             f"However, we got {provided_key}. Please update your configuration file and try again. "
                             f"Exiting...")
            sys.exit(1)

    def get_version_version_name(self):
        if self.version_activate:
            try:
                version_name = self._json_config["model"]["version_params"]["version_name"]
                return version_name
            except KeyError:
                logging.critical('version_params in the model section was activated but no value for "version_name" '
                                 'was provided. Please update your configuration file and try again. Exiting...')
                sys.exit(1)
