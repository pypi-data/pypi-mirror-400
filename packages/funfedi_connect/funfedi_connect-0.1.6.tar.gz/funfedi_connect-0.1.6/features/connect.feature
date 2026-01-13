Feature: Funfedi Connect support

    Background:
        Given A Fediverse application

    @webfinger
    Scenario: The webfinger response is ok
        When Webfinger is queried as "webfinger_response" for the acct-uri of the application
        Then the request "webfinger_response" has status code "200"
        And the response "webfinger_response" has content-type "application/jrd+json"
        And the response "webfinger_response" satisfies "https://schemas.funfedi.dev/assets/application-jrd-json.schema.json"

    @public-timeline
    Scenario: Can fetch public timeline
        Given the object parsing is build
        When a message is send from "pasture-one-actor" to the application
        Then the public timeline contains the message

    @fix-https:sharkey
    @post
    Scenario: Can post
        When a message is posted from the application
        Then "pasture-one-actor" can read it as "created_object"

    @webfinger
    Scenario: Actor
        When the actor uri is determined
        Then "pasture-one-actor" can read it as "actor_object"

    @event
    Scenario: Can create an event
        Given the event parsing is build
        When an event is send from "pasture-one-actor" to the application
        Then the event exists
