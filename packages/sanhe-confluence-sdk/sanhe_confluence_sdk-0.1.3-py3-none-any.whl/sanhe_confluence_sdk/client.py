# -*- coding: utf-8 -*-

from functools import cached_property

from sanhe_atlassian_sdk.api import Atlassian


class Confluence(Atlassian):
    @cached_property
    def _root_url(self) -> str:
        return f"{self.url}/wiki/api/v2"
