from .config import FORM
from .helpers.form import VIEW_TYPE_TAG

_models_ = None


def load_json():
    """
    Lazy loading of the form.
    """
    global _models_

    if _models_ is None:
        _models_ = FORM.json()
    for view_type in _models_.keys():
        _models_[view_type][VIEW_TYPE_TAG] = view_type
    return _models_


def get_default_models(view_type):
    """
    Return the default models for a given view type to forward to the front-end via API

    Args:
        view_type: an instance of ViewType
    """
    models = load_json()
    return models[view_type.value]


def parse_experiment(payload):
    """
    Construct a experiment protobuf from the payload

    Args:
        payload (dict): a dict as sent to the API
    """
    # Pop the model key and create the ExperimentBuilder
    return FORM.parse(payload)
