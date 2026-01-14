#
#  Copyright 2026 by Dmitry Berezovsky, MIT License
#
import datetime
from typing import cast

from django.apps import apps
from django.db import models
from django.utils.module_loading import import_string

__all__ = ["get_model_by_name", "get_class_by_name", "datetime_now"]


def get_model_by_name(model_name: str) -> type[models.Model]:
    """Get a Django model class by its dotted name.

    :param model_name: Dotted model name (e.g., 'app_label.ModelName').
    :return: Model class.
    :raises ValueError: If the model cannot be found.
    """
    try:
        app_label, model = model_name.split(".", 1)
        return cast(type[models.Model], apps.get_model(app_label, model))
    except LookupError as err:
        raise ValueError(f"Model {model_name} not found") from err


def get_class_by_name(dotted_path: str) -> type:
    """Import and return a class by its dotted Python path.

    :param dotted_path: Dotted Python path to the class.
    :return: Imported class type.
    """
    return import_string(dotted_path)


def datetime_now() -> datetime.datetime:
    """Return the current datetime in UTC.

    :return: Current datetime with UTC timezone.
    """
    return datetime.datetime.now(tz=datetime.UTC)
