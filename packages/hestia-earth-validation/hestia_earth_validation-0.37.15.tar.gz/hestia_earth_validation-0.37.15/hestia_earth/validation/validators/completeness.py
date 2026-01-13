from typing import List
from hestia_earth.schema import (
    Completeness,
    SiteSiteType,
    TermTermType,
    CompletenessField,
    COMPLETENESS_MAPPING,
)
from hestia_earth.utils.model import filter_list_term_type
from hestia_earth.utils.tools import list_sum, flatten, non_empty_list

from hestia_earth.validation.utils import _filter_list_errors, contains_grazing_animals
from hestia_earth.validation.terms import TERMS_QUERY, get_terms


def _validate_completeness_fields(fields: List[str]):
    all_fields = Completeness().required
    assert all([f in all_fields for f in fields])


def _validate_cropland(data_completeness: dict, site: dict):
    validate_keys = [CompletenessField.ANIMALFEED.value, TermTermType.EXCRETA.value]
    _validate_completeness_fields(validate_keys)

    site_type = site.get("siteType")

    def validate_key(key: str):
        return data_completeness.get(key) is True or {
            "level": "warning",
            "dataPath": f".completeness.{key}",
            "message": f"should be true for site of type {site_type}",
        }

    return site_type not in [
        SiteSiteType.CROPLAND.value,
        SiteSiteType.GLASS_OR_HIGH_ACCESSIBLE_COVER.value,
    ] or _filter_list_errors(map(validate_key, validate_keys))


def _validate_all_values(data_completeness: dict):
    """
    Validate completeness fields are all set to False

    When all completeness fields are set to False, this might be an error. This validation will give a warning.
    """
    values = data_completeness.values()
    return next(
        (value for value in values if isinstance(value, bool) and value is True), False
    ) or {
        "level": "warning",
        "dataPath": ".completeness",
        "message": "may not all be set to false",
    }


def _has_material_terms(cycle: dict):
    materials = filter_list_term_type(cycle.get("inputs", []), TermTermType.MATERIAL)
    return len(materials) > 0 and any(
        [list_sum(material.get("value", [0])) > 0 for material in materials]
    )


def _has_terms(blank_nodes: list, term_ids: list, allow_no_value: bool = True):
    values = [v for v in blank_nodes if v.get("term", {}).get("@id") in term_ids]
    return (
        len(values) > 0
        if allow_no_value
        else any([len(v.get("value", [])) > 0 for v in values])
    )


def _validate_material(cycle: dict):
    """
    Validate completeness `material`

    This validation will give an error when:
    - `material` is set as `complete`;
    - and the Cycle contains `fuel` inputs (like `gasoline` or `petrol`);
    - but the Cycle does not contain any `material` inputs.

    To fix the error, set the completeness to `false`, or add any missing `material` inputs.
    """
    completenes_key = CompletenessField.MATERIAL.value
    _validate_completeness_fields([completenes_key])

    is_complete = cycle.get("completeness", {}).get(completenes_key, False)
    fuel_ids = get_terms(TERMS_QUERY.FUEL)
    return (
        not is_complete
        or not _has_terms(cycle.get("inputs", []), fuel_ids, True)
        or _has_material_terms(cycle)
        or {
            "level": "error",
            "dataPath": ".completeness.material",
            "message": "must be set to false when specifying fuel use",
            "params": {"allowedValues": fuel_ids},
        }
    )


def _validate_freshForage(cycle: dict, site: dict):
    """
    Validate completeness `freshForage`

    This validation will give an error when:
    - `freshForage` is set as `complete`;
    - the `siteType` is `cropland` or `permanent pasture`;
    - the Cycle contains grazing animals (see the lookup `isGrazingAnimal` on the animal products);
    - the Cycle does not contain any `forage` inputs.

    To fix this error, set the completeness to `false`, or add any missing `forage` inputs.
    """
    completenes_key = CompletenessField.FRESHFORAGE.value
    _validate_completeness_fields([completenes_key])

    is_complete = cycle.get("completeness", {}).get(completenes_key, False)
    site_type = site.get("siteType")
    has_grazing_animal = contains_grazing_animals(cycle)

    forage_terms = get_terms(TERMS_QUERY.FORAGE) if has_grazing_animal else []
    has_forage = (
        _has_terms(
            flatten(
                cycle.get("inputs", [])
                + [a.get("inputs", []) for a in cycle.get("animals", [])]
            ),
            forage_terms,
            allow_no_value=False,
        )
        if has_grazing_animal
        else False
    )

    return (
        not is_complete
        or site_type
        not in [
            SiteSiteType.CROPLAND.value,
            SiteSiteType.PERMANENT_PASTURE.value,
        ]
        or not has_grazing_animal
        or has_forage
        or {
            "level": "error",
            "dataPath": ".completeness.freshForage",
            "message": "must have inputs representing the forage when set to true",
            "params": {"siteType": site_type},
        }
    )


