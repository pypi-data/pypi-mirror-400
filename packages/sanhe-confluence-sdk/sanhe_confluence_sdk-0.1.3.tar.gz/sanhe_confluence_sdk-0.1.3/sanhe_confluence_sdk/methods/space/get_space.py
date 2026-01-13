# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from func_args.api import REQ, OPT

from ...client import Confluence

from ..model import api_field, BaseRequest, PathParams, QueryParams, BaseResponse


# ------------------------------------------------------------------------------
# Input
# ------------------------------------------------------------------------------
@dataclasses.dataclass(frozen=True)
class GetSpaceRequestPathParams(PathParams):
    id: int = api_field(REQ)


@dataclasses.dataclass(frozen=True)
class GetSpaceRequestQueryParams(QueryParams):
    description_format: str = api_field(OPT, "description-format")
    include_icon: bool = api_field(OPT, "include-icon")
    include_operations: bool = api_field(OPT, "include-operations")
    include_properties: bool = api_field(OPT, "include-properties")
    include_permissions: bool = api_field(OPT, "include-permissions")
    include_role_assignments: bool = api_field(OPT, "include-role-assignments")
    include_labels: bool = api_field(OPT, "include-labels")


@dataclasses.dataclass(frozen=True)
class GetSpaceRequest(BaseRequest):
    """
    See: https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-id-get
    """

    path_params: GetSpaceRequestPathParams = dataclasses.field(
        default_factory=GetSpaceRequestPathParams
    )
    query_params: GetSpaceRequestQueryParams = dataclasses.field(
        default_factory=GetSpaceRequestQueryParams
    )

    @property
    def _path(self) -> str:
        return f"/spaces/{self.path_params.id}"

    def sync(self, client: Confluence) -> "GetSpaceResponse":
        return self._sync_get(GetSpaceResponse, client)


