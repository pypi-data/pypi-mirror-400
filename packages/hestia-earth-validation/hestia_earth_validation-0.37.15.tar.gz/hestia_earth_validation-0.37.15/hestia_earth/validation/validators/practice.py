from hestia_earth.schema import SiteSiteType, TermTermType
from hestia_earth.utils.model import (
    filter_list_term_type,
    find_term_match,
    find_primary_product,
)
from hestia_earth.utils.tools import flatten, list_sum, safe_parse_float, non_empty_list
from hestia_earth.utils.lookup import download_lookup, get_table_value
from hestia_earth.utils.blank_node import get_node_value

from hestia_earth.validation.utils import (
    _filter_list_errors,
    get_lookup_value,
    is_permanent_crop,
    blank_node_properties_group,
)
from hestia_earth.validation.terms import TERMS_QUERY, get_terms
from .shared import valid_list_sum, is_value_below


def _is_irrigated(term: dict):
    def fallback():
        term_id = get_lookup_value(term, "correspondingWaterRegimeTermId")
        return (
            _is_irrigated({"@id": term_id, "termType": TermTermType.WATERREGIME.value})
            if term_id
            else False
        )

    return not not get_lookup_value(term, "irrigated") or fallback()


def validate_defaultValue(data: dict, list_key: str = "practices"):
    def validate(values: tuple):
        index, practice = values
        term = practice.get("term", {})
        has_value = len(practice.get("value", [])) > 0
        is_value_required = any([term.get("units", "").startswith("%")])
        default_value = get_lookup_value(term, "defaultValue")
        return (
            has_value
            or default_value is None
            or is_value_required
            or {
                "level": "warning",
                "dataPath": f".{list_key}[{index}]",
                "message": "should specify a value when HESTIA has a default one",
                "params": {"term": term, "expected": default_value},
            }
        )

    return _filter_list_errors(
        flatten(map(validate, enumerate(data.get(list_key, []))))
    )


def validate_longFallowDuration(practices: list):
    """
    Validate `longFallowDuration` value

    This validation ensures the `longFallowDuration` value is not longer than 5 years.
    """
    max_nb_years = 5
    longFallowDuration = find_term_match(practices, "longFallowDuration", None)
    longFallowDuration_index = (
        practices.index(longFallowDuration) if longFallowDuration else 0
    )
    value = list_sum(longFallowDuration.get("value", [0])) if longFallowDuration else 0
    rotationDuration = list_sum(
        find_term_match(practices, "rotationDuration").get("value", 0)
    )
    return (
        value == 0
        or ((rotationDuration - value) / value) < max_nb_years * 365
        or {
            "level": "error",
            "dataPath": f".practices[{longFallowDuration_index}].value",
            "message": "longFallowDuration must be lower than 5 years",
        }
    )


def validate_waterRegime_rice_products(cycle: dict, list_key: str = "practices"):
    """
    Validate corresponding `waterRegime` practices with Rice products

    This validation ensures that the correct `waterRegime` practice can be used with the specified Rice product.
    """
    all_rice_product_ids = get_terms(TERMS_QUERY.RICE)
    primary_product = find_primary_product(cycle) or {}
    primary_product_id = primary_product.get("term", {}).get("@id")
    is_rice_product = primary_product_id in all_rice_product_ids

    practice_term_type = TermTermType.WATERREGIME.value

    def validate(values: tuple):
        index, practice = values
        term = practice.get("term", {})
        term_type = term.get("termType")
        has_value = list_sum(practice.get("value") or [0], 0) > 0
        allowed_product_ids = (
            get_lookup_value(term, "allowedRiceTermIds") or ""
        ).split(";")
        is_allowed = primary_product_id in allowed_product_ids
        return (
            term_type != practice_term_type
            or not has_value
            or is_allowed
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}].term",
                "message": "rice products not allowed for this water regime practice",
                "params": {
                    "term": term,
                    "products": [primary_product.get("term", {})],
                    "expected": allowed_product_ids,
                },
            }
        )

    return not is_rice_product or _filter_list_errors(
        flatten(map(validate, enumerate(cycle.get(list_key, []))))
    )


