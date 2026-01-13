import csv
import pytest
import requests
from . import application_names_as_list, application_for_name


@pytest.mark.parametrize("name", application_names_as_list())
def test_application(name):
    result = application_for_name(name)

    assert result.acct_uri.startswith("acct")


@pytest.mark.parametrize("name", application_names_as_list())
def test_application_name(name):
    result = application_for_name(name)

    assert result.application_name == name


def test_implemented_containers():
    csv_data = requests.get("https://containers.funfedi.dev/assets/latest_versions.csv")
    lines = csv_data.text.split("\n")
    data = csv.DictReader(lines[1:], fieldnames=lines[0].split(","))
    applications = [x["application"] for x in data]

    containers = set(applications)

    implemented_containers = set(application_names_as_list())
    unimplemented_containers = containers - implemented_containers

    missing_containers = {"mbin"}

    assert unimplemented_containers == missing_containers


def test_applications_as_list():
    result = application_names_as_list()

    assert isinstance(result, list)
