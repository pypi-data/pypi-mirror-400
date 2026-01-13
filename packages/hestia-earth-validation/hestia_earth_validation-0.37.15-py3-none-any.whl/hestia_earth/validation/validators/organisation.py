"""
Organisation validation

Here is the list of validations running on a [Organisation](/schema/Organisation).
"""

from .shared import (
    validate_node_dates,
    need_validate_coordinates,
    validate_coordinates,
    validate_area,
    need_validate_area,
    validate_date_lt_today,
    validate_country_region,
)


def validate_organisation(organisation: dict, node_map: dict = {}):
    return [
        validate_node_dates(organisation),
        validate_date_lt_today(organisation, "startDate"),
        validate_date_lt_today(organisation, "endDate"),
        validate_country_region(organisation),
        (
            validate_coordinates(organisation)
            if need_validate_coordinates(organisation)
            else True
        ),
        validate_area(organisation) if need_validate_area(organisation) else True,
    ]
