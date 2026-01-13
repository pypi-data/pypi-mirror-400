import traceback
from hestia_earth.schema import (
    NodeType,
    TermTermType,
    SiteSiteType,
    CycleFunctionalUnit,
)
from hestia_earth.utils.model import find_term_match, find_primary_product
from hestia_earth.utils.tools import non_empty_list, flatten

from hestia_earth.validation.log import logger
from hestia_earth.validation.utils import (
    _filter_list_errors,
    update_error_path,
    is_live_animal_cycle,
    get_lookup_value,
)
from hestia_earth.validation.distribution import is_enabled as distribution_is_enabled
from .shared import validate_country, CROP_SITE_TYPE

MUST_INCLUDE_ID_TERM_TYPES = [TermTermType.INORGANICFERTILISER.value]
FEED_TERM_TYPES = [
    TermTermType.ANIMALPRODUCT.value,
    TermTermType.CROP.value,
    TermTermType.FEEDFOODADDITIVE.value,
    TermTermType.FORAGE.value,
    TermTermType.LIVEAQUATICSPECIES.value,
    TermTermType.PROCESSEDFOOD.value,
    TermTermType.WASTE.value,
]
FEED_SITE_TYPE = [
    SiteSiteType.CROPLAND.value,
    SiteSiteType.PERMANENT_PASTURE.value,
    SiteSiteType.ANIMAL_HOUSING.value,
]


def validate_must_include_id(inputs: list):
    """
    Validate inorganic fertilisers nutrients

    Some fertilizers contain more than one nutrient. For example `Monoammonium Phosphate` has the formula (NH4)(H2PO4)
    and therefore contains both nitrogen (N) and phosphorus (P). If only `Monoammonium Phosphate (as N)` is added,
    HESTIA will underrepresent the amount of nutrients added.
    """

    def missingRequiredIds(term: dict):
        other_term_ids = (get_lookup_value(term, "complementaryTermIds") or "").split(
            ";"
        )
        return non_empty_list(
            [
                term_id
                for term_id in other_term_ids
                if find_term_match(inputs, term_id, None) is None
            ]
        )

    def validate(values: tuple):
        index, input = values
        term = input.get("term", {})
        should_validate = term.get("termType") in MUST_INCLUDE_ID_TERM_TYPES
        missing_ids = missingRequiredIds(term) if should_validate else []
        # added gap-filling which makes it non-required anymore
        return len(missing_ids) == 0 or {
            "level": "warning",
            "dataPath": f".inputs[{index}]",
            "message": "should add missing inputs",
            "params": {"expected": missing_ids},
        }

    return _filter_list_errors(map(validate, enumerate(inputs)))


def validate_input_country(node: dict, list_key: list = "inputs"):
    def validate(values: tuple):
        index, input = values
        country = input.get("country")
        error = country is None or validate_country(input)
        return error is True or update_error_path(error, list_key, index)

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))


def validate_related_impacts(node: dict, list_key: list, node_map: dict = {}):
    """
    Validation Cycle of related Impact Assessment is not the Cycle itself

    This validation ensures that no loop is being created, such as `Cycle` -> `ImpactAssessment` -> `Cycle`,
    e.g., that it is not possible to link a Cycle back to itself through the `inputs.impactAssessment` field.
    """
    related_impacts = node_map.get(NodeType.IMPACTASSESSMENT.value)

    def validate(values: tuple):
        index, input = values
        impact_id = input.get("impactAssessment", {}).get("id")
        impact = related_impacts.get(impact_id) if impact_id else None
        related_node_id = (
            impact.get(node.get("type").lower(), {}).get("id") if impact else None
        )
        return (
            related_node_id is None
            or related_node_id != node.get("id")
            or {
                "level": "error",
                "dataPath": f".inputs[{index}].impactAssessment",
                "message": "can not be linked to the same type",
                "params": {"current": node.get("type")},
            }
        )

    return (
        _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))
        if related_impacts
        else True
    )


def _validate_input_value(cycle: dict, country: dict, list_key: str, threshold: float):
    from hestia_earth.distribution.utils.cycle import (
        group_cycle_inputs,
        get_input_group,
    )
    from .distribution import (
        get_stats_by_group_key,
        cycle_completeness_key,
        validate as validate_distribution,
    )

    groups = group_cycle_inputs(cycle)
    completeness = cycle.get("completeness", {})
    country_id = country.get("@id")
    product = find_primary_product(cycle) or {}
    product_id = product.get("term", {}).get("@id")

    def validate(values: tuple):
        index, input = values

        input_id = input.get("term", {}).get("@id")
        group_key = get_input_group(input)
        input_value = groups.get(group_key)

        def _get_mu_sd():
            return get_stats_by_group_key(group_key, country_id, product_id, input_id)

        complete = completeness.get(cycle_completeness_key(group_key), False)
        valid, outliers, min, max = (
            validate_distribution([input_value], threshold, get_mu_sd=_get_mu_sd)
            if complete
            else (True, None, None, None)
        )

        return valid or {
            "level": "warning",
            "dataPath": f".{list_key}[{index}].value",
            "message": "is outside confidence interval",
            "params": {
                "term": input.get("term", {}),
                "group": group_key,
                "country": country,
                "outliers": outliers,
                "threshold": threshold,
                "min": min,
                "max": max,
            },
        }

    return validate


