import logging

from connexion.exceptions import Unauthorized
from flask import abort, current_app as app

from . import UpstreamProviderError, provider

logger = logging.getLogger(__name__)

ALLOWED_CHANNELS: list[str] = [
    "sig-memes-and-nonsense"
]


def _format_query(original_query: str, allowed_channels: list[str]) -> str:
    return " ".join(f"in:{channel}" for channel in allowed_channels) + " " + original_query


def search(body):
    try:
        query = _format_query(body["query"], ALLOWED_CHANNELS)
        data = provider.search(query)
        logger.info(f"Found {len(data)} results")
    except UpstreamProviderError as error:
        logger.error(f"Upstream search error: {error.message}")
        abort(502, error.message)
    except AssertionError as error:
        logger.error(f"Slack config error: {error}")
        abort(502, f"Slack config error: {error}")

    return {"results": data}, 200, {"X-Connector-Id": app.config.get("APP_ID")}


def apikey_auth(token):
    api_key = app.config.get("CONNECTOR_API_KEY", "")
    if api_key != "" and token != api_key:
        raise Unauthorized()
    # successfully authenticated
    return {}
