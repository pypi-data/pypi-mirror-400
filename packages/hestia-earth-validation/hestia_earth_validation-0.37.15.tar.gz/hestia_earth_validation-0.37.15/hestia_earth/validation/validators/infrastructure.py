from hestia_earth.utils.date import diff_in, TimeUnit

from hestia_earth.validation.utils import _filter_list_errors


def validate_lifespan(infrastructure: list):
    """
    Validate defaultLifespan

    This validation will give an error if the duration between the start and the end dates is not equal to the
    `defaultLifespan`.
    """

    def validate(values: tuple):
        index, value = values
        start_date = value.get("startDate")
        end_date = value.get("endDate")
        lifespan = value.get("defaultLifespan", -1)
        diff = (
            round(diff_in(start_date, end_date, TimeUnit.YEAR), 1)
            if start_date and end_date
            else -1
        )
        return (
            lifespan == -1
            or diff == -1
            or diff == round(lifespan, 1)
            or {
                "level": "error",
                "dataPath": f".infrastructure[{index}].defaultLifespan",
                "message": "must equal to endDate - startDate in decimal years",
                "params": {"expected": diff},
            }
        )

    return _filter_list_errors(map(validate, enumerate(infrastructure)))
