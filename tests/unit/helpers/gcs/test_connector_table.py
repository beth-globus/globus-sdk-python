from __future__ import annotations

import inspect
import sys
import uuid

import pytest

from globus_sdk import ConnectorTable, GCSClient, GlobusConnectServerConnector, exc


def test_deprecated_connector_lookup_method_warns():
    client = GCSClient("foo.bar.example.org")
    with pytest.warns(exc.RemovedInV4Warning):
        assert client.connector_id_to_name("foo") is None


@pytest.mark.parametrize("connector_data", ConnectorTable._connectors)
def test_lookup_by_attribute(connector_data):
    attrname, connector_name, _ = connector_data

    connector = getattr(ConnectorTable, attrname)
    assert connector.name == connector_name


@pytest.mark.parametrize("connector_data", ConnectorTable._connectors)
@pytest.mark.parametrize("as_uuid", (True, False))
def test_lookup_by_id(connector_data, as_uuid):
    _, connector_name, connector_id = connector_data

    if as_uuid:
        connector_id = uuid.UUID(connector_id)

    connector = ConnectorTable.lookup_by_id(connector_id)
    assert connector.name == connector_name


@pytest.mark.parametrize("connector_data", ConnectorTable._connectors)
def test_lookup_by_name(connector_data):
    _, connector_name, connector_id = connector_data

    connector = ConnectorTable.lookup(connector_name)
    assert connector.connector_id == connector_id


@pytest.mark.parametrize(
    "lookup_name, expect_name",
    (
        ("Google Drive", "Google Drive"),
        ("google drive", "Google Drive"),
        ("google_drive", "Google Drive"),
        ("google-drive", "Google Drive"),
        ("google-----drive", "Google Drive"),
        ("google-_-drive", "Google Drive"),  # moody
        ("  google_-drIVE", "Google Drive"),
        ("google_-drIVE    ", "Google Drive"),
        ("   GOOGLE DRIVE    ", "Google Drive"),
    ),
)
def test_lookup_by_name_normalization(lookup_name, expect_name):
    connector = ConnectorTable.lookup(lookup_name)
    assert connector.name == expect_name


@pytest.mark.parametrize("name", [c.name for c in ConnectorTable.all_connectors()])
def test_all_connector_names_map_to_attributes(name):
    connector = ConnectorTable.lookup(name)
    assert connector is not None
    name = name.replace(" ", "_").upper()
    assert getattr(ConnectorTable, name) == connector


@pytest.mark.skipif(
    sys.version_info < (3, 10), reason="inspect.get_annotations added in 3.10"
)
def test_all_connector_attributes_are_assigned():
    # build a list of attribute names annotated with
    # `t.ClassVar[GlobusConnectServerConnector]`
    annotated_attributes = []
    for attribute, annotation in inspect.get_annotations(ConnectorTable).items():
        # get_annotations does not interpret string-ized annotations by default, so we
        # receive the relevant values as strings, making comparison simple
        if annotation != "t.ClassVar[GlobusConnectServerConnector]":
            continue
        annotated_attributes.append(attribute)

    # confirm that we got the right number of annotated items
    assert len(annotated_attributes) == len(ConnectorTable._connectors)
    # now confirm that all of these are assigned values
    for attribute in annotated_attributes:
        instance = getattr(ConnectorTable, attribute)
        assert isinstance(instance, GlobusConnectServerConnector)
