import json

from behave_auto_docstring import when, then
import jsonschema

from funfedi_connect.testing.helpers import attach
from funfedi_connect.types import Attachments


@when('Webfinger is queried as "{response_name}" for the acct-uri of the application')
async def webfinger_is_queried(context, response_name):
    acct_uri = context.fediverse_application.acct_uri
    domain = context.fediverse_application.domain
    webfinger_uri = f"http://{domain}/.well-known/webfinger?resource={acct_uri}"
    context.responses[response_name] = await context.session.get(webfinger_uri)


@then('the request "{response_name}" has status code "{status_code}"')
def check_status_code(context, response_name, status_code):
    response = context.responses[response_name]

    assert response.status == int(status_code), f"Got status code {response.status}"


@then('the response "{response_name}" has content-type "{content_type}"')
def check_content_type(context, response_name, content_type):
    response = context.responses[response_name]
    response_content_type = response.headers["content-type"]

    assert response_content_type.startswith(content_type), (
        f"Got content type {response_content_type}"
    )


@then('the response "{response_name}" satisfies "{schema_url}"')
async def response_check_schema(context, response_name, schema_url):
    schema_response = await context.session.get(
        schema_url, headers={"accept": "application/json"}
    )
    schema = json.loads(await schema_response.text())
    response = context.responses[response_name]
    response_data = await response.json()

    attach(Attachments.webfinger_response, response_data)

    jsonschema.validate(response_data, schema)


@when("the actor uri is determined")
async def specify_actor(context):
    context.object_uri = await context.fediverse_application._determine_actor_uri(
        context.session
    )