def validate_croppingDuration_riceGrainInHuskFlooded(
    cycle: dict, list_key: str = "practices"
):
    """
    Validate "Rice, grain (in husk), flooded" cropping duration

    When "Rice, grain (in husk), flooded" is used as a product, this validation will check the practice
    `croppingDuration`, and make sure the value is between
    `Rice_croppingDuration_days_min` and `Rice_croppingDuration_days_max` lookup values.
    """
    has_product = find_term_match(cycle.get("products", []), "riceGrainInHuskFlooded")

    practice_id = "croppingDuration"
    practice_index = (
        next(
            (
                i
                for i, p in enumerate(cycle.get(list_key, []))
                if p.get("term", {}).get("@id") == practice_id
            ),
            -1,
        )
        if has_product
        else -1
    )

    lookup = download_lookup("region-ch4ef-IPCC2019.csv")
    country_id = cycle.get("site", {}).get("country", {}).get("@id")
    min_value = safe_parse_float(
        get_table_value(
            lookup, "term.id", country_id, "Rice_croppingDuration_days_min"
        ),
        None,
    )
    max_value = safe_parse_float(
        get_table_value(
            lookup, "term.id", country_id, "Rice_croppingDuration_days_max"
        ),
        None,
    )

    value = (
        list_sum(cycle.get(list_key, [])[practice_index].get("value", []))
        if practice_index >= 0
        else None
    )

    return (
        practice_index == -1
        or all([is_value_below(value, max_value), is_value_below(min_value, value)])
        or {
            "level": "error",
            "dataPath": f".{list_key}[{practice_index}].value",
            "message": "croppingDuration must be between min and max",
            "params": {"min": min_value, "max": max_value},
        }
    )


def validate_excretaManagement(node: dict, practices: list):
    """
    Validate excreta management and input

    If there is a Practice of termType = excretaManagement, there must be an Input of termType = excreta.
    """
    has_input = (
        len(filter_list_term_type(node.get("inputs", []), TermTermType.EXCRETA)) > 0
    )
    has_practice = (
        len(filter_list_term_type(practices, TermTermType.EXCRETAMANAGEMENT)) > 0
    )
    return (
        not has_practice
        or has_input
        or {
            "level": "error",
            "dataPath": ".practices",
            "message": "an excreta input is required when using an excretaManagement practice",
        }
    )


NO_TILLAGE_ID = "noTillage"
FULL_TILLAGE_ID = "fullTillage"
TILLAGE_DEPTH_ID = "tillageDepth"
NB_TILLAGES_ID = "numberOfTillages"


def _practice_is_tillage(practice: dict):
    term = practice.get("term", {})
    term_type = practice.get("term", {}).get("termType")
    return (
        True
        if term_type == TermTermType.OPERATION.value
        and get_lookup_value(term, "isTillage")
        else False
    )


def validate_no_tillage(practices: list):
    """
    Validate using `noTillage`

    Some practices require tillage, and adding the practice `noTillage` is not allowed.
    """
    tillage_practices = filter_list_term_type(practices, TermTermType.TILLAGE)
    no_tillage = find_term_match(tillage_practices, NO_TILLAGE_ID, None)
    no_value = list_sum(no_tillage.get("value", [100]), 100) if no_tillage else 0

    return _filter_list_errors(
        [
            {
                "level": "error",
                "dataPath": f".practices[{index}]",
                "message": "is not allowed in combination with noTillage",
            }
            for index, p in enumerate(practices)
            if _practice_is_tillage(p)
        ]
        if no_value == 100
        else []
    )


_TILLAGE_SITE_TYPES = [SiteSiteType.CROPLAND.value]


def validate_tillage_site_type(practices: list, site: dict):
    """
    Validate set tillage on cropland

    For cropland, it is preferable to set the tillage type.
    """
    has_tillage = len(filter_list_term_type(practices, TermTermType.TILLAGE)) > 0
    site_type = site.get("siteType")
    return (
        site_type not in _TILLAGE_SITE_TYPES
        or has_tillage
        or {
            "level": "warning",
            "dataPath": ".practices",
            "message": "should contain a tillage practice",
        }
    )


