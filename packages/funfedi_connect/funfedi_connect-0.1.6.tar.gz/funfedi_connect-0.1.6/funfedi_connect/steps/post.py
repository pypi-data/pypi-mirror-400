from behave_auto_docstring import when


@when("a message is posted from the application")
async def a_message_is_posted(context):
    poster = await context.fediverse_application.build_poster(context.session)

    object_uri = await poster(context.session, "Some message")

    if context.fix_https:
        object_uri = object_uri.replace("https://", "http://")

    assert object_uri.startswith("http://")

    context.object_uri = object_uri
