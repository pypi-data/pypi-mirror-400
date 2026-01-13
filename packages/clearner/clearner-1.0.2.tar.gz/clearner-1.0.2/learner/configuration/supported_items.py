# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

SUPPORTED_ENGINES = ["Recommender", "Classifier", "Regressor", "DeepClassifier", "DeepRegressor",
                     "ImageClassifier", "DML"]

SUPPORTED_MODELS = {"Classifier": ["AdaBoostClassifier",
                                   "BaggingClassifier",
                                   "BernoulliNB",
                                   "CatBoostClassifier",
                                   "DecisionTreeClassifier",
                                   "ExtraTreeClassifier",
                                   "ExtraTreesClassifier",
                                   "GaussianNB",
                                   "GaussianProcessClassifier",
                                   "GradientBoostingClassifier",
                                   "KNeighborsClassifier",
                                   "LGBMClassifier",
                                   "LinearDiscriminantAnalysis",
                                   "LogisticRegression",
                                   "MLPClassifier",
                                   "MultinomialNB",
                                   "QuadraticDiscriminantAnalysis",
                                   "RandomForestClassifier",
                                   "SVC",
                                   "XGBClassifier",
                                   "CalibratedAdaBoostClassifier",
                                   "CalibratedBaggingClassifier",
                                   "CalibratedBernoulliNB",
                                   "CalibratedCatBoostClassifier",
                                   "CalibratedDecisionTreeClassifier",
                                   "CalibratedExtraTreeClassifier",
                                   "CalibratedExtraTreesClassifier",
                                   "CalibratedGaussianNB",
                                   "CalibratedGaussianProcessClassifier",
                                   "CalibratedGradientBoostingClassifier",
                                   "CalibratedKNeighborsClassifier",
                                   "CalibratedLGBMClassifier",
                                   "CalibratedLinearDiscriminantAnalysis",
                                   "CalibratedLogisticRegression",
                                   "CalibratedMLPClassifier",
                                   "CalibratedMultinomialNB",
                                   "CalibratedQuadraticDiscriminantAnalysis",
                                   "CalibratedRandomForestClassifier",
                                   "CalibratedSVC",
                                   "CalibratedXGBClassifier",
                                   ],

                    "Regressor": ["AdaBoostRegressor",
                                  "BaggingRegressor",
                                  "CatBoostRegressor",
                                  "DecisionTreeRegressor",
                                  "ExtraTreeRegressor",
                                  "ExtraTreesRegressor",
                                  "GaussianProcessRegressor",
                                  "GradientBoostingRegressor",
                                  "HuberRegressor",
                                  "KNeighborsRegressor",
                                  "Lasso",
                                  "LGBMRegressor",
                                  "LinearRegression",
                                  "RadiusNeighborsRegressor",
                                  "RandomForestRegressor",
                                  "Ridge",
                                  "SGDRegressor",
                                  "SVR",
                                  "XGBRegressor"
                                  ],

                    "DeepClassifier": ["DeepClassifier"],

                    "DeepRegressor": ["DeepRegressor"],
                    "ImageClassifier": ["ImageClassifier",
                                        "AlexNet",
                                        "VGG11",
                                        "VGG11_BN",
                                        "VGG13",
                                        "VGG13_BN",
                                        "VGG16",
                                        "VGG16_BN",
                                        "VGG19",
                                        "VGG19_BN",
                                        "ResNet18",
                                        "ResNet34",
                                        "ResNet50",
                                        "ResNet101",
                                        "ResNet152",
                                        "DenseNet121",
                                        "DenseNet169",
                                        "DenseNet161",
                                        "DenseNet201",
                                        "GoogLeNet",
                                        "ShuffleNet_V2_x0_5",
                                        "ShuffleNet_V2_x1_0",
                                        "MobileNet_V2",
                                        "MobileNet_V3_Large",
                                        "MobileNet_V3_Small",
                                        "ResNext50_32x4d",
                                        "ResNext101_32x8d",
                                        "Wide_ResNet50_2",
                                        "Wide_ResNet101_2",
                                        "MNASNet0_5",
                                        "MNASNet1_0",
                                        ],
                    "DML": ["LinearDML",
                            "DML",
                            "NonParamDML"]
                    }

SUPPORTED_DML_MODEL_FINAL_TYPES = ["RidgeCV",
                                   "LassoCV",
                                   "AdaBoostRegressor",
                                   "BaggingRegressor",
                                   "CatBoostRegressor",
                                   "DecisionTreeRegressor",
                                   "ExtraTreeRegressor",
                                   "ExtraTreesRegressor",
                                   "GaussianProcessRegressor",
                                   "GradientBoostingRegressor",
                                   "HuberRegressor",
                                   "KNeighborsRegressor",
                                   "Lasso",
                                   "LGBMRegressor",
                                   "LinearRegression",
                                   "RadiusNeighborsRegressor",
                                   "RandomForestRegressor",
                                   "Ridge",
                                   "SGDRegressor",
                                   "SVR",
                                   "XGBRegressor"
                                   ]