# ------------------------------------------------------------------------------
# Output
# ------------------------------------------------------------------------------
# --- Deepest nested objects first ---
@dataclasses.dataclass(frozen=True)
class GetSpaceResponseDescriptionPlain(BaseResponse):
    """BodyType schema for plain text representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseDescriptionView(BaseResponse):
    """BodyType schema for view (HTML) representation."""

    @cached_property
    def representation(self) -> str:
        return self._get("representation")

    @cached_property
    def value(self) -> str:
        return self._get("value")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseDescription(BaseResponse):
    """SpaceDescription schema."""

    @cached_property
    def plain(self) -> GetSpaceResponseDescriptionPlain:
        return self._new(GetSpaceResponseDescriptionPlain, "plain")

    @cached_property
    def view(self) -> GetSpaceResponseDescriptionView:
        return self._new(GetSpaceResponseDescriptionView, "view")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseIcon(BaseResponse):
    """SpaceIcon schema."""

    @cached_property
    def path(self) -> str:
        return self._get("path")

    @cached_property
    def apiDownloadLink(self) -> str:
        return self._get("apiDownloadLink")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseLinks(BaseResponse):
    """SpaceLinks schema."""

    @cached_property
    def webui(self) -> str:
        return self._get("webui")


# --- Optional nested objects for expanded fields ---
@dataclasses.dataclass(frozen=True)
class GetSpaceResponseLabel(BaseResponse):
    """Label schema for space labels."""

    @cached_property
    def prefix(self) -> str:
        return self._get("prefix")

    @cached_property
    def name(self) -> str:
        return self._get("name")

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def label(self) -> str:
        return self._get("label")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseLabelsLinks(BaseResponse):
    """Links for labels pagination."""

    @cached_property
    def next(self) -> str:
        return self._get("next")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseLabelsMeta(BaseResponse):
    """Meta information for labels pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseLabels(BaseResponse):
    """Container for space labels with pagination."""

    @cached_property
    def results(self) -> list[GetSpaceResponseLabel]:
        return self._new_many(GetSpaceResponseLabel, "results")

    @cached_property
    def meta(self) -> GetSpaceResponseLabelsMeta:
        return self._new(GetSpaceResponseLabelsMeta, "meta")

    @cached_property
    def links(self) -> GetSpaceResponseLabelsLinks:
        return self._new(GetSpaceResponseLabelsLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseProperty(BaseResponse):
    """SpaceProperty schema."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def key(self) -> str:
        return self._get("key")

    @cached_property
    def value(self) -> str:
        """Value stored as JSON string."""
        return self._get("value")

    @cached_property
    def version(self) -> int:
        return self._get("version")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePropertiesLinks(BaseResponse):
    """Links for properties pagination."""

    @cached_property
    def next(self) -> str:
        return self._get("next")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePropertiesMeta(BaseResponse):
    """Meta information for properties pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseProperties(BaseResponse):
    """Container for space properties with pagination."""

    @cached_property
    def results(self) -> list[GetSpaceResponseProperty]:
        return self._new_many(GetSpaceResponseProperty, "results")

    @cached_property
    def meta(self) -> GetSpaceResponsePropertiesMeta:
        return self._new(GetSpaceResponsePropertiesMeta, "meta")

    @cached_property
    def links(self) -> GetSpaceResponsePropertiesLinks:
        return self._new(GetSpaceResponsePropertiesLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseOperation(BaseResponse):
    """Operation schema."""

    @cached_property
    def operation(self) -> str:
        return self._get("operation")

    @cached_property
    def targetType(self) -> str:
        return self._get("targetType")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseOperationsLinks(BaseResponse):
    """Links for operations pagination."""

    @cached_property
    def next(self) -> str:
        return self._get("next")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseOperationsMeta(BaseResponse):
    """Meta information for operations pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseOperations(BaseResponse):
    """Container for space operations with pagination."""

    @cached_property
    def results(self) -> list[GetSpaceResponseOperation]:
        return self._new_many(GetSpaceResponseOperation, "results")

    @cached_property
    def meta(self) -> GetSpaceResponseOperationsMeta:
        return self._new(GetSpaceResponseOperationsMeta, "meta")

    @cached_property
    def links(self) -> GetSpaceResponseOperationsLinks:
        return self._new(GetSpaceResponseOperationsLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermissionSubject(BaseResponse):
    """Subject for permission."""

    @cached_property
    def type(self) -> str:
        return self._get("type")

    @cached_property
    def identifier(self) -> str:
        return self._get("identifier")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermissionOperation(BaseResponse):
    """Operation details for permission."""

    @cached_property
    def key(self) -> str:
        return self._get("key")

    @cached_property
    def targetType(self) -> str:
        return self._get("targetType")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermission(BaseResponse):
    """SpacePermission schema."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def principal(self) -> GetSpaceResponsePermissionSubject:
        return self._new(GetSpaceResponsePermissionSubject, "principal")

    @cached_property
    def operation(self) -> GetSpaceResponsePermissionOperation:
        return self._new(GetSpaceResponsePermissionOperation, "operation")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermissionsLinks(BaseResponse):
    """Links for permissions pagination."""

    @cached_property
    def next(self) -> str:
        return self._get("next")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermissionsMeta(BaseResponse):
    """Meta information for permissions pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponsePermissions(BaseResponse):
    """Container for space permissions with pagination."""

    @cached_property
    def results(self) -> list[GetSpaceResponsePermission]:
        return self._new_many(GetSpaceResponsePermission, "results")

    @cached_property
    def meta(self) -> GetSpaceResponsePermissionsMeta:
        return self._new(GetSpaceResponsePermissionsMeta, "meta")

    @cached_property
    def links(self) -> GetSpaceResponsePermissionsLinks:
        return self._new(GetSpaceResponsePermissionsLinks, "_links")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseRoleAssignmentPrincipal(BaseResponse):
    """Principal for role assignment."""

    @cached_property
    def principalType(self) -> str:
        return self._get("principalType")

    @cached_property
    def principalId(self) -> str:
        return self._get("principalId")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseRoleAssignment(BaseResponse):
    """RoleAssignment schema."""

    @cached_property
    def principal(self) -> GetSpaceResponseRoleAssignmentPrincipal:
        return self._new(GetSpaceResponseRoleAssignmentPrincipal, "principal")

    @cached_property
    def roleId(self) -> str:
        return self._get("roleId")

    @cached_property
    def roleName(self) -> str:
        return self._get("roleName")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseRoleAssignmentsLinks(BaseResponse):
    """Links for role assignments pagination."""

    @cached_property
    def next(self) -> str:
        return self._get("next")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseRoleAssignmentsMeta(BaseResponse):
    """Meta information for role assignments pagination."""

    @cached_property
    def hasMore(self) -> bool:
        return self._get("hasMore")

    @cached_property
    def cursor(self) -> str:
        return self._get("cursor")


@dataclasses.dataclass(frozen=True)
class GetSpaceResponseRoleAssignments(BaseResponse):
    """Container for space role assignments with pagination."""

    @cached_property
    def results(self) -> list[GetSpaceResponseRoleAssignment]:
        return self._new_many(GetSpaceResponseRoleAssignment, "results")

    @cached_property
    def meta(self) -> GetSpaceResponseRoleAssignmentsMeta:
        return self._new(GetSpaceResponseRoleAssignmentsMeta, "meta")

    @cached_property
    def links(self) -> GetSpaceResponseRoleAssignmentsLinks:
        return self._new(GetSpaceResponseRoleAssignmentsLinks, "_links")


# --- Main response object ---
@dataclasses.dataclass(frozen=True)
class GetSpaceResponse(BaseResponse):
    """SpaceSingle schema - response for getting a single space by ID."""

    @cached_property
    def id(self) -> str:
        return self._get("id")

    @cached_property
    def key(self) -> str:
        return self._get("key")

    @cached_property
    def name(self) -> str:
        return self._get("name")

    @cached_property
    def type(self) -> str:
        """SpaceType enum: global, collaboration, knowledge_base, personal, etc."""
        return self._get("type")

    @cached_property
    def status(self) -> str:
        """SpaceStatus enum: current, archived."""
        return self._get("status")

    @cached_property
    def authorId(self) -> str:
        return self._get("authorId")

    @cached_property
    def currentActiveAlias(self) -> str:
        return self._get("currentActiveAlias")

    @cached_property
    def createdAt(self) -> str:
        """ISO 8601 date-time string."""
        return self._get("createdAt")

    @cached_property
    def homepageId(self) -> str:
        return self._get("homepageId")

    @cached_property
    def description(self) -> GetSpaceResponseDescription:
        return self._new(GetSpaceResponseDescription, "description")

    @cached_property
    def icon(self) -> GetSpaceResponseIcon:
        return self._new(GetSpaceResponseIcon, "icon")

    @cached_property
    def labels(self) -> GetSpaceResponseLabels:
        """Available when include_labels=True."""
        return self._new(GetSpaceResponseLabels, "labels")

    @cached_property
    def properties(self) -> GetSpaceResponseProperties:
        """Available when include_properties=True."""
        return self._new(GetSpaceResponseProperties, "properties")

    @cached_property
    def operations(self) -> GetSpaceResponseOperations:
        """Available when include_operations=True."""
        return self._new(GetSpaceResponseOperations, "operations")

    @cached_property
    def permissions(self) -> GetSpaceResponsePermissions:
        """Available when include_permissions=True."""
        return self._new(GetSpaceResponsePermissions, "permissions")

    @cached_property
    def roleAssignments(self) -> GetSpaceResponseRoleAssignments:
        """Available when include_role_assignments=True. Only for RBAC EAP sites."""
        return self._new(GetSpaceResponseRoleAssignments, "roleAssignments")

    @cached_property
    def links(self) -> GetSpaceResponseLinks:
        return self._new(GetSpaceResponseLinks, "_links")
