from hestia_earth.schema import TermTermType, SiteSiteType
from hestia_earth.utils.tools import flatten, non_empty_list
from hestia_earth.utils.model import find_term_match

from hestia_earth.validation.utils import (
    _filter_list_errors,
    update_error_path,
    get_lookup_value,
)


def validate_has_animals(cycle: dict):
    """
    Validate Cycle contains animals blank node

    For `liveAnimal` production Cycles, it is recommended to include animal blank nodes.
    """
    has_liveAnimal = any(
        p
        for p in cycle.get("products", [])
        if p.get("term", {}).get("termType") == TermTermType.LIVEANIMAL.value
    )
    has_animals = len(cycle.get("animals", [])) > 0
    return (
        not has_liveAnimal
        or has_animals
        or {
            "level": "warning",
            "dataPath": "",
            "message": "should specify the herd composition",
        }
    )


def validate_duplicated_feed_inputs(cycle: dict):
    """
    Validate feed inputs are not duplicated for Animals

    This validation ensures that the same Input marked with `isAnimalFeed` are not added in both `inputs` and `animals`.
    """
    feed_input_ids = [
        i.get("term", {}).get("@id")
        for i in cycle.get("inputs", [])
        if i.get("isAnimalFeed", False)
    ]

    def validate_animal_input(values: tuple):
        index, input = values
        term = input.get("term", {})
        term_id = term.get("@id")
        return term_id not in feed_input_ids or {
            "level": "error",
            "dataPath": f".inputs[{index}]",
            "message": "must not add the feed input to the Cycle as well",
            "params": {"term": term},
        }

    def validate_animal(values: tuple):
        index, blank_node = values
        errors = list(
            map(validate_animal_input, enumerate(blank_node.get("inputs", [])))
        )
        return _filter_list_errors(
            [
                update_error_path(error, "animals", index)
                for error in errors
                if error is not True
            ]
        )

    blank_nodes = enumerate(cycle.get("animals", []))
    return _filter_list_errors(flatten(map(validate_animal, blank_nodes)))


def validate_has_pregnancyRateTotal(cycle: dict):
    """
    Validate specifying the pregnancy rate for Animals

    Using the lookup `productTermIdsAllowed` on the Term `pregnancyRateTotal`, this validation will recommend the user
    to add the property `pregnancyRateTotal` on the Animal blank node.
    """
    term_id = "pregnancyRateTotal"
    term = {"@id": term_id, "termType": TermTermType.PROPERTY.value}
    allowed_term_ids = get_lookup_value(term, "productTermIdsAllowed").split(";")

    def validate(values: tuple):
        index, blank_node = values
        is_allowed_term = blank_node.get("term", {}).get("@id") in allowed_term_ids
        has_property = (
            find_term_match(blank_node.get("properties", []), term_id, None) is not None
        )
        return (
            not is_allowed_term
            or has_property
            or {
                "level": "warning",
                "dataPath": f".animals[{index}].properties",
                "message": "should specify the pregnancy rate",
                "params": {"expected": term_id},
            }
        )

    blank_nodes = enumerate(cycle.get("animals", []))
    return _filter_list_errors(flatten(map(validate, blank_nodes)))


def validate_has_milkYieldPractice(cycle: dict, sites: list = []):
    """
    Validate specifying a "Milk yield" practice for Animals

    Using the lookup `milkYieldPracticeTermIds` on the Animal term, this validation will recommend the user to add any
    Practice that matches one of the Term, if none has been set.
    """
    blank_nodes = enumerate(cycle.get("animals", []))
    lookup_col = "milkYieldPracticeTermIds"
    valid_site_type = any(
        [
            site.get("siteType")
            in [SiteSiteType.PERMANENT_PASTURE.value, SiteSiteType.CROPLAND.value]
            for site in sites
        ]
    )

    def validate(values: tuple):
        index, blank_node = values
        term = blank_node.get("term")
        practice_term_ids = non_empty_list(
            (get_lookup_value(term, lookup_col) or "").split(";")
        )
        has_practice = any(
            [
                find_term_match(blank_node.get("practices", []), term_id, False)
                for term_id in practice_term_ids
            ]
        )
        return (
            not practice_term_ids
            or has_practice
            or {
                "level": "warning",
                "dataPath": f".animals[{index}]",
                "message": "should specify the a milkYield practice",
                "params": {"expected": practice_term_ids},
            }
        )

    return not valid_site_type or _filter_list_errors(
        flatten(map(validate, blank_nodes))
    )
