# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for validating a data set against the requirements that are either defined in a separate
metadata file or provided by user in the configuration file"""

import sys
import warnings
import logging
import valideer as v
import numpy as np
import pandas as pd

from learner.configuration.configuration import Configuration


class DataValidator:
    def __init__(self, conf: Configuration, data_type="train"):
        """Accept a dataset and a conf object to validate the data set against the information provided in the conf
        object

        :param conf: a conf object (an instance of the Configuration class in configuration module)
        :param data_type: the data type, it can be "train", "validation" or "test"
        """
        self._conf = conf
        self._data_type = data_type
        self._learner_psi_calculator = None

    @property
    def conf(self):
        return self._conf

    @property
    def learner_psi_calculator(self):
        return self._learner_psi_calculator

    @property
    def data_type(self):
        return self._data_type

    def validate_against_meta_data(self, meta_data, data):
        """Validate the data against a meta_data file

        :param meta_data: the meta_data file
        :param data: a pandas dataframe
        :return: None
        """
        logging.info("Validating the data against the meta_data file...")

        # loop through columns and create new dict with just column and schema needed for validation
        schema_dict = dict()
        for col in meta_data['column']:
            for key, value in meta_data['column'][col].items():
                if key == 'schema':
                    schema_dict[col] = [value]
                    
        val = v.parse(schema_dict)
        for col in data.columns:
            if not val.is_valid(data[[col]].dropna().to_dict('list')):
                message = f"Data in column {col} is Not Valid, type expected: {schema_dict[col]}"
                if self.conf.validation.dtypes_against_metadata_behavior == "error":
                    raise Exception(message)
                else:
                    warnings.warn(message, Warning)

        logging.info("Finished validating against meta_data...")

    def check_nulls_in_col(self, data, col):
        """Check if the target column has any missing values.

        :param data: a pandas dataframe
        :param col: the column to check for missing values. This is usually the target column
        :return: None
        """
        logging.info("Checking if the target contains missing values...")
        try:
            num_nulls = data[col].isnull().sum()
            if num_nulls:
                if self.conf.validation.nulls_in_target_behavior == "error":
                    logging.critical(f"The target column contains {num_nulls} rows with missing values. Exiting...")
                    sys.exit(1)
                else:
                    data.dropna(subset=[col], inplace=True)
                    warnings.warn(f"The target column contains {num_nulls} rows with missing values. Those rows will be dropped "
                                  "from the dataset", Warning)
                    if data.empty:
                        logging.error("Looks like all values in the target column are missing, please check your data."
                                      " Exiting...")
                        sys.exit(1)

        except KeyError:
            logging.info("target_col is not in the data or not loaded. Skipping check_nulls_in_target...")

    def check_dtype_of_num_cols(self, data):
        """Ensure the columns passed as numerical columns are actually numeric. Learner only issues a warning if it
        finds out some columns are not numeric.

        :param data: a pandas dataframe
        :return: None
        """
        if self._conf.process.to_numeric_cols and self._conf.process.to_numeric_activate:
            logging.info("Checking data types of numerical columns...")
            # get columns with numeric datatypes
            numeric_columns_types = [np.issubdtype(data[col].dtype, np.number)
                                     for col in self._conf.process.to_numeric_cols]
            # first check to see any num_cols is defined, if not just return the data
            # if num_cols is defined, make sure all passed columns are of type number (int and float).
            if not all(numeric_columns_types):
                message = """Column(s) passed {0} can't be converted to numeric data type. This may cause some 
                              errors. Check the data""".format([col_name for col_name in self._conf.process.to_numeric_cols
                                                               if np.issubdtype(data[col_name].dtype, np.number)
                                                               is False])
                if self.conf.validation.to_numeric_behavior == "error":
                    logging.critical(f"{message}. Exiting...")
                    sys.exit(1)
                else:
                    warnings.warn(message, UserWarning)

    def check_nulls_portion(self, data):
        """Perform the data validation related to the null portion. In this method, we first obtain a dataframe
        containing the features and the missing ratio. Then, depending on the input parameters, we'll use that
        information to validate the data. We first do the validation for specific columns, then do all other columns.

        :param data: a pandas dataframe
        :return: None
        """
        missing_df = self._get_missing_df(data)
        if missing_df.empty:
            return

        sample_count = data.shape[0]
        for param in self.conf.validation.nulls_portion_specific_cols_params:
            if sample_count >= param["min_sample"]:
                missing_portion = missing_df[missing_df["feature"] == param["name"]]["missing_ratio"].values[0]
                if missing_portion > param["threshold"]:
                    message = (f"The portion of nulls in {param['name']} is {round(missing_portion, 2)}, " 
                               f"which is higher than the defined threshold of {param['threshold']}")
                    if param["behavior"] == "error":
                        logging.critical(f"{message}. Exiting...")
                        sys.exit(1)
                    else:
                        warnings.warn(message, Warning)

        if self.conf.validation.nulls_portion_all_cols_activate:
            if sample_count >= self.conf.validation.nulls_portion_all_cols_min_sample:
                df = missing_df[
                          (~missing_df["feature"].isin(self.conf.validation.nulls_portion_specific_cols)) &\
                          (missing_df["missing_ratio"] > self.conf.validation.nulls_portion_all_cols_threshold)
                      ]
                if not df.empty:
                    message = (f"The null portion is greater than the defined threshold of "
                               f"{self.conf.validation.nulls_portion_all_cols_threshold} in some columns. "
                               f"Below is the detailed information:\n {df}")
                    if self.conf.validation.nulls_portion_all_cols_behavior == "error":
                        logging.critical(message)
                        sys.exit(1)
                    else:
                        warnings.warn(message, Warning)

    def _get_missing_df(self, data):
        """Use the self.data pandas dataframe and construct a new dataframe with the columns: "feature", "missing_count",
        and "missing_ratio". Here we make sure we only do the calculation for relevant columns for performance reasons.

        :param data: a pandas dataframe
        :return: a pandas dataframe containing three columns: "feature", "missing_count", and "missing_ratio"
        """
        missing_df = pd.DataFrame()
        # we do the nulls portion calculations for all the columns if all_cols is activated
        # otherwise we use the specified columns
        if self.conf.validation.nulls_portion_all_cols_activate:
            missing_df = data.isnull().sum(axis=0).reset_index()
        elif self.conf.validation.nulls_portion_specific_cols_params:
            missing_df = data[self.conf.validation.nulls_portion_specific_cols].isnull().sum(axis=0).reset_index()
        if missing_df.empty is False:
            missing_df.columns = ["feature", "missing_count"]
            missing_df['missing_ratio'] = (missing_df["missing_count"] / data.shape[0])
        return missing_df

    def check_psi(self, data):
        """During training, learner_psi_calculator is not populated. In that case, we instantiate a LearnerPSICalculator
        object and fit it. During inference, learner_psi_calculator will be populated. In that case, we call the
        transform method.

        :param data: a pandas dataframe
        :return: None
        """
        if not self._learner_psi_calculator:
            self._learner_psi_calculator = LearnerPSICalculator(self.conf)
            self._learner_psi_calculator.fit(data)
        else:
            self._learner_psi_calculator.transform(data)

    def validate_data(self, data, data_type):
        """The main function that runs all the instance methods if the validation flag is set to true

        :param data: a pandas dataframe
        :return: None
        """
        logging.info("Validating the data...")

        if self._conf.data.meta_data_file and self._conf.validation.dtypes_against_metadata_activate:
            self.validate_against_meta_data(self._conf.data.meta_data, data)

        # we care about nulls in target only when data_type is train or validation
        if data_type != "test" and self.conf.validation.nulls_in_target_activate:
            self.check_nulls_in_col(data, self._conf.column.target_col)
        if self.conf.validation.to_numeric_activate:
            self.check_dtype_of_num_cols(data)
        self.check_nulls_portion(data)
        self.check_psi(data)
        logging.info("Successfully validated the data")


class LearnerPSICalculator:
    """LearnerPSICalculator is a validation class to compute the Population Stability Index (PSI) in order to detect
    drift in the distribution of the inference data when compared to the training data. The definition of PSI may be
    found here: https://encord.com/glossary/population-stability-index-psi/. During training, the fit method is called.
    The fit method basically computes the distribution of the training data. During inference, the transform method
    computes the distribution of the inference data. From there, we calculate psi values and issue warning or errors
    depending on the user input. The details of what columns to consider, what settings to use, or what behavior to
    trigger will be defined by the user and is provided in the conf object.
    """
    def __init__(self, conf: Configuration):
        """Initialize a LearnerPSICalculator using an object of the Configuration class and  assigning the necessary
        instance attributes.

        :param conf: an instance of the Configuration class
        """
        self._conf = conf
        self.training_data = {}

    @property
    def conf(self):
        return self._conf

    def fit(self, data):
        """During training, we calculate the distribution of each column to populate training_data instance attribute.
        "Distribution" here means "breakpoints" and "percents". The calculations is done by calling the
        _compute_distribution_for_a_col method and providing the necessary information. In this method, we first take
        care of specific cols. Then we exclude target and drop_from_train and do other columns assuming the user has
        requested it.

        :param data: a pandas dataframe
        :return: None
        """
        logging.info("Calculating the Population Stability Index using LearnerPSICalculator...")
        sample_count = data.shape[0]
        # we first do the calculations for specific columns
        for param in self.conf.validation.psi_specific_cols_params:
            if sample_count >= param["min_sample"]:
                col = param["name"]
                try:
                    self._compute_distribution_for_a_col(data, col, param["buckets"], param["threshold"], param["behavior"], param["min_sample"])
                except Exception as e:
                    logging.critical(f"Unable to compute PSI for the {col}. The error is: {e}. Exiting...")
                    sys.exit(1)
        if self.conf.validation.psi_all_cols_activate and sample_count >= self.conf.validation.psi_all_cols_min_sample:
            exclude_cols = self.conf.validation.nulls_portion_specific_cols + self.conf.column.drop_from_train + [self.conf.column.target_col]
            for col in data.columns:
                if col in exclude_cols:
                    continue
                try:
                    self._compute_distribution_for_a_col(data,
                                                         col,
                                                         buckets=self.conf.validation.psi_all_cols_buckets,
                                                         threshold=self.conf.validation.psi_all_cols_threshold,
                                                         behavior=self.conf.validation.psi_all_cols_behavior,
                                                         min_sample=self.conf.validation.psi_all_cols_min_sample)
                except Exception as e:
                    logging.debug(f"Unable to compute PSI for the {col}. The error is: {e}.")
                    del self.training_data[col]

        logging.info("Successfully Calculate the Population Stability Index using LearnerPSICalculator.")

    def _compute_distribution_for_a_col(self, data, col, buckets, threshold, behavior, min_sample):
        """Compute the "breakpoints" and "percents" for a column in a pandas dataframe. breakpoints are calculated using
        the minimum and maximum values in the column and the number of buckets. The percents will then be the % of
        records in each bin.

        :param data: a pandas dataframe
        :param col: the name of the column in the dataframe
        :param buckets: the number of buckets for calculating the breakpoints
        :param threshold: the threshold value specific to the column
        :param behavior: the behavior to show; could be "error" or "warning"
        :param min_sample: the minimum number of samples in order to do the calculations during the inference
        :return: None
        """
        self.training_data[col] = {}
        self.training_data[col]["threshold"] = threshold
        self.training_data[col]["behavior"] = behavior
        self.training_data[col]["min_sample"] = min_sample
        self.training_data[col]["buckets"] = buckets
        self.training_data[col]["breakpoints"] = np.linspace(data[col].min(), data[col].max(), buckets + 1)
        self.training_data[col]["percents"] = np.histogram(data[col], bins=self.training_data[col]["breakpoints"])[0] / len(data[col])

    def transform(self, data):
        """During inference, assuming training_data attribute is populated, we iterate through each column and compute
        the distribution of the inference data using the breakpoints from the training data. We then calculate psi
        value (using the _calculate_psi method). Then, depending on the requested behavior, we issue a warning or an
        error if the psi value is greater than the desired threshold.

        :param data: a pandas dataframe
        :return: None
        """
        if not self.training_data:
            # we should not ge here but just in case
            return
        sample_count = data.shape[0]
        for col in self.training_data:
            if sample_count > self.training_data[col]["min_sample"]:
                inference_percents = np.histogram(data[col], bins=self.training_data[col]["breakpoints"])[0] / len(data[col])
                psi_value = self._calculate_psi(self.training_data[col]["percents"], inference_percents)
                if psi_value > self.training_data[col]["threshold"]:
                    message = (f"PSI for {col} indicates a significant drift of {round(psi_value, 3)}, which is greater than the "
                               f"defined threshold of {self.training_data[col]['threshold']}")
                    if self.training_data[col]["behavior"] == "error":
                        logging.critical(f"{message}. Exiting...")
                        sys.exit(1)
                    else:
                        warnings.warn(message, Warning)

    def _calculate_psi(self, inference_percents, training_percents):
        """Accept two arrays of percentages and compute the psi. Then return the computed value.

        :param inference_percents: the fist array of percents.
        :param training_percents: the second array of percents.
        :return: the computed psi.
        """
        def sub_psi(e_perc, a_perc):
            if a_perc == 0:
                a_perc = 0.0001
            if e_perc == 0:
                e_perc = 0.0001
            return (e_perc - a_perc) * np.log(e_perc / a_perc)

        psi_values = [sub_psi(e, a) for e, a in zip(inference_percents, training_percents)]
        return np.sum(psi_values)


def check_nulls_in_col(data, col):
    """Check if the col column has any missing values.

    :param data: a pandas dataframe
    :param col: the column to check for missing values. This is usually the target column
    :return: None
    """
    logging.info(f"Checking if the {col} contains missing values...")
    try:
        num_nulls = data[col].isnull().sum()
        if num_nulls:
            data.dropna(subset=[col], inplace=True)
            warnings.warn(f"The {col} column contains {num_nulls} rows with missing values. Those rows will be dropped "
                          "from the dataset", Warning)
            if data.empty:
                logging.error("Looks like all values in the target column are missing, please check your data."
                              " Exiting...")
                sys.exit(1)
    except KeyError:
        logging.info(f"{col} is not in the data or not loaded. Exiting...")
        sys.exit(1)
