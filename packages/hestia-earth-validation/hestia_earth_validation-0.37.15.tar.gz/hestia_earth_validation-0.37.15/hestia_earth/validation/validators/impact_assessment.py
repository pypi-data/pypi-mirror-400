"""
Impact Assessment validation

Here is the list of validations running on a [Impact Assessment](/schema/ImpactAssessment).
"""

from hestia_earth.utils.tools import flatten

from hestia_earth.validation.utils import (
    find_linked_node,
    find_by_product,
    find_by_unique_product,
)
from .shared import (
    validate_list_min_below_max,
    validate_country_region,
    validate_list_country_region,
    validate_list_term_percent,
    validate_linked_source_privacy,
    validate_date_lt_today,
    validate_list_model,
    validate_private_has_source,
    validate_list_value_between_min_max,
    is_date_equal,
    validate_other_model,
    validate_nested_existing_node,
)
from .emission import validate_methodTier_background
from .indicator import (
    validate_characterisedIndicator_model,
    validate_landTransformation,
    validate_inonising_compounds_waste,
)


def validate_empty(impact_assessment: dict):
    """
    Validate the Impact Assesment is not empty

    Adding an Impact Assessment without a Cycle, and no `emissionsResourceUse` or `impacts` or `endpoints`,
    is not allowed. You must set at least one of these fields, as otherwise the Impact Assessment will remain empty.
    """
    return any(
        [
            impact_assessment.get("cycle"),
            impact_assessment.get("emissionsResourceUse", []),
            len(impact_assessment.get("impacts", [])) > 0,
            len(impact_assessment.get("endpoints", [])) > 0,
        ]
    ) or {
        "level": "error",
        "dataPath": "",
        "message": "should not be empty",
        "params": {"type": "ImpactAssessment"},
    }


def validate_linked_cycle_product(impact_assessment: dict, cycle: dict):
    """
    Validate the product exist in the linked Cycle

    When linking an Impact Assessment with a Cycle, the `product` must refer to a `Product` of the Cycle.
    Plase make sure to set the exact same field on both the Impact Assessment and Cycle product.
    """
    product = impact_assessment.get("product", {})
    cycle_product = find_by_product(cycle, product) or find_by_unique_product(
        cycle, product
    )
    return cycle_product is not None or {
        "level": "error",
        "dataPath": ".product",
        "message": "should be included in the cycle products",
        "params": {
            "product": product.get("term", {}),
            "node": {"type": "Cycle", "id": cycle.get("id", cycle.get("@id"))},
        },
    }


def validate_linked_cycle_endDate(impact_assessment: dict, cycle: dict):
    """
    Validate `endDate`

    This validation will ensure the Impact Assessment `endDate` is the same as the linked Cycle, when provided.
    """
    key = "endDate"
    return is_date_equal(impact_assessment.get(key), cycle.get(key), True) or {
        "level": "error",
        "dataPath": f".{key}",
        "message": "must be equal to the Cycle endDate",
    }


def validate_impact_assessment(impact_assessment: dict, node_map: dict = {}):
    cycle = find_linked_node(node_map, impact_assessment.get("cycle", {}))
    return [
        validate_empty(impact_assessment),
        validate_date_lt_today(impact_assessment, "startDate"),
        validate_date_lt_today(impact_assessment, "endDate"),
        validate_linked_source_privacy(impact_assessment, "source", node_map),
        validate_private_has_source(impact_assessment, "source"),
        validate_country_region(impact_assessment),
        validate_linked_cycle_product(impact_assessment, cycle) if cycle else True,
        validate_linked_cycle_endDate(impact_assessment, cycle) if cycle else True,
        validate_nested_existing_node(impact_assessment, "cycle"),
        validate_nested_existing_node(impact_assessment, "site"),
    ] + flatten(
        (
            [
                validate_list_country_region(impact_assessment, "emissionsResourceUse"),
                validate_list_min_below_max(impact_assessment, "emissionsResourceUse"),
                validate_list_value_between_min_max(
                    impact_assessment, "emissionsResourceUse"
                ),
                validate_list_term_percent(impact_assessment, "emissionsResourceUse"),
                validate_characterisedIndicator_model(
                    impact_assessment, "emissionsResourceUse"
                ),
                validate_landTransformation(impact_assessment, "emissionsResourceUse"),
                validate_methodTier_background(
                    impact_assessment, "emissionsResourceUse"
                ),
                validate_other_model(impact_assessment, "emissionsResourceUse"),
                validate_inonising_compounds_waste(
                    impact_assessment, "emissionsResourceUse"
                ),
            ]
            if len(impact_assessment.get("emissionsResourceUse", [])) > 0
            else []
        )
        + (
            [
                validate_list_country_region(impact_assessment, "emissionsResourceUse"),
                validate_list_min_below_max(impact_assessment, "impacts"),
                validate_list_value_between_min_max(impact_assessment, "impacts"),
                validate_list_term_percent(impact_assessment, "impacts"),
                validate_list_model(impact_assessment, "impacts"),
                validate_characterisedIndicator_model(impact_assessment, "impacts"),
                validate_other_model(impact_assessment, "emissionsResourceUse"),
            ]
            if len(impact_assessment.get("impacts", [])) > 0
            else []
        )
        + (
            [
                validate_list_country_region(impact_assessment, "emissionsResourceUse"),
                validate_list_min_below_max(impact_assessment, "endpoints"),
                validate_list_value_between_min_max(impact_assessment, "endpoints"),
                validate_list_term_percent(impact_assessment, "endpoints"),
                validate_other_model(impact_assessment, "emissionsResourceUse"),
            ]
            if len(impact_assessment.get("endpoints", [])) > 0
            else []
        )
    )