def validate_tillage_values(practices: list):
    """
    Validate tillage values

    Validate these 2 cases:
    - if `noTillage` is set, the number of tillages must be `0`;
    - if `fullTillage` is set, the number of tillages can not be `0`.

    To fix this error, you either need to change the tillage, or add the correct number of tillages.
    """
    tillage_100_index = next(
        (
            index
            for index in range(0, len(practices))
            if all(
                [
                    practices[index].get("term", {}).get("termType")
                    == TermTermType.TILLAGE.value,
                    list_sum(practices[index].get("value", [0])) == 100,
                ]
            )
        ),
        -1,
    )
    tillage_100_practice = (
        practices[tillage_100_index] if tillage_100_index >= 0 else None
    )
    tillage_100_term = (tillage_100_practice or {}).get("term", {})

    tillage_depth_practice = find_term_match(practices, TILLAGE_DEPTH_ID)
    nb_tillages_practice = find_term_match(practices, NB_TILLAGES_ID)
    return (
        (
            {
                "level": "error",
                "dataPath": f".practices[{tillage_100_index}]",
                "message": "cannot use no tillage if depth or number of tillages is not 0",
            }
            if all(
                [
                    tillage_100_term.get("@id") == NO_TILLAGE_ID,
                    any(
                        [
                            tillage_depth_practice
                            and list_sum(tillage_depth_practice.get("value", [0])) > 0,
                            nb_tillages_practice
                            and list_sum(nb_tillages_practice.get("value", [0])) > 0,
                        ]
                    ),
                ]
            )
            else (
                {
                    "level": "error",
                    "dataPath": f".practices[{tillage_100_index}]",
                    "message": "cannot use full tillage if depth or number of tillages is 0",
                }
                if all(
                    [
                        tillage_100_term.get("@id") == FULL_TILLAGE_ID,
                        any(
                            [
                                tillage_depth_practice
                                and list_sum(tillage_depth_practice.get("value", [1]))
                                == 0,
                                nb_tillages_practice
                                and list_sum(nb_tillages_practice.get("value", [1]))
                                == 0,
                            ]
                        ),
                    ]
                )
                else True
            )
        )
        if tillage_100_practice
        else True
    )


def validate_liveAnimal_system(cycle: dict, site: dict):
    """
    Validate animal production has a `system` practice

    For animal production Cycles, it is recommended to add a `system` Practice. We are using the lookup
    `recommendedSystemTermIds` to determine which Practice should be set, according to the primary Product.
    """
    site_type = site.get("siteType")
    primary_product = find_primary_product(cycle) or {}
    recommended_practice_ids = (
        get_lookup_value(primary_product.get("term"), "recommendedSystemTermIds") or ""
    ).split(";")
    has_practice = any(
        [
            find_term_match(cycle.get("practices", []), term_id, False)
            for term_id in recommended_practice_ids
        ]
    )
    return (
        site_type
        not in [
            SiteSiteType.PERMANENT_PASTURE.value,
            SiteSiteType.ANIMAL_HOUSING.value,
        ]
        or not recommended_practice_ids
        or has_practice
        or {
            "level": "warning",
            "dataPath": ".practices",
            "message": "should add an animal production system",
            "params": {"expected": recommended_practice_ids},
        }
    )


PASTURE_GRASS_TERM_ID = "pastureGrass"


def validate_has_pastureGrass(data: dict, site: dict, list_key: str = "practices"):
    """
    Validate `pastureGrass` is specified

    This validation encourages the user to specify the `pastureGrass` practice, when production occurs on a
    `permanent pasture`.
    """
    site_type = site.get("siteType")
    has_practice = (
        find_term_match(data.get(list_key, []), PASTURE_GRASS_TERM_ID, None) is not None
    )
    return (
        site_type not in [SiteSiteType.PERMANENT_PASTURE.value]
        or has_practice
        or {
            "level": "warning",
            "dataPath": f".{list_key}",
            "message": "should add the term pastureGrass",
        }
    )


