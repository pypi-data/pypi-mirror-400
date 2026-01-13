from SmartEco.SmartML.models.registry import list_models, get_model

def test_registry_classification():
    models = list_models("classification")
    assert isinstance(models, list)
    assert len(models) > 0

def test_registry_regression():
    models = list_models("regression")
    assert isinstance(models, list)
    assert len(models) > 0
