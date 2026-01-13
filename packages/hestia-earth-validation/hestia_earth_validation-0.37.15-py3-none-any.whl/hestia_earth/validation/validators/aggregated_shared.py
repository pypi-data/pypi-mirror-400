def validate_id(node: dict):
    """
    Validate aggregated node `id`

    Validate the node `id` has been correctly formatted.
    If this validation fails, it indicates an error in the aggregation engine, and an issue must be raised.
    """
    node_id = node.get("id", "")
    # there should be 4 different components to the id
    node_id_length = len(node_id.split("-"))
    return (
        not node_id
        or node_id_length >= 4
        or {
            "level": "error",
            "dataPath": ".id",
            "message": "aggregation id must contain a product, region, start, and end year",
        }
    )
