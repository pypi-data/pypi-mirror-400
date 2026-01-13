from fediverse_pasture.one_actor import bovine_actor_and_session

from behave_auto_docstring import then

from funfedi_connect.types import Attachments
from funfedi_connect.testing.helpers import attach


@then('"{domain}" can read it as "{attachment_name}"')
async def can_read_attachment(context, domain, attachment_name):
    attachment = Attachments(attachment_name)
    async with bovine_actor_and_session(f"http://{domain}") as (
        bovine_actor,
        actor,
        session,
    ):
        result = await bovine_actor.get(context.object_uri)

        assert result
        attach(attachment, result)

        assert result.get("id") == context.object_uri