def _validate_ingredient(cycle: dict, site: dict, other_sites: list = []):
    """
    Validate completeness `ingredient`

    This validation will give an error when:
    - `ingredient` is set as `complete`, and `siteType` = `agri-food processor`, but there are no `inputs`;
    - or `ingredient` is set as `incomplete`, but the `siteType` is not `agri-food processor`.

    To fix this error, either change the `siteType`,
    or only set as complete if ingredients have been specified as inputs.
    """
    completenes_key = CompletenessField.INGREDIENT.value
    _validate_completeness_fields([completenes_key])

    is_complete = cycle.get("completeness", {}).get(completenes_key, False)
    all_sites = non_empty_list([site] + (other_sites or []))
    site_types = non_empty_list([s.get("siteType") for s in all_sites])
    has_inputs = len(cycle.get("inputs", [])) > 0
    is_processor = any(
        [
            site_type == SiteSiteType.AGRI_FOOD_PROCESSOR.value
            for site_type in site_types
        ]
    )

    return (
        (
            # if complete, agri-processor must have inputs
            not is_processor
            or has_inputs
            or {
                "level": "error",
                "dataPath": ".completeness.ingredient",
                "message": "must have inputs to represent ingredients",
                "params": {"siteType": site.get("siteType")},
            }
        )
        if is_complete
        else (
            # only agri-food processor can be incomplete
            is_processor
            or {
                "level": "error",
                "dataPath": ".completeness.ingredient",
                "message": "ingredients should be complete",
                "params": {"siteType": site.get("siteType")},
            }
        )
    )


def _validate_animalPopulation(cycle: dict):
    """
    Validate completeness `animalPopulation`

    This validation will give an error when:
    - `animalPopulation` is set as `complete`;
    - there are Products with `termType` = `liveAnimal` or `liveAquaticSpecies`;
    - and there are no animal blank nodes.

    To fix this error, set the completeness to `false`, or add any missing animal blank nodes.
    """
    completenes_key = CompletenessField.ANIMALPOPULATION.value
    _validate_completeness_fields([completenes_key])

    is_complete = cycle.get("completeness", {}).get(completenes_key, False)

    animal_products = filter_list_term_type(
        cycle.get("products", []),
        [TermTermType.LIVEANIMAL, TermTermType.LIVEAQUATICSPECIES],
    )

    return (
        not is_complete
        or not animal_products
        or bool(cycle.get("animals"))
        or {
            "level": "error",
            "dataPath": ".completeness.animalPopulation",
            "message": "animal population must not be complete",
        }
    )


def validate_completeness(cycle: dict, site=None, other_sites=[]):
    data_completeness = cycle.get("completeness", {})
    return _filter_list_errors(
        [
            _validate_all_values(data_completeness),
            _validate_material(cycle),
            _validate_animalPopulation(cycle),
            _validate_cropland(data_completeness, site) if site else True,
            _validate_freshForage(cycle, site) if site else True,
            _validate_ingredient(cycle, site, other_sites) if site else True,
        ]
    )


def _blank_node_completeness_key(blank_node: dict, site: dict):
    blank_node_type = blank_node.get("@type") or blank_node.get("type")
    term_type = blank_node.get("term", {}).get("termType")
    site_type = (site or {}).get("siteType")
    return COMPLETENESS_MAPPING.get("siteType", {}).get(site_type, {}).get(
        blank_node_type, {}
    ).get(term_type) or COMPLETENESS_MAPPING.get(blank_node_type, {}).get(term_type)


def _validate_completeness_blank_nodes_key(cycle: dict, site: dict, list_key: str):
    """
    Validate blank nodes value when complete

    This validation uses a mapping from a completeness field to a list of blank nodes, and gives an error when any
    corresponding blank node has been added without a `value`.

    For example:
    - if `cropResidue` is set as `complete`, then all `cropResidue` products or `cropResidueManagement` practices
    must contain a `value`;
    - if `animalFeed` is complete, then all `animalProduct`, `crop`, or `processedFood` inputs must contain a `value`.

    The mapping can be found in the
    [Completeness yaml source file](https://gitlab.com/hestia-earth/hestia-schema/-/blob/master/yaml/Completeness.yaml).

    To fix this error, make sure all blank nodes with matching completeness have a `value`, when set as `complete`.
    """
    completeness = cycle.get("completeness", {})

    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get("term", {})
        completeness_key = _blank_node_completeness_key(blank_node, site)
        value = blank_node.get("value")
        has_value = value is not None and (
            not isinstance(value, list) or len(value) > 0
        )
        return (
            has_value
            or not completeness_key
            or not completeness.get(completeness_key)
            or {
                "level": "error",
                "dataPath": f".{list_key}[{index}]",
                "message": "must not be blank if complete",
                "params": {"term": term, "expected": completeness_key},
            }
        )

    return _filter_list_errors(
        flatten(map(validate, enumerate(cycle.get(list_key, []))))
    )


def validate_completeness_blank_nodes(cycle: dict, site: dict = {}):
    # use the completeness mapping to validate the values provided
    list_keys = ["animals", "inputs", "products", "practices"]
    return _filter_list_errors(
        flatten(
            [
                _validate_completeness_blank_nodes_key(cycle, site, list_key)
                for list_key in list_keys
                if cycle.get(list_key)
            ]
        )
    )
