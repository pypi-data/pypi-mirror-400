"""SDK for building singer-compliant taps."""

from hotglue_singer_sdk.streams.core import Stream
from hotglue_singer_sdk.streams.graphql import GraphQLStream
from hotglue_singer_sdk.streams.rest import RESTStream
from hotglue_singer_sdk.streams.sql import SQLConnector, SQLStream

__all__ = [
    "Stream",
    "GraphQLStream",
    "RESTStream",
    "SQLStream",
    "SQLConnector",
]
