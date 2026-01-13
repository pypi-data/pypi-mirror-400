from _typeshed import Incomplete

TIME_UNIT_TO_SECOND_MAPPING: Incomplete

def convert_ttl_to_seconds(ttl: str | int) -> int:
    '''Convert TTL (time-to-live) string with time units to seconds.

    Supported units: s (seconds), m (minutes), h (hours), d (days), w (weeks), y (years).

    Examples:
        "2m" -> 120 (2 minutes in seconds)
        "1h" -> 3600 (1 hour in seconds)
        "1y" -> 31536000 (1 year in seconds)
        300 -> 300 (numeric input returned as is)

    Args:
        ttl (str | int): Time to live value with optional unit suffix (e.g., "2m", "1h", "1y")
            or numeric value in seconds.

    Returns:
        int: TTL converted to seconds.

    Raises:
        ValueError: If the input format is invalid.
    '''
