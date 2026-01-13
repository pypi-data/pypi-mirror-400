
.. image:: https://readthedocs.org/projects/sanhe-confluence-sdk/badge/?version=latest
    :target: https://sanhe-confluence-sdk.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/sanhe_confluence_sdk-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/sanhe_confluence_sdk-project

.. image:: https://img.shields.io/pypi/v/sanhe-confluence-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-confluence-sdk

.. image:: https://img.shields.io/pypi/l/sanhe-confluence-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-confluence-sdk

.. image:: https://img.shields.io/pypi/pyversions/sanhe-confluence-sdk.svg
    :target: https://pypi.python.org/pypi/sanhe-confluence-sdk

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://sanhe-confluence-sdk.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/sanhe_confluence_sdk-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/sanhe-confluence-sdk#files


Welcome to ``sanhe_confluence_sdk`` Documentation
==============================================================================
.. image:: https://sanhe-confluence-sdk.readthedocs.io/en/latest/_static/sanhe_confluence_sdk-logo.png
    :target: https://sanhe-confluence-sdk.readthedocs.io/en/latest/

``sanhe_confluence_sdk`` is a Pythonic SDK for the Confluence REST API v2.

**Features**:

- **Everything is a Class**: All requests and responses are represented as Python dataclasses with full type hints.
- **IDE Friendly**: With complete type annotations, you get autocomplete and inline documentation in your IDE.
- **Access Raw Data**: Every response object has a ``.raw_data`` attribute that gives you the original JSON dictionary if needed.
- **Consistent Pattern**: All API calls follow the same pattern - create a Request, call ``.sync(client)``, get a Response.


.. _install:

Install
------------------------------------------------------------------------------

``sanhe_confluence_sdk`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install sanhe-confluence-sdk

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade sanhe-confluence-sdk


Quick Start
------------------------------------------------------------------------------

**Create a Client**:

.. code-block:: python

    from sanhe_confluence_sdk.api import Confluence

    client = Confluence(
        url="https://your-domain.atlassian.net",
        username="your-email@example.com",
        password="your-api-token",  # https://id.atlassian.com/manage-profile/security/api-tokens
    )

**Basic Usage**:

.. code-block:: python

    from sanhe_confluence_sdk.api import Confluence, m

    client = Confluence(...)

    # Create a request and execute it
    request = m.GetSpacesRequest()
    response = request.sync(client)

    # Access typed results
    for space in response.results:
        print(f"Space: {space.name} (key={space.key})")

    # Access raw JSON data
    print(response.raw_data)

**Pagination**:

.. code-block:: python

    from sanhe_confluence_sdk.api import Confluence, paginate
    from sanhe_confluence_sdk.methods.space.get_spaces import (
        GetSpacesRequest,
        GetSpacesResponse,
    )

    client = Confluence(...)

    for response in paginate(
        client=client,
        request=GetSpacesRequest(),
        response_type=GetSpacesResponse,
        page_size=25,
        max_items=100,
    ):
        for space in response.results:
            print(f"Space: {space.name}")

For more details, see the `Full Documentation <https://sanhe-confluence-sdk.readthedocs.io/en/latest/>`_.
