import datetime
from behave_auto_docstring import when, then

from fediverse_pasture.send.modifier import ModifierBuilder
from fediverse_pasture.runner import ActivitySender
from fediverse_pasture.one_actor import bovine_actor_and_session

from funfedi_connect.testing.helpers import attach
from funfedi_connect.types import Attachments


@when('an event is send from "{domain}" to the application')
async def send_message_to_domain(context, domain):
    modifier = ModifierBuilder("text").build()
    uri = context.event_parsing.actor_id

    async with bovine_actor_and_session(f"http://{domain}") as (
        bovine_actor,
        actor,
        session,
    ):
        sender = ActivitySender.for_actor(bovine_actor, actor)
        sender.sending_config.include_mention = False
        sender.sending_config.include_cc = True
        sender.init_create_note(modifier)

        assert sender.note

        sender.note["type"] = "Event"
        sender.note["name"] = "my event"
        sender.note["startTime"] = (
            datetime.datetime.now() + datetime.timedelta(days=4)
        ).isoformat()
        sender.note["endTime"] = (
            datetime.datetime.now() + datetime.timedelta(days=4, hours=3)
        ).isoformat()
        sender.note["location"] = {"type": "VirtualLocation", "url": "http://localhost"}

        result = await sender.send(uri)
        if result is None:
            raise Exception("Failed to send message")

        activity = sender.activity
        if not isinstance(activity, dict):
            raise Exception("failed to send activity")

        attach(Attachments.send_activity, activity)

        context.send_object_id = activity.get("object", {}).get("id")


@then("the event exists")
async def an_event_exists(context):
    result = await context.event_parsing.object_getter(
        context.session, context.send_object_id
    )

    assert isinstance(result, dict)

    attach(Attachments.event_item, result)
