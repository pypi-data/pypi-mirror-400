# -*- coding: utf-8 -*-

import dataclasses
from functools import cached_property

from ..model import BaseResponse


@dataclasses.dataclass(frozen=True)
class Links(BaseResponse):
    """MultiEntityLinks schema for pagination."""

    @cached_property
    def next(self) -> str:
        """Relative URL for the next set of results using cursor pagination."""
        return self._get("next")

    @cached_property
    def base(self) -> str:
        """Base URL of the Confluence site."""
        return self._get("base")
