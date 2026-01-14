import rich


def simplified_argument_matching(expected, actual):
    if actual is None:
        return False
    for field in actual:
        if field not in expected:
            return False

    return True


def check_labeled_messages_empty(labeled_messages):
    """Check if labeled messages are empty and print warning if so.

    Args:
        labeled_messages: Dictionary of labeled messages to check

    Returns:
        bool: True if empty, False otherwise
    """
    if not labeled_messages:
        rich.print("[r] Labeled Messages are empty. No extraction performed.")
        return True
    return False
