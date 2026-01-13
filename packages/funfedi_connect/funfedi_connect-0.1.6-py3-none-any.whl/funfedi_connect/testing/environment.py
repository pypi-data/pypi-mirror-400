import logging

from bovine.testing.features import (
    before_all,  # noqa: F401
    before_scenario as bovine_before_scenario,
    after_scenario,  # noqa: F401
)  # noqa: F401

from funfedi_connect.applications import application_for_name
from funfedi_connect.types.feature import to_features

from .helpers import get_app_name, get_app_version, make_feature_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def before_feature(context, feature):
    app_name = get_app_name()
    app_version = get_app_version()
    feature.name = make_feature_name(feature.name, app_name, app_version)
    feature.name = f"{app_name}: {feature.name}"
    context.fediverse_application = application_for_name(app_name)


def before_scenario(context, scenario):
    features = to_features(scenario.tags)
    app_features = context.fediverse_application.features

    for feature in features:
        if feature not in app_features:
            raise Exception("Should be skipped")
            # context.abort()

    if f"fix-https:{get_app_name()}" in scenario.tags:
        context.fix_https = True
    else:
        context.fix_https = False

    bovine_before_scenario(context, scenario)
