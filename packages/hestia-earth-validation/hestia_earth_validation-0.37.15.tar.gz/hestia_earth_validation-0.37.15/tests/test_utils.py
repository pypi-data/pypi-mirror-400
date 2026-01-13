import pytest

from hestia_earth.validation.utils import match_value_type, _group_nodes


@pytest.mark.parametrize(
    "value,value_type,is_valid",
    [
        (10, "number", True),
        (True, "number", False),
        ([10, 20], "number", True),
        ([10, True], "number", False),
        ([True, False], "boolean", True),
        (True, "boolean", True),
        ([10, 20], "boolean", False),
    ],
)
def test_match_value_type(value, value_type: str, is_valid: bool):
    assert match_value_type(value_type, value) == is_valid, value


def test_group_nodes():
    site1 = {"@type": "Site", "@id": "1"}
    site2 = {"@type": "Site", "@id": "2"}
    site3 = {"@type": "Site", "@id": "3"}
    site4 = {"@type": "Site", "@id": "4"}
    cycle1 = {"@type": "Cycle", "@id": "1"}
    cycle2 = {"@type": "Cycle", "@id": "2", "site": site2}
    cycle3 = {"@type": "Cycle", "@id": "3", "otherSites": [site4]}
    impact1 = {"@type": "ImpactAssessment", "@id": "1", "cycle": cycle1, "site": site1}
    nodes = [impact1, cycle2, cycle3, site3]
    assert _group_nodes(nodes) == {
        "ImpactAssessment": {"1": impact1},
        "Cycle": {"1": cycle1, "2": cycle2, "3": cycle3},
        "Site": {"1": site1, "2": site2, "3": site3, "4": site4},
    }
