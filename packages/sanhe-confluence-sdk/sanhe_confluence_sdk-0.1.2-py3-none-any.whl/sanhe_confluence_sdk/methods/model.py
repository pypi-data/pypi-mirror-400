# -*- coding: utf-8 -*-

import typing as T
import json
import dataclasses

from func_args.api import BaseFrozenModel, remove_optional, T_KWARGS, REQ
from func_args.vendor import sentinel
from httpx import Response, HTTPStatusError

from ..client import Confluence

NA = sentinel.create(name="NA")

# TypeVar for generic response class in _sync_get, _new, _new_many
T_Response = T.TypeVar("T_Response", bound="BaseResponse")
T_METHOD = T.Literal[
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
]


def api_field(
    default: T.Any,
    wire_name: str | None = None,
):
    if wire_name:
        metadata = {"wire_name": wire_name}
    else:
        metadata = None
    return dataclasses.field(default=default, metadata=metadata)


@dataclasses.dataclass(frozen=True)
class BaseModel(BaseFrozenModel):
    def to_api_kwargs(self) -> T_KWARGS:
        """
        Convert this model to API-ready kwargs dict.
        """
        kwargs = self.to_kwargs()
        for field in dataclasses.fields(self):
            try:
                name = field.metadata["wire_name"]
                kwargs[name] = kwargs.pop(field.name)
            except:
                pass
        return kwargs


# ------------------------------------------------------------------------------
# Request
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class PathParams(BaseModel):
    pass


@dataclasses.dataclass(frozen=True)
class QueryParams(BaseModel):
    pass


@dataclasses.dataclass(frozen=True)
class BodyParams(BaseModel):
    pass


@dataclasses.dataclass(frozen=True)
class BaseRequest(BaseModel):
    path_params: PathParams = dataclasses.field(default_factory=PathParams)
    query_params: QueryParams = dataclasses.field(default_factory=QueryParams)
    body_params: BodyParams = dataclasses.field(default_factory=BodyParams)

    @property
    def _path(self) -> str:
        """
        Returns the API endpoint path relative to the client's root URL.

        For example, if root URL is "https://example.atlassian.net/wiki/api/v2"
        and path is "/spaces", the full URL becomes
        "https://example.atlassian.net/wiki/api/v2/spaces".
        """
        raise NotImplementedError

    @property
    def _params(self) -> T_KWARGS:  # pragma: no cover
        """
        Constructs query parameters from request attributes.

        Subclasses should override this to return attribute-to-parameter mappings.
        The returned dict will be processed by :meth:`_final_params` to remove
        optional/sentinel values before sending.
        """
        params = self.query_params.to_api_kwargs()
        return params if len(params) else None

    @property
    def _body(self) -> T_KWARGS:  # pragma: no cover
        """
        Constructs request body from request attributes.

        Subclasses should override this to return attribute-to-body field mappings
        for POST/PUT/PATCH requests. The returned dict will be processed by
        :meth:`_final_body` to remove optional/sentinel values before sending.
        """
        params = self.body_params.to_api_kwargs()
        return params if len(params) else None

    def sync(
        self,
        client: Confluence,
    ) -> "T_RESPONSE":
        raise NotImplementedError

    def _sync(
        self,
        method: T_METHOD,
        klass: type[T_Response] | None,
        client: Confluence,
    ):
        url = f"{client._root_url}{self._path}"
        params = self._params
        body = self._body
        # --- for debug only
        # print("----- method")  # for debug only
        # print(method)  # for debug only
        # print("----- url")  # for debug only
        # print(url)  # for debug only
        # print("----- params")  # for debug only
        # print(json.dumps(params, indent=4))  # for debug only
        # if method in ["POST", "PUT", "PATCH"]:
        #     print("----- body")  # for debug only
        #     print(json.dumps(body, indent=4))  # for debug only

        http_res = client.sync_client.request(
            method=method,
            url=url,
            params=params,
            json=body,
        )

        return klass.from_success_http_response(http_res)

    def _sync_get(
        self,
        klass: type[T_Response],
        client: Confluence,
    ):  # pragma: no cover
        return self._sync("GET", klass, client)

    def _sync_post(
        self,
        klass: type[T_Response],
        client: Confluence,
    ):  # pragma: no cover
        return self._sync("POST", klass, client)

    def _sync_put(
        self,
        klass: type[T_Response],
        client: Confluence,
    ):  # pragma: no cover
        return self._sync("PUT", klass, client)

    def _sync_delete(
        self,
        klass: type[T_Response],
        client: Confluence,
    ):  # pragma: no cover
        return self._sync("DELETE", klass, client)


T_REQUEST = T.TypeVar("T_REQUEST", bound=BaseRequest)


# ------------------------------------------------------------------------------
# Response
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class BaseResponse(BaseModel):
    _raw_data: T_KWARGS = dataclasses.field()
    _http_res: Response | None = dataclasses.field(default=None)

    @property
    def raw_data(self):
        """
        Returns the underlying raw JSON data as a read-only accessor.

        The internal ``_raw_data`` attribute uses underscore prefix to indicate
        it should not be modified directly. This property provides safe read
        access while preserving immutability of the response object.
        """
        return self._raw_data

    @property
    def http_res(self) -> Response | None:
        """
        Returns the underlying HTTP response object, if available.

        This allows access to HTTP metadata such as status code and headers.
        """
        return self._http_res

    @classmethod
    def from_success_http_response(
        cls,
        http_res: Response,
    ):
        try:
            http_res.raise_for_status()
        except HTTPStatusError as e:
            # print("----- error")  # for debug only
            # print(f"http error: {e}")  # for debug only
            # print(f"status_code: {e.response.status_code}")  # for debug only
            # print(f"headers: {e.response.headers}")  # for debug only
            # print(f"body: {e.response.text}")  # for debug only
            raise

        if http_res.status_code == 204:
            return cls(_raw_data={}, _http_res=http_res)
        else:
            return cls(_raw_data=http_res.json(), _http_res=http_res)

    def _get(self, field: str):
        """
        Gets a simple field value from the raw data.

        We use NA sentinel to indicate "field not present" vs None value.
        """
        return self._raw_data.get(field, NA)

    def _new(self, klass: type[T_Response], field: str):
        """
        Creates a nested response object from a field in the raw data.

        This method handles the three possible states of optional nested objects
        in API responses, allowing callers to distinguish between "field absent"
        vs "field explicitly null" vs "field has data":

        1. Field exists with JSON object → returns new instance of ``klass``
        2. Field exists with None value → returns None (explicit null in API)
        3. Field absent → returns NA sentinel (field not requested/available)
        """
        value = self._raw_data.get(field, NA)
        if value is NA:
            return NA
        elif value is None:
            return value
        else:
            return klass(_raw_data=value)

    def _new_many(self, klass: type[T_Response], field: str):
        """
        Creates a list of nested response objects from an array field.

        This method handles the three possible states of optional array fields
        in API responses, allowing callers to distinguish between "field absent"
        vs "field explicitly null" vs "field has data":

        1. Field exists with list of JSON objects → returns list of ``klass`` instances
        2. Field exists with None value → returns None (explicit null in API)
        3. Field absent → returns NA sentinel (field not requested/available)
        """
        value = self._raw_data.get(field, NA)
        if value is NA:
            return NA
        elif value is None:
            return value
        else:
            return [klass(_raw_data=raw_data) for raw_data in value]


T_RESPONSE = T.TypeVar("T_RESPONSE", bound=BaseResponse)
