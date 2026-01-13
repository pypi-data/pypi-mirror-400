from dataclasses import dataclass

from funfedi_connect.types import (
    ApplicationConfiguration,
    ImplementedFeature,
)


@dataclass
class WebfingerOnlyApplication(ApplicationConfiguration):
    domain: str
    username: str
    application_name: str
    features = [ImplementedFeature.webfinger]
