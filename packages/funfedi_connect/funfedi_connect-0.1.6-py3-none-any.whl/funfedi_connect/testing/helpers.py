import os
import json
import allure
from funfedi_connect.types import Attachments


def attach(attachment: Attachments, data: dict):
    allure.attach(
        json.dumps(data, indent=2),
        name=str(attachment),
        attachment_type="application/json",
        extension="json",
    )


def get_app_name():
    app_name = os.environ.get("FEDI_APP")
    if app_name is None:
        raise Exception("An application needs to be provided in FEDI_APP")
    return app_name


def get_app_version():
    return os.environ.get("FEDI_APP_VERSION")


def make_feature_name(feature_name: str, app_name: str, app_version: str | None):
    """
    ```
    >>> make_feature_name("feature", "app", None)
    'app: feature'

    >>> make_feature_name("feature", "app", "0.1.0")
    'app 0.1.0: feature'

    """
    if app_version:
        return f"{app_name} {app_version}: {feature_name}"

    return f"{app_name}: {feature_name}"
