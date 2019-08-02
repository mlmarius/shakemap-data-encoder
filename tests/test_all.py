import json
import pytest
import xml.etree.cElementTree as ET

import shakemap_data_encoder as sde

@pytest.fixture
def data():
    with open('./data/gm_1416683657.json') as f:
        return json.load(f)


def test_event_xml(caplog, data):
    xmlstring = sde.get_event_xml(data)
    elem = ET.fromstring(xmlstring)
    assert elem.attrib['depth'] == "40.9"
    assert elem.attrib['lat'] == "45.8683"
    assert elem.attrib['lon'] == "27.1517"


def test_get_ci_xml(caplog, data):
    xmlstring = sde.get_ci_xml(data)
    assert xmlstring == ''
