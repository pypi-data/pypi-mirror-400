from behave_auto_docstring import given

from funfedi_connect.testing.helpers import attach, get_app_name, get_app_version
from funfedi_connect.types import Attachments
from funfedi_connect.version import __version__


@given("A Fediverse application")
def a_fediverse_application(context):
    assert context.fediverse_application
    attach(
        Attachments.meta_data,
        {
            "funfedi_connect_version": __version__,
            "app_version": get_app_version(),
            "app_name": get_app_name(),
        },
    )


@given("the object parsing is build")
async def build_object_parsing(context):
    context.object_parsing = await context.fediverse_application.build_object_parsing(
        context.session
    )
    assert context.object_parsing


@given("the event parsing is build")
async def event_parsing(context):
    context.event_parsing = await context.fediverse_application.build_event_parsing(
        context.session
    )
    assert context.event_parsing
