from behave_auto_docstring import when, then

from fediverse_pasture.send.modifier import ModifierBuilder
from fediverse_pasture.runner import ActivitySender
from fediverse_pasture.one_actor import bovine_actor_and_session

from funfedi_connect.testing.helpers import attach
from funfedi_connect.types import Attachments


@when('a message is send from "{domain}" to the application')
async def send_message_to_domain(context, domain):
    modifier = ModifierBuilder("text").build()
    uri = context.object_parsing.actor_id

    async with bovine_actor_and_session(f"http://{domain}") as (
        bovine_actor,
        actor,
        session,
    ):
        sender = ActivitySender.for_actor(bovine_actor, actor)
        sender.sending_config.include_mention = True
        sender.sending_config.include_cc = True
        sender.init_create_note(modifier)

        result = await sender.send(uri)
        if result is None:
            raise Exception("Failed to send message")

        activity = sender.activity
        if not isinstance(activity, dict):
            raise Exception("failed to send activity")

        attach(Attachments.send_activity, activity)

        context.send_object_id = activity.get("object", {}).get("id")


@then("the public timeline contains the message")
async def public_timeline_contains_message(context):
    result = await context.object_parsing.object_getter(
        context.session, context.send_object_id
    )

    assert result

    attach(Attachments.timeline_item, result)