def validate_input_distribution_value(
    cycle: dict, site: dict, list_key: str = "inputs", threshold: float = 0.95
):
    try:
        country = site.get("country", {})
        inputs = cycle.get(list_key, [])
        validate_input = (
            _validate_input_value(cycle, country, list_key, threshold)
            if distribution_is_enabled()
            else None
        )
        return (
            (
                site.get("siteType") not in CROP_SITE_TYPE
                or _filter_list_errors(map(validate_input, enumerate(inputs)))
            )
            if distribution_is_enabled()
            else True
        )
    except Exception:
        stack = traceback.format_exc()
        logger.error(f"Error validating using distribution: '{stack}'")
        return True


def validate_animalFeed_requires_isAnimalFeed(cycle: dict, site: dict):
    """
    Validate `isAnimalFeed`

    This validation returns an error when:
    - the `siteType` is `cropland`, `permanent pasture`, or `animal housing`;
    - the primary product is an animal;
    - some of the Cycle or animal inputs do not have `isAnimalFeed` set.

    To fix this error, please set `isAnimalFeed` on all relevant inputs.
    """

    site_type = site.get("siteType")
    is_liveAnimal = is_live_animal_cycle(cycle)

    def validate(values: tuple):
        index, input = values
        term_type = input.get("term", {}).get("termType")
        return (
            term_type not in FEED_TERM_TYPES
            or input.get("isAnimalFeed") is not None
            or {
                "level": "error",
                "dataPath": f".inputs[{index}]",
                "message": "must specify is it an animal feed",
            }
        )

    def validate_animal(values: tuple):
        index, blank_node = values
        errors = list(map(validate, enumerate(blank_node.get("inputs", []))))
        return _filter_list_errors(
            [
                update_error_path(error, "animals", index)
                for error in errors
                if error is not True
            ]
        )

    return (
        site_type not in FEED_SITE_TYPE
        or not is_liveAnimal
        or _filter_list_errors(
            flatten(
                list(map(validate, enumerate(cycle.get("inputs", []))))
                + [list(map(validate_animal, enumerate(cycle.get("animals", []))))]
            )
        )
    )


def validate_saplings(cycle: dict, list_key: str = "inputs"):
    """
    Validate `saplings`

    This validation will force using the input `saplingsDepreciatedAmountPerCycle` when:
    - the Cycle `functionalUnit` is equal to `1 ha`;
    - and the primary Product termType is `Crop`;
    - and the lookup `is_Plantation` is `TRUE` for the `Crop`;
    - and there is a `Saplings` input.
    """
    functional_unit = cycle.get("functionalUnit")
    product = (find_primary_product(cycle) or {}).get("term", {})
    product_term_type = product.get("termType")
    product_is_plantation = not not get_lookup_value(product, "isPlantation")

    term_id = "saplings"
    inputs = cycle.get(list_key, [])
    saplings_indexes = [
        i for i in range(len(inputs)) if inputs[i].get("term", {}).get("@id") == term_id
    ]

    return (
        functional_unit != CycleFunctionalUnit._1_HA.value
        or product_term_type != TermTermType.CROP.value
        or not product_is_plantation
        or len(saplings_indexes) == 0
        or _filter_list_errors(
            [
                {
                    "level": "error",
                    "dataPath": f".{list_key}[{index}].term",
                    "message": "saplings cannot be used as an input here",
                    "params": {
                        "current": term_id,
                        "expected": "saplingsDepreciatedAmountPerCycle",
                    },
                }
            ]
            for index in saplings_indexes
        )
    )


def validate_input_is_product(node: dict, list_key: str = "inputs"):
    """
    Validate input must be used a a product

    Some Terms can only be used a Product. When any of these terms are used as Input, an error will be given.
    """

    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get("term", {})
        must_be_product = get_lookup_value(term, "mustBeProduct")
        return not must_be_product or {
            "level": "error",
            "dataPath": f".{list_key}[{index}].term",
            "message": "must be a product",
            "params": {"term": term},
        }

    return _filter_list_errors(map(validate, enumerate(node.get(list_key, []))))