classifier_scores = {"accuracy": "class",
                     "average_precision": "proba",
                     "brier_score_loss": "proba",
                     "classification_report": "class",
                     "confusion_matrix": "class",
                     "f1": "class",
                     "fbeta": "class",
                     "hamming_loss": "class",
                     "jaccard": "class",
                     "log_loss": "proba",
                     "matthews_corrcoef": "class",
                     "precision": "class",
                     "precision_recall_fscore_support": "class",
                     "recall": "class",
                     "roc_auc": "proba",
                     "zero_one_loss": "class"
                     }

regressor_scores = {"explained_variance": None,
                    "mean_absolute_error": None,
                    "mean_squared_error": None,
                    "mean_squared_log_error": None,
                    "median_absolute_error": None,
                    "r2": None,
                    "root_mean_squared_error": None,
                    "spearman_r": None
                    }

deep_classifier_scores = {"accuracy": "class",
                           "average_precision": "proba",
                           "brier_score_loss": "proba",
                           "f1": "class",
                           "fbeta": "class",
                           "hamming_loss": "class",
                           "jaccard": "class",
                           "log_loss": "proba",
                           "matthews_corrcoef": "class",
                           "precision": "class",
                           "recall": "class",
                          "roc_auc": "proba",
                          "zero_one_loss": "class"
                          }

SUPPORTED_SCORE_TYPES = {"Classifier": classifier_scores,

                         "Regressor": regressor_scores,
                         "DeepClassifier": deep_classifier_scores,
                         "DeepRegressor": regressor_scores,
                         "ImageClassifier": deep_classifier_scores,
                         "DML": {"MSE": None}
                         }

SUPPORTED_INPUT_TYPES = {"Classifier": ["file", "query"],
                         "Regressor": ["file", "query"],
                         "DeepClassifier": ["file", "query"],
                         "DeepRegressor": ["file", "query"],
                         "Recommender": ["file", "query"],
                         "ImageClassifier": ["file", "folder"],
                         "DML": ["file", "query"]
                         }

SUPPORTED_SEGMENTERS = ["static", "dynamic", "value"]

SUPPORTED_DUPLICATES_FOR_SEGMENTERS = ["merge", "drop"]

SUPPORTED_IMBALANCED_METHODS = {"o": "oversampling",
                                "u": "undersampling"}

SUPPORTED_SPLIT_METHODS = {"r": "random",
                           "s": "sort"}

DATE_ITEMS = ["year", "month", "day", "hour", "minute", "quarter", "dayofweek", "weekofyear", "dayofyear",
              "is_month_start", "is_month_end", "is_quarter_start", "is_quarter_end", "is_year_start", "is_year_end",
              "is_leap_year"]

SUPPORTED_DB_TYPES = ["presto", "postgres", "mysql", "snowflake"]

SUPPORTED_NARRATIVE_METHODS = ["importance", "order"]

SUPPORTED_ENGINES_FOR_TARGET_LOG_TRANSFORM = ["Regressor", "DeepRegressor"]

SUPPORTED_ENGINES_FOR_TRIAD_COMBINE = ["Regressor"]

SUPPORTED_ENGINES_FOR_MEAN_COMBINE = ["Regressor", "Classifier"]

SUPPORTED_MEAN_COMBINE_TYPES = ["arithmetic", "geometric"]

SUPPORTED_ENGINE_FOR_PREDICTIONS_VS_ACTUALS_PLOT = ["Regressor", "DeepRegressor"]

SUPPORTED_ENGINE_FOR_CALIBRATION_CURVE_PLOT = ["Classifier", "DeepClassifier"]

SUPPORTED_STEMMERS = ["ARLSTem", "Cistem", "ISRIStemmer", "LancasterStemmer", "PorterStemmer", "RegexpStemmer",
                      "SnowballStemmer"]

SUPPORTED_GROUPBY_AGGREGATION_FUNCTIONS = ["mean", "sum", "size", "count", "std", "var", "sem", "min", "max"]

SUPPORTED_ENGINES_FOR_LEARNING_RATE_PARAMS = ["DeepClassifier", "DeepRegressor", "ImageClassifier"]

SUPPORTED_FILE_FORMATS = ["csv", "parquet", "feather"]

SUPPORTED_VALIDATION_BEHAVIOR = ["error", "warning"]
