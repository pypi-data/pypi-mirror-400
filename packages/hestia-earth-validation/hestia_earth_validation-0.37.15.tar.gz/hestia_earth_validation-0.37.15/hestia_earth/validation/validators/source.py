"""
Source validation

Here is the list of validations running on a [Source](/schema/Source).
"""

from .shared import validate_date_lt_today


def validate_source(source: dict, node_map: dict = {}):
    return [validate_date_lt_today(source, "bibliography.year")]
