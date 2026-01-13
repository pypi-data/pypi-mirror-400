from unittest.mock import patch

from funfedi_connect.types import Attachments
from .helpers import attach


def test_attach():
    with patch("allure.attach") as mock:
        attach(Attachments.actor_object, {})

        mock.assert_called_once_with(
            "{}",
            name="actor_object",
            attachment_type="application/json",
            extension="json",
        )