def validate_pastureGrass_key_termType(data: dict, list_key: str = "practices"):
    """
    Validate `pastureGrass` practice has a `landCover` key

    When adding the `pastureGrass` practice, you must specify a key using a Term from the `landCover` glossary.
    """
    validate_key_termType = TermTermType.LANDCOVER.value

    def validate(values: tuple):
        index, practice = values
        term_id = practice.get("term", {}).get("@id")
        key_termType = practice.get("key", {}).get("termType")
        return (
            term_id != PASTURE_GRASS_TERM_ID
            or not key_termType
            or key_termType == validate_key_termType
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}].key",
                "message": "pastureGrass key termType must be landCover",
                "params": {
                    "value": key_termType,
                    "expected": validate_key_termType,
                    "term": practice.get("key", {}),
                },
            }
        )

    return _filter_list_errors(
        flatten(map(validate, enumerate(data.get(list_key, []))))
    )


def validate_pastureGrass_key_value(data: dict, list_key: str = "practices"):
    """
    Validate sum of `pastureGrass`

    This validation ensures that the sum of all `pastureGrass.value` is equal to 100%.
    """
    practices = [
        p
        for p in data.get(list_key, [])
        if p.get("term", {}).get("@id") == PASTURE_GRASS_TERM_ID
    ]
    total_value, valid_sum = valid_list_sum(practices)
    return (
        {
            "level": "error",
            "dataPath": f".{list_key}",
            "message": "all values must be numbers",
        }
        if not valid_sum
        else len(practices) == 0
        or total_value == 100
        or {
            "level": "error",
            "dataPath": f".{list_key}",
            "message": "the sum of all pastureGrass values must be 100",
            "params": {"expected": 100, "current": total_value},
        }
    )


def validate_permanent_crop_productive_phase(cycle: dict, list_key: str = "practices"):
    """
    Validate productive phase of permanent crops

    This validation makes sure the following term is adding for pemanent crops, when the primary product value is `0`:
    `productivePhasePermanentCrops`.
    """
    practice_id = "productivePhasePermanentCrops"
    permanent_crop = is_permanent_crop(cycle)
    primary_product = find_primary_product(cycle) or {}
    product_value = list_sum(primary_product.get("value", [-1]), default=-1)
    has_practice = (
        find_term_match(cycle.get(list_key, []), practice_id, None) is not None
    )
    return (
        not permanent_crop
        or product_value != 0
        or has_practice
        or {
            "level": "error",
            "dataPath": f".{list_key}",
            "message": "must add the term productivePhasePermanentCrops",
        }
    )


_PROCESSING_SITE_TYPES = [SiteSiteType.AGRI_FOOD_PROCESSOR.value]


def _is_processing_operation(practice: dict):
    return not (not get_lookup_value(practice.get("term", {}), "isProcessingOperation"))


def validate_primaryPercent(cycle: dict, site: dict, list_key: str = "practices"):
    """
    Validate using `primaryPercent` based on the `siteType`

    This validation:
    - prevents using `primaryPercent` on practices when the `siteType` is not `agri-food processor`.
    - prevents using `primaryPercent` on non-processing practices when the `siteType` is `agri-food processor`.
    """
    site_type = site.get("siteType")

    def validate_siteType(values: tuple):
        index, practice = values
        return "primaryPercent" not in practice or {
            "level": "error",
            "dataPath": f".{list_key}[{index}]",
            "message": "primaryPercent not allowed on this siteType",
            "params": {"current": site_type, "expected": _PROCESSING_SITE_TYPES},
        }

    def validate_operation(values: tuple):
        index, practice = values
        return (
            "primaryPercent" not in practice
            or _is_processing_operation(practice)
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}]",
                "message": "primaryPercent not allowed on this practice",
            }
        )

    validator = (
        validate_operation if site_type in _PROCESSING_SITE_TYPES else validate_siteType
    )
    return _filter_list_errors(map(validator, enumerate(cycle.get(list_key, []))))


