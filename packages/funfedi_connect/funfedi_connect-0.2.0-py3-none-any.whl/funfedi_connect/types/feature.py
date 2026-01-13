from enum import StrEnum, auto


class ImplementedFeature(StrEnum):
    """Available implemented features"""

    webfinger = auto()
    public_timeline = auto()
    post = auto()
    event = auto()

    @staticmethod
    def from_tag(tag: str):
        """
        ```
        >>> ImplementedFeature.from_tag("public-timeline")
        <ImplementedFeature.public_timeline: 'public_timeline'>

        ```
        """
        tag = tag.replace("-", "_")

        return ImplementedFeature(tag)

    @property
    def behave_tag(self):
        """Returns as the tag used in behave, e.g.

        ```
        >>> ImplementedFeature.public_timeline.behave_tag
        'public-timeline'

        ```
        """
        return self.value.replace("_", "-")


def to_features(tags: list[str]):
    """
    ```
    >>> to_features(["wip", "webfinger"])
    [<ImplementedFeature.webfinger: 'webfinger'>]

    ```
    """

    result = []
    for tag in tags:
        try:
            result.append(ImplementedFeature.from_tag(tag))
        except Exception:
            ...

    return result
