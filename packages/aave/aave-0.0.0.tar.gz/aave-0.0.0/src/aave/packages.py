from .types import Version


def get_market_addresses(version: Version):
    match version:
        case Version.V3:
            return []
