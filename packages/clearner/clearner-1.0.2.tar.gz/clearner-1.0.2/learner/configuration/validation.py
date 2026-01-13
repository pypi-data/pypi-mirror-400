# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential
import sys

import warnings
import logging

from learner.data_worker.data_loader import get_value
from learner.configuration.supported_items import SUPPORTED_VALIDATION_BEHAVIOR
from learner.validator.input_validator import validate_subset_list, validate_in_range


class ValidationConfiguration:

    def __init__(self, json_config):
        self._json_config = json_config

        self.dtypes_against_metadata_activate = get_value(self._json_config, True, "validation", "dtypes_against_metadata_params", "activate")
        self.dtypes_against_metadata_behavior = self.get_dtypes_against_metadata_behavior()
        self.nulls_in_target_activate = get_value(self._json_config, True, "validation", "nulls_in_target_params", "activate")
        self.nulls_in_target_behavior = self.get_nulls_in_target_behavior()
        self.to_numeric_activate = get_value(self._json_config, True, "validation", "to_numeric_params", "activate")
        self.to_numeric_behavior = self.get_to_numeric_behavior()
        self.nulls_portion_all_cols_activate = get_value(self._json_config, False, "validation", "nulls_portion_params", "all_cols_params", "activate")
        self.nulls_portion_all_cols_min_sample = get_value(self._json_config, 200000, "validation", "nulls_portion_params", "all_cols_params", "min_sample")
        self.nulls_portion_all_cols_threshold = self.get_nulls_portion_all_cols_threshold()
        self.nulls_portion_all_cols_behavior = self.get_nulls_portion_all_cols_behavior()
        # the get_nulls_portion_specific_cols_params method populates this
        self.nulls_portion_specific_cols = []
        self.nulls_portion_specific_cols_params = self.get_nulls_portion_specific_cols_params()

        self.psi_all_cols_activate = get_value(self._json_config, False, "validation", "psi_params", "all_cols_params", "activate")
        self.psi_all_cols_min_sample = get_value(self._json_config, 200000, "validation", "psi_params", "all_cols_params", "min_sample")
        self.psi_all_cols_buckets = self.get_psi_all_cols_buckets()
        self.psi_all_cols_threshold = self.get_psi_all_cols_threshold()
        self.psi_all_cols_behavior = self.get_psi_all_cols_behavior()
        # the get_psi_specific_cols_params method populates this
        self.psi_specific_cols = []
        self.psi_specific_cols_params = self.get_psi_specific_cols_params()

    def get_validate(self):
        try:
            validate = self._json_config["validation"]["validate"]
            if not validate:
                warnings.warn("Validation flag is set to false, this can lead to errors or unexpected results",
                              UserWarning)
            return validate
        except KeyError:
            return True

    def get_dtypes_against_metadata_behavior(self):
        try:
            behavior = self._json_config["validation"]["dtypes_against_metadata_params"]["behavior"]
            validate_subset_list(parent_list=SUPPORTED_VALIDATION_BEHAVIOR,
                                 parent_name="supported validation behavior",
                                 subset_list=[behavior],
                                 subset_name="defined behavior in dtypes_against_metadata_params")
            return behavior
        except KeyError:
            return "error"

    def get_nulls_in_target_behavior(self):
        try:
            behavior = self._json_config["validation"]["nulls_in_target_params"]["behavior"]
            validate_subset_list(parent_list=SUPPORTED_VALIDATION_BEHAVIOR,
                                 parent_name="supported validation behavior",
                                 subset_list=[behavior],
                                 subset_name="defined behavior in nulls_in_target_params")
            return behavior
        except KeyError:
            return "error"

    def get_to_numeric_behavior(self):
        try:
            behavior = self._json_config["validation"]["to_numeric_params"]["behavior"]
            validate_subset_list(parent_list=SUPPORTED_VALIDATION_BEHAVIOR,
                                 parent_name="supported validation behavior",
                                 subset_list=[behavior],
                                 subset_name="defined behavior in to_numeric_params")
            return behavior
        except KeyError:
            return "error"

    def get_nulls_portion_all_cols_threshold(self):
        try:
            threshold = self._json_config["validation"]["nulls_portion_params"]["all_cols_params"]["threshold"]
            validate_in_range(threshold, minimum=0, maximum=1)
            return threshold
        except KeyError:
            return 0.9

    def get_nulls_portion_all_cols_behavior(self):
        try:
            behavior = self._json_config["validation"]["nulls_portion_params"]["all_cols_params"]["behavior"]
            validate_subset_list(parent_list=SUPPORTED_VALIDATION_BEHAVIOR,
                                 parent_name="supported validation behavior",
                                 subset_list=[behavior],
                                 subset_name="defined behavior in all_cols_params of nulls_portion_params")
            return behavior
        except KeyError:
            return "error"

    def get_nulls_portion_specific_cols_params(self):
        try:
            params = []
            defined_params = self._json_config["validation"]["nulls_portion_params"]["specific_cols_params"]
            for defined_param in defined_params:
                default_dict = {"activate": False, "min_sample": 200000, "threshold": 0.9, "behavior": "error"}
                default_dict.update(defined_param)
                if default_dict["activate"] is False:
                    continue
                if "name" not in default_dict:
                    logging.critical("Each item in the specific_cols_params section of nulls_portion_params must "
                                     "contain the 'name' key. Please update your configuration file and try again. "
                                     "Exiting...")
                    sys.exit(1)

                params.append(default_dict)
                self.nulls_portion_specific_cols.append(default_dict["name"])
            return params
        except KeyError:
            return []

    def get_psi_all_cols_buckets(self):
        try:
            buckets = self._json_config["validation"]["psi_params"]["all_cols_params"]["buckets"]
            validate_in_range(buckets, minimum=4, maximum=20)
            return buckets
        except KeyError:
            return 8

    def get_psi_all_cols_threshold(self):
        try:
            threshold = self._json_config["validation"]["psi_params"]["all_cols_params"]["threshold"]
            validate_in_range(threshold, minimum=0, maximum=1)
            return threshold
        except KeyError:
            return 0.2

    def get_psi_all_cols_behavior(self):
        try:
            behavior = self._json_config["validation"]["psi_params"]["all_cols_params"]["behavior"]
            validate_subset_list(parent_list=SUPPORTED_VALIDATION_BEHAVIOR,
                                 parent_name="supported validation behavior",
                                 subset_list=[behavior],
                                 subset_name="defined behavior in all_cols_params of psi_params")
            return behavior
        except KeyError:
            return "error"

    def get_psi_specific_cols_params(self):
        try:
            params = []
            defined_params = self._json_config["validation"]["psi_params"]["specific_cols_params"]
            for defined_param in defined_params:
                default_dict = {"activate": False, "min_sample": 200000, "threshold": 0.2, "behavior": "error", "buckets": 8}
                default_dict.update(defined_param)
                if default_dict["activate"] is False:
                    continue
                if "name" not in default_dict:
                    logging.critical("Each item in the specific_cols_params section of psi_params must "
                                     "contain the 'name' key. Please update your configuration file and try again. "
                                     "Exiting...")
                    sys.exit(1)

                params.append(default_dict)
                self.nulls_portion_specific_cols.append(default_dict["name"])
            return params
        except KeyError:
            return []
