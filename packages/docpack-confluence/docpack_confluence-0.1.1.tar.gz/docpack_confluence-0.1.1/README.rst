
.. image:: https://readthedocs.org/projects/docpack-confluence/badge/?version=latest
    :target: https://docpack-confluence.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/docpack_confluence-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/docpack_confluence-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/docpack_confluence-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/docpack_confluence-project

.. image:: https://img.shields.io/pypi/v/docpack-confluence.svg
    :target: https://pypi.python.org/pypi/docpack-confluence

.. image:: https://img.shields.io/pypi/l/docpack-confluence.svg
    :target: https://pypi.python.org/pypi/docpack-confluence

.. image:: https://img.shields.io/pypi/pyversions/docpack-confluence.svg
    :target: https://pypi.python.org/pypi/docpack-confluence

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/docpack_confluence-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/docpack_confluence-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://docpack-confluence.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/docpack_confluence-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/docpack_confluence-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/docpack_confluence-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/docpack-confluence#files


docpack_confluence
==============================================================================
.. image:: https://docpack-confluence.readthedocs.io/en/latest/_static/docpack_confluence-logo.png
    :target: https://docpack-confluence.readthedocs.io/en/latest/

**Batch export Confluence pages to AI-ready formats.**

``docpack_confluence`` helps you export Confluence documentation to Markdown/XML files optimized for AI knowledge bases. Whether you're building a RAG pipeline, uploading to ChatGPT/Claude/Gemini, or creating a custom knowledge base, this library handles the heavy lifting.


Why Use This Library?
------------------------------------------------------------------------------
- **Precise Selection**: Use gitignore-style ``include``/``exclude`` patterns to export exactly the pages you need
- **AI-Ready Output**: Generates XML-wrapped Markdown with source URLs and metadata
- **All-in-One Export**: Merge all pages into a single file for easy drag-and-drop to AI platforms
- **Multi-Space Support**: Export from multiple Confluence spaces (even different sites) in one operation
- **Deep Hierarchy Support**: Handles Confluence's API depth limitations automatically


Quick Example
------------------------------------------------------------------------------

.. code-block:: python

    from pathlib import Path
    from sanhe_confluence_sdk import Confluence
    from docpack_confluence.api import SpaceExportConfig, ExportSpec

    # Setup client
    client = Confluence(
        url="https://your-domain.atlassian.net",
        username="your-email@example.com",
        password="your-api-token",  # From https://id.atlassian.com/manage-profile/security/api-tokens
    )

    # Export with include/exclude patterns
    spec = ExportSpec(
        space_configs=[
            SpaceExportConfig(
                client=client,
                space_key="DOCS",
                include=[
                    "https://your-domain.atlassian.net/wiki/spaces/DOCS/pages/123/User-Guide/**",
                ],
                exclude=[
                    "https://your-domain.atlassian.net/wiki/spaces/DOCS/pages/456/Internal/**",
                ],
            ),
        ],
        dir_out=Path("./export"),
    )
    spec.export()

    # Output:
    # ./export/
    #   space_key_DOCS/
    #     User Guide ~ Getting Started.xml
    #     User Guide ~ Configuration.xml
    #     ...
    #   all_in_one_knowledge_base.txt  <- Ready for AI platforms!

**Pattern Syntax**:

- ``/**`` - Include page and all descendants
- ``/*`` - Include descendants only (not the page itself)
- No suffix - Include only the specific page


.. _install:

Install
------------------------------------------------------------------------------

.. code-block:: console

    $ pip install docpack-confluence

For full documentation, visit `docpack-confluence.readthedocs.io <https://docpack-confluence.readthedocs.io/>`_.
