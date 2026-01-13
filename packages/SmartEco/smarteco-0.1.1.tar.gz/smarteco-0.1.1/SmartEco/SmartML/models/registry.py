from __future__ import annotations



from .BaseLines_Class import (
    LogisticModel,
    SVCModel,
    KNNClassifierModel,
    NaiveBayesModel,
)

from .Trees_Class import (
    LightGBMClassifierModel,
    XGBoostClassifierModel,
    CatBoostClassifierModel,
    RandomForestClassifierModel,
    ExtraTreesClassifierModel,
)

from .DL_Class import (
    TabNetClassifierModel,
    FTTransformerClassifierModel,
    TabTransformerClassifierModel,
    SAINTClassifierModel,
    MLPClassifierModel,
    NODEClassifierModel,
    NAMClassifierModel,
    GrowNetClassifierModel,
    ModernNCAClassifierModel,
)

from .SmartKNN import SmartKNNClassifierModel


from .BaseLine_Reg import (
    LinearRegModel,
    RidgeModel,
    LassoModel,
    ElasticNetModel,
    SVRModel,
    KNNRegressorModel,
)

from .Trees_Reg import (
    LightGBMRegressorModel,
    XGBoostRegressorModel,
    CatBoostRegressorModel,
    RandomForestRegressorModel,
    ExtraTreesRegressorModel,
)

from .DL_Reg import (
    TabNetRegressorModel,
    FTTransformerRegressorModel,
    TabTransformerRegressorModel,
    SAINTRegressorModel,
    MLPRegressorModel,
    NODERegressorModel,
    NAMRegressorModel,
    DeepGBMRegressorModel,
    GrowNetRegressorModel,
)

from .SmartKNN import SmartKNNRegressorModel


def _clean_registry(registry: dict) -> dict:
    return {name: cls for name, cls in registry.items() if cls is not None}


CLASSIFICATION_MODELS = _clean_registry({
    "logistic": LogisticModel,
    "svc": SVCModel,
    "knn": KNNClassifierModel,
    "naive_bayes": NaiveBayesModel,
    "lightgbm": LightGBMClassifierModel,
    "xgboost": XGBoostClassifierModel,
    "catboost": CatBoostClassifierModel,
    "random_forest": RandomForestClassifierModel,
    "extra_trees": ExtraTreesClassifierModel,
    "tabnet": TabNetClassifierModel,
    "ft_transformer": FTTransformerClassifierModel,
    "tab_transformer": TabTransformerClassifierModel,
    "saint": SAINTClassifierModel,
    "mlp": MLPClassifierModel,
    "node": NODEClassifierModel,
    "nam": NAMClassifierModel,
    "grownet": GrowNetClassifierModel,
    "modern_nca": ModernNCAClassifierModel,
    "smartknn": SmartKNNClassifierModel,
})


REGRESSION_MODELS = _clean_registry({
    "linear": LinearRegModel,
    "ridge": RidgeModel,
    "lasso": LassoModel,
    "elasticnet": ElasticNetModel,
    "svr": SVRModel,
    "knn": KNNRegressorModel,
    "lightgbm": LightGBMRegressorModel,
    "xgboost": XGBoostRegressorModel,
    "catboost": CatBoostRegressorModel,
    "random_forest": RandomForestRegressorModel,
    "extra_trees": ExtraTreesRegressorModel,
    "tabnet": TabNetRegressorModel,
    "ft_transformer": FTTransformerRegressorModel,
    "tab_transformer": TabTransformerRegressorModel,
    "saint": SAINTRegressorModel,
    "mlp": MLPRegressorModel,
    "node": NODERegressorModel,
    "nam": NAMRegressorModel,
    "deepgbm": DeepGBMRegressorModel,
    "grownet": GrowNetRegressorModel,
    "smartknn": SmartKNNRegressorModel,
})



def list_models(task: str):
    if task == "classification":
        return sorted(CLASSIFICATION_MODELS.keys())
    if task == "regression":
        return sorted(REGRESSION_MODELS.keys())
    raise ValueError(f"Unknown task: {task}")


def get_model(task: str, model_name: str):
    key = model_name.lower()

    if task == "classification":
        registry = CLASSIFICATION_MODELS
    elif task == "regression":
        registry = REGRESSION_MODELS
    else:
        raise ValueError(f"Unknown task: {task}")

    if key not in registry:
        raise KeyError(
            f"Model '{model_name}' not found for task '{task}'.\n"
            f"Available models: {sorted(registry.keys())}"
        )

    cls = registry[key]
    if cls is None:
        raise ImportError(
            f"Model '{model_name}' is unavailable (missing optional dependency)"
        )

    return cls()
