from pathlib import Path
import click

from .types import ApplicationConfiguration

from .applications import application_for_name, application_names_as_list


@click.group
def main(): ...


def features_string_for_app(app: ApplicationConfiguration):
    return ", ".join(sorted([str(x) for x in app.features]))


@main.command()
@click.option("--for_docs", is_flag=True, default=False)
def list_applications(for_docs: bool):
    if for_docs:
        Path("snippets").mkdir(exist_ok=True)
        with open("snippets/applications.md", "w") as f:
            f.write("| name | acct-uri | features |\n")
            f.write("| --- | --- | --- |\n")
            for name in application_names_as_list():
                app = application_for_name(name)
                feature_string = features_string_for_app(app)
                f.write(f"| {name} | `{app.acct_uri}` | {feature_string} |\n")
        return

    for name in application_names_as_list():
        app = application_for_name(name)
        print(name + ", " + app.acct_uri)
        print("    " + features_string_for_app(app))


if __name__ == "__main__":
    main()
