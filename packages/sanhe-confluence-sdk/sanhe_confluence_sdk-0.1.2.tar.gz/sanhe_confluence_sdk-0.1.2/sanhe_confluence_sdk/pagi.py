# -*- coding: utf-8 -*-

import typing as T
import dataclasses

from .client import Confluence
from .methods.model import (
    T_REQUEST,
    T_RESPONSE,
)
from .methods.common.links import Links


class PaginationError(Exception):
    """Base exception for pagination errors."""

    pass


class MissingLinksError(PaginationError):
    """
    Raised when response doesn't have expected '_links' structure for pagination.

    This indicates the API response format doesn't match the expected pagination
    pattern (response should have '_links.next' for more pages).
    """

    pass


def paginate(
    client: Confluence,
    request: T_REQUEST,
    response_type: type[T_RESPONSE],
    page_size: int,
    max_items: int,
    max_pages: int = 100,
    limit_field: str = "limit",
    results_field: str = "results",
) -> T.Iterator[T_RESPONSE]:
    """
    Generic paginator for Confluence API list endpoints.

    :param client: Confluence client instance.
    :param request: Initial request object (must have query_params).
    :param response_type: Response class type for deserialization.
    :param page_size: Number of items per page (API's limit parameter).
    :param max_items: Stop fetching when total items >= this value.
        If less than page_size, it will be adjusted to page_size.
    :param max_pages: Maximum number of pages to fetch (default 100).
        This is a safeguard against infinite loops.
    :param limit_field: Name of the limit query parameter (default "limit").
    :param results_field: Name of the results field in response (default "results").

    :yields: Response objects, one per page.

    :raises MissingLinksError: If response doesn't have expected '_links' structure.
    """
    # --- Parameter validation ---
    if page_size < 1:  # pragma: no cover
        raise ValueError("page_size must be >= 1")
    if max_pages < 1:  # pragma: no cover
        raise ValueError("max_pages must be >= 1")
    # Adjust max_items if less than page_size (you'll get at least one page)
    if max_items < page_size:  # pragma: no cover
        max_items = page_size

    n_fetched_items = 0

    # Adjust the request with the desired page_size
    request = dataclasses.replace(
        request,
        query_params=dataclasses.replace(
            request.query_params,
            **{limit_field: page_size},
        ),
    )
    response = request.sync(client)  # paginator only uses sync request
    yield response

    # Fetch subsequent pages (at most max_pages - 1, since first page already fetched)
    for _ in range(max_pages - 1):
        n_fetched_items += len(response.raw_data.get(results_field, []))
        if n_fetched_items >= max_items:
            break

        # Validate response has expected pagination structure
        try:
            links: Links = response.links
        except AttributeError:  # pragma: no cover
            raise MissingLinksError(
                f"Response type '{type(response).__name__}' doesn't have 'links' attribute. "
                f"This API may not support pagination."
            )

        # links.next is either NA (no more pages) or a str (next page URL)
        if not isinstance(links.next, str):
            break

        url = client.url + links.next
        http_res = client.sync_client.get(url=url)
        response = response_type.from_success_http_response(http_res)
        yield response
