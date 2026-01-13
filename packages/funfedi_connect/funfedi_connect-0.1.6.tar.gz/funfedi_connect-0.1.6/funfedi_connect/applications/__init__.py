from funfedi_connect.applications.cattle_grid import CattleGridApplication
from .gancio import GancioApplication
from .webfinger_only import WebfingerOnlyApplication
from funfedi_connect.types import ApplicationConfiguration

from .misskey import MisskeyApplication
from .mastodon import MastodonApplication
from .mitra import MitraApplication
from .lemmy import LemmyApplication
from .pyfedi import PyFediApplication
from .friendica import FriendicaApplication

mastodon_like_apps = {
    name: MastodonApplication(name, user, application_name=name)
    for name, user in [
        ("akkoma", "witch"),
        ("gotosocial", "cookie"),
        ("hollo", "john"),
        ("mastodon", "hippo"),
        ("pleroma", "full"),
        ("sharkey", "willy"),
        ("snac2", "snack"),
    ]
}

name_to_application = {
    **mastodon_like_apps,
    "cattle_grid": CattleGridApplication("cattle-grid", "buttercup"),
    "friendica": FriendicaApplication("friendica", "friend"),
    "gancio": GancioApplication(
        "gancio",
        "relay",
    ),
    "lemmy": LemmyApplication("lemmy", "cliff"),
    "misskey": MisskeyApplication("misskey", "kitty"),
    "mitra": MitraApplication("mitra", "admin"),
    "mobilizon": WebfingerOnlyApplication(
        "mobilizon",
        "rose",
        application_name="mobilizon",
    ),
    "pyfedi": PyFediApplication("pyfedi.local", "pie", application_name="pyfedi"),
}


def application_for_name(name: str) -> ApplicationConfiguration:
    """For a given name returns the corresponding application configuration"""
    if name in name_to_application:
        return name_to_application[name]

    raise Exception("Unknown application")


def application_names_as_list() -> list[str]:
    """Returns the list of all implemented applications"""
    return sorted(list(name_to_application.keys()))