def validate_processing_operation(cycle: dict, site: dict, list_key: str = "practices"):
    """
    Validate requires `primaryPercent`

    When the `siteType`=`agri-food processor`, at least one `operation` Practice with `primaryPercent` must be set.
    Note: we also use the lookup `isProcessingOperation` on the `operation` to know if they qualify.
    """
    operations = filter_list_term_type(cycle.get(list_key, []), TermTermType.OPERATION)
    primary_processing_operations = [
        v
        for v in operations
        if all([_is_processing_operation(v), (v.get("primaryPercent") or 0) > 0])
    ]
    site_type = site.get("siteType")
    is_valid = any(
        [
            site_type not in _PROCESSING_SITE_TYPES,
            len(primary_processing_operations) > 0,
        ]
    )
    return is_valid or {
        "level": "error",
        "dataPath": f".{list_key}" if operations else "",
        "message": "must have a primary processing operation",
    }


def validate_landCover_match_products(
    cycle: dict, site: dict, list_key: str = "practices"
):
    """
    Validate that at least one `landCover` practice matches an equivalent Product

    When adding a `landCover` Practice to a Cycle, the Practice must match a Product.
    We use the lookup `landCoverTermId` on existing Products to match the 2 together.
    If no correspondance is found, an error is shown.
    """
    landCover_practice_ids = [
        p.get("term", {}).get("@id")
        for p in filter_list_term_type(
            cycle.get("practices", []), TermTermType.LANDCOVER
        )
        # ignore any practices with a `blankNodesGroup=Cover crops`
        if blank_node_properties_group(p) != "Cover crops"
    ]
    landCover_product_ids = non_empty_list(
        [
            get_lookup_value(p.get("term", {}), "landCoverTermId")
            for p in cycle.get("products", [])
        ]
    )
    is_cropland = site.get("siteType") == SiteSiteType.CROPLAND.value

    return (
        not is_cropland
        or not landCover_practice_ids
        or not landCover_product_ids
        or any(
            [(term_id in landCover_product_ids) for term_id in landCover_practice_ids]
        )
        or {
            "level": "error",
            "dataPath": f".{list_key}",
            "message": "at least one landCover practice must match an equivalent product",
            "params": {
                "current": landCover_practice_ids,
                "expected": landCover_product_ids,
            },
        }
    )


def validate_practices_management(cycle: dict, site: dict, list_key: str = "practices"):
    """
    Validate Cycle Practices and Site Management

    This validation is to ensure that the same Management and Practices added on the Site and related Cycles, with the
    same `term` and `startDate` + `endDate`, have the same `value`.
    Since HESTIA will automatically gap-fill the Management node from the Cycle, removing them will fix this error.
    """
    # validate that practices and management nodes, with same term and dates, have the same value
    management_nodes = site.get("management", [])

    def validate(values: tuple):
        index, practice = values
        term_id = practice.get("term", {}).get("@id")
        value = get_node_value(practice)
        management_node = [
            v
            for v in management_nodes
            if all(
                [
                    v.get("term", {}).get("@id") == term_id,
                    v.get("startDate") == practice.get("startDate"),
                    v.get("endDate") == practice.get("endDate"),
                ]
            )
        ]
        return (
            len(management_node) == 0
            or management_node[0].get("value") == value
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}].value",
                "message": "should match the site management node value",
                "params": {
                    "current": value,
                    "expected": management_node[0].get("value"),
                },
            }
        )

    return (
        _filter_list_errors(flatten(map(validate, enumerate(cycle.get(list_key, [])))))
        if management_nodes
        else True
    )


def validate_irrigated_complete_has_inputs(cycle: dict):
    """
    Validate irrigated Cycles with complete `water` have `water` inputs

    When the Cycle `water` completeness is set to `True`, and "irrigation" practices are used, there must be at least
    1 Input of `termType`=`water`. Otherwise, the completeness should be marked as `False`.
    """
    is_complete = cycle.get("completeness", {}).get(TermTermType.WATER.value)
    has_irrigated_practice = (
        any([_is_irrigated(v.get("term", {})) for v in cycle.get("practices", [])])
        if is_complete
        else False
    )
    has_water_inputs = (
        list_sum(
            list(
                map(
                    get_node_value,
                    filter_list_term_type(cycle.get("inputs", []), TermTermType.WATER),
                )
            ),
            default=0,
        )
        > 0
        if is_complete
        else False
    )

    return any([not is_complete, not has_irrigated_practice, has_water_inputs]) or {
        "level": "error",
        "dataPath": ".inputs",
        "message": "must contain water inputs",
    }
