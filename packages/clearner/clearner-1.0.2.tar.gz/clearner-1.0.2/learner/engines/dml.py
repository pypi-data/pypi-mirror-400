# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

"""The main module for the DML engine.
"""
import sys
import logging

from learner.data_worker.data_manager import TestDataManager, ValidationDataManager
from learner.model_manager.prediction_manager import DMLPredictor, RegressorPredictor, ClassifierPredictor
from learner.model_manager.dmls import DMLHandler
from learner.data_worker.output_handler import OutputHandler, pickle_object
from learner.engines.base_standard_engine import BaseStandard
from learner.utilities.timer import timeit
from learner.utilities.context_manager import temporary_attrs, AttributeChange
from learner.configuration.configuration import Configuration
from learner.analysis.analysis import Analysis
from learner.utilities.templates import (SAVE_MODEL_PATH, FEATURE_IMPORTANCE_PATH)
from learner.model_manager.scoring_manager import DMLScorer


class DML(BaseStandard):
    """The DML engine class. This class inherits from the BaseStandard class. Because model_y and model_t are either
    a classifier or a regressor, the base class handles those models."""

    def __init__(self, conf: Configuration):
        """Take a conf object (from the Configuration class) to run a dml engine.

        :param conf: a conf object
        """
        super(DML, self).__init__(conf)
        self._drop_cols = self._conf.column.drop_from_train + \
                          [self._conf.column.model_y_target_col, self._conf.column.model_t_target_col]

    @timeit("build the model(s)")
    def run_engine(self):
        """The main function for driving the engine.
        If train_models is set to true, we first train model_y and model_t.
        Then, we run inference for those models. This could be making prediction using the validation data or even test
        data. Next, we train the dml models. The order of operations is important because the dml model needs the trained
        model_y and model_t. After than we run inference using the dml model.
        If set train is not set to true, we load the pretrained models including model_t, model_y, and dml models.
        The load_and_run_pretrained_models method will only run inference using model_y and model_t. After that, we
        run inference using the dml model.

        :return: None
        """
        if self._conf.model.train_models:
            self.data = self.processor.dml_process_data(self.data, list(self.data.drop(self._drop_cols + self.conf.column.id_cols, axis=1).columns))
            self.train_models()
            self.run_inference()
            self.train_dml_model(self.models_dict)
            self.dml_predict(self.models_dict)
        else:
            self.load_and_run_pretrained_models()
            self.dml_predict(self.loaded_models_dict)

        # self.validate_output()
        self.handle_analysis(self.models_dict or self.loaded_models_dict)

    @timeit("train the y and t model(s)")
    def train_models(self):
        """Train model_y and model_t based on the user input. Here, we call the base class's fit_models method, but we
        temporarily pretend we are a Regressor or a Classifier engine. We then save the models or run feature importance
        if requested.

        :return: None
        """
        logging.info("Building the y and t models...")
        for tag, mdl in self.models_dict.items():
            if tag == "dml":
                continue
            logging.info(f"Fitting {tag} model")
            temp_engine = 'Regressor' if tag == "model_y" or self.conf.dml.discrete_treatment is False else 'Classifier'
            temp_target_col = self.conf.column.model_y_target_col if tag == "model_y" else self.conf.column.model_t_target_col
            # when training model y or t, we want to assume we are Regressor or Classifier engine
            with temporary_attrs([AttributeChange(self.conf, 'engine', temp_engine),
                                  AttributeChange(self.conf.column, 'target_col', temp_target_col),
                                  ]):
                self.fit_models(self.data, mdl, self._drop_cols)

            # save models
            if self._conf.model.save_models:
                filename = SAVE_MODEL_PATH.format(
                    path=self._conf.model.models_dict[tag]["path"],
                    output_name=self._conf.workspace.name,
                    tag=tag,
                    sep_timetag=str(self._conf.sep_timetag),
                    ext=".sav"
                )
                pickle_object(self.conf, self._conf.model.models_dict[tag]["path"], filename, dict({tag: mdl}),
                              self.processor, self.feature_engineering, self.validator)

            # handle feature importance if requested
            if self._conf.analysis.importance_activate:
                analysis = Analysis(self._conf)
                filename = FEATURE_IMPORTANCE_PATH.format(
                    output_name=self._conf.workspace.name,
                    tag=str(tag),
                    sep_timetag=str(self._conf.sep_timetag)
                )
                analysis.handle_feature_importance(mdl, filename)

    @timeit("run inference")
    def run_inference(self):
        """Run inference using model_y and model_t. Here, we again need to temporarily pretend we are a regressor or a
        classifier engine and temporarily modify some fields. This allows us to safely use the existing engines to make
        predictions, score predictions, and validate output without writing new code.

        :return: None
        """
        for tag, mdl in self.models_dict.items():
            if tag == "dml":
                continue
            logging.info(f"Running inference using {tag} model")
            temp_engine = 'Regressor' if tag == "model_y" or self.conf.dml.discrete_treatment is False else 'Classifier'
            temp_target_col = self.conf.column.model_y_target_col if tag == "model_y" else self.conf.column.model_t_target_col
            temp_validation_prediction_type = self.conf.data.model_y_validation_prediction_type if tag == "model_y" else self.conf.data.model_t_validation_prediction_type
            temp_validation_score_activate = self.conf.data.model_y_validation_score_activate if tag == "model_y" else self.conf.data.model_t_validation_score_activate
            temp_validation_score_types = self.conf.data.model_y_validation_score_types if tag == "model_y" else self.conf.data.model_t_validation_score_types
            temp_validation_add_timetag = self.conf.data.model_y_validation_add_timetag if tag == "model_y" else self.conf.data.model_t_validation_add_timetag
            temp_validation_column_name = self.conf.data.model_y_validation_column_name if tag == "model_y" else self.conf.data.model_t_validation_column_name
            temp_validation_join_cols = self.conf.data.model_y_validation_join_cols if tag == "model_y" else self.conf.data.model_t_validation_join_cols
            with temporary_attrs([AttributeChange(self.conf, 'engine', temp_engine),
                                  AttributeChange(self.conf.column, 'target_col', temp_target_col),
                                  AttributeChange(self.conf.data, 'validation_prediction_type', temp_validation_prediction_type),
                                  AttributeChange(self.conf.data, 'validation_score_activate', temp_validation_score_activate),
                                  AttributeChange(self.conf.data, 'validation_score_types', temp_validation_score_types),
                                  AttributeChange(self.conf.data, 'validation_add_timetag', temp_validation_add_timetag),
                                  AttributeChange(self.conf.data, 'validation_column_name', temp_validation_column_name),
                                  AttributeChange(self.conf.data, 'validation_join_cols', temp_validation_join_cols),
                                  AttributeChange(self, 'models_dict', {tag: self.models_dict[tag]}),
                                  AttributeChange(self.conf.model, 'nrows_score', 0),
                                  ]):
                self.predict()
                self.score_prediction()
                self.validate_output()

    def load_and_run_pretrained_models(self):
        """Load the pretrained model_y and model_t and run inference. Here, we leverage the base class's load_models
        method to populate loaded_models_dict attribute. However, we cannot run the predict and score_prediction in that
        method because the engine and other parameters must change before. The reason is that model_t and model_y could
        either be a regressor or a classifier model. Once the loaded_models_dict is populated, we iterate through items,
        temporarily change engine and some other attributes, and call the predict and validate_output method of the base
        class.

        :return: None
        """
        with temporary_attrs([AttributeChange(self, 'predict', self.temp_predict),
                              AttributeChange(self, 'score_prediction', self.temp_score_prediction)
                              ]):
            self.load_models(self._conf.workspace.path)
        for tag, mdl in self.loaded_models_dict.items():
            if tag == "dml":
                continue
            logging.info(f"Running inference using {tag} model")
            temp_engine = 'Regressor' if tag == "model_y" or self.conf.dml.discrete_treatment is False else 'Classifier'
            temp_target_col = self.conf.column.model_y_target_col if tag == "model_y" else self.conf.column.model_t_target_col
            temp_validation_prediction_type = self.conf.data.model_y_validation_prediction_type if tag == "model_y" else self.conf.data.model_t_validation_prediction_type
            temp_validation_score_activate = self.conf.data.model_y_validation_score_activate if tag == "model_y" else self.conf.data.model_t_validation_score_activate
            temp_validation_score_types = self.conf.data.model_y_validation_score_types if tag == "model_y" else self.conf.data.model_t_validation_score_types
            temp_validation_add_timetag = self.conf.data.model_y_validation_add_timetag if tag == "model_y" else self.conf.data.model_t_validation_add_timetag
            temp_validation_column_name = self.conf.data.model_y_validation_column_name if tag == "model_y" else self.conf.data.model_t_validation_column_name
            temp_validation_join_cols = self.conf.data.model_y_validation_join_cols if tag == "model_y" else self.conf.data.model_t_validation_join_cols
            with temporary_attrs([AttributeChange(self.conf, 'engine', temp_engine),
                                  AttributeChange(self.conf.column, 'target_col', temp_target_col),
                                  AttributeChange(self.conf.data, 'validation_prediction_type', temp_validation_prediction_type),
                                  AttributeChange(self.conf.data, 'validation_score_activate', temp_validation_score_activate),
                                  AttributeChange(self.conf.data, 'validation_score_types', temp_validation_score_types),
                                  AttributeChange(self.conf.data, 'validation_add_timetag', temp_validation_add_timetag),
                                  AttributeChange(self.conf.data, 'validation_column_name', temp_validation_column_name),
                                  AttributeChange(self.conf.data, 'validation_join_cols', temp_validation_join_cols),
                                  AttributeChange(self, 'models_dict', {tag: self.loaded_models_dict[tag]}),
                                  AttributeChange(self.conf.model, 'nrows_score', 0),
                                  ]):
                self.predict()
                self.validate_output()

    def temp_predict(self):
        """A placeholder method to temporarily replace the predict method of the base class.

        :return: None
        """
        pass

    def temp_score_prediction(self):
        """A placeholder method to temporarily replace the score_prediction method of the base class.

        :return: None
        """
        pass

    def train_dml_model(self, models_dict):
        """Call fit_dml_models to train the dml models. If requested, save the model object.

        :param models_dict: when train_models is set to true, this is the models_dict, otherwise it's loaded_models_dict.
        :return: None
        """
        logging.info("Building the DML model...")
        tag = "dml"
        mdl = models_dict[tag]

        self.fit_dml_models(self.data, self.models_dict, self._drop_cols)

        # save models
        if self._conf.model.save_models:
            filename = SAVE_MODEL_PATH.format(
                path=self._conf.model.models_dict[tag]["path"],
                output_name=self._conf.workspace.name,
                tag=tag,
                sep_timetag=str(self._conf.sep_timetag),
                ext=".sav"
            )
            pickle_object(self.conf, self._conf.model.models_dict[tag]["path"], filename, dict({tag: mdl}),
                          self.processor, self.feature_engineering, self.validator)

    @timeit("fit DML models")
    def fit_dml_models(self, train_data, models_dict, drop_cols):
        """Call the static method of DMLHandler to fit the DML model and populate the value of "model" key.

        :param train_data: the training dataset
        :param models_dict: models_dict or loaded_models_dict dictionaries. This is the full dictionary not a single item.
        :param drop_cols: a list of columns that should be excluded from training
        :return: None
        """
        # save the train_features in case we need to use them later
        models_dict["dml"]["train_features"] = train_data.drop(drop_cols, axis=1).columns

        models_dict["dml"]["model"] = DMLHandler.learner_fit(
            train_data.drop(drop_cols, axis=1),
            train_data[self._conf.column.model_y_target_col],
            train_data[self._conf.column.model_t_target_col],
            models_dict,
            self.conf.dml.bootstrap_inference_params
        )

    @timeit("make predictions using the trained DML model(s)")
    def dml_predict(self, models_dict):
        """Call predict_validation if we need to score the models using validation data and call predict_test if we
        need to make predictions on test data.

        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Making DML predictions using validation data...")
            self.dml_predict_validation(models_dict)
        if self._conf.data.test_prediction_activate:
            logging.info("Making DML predictions using test data...")
            self.dml_predict_test(models_dict)

    def dml_predict_validation(self, models_dict):
        """Use the trained models to make predictions on validation data. Unlike test data, the entire validation data
        is loaded in memory when making predictions on validation data. This method is similar to the predict_validation
        method of the base class. The difference is that it only handles the "dml" model.

        :param models_dict:
        :return:
        """
        validation_manager = ValidationDataManager(self._conf, self.processor, self.feature_engineering, self.validator)
        validation_manager.data = validation_manager.processor.dml_process_data(validation_manager.data, list(validation_manager.data.drop(self._drop_cols + self.conf.column.id_cols, axis=1).columns))
        tag = "dml"
        mdl = models_dict[tag]
        predictor = DMLPredictor(mdl, self._conf)

        prediction_df, data = predictor.make_predictions(validation_manager.data,
                                                         data_type="validation",
                                                         prediction_type=self._conf.data.validation_prediction_type,
                                                         column_name=self._conf.data.validation_column_name)

        predictor.write_predictions(tag,
                                    prediction_df,
                                    data,
                                    data_type="validation",
                                    add_timetag=self._conf.data.validation_add_timetag,
                                    add_version=self._conf.model.version_activate,
                                    version_name=self._conf.model.version_version_name,
                                    version_column_name=self._conf.model.version_column_name
                                    )
        self.dml_score_prediction(validation_manager.data[mdl["train_features"]])

    def dml_predict_test(self, models_dict):
        """Use the trained models to make predictions. Making predictions are performed by iterating through the
        test dataset. The test dataset can be very large and we process it in chunks. This method is similar to the
        predict_test method of the base class. The difference is that it only handles the "dml" model.

        :param models_dict:
        :return:
        """
        test_manager = TestDataManager(self._conf, self.processor, self.feature_engineering, self.validator)
        reader = test_manager.get_reader()

        num_chunks = 0
        for index, chunk in enumerate(reader):
            num_chunks += 1
            test_data = test_manager.get_reader_data(chunk)
            test_data = test_manager.processor.dml_process_data(test_data, list(test_data.drop(self._drop_cols + self.conf.column.id_cols, axis=1, errors='ignore').columns))

            for tag, mdl in models_dict.items():
                if tag != "dml":
                    continue
                predictor = DMLPredictor(mdl, self._conf)

                prediction_df, data = predictor.make_predictions(test_data,
                                                                 data_type="test",
                                                                 column_name=self._conf.data.test_column_name,
                                                                 prediction_type=self._conf.data.test_prediction_type)

                predictor.write_predictions(tag,
                                            prediction_df,
                                            data,
                                            index,
                                            data_type="test",
                                            add_timetag=self._conf.data.test_add_timetag,
                                            add_version=self._conf.model.version_activate,
                                            version_name=self._conf.model.version_version_name,
                                            version_column_name=self._conf.model.version_column_name)

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, {"dml": models_dict["dml"]})

    def predict_validation(self):
        """Use the trained models to make predictions on validation data. Unlike test data, the entire validation data
        is loaded in memory when making predictions on validation data.

        :return: None
        """
        validation_manager = ValidationDataManager(self._conf, self.processor, self.feature_engineering, self.validator)
        validation_manager.data = validation_manager.processor.dml_process_data(validation_manager.data, list(validation_manager.data.drop(self._drop_cols + self.conf.column.id_cols, axis=1).columns))
        for tag, mdl in self.models_dict.items():
            predictor = getattr(sys.modules[__name__], self._conf.engine + "Predictor")(mdl, self._conf)

            prediction_df, data = predictor.make_predictions(validation_manager.data,
                                                             data_type="validation",
                                                             prediction_type=self._conf.data.validation_prediction_type,
                                                             column_name=self._conf.data.validation_column_name)

            predictor.write_predictions(tag,
                                        prediction_df,
                                        data,
                                        data_type="validation",
                                        add_timetag=self._conf.data.validation_add_timetag,
                                        add_version=self._conf.model.version_activate,
                                        version_name=self._conf.model.version_version_name,
                                        version_column_name=self._conf.model.version_column_name
                                        )

            self.handle_shap(mdl, validation_manager.data, tag)

    def predict_test(self):
        """Use the trained models to make predictions. Making predictions are performed by iterating through the
        test dataset. The test dataset can be very large and we process it in chunks.

        :return: None
        """
        test_manager = TestDataManager(self._conf, self.processor, self.feature_engineering, self.validator)
        reader = test_manager.get_reader()

        num_chunks = 0
        for index, chunk in enumerate(reader):
            num_chunks += 1
            test_data = test_manager.get_reader_data(chunk)
            test_data = test_manager.processor.dml_process_data(test_data, list(test_data.drop(self._drop_cols + self.conf.column.id_cols, axis=1, errors="ignore").columns))

            for tag, mdl in self.models_dict.items():
                predictor = getattr(sys.modules[__name__], self._conf.engine + "Predictor")(mdl, self._conf)

                prediction_df, data = predictor.make_predictions(test_data,
                                                                 data_type="test",
                                                                 column_name=self._conf.data.test_column_name,
                                                                 prediction_type=self._conf.data.test_prediction_type)

                predictor.write_predictions(tag,
                                            prediction_df,
                                            data,
                                            index,
                                            data_type="test",
                                            add_timetag=self._conf.data.test_add_timetag,
                                            add_version=self._conf.model.version_activate,
                                            version_name=self._conf.model.version_version_name,
                                            version_column_name=self._conf.model.version_column_name)
                self.handle_shap(mdl, test_data, tag, index)

            # keep track of number of rows in test dataset for validation purposes
            self.conf.model.nrows_score += chunk.shape[0]

        output = OutputHandler(self._conf, data_type="test")
        output.concat_chunk_csv(num_chunks, self.models_dict)
        if self.shap is not None:
            output.concat_dict_of_csv_files(self.shap.final_filenames)

    @timeit("compute the predictions scores")
    def dml_score_prediction(self, data):
        """Score the predictions using the validation dataset. Please note that we cannot score the models using test
        data because the test data does not have the target column.

        :return: None
        """
        if self._conf.data.validation_score_activate:
            logging.info("Computing the prediction scores...")
            scorer = DMLScorer(self.conf, self.models_dict, data, self.processor)
            scorer.score()

