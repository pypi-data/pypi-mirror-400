CHANGELOG
=========

PyPI pythonic-fp-gadgets project.

Semantic Versioning
-------------------

Strict 3 digit semantic versioning

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See `Semantic Versioning 2.0.0 <https://semver.org>`_.

Releases and Important Milestones
---------------------------------

PyPI 4.0.2 - 2026-01-TBD
~~~~~~~~~~~~~~~~~~~~~~~~

Docstring improvements based on lessons learned from my PyPI
boring-math-abstract-algebra project.

PyPI v4.0.1 - 2025-12-02
~~~~~~~~~~~~~~~~~~~~~~~~

Move functions out of their own packages to __init__.py (2025-10-13).

- latest_common_ancestor.lca -> first_common_ancestor
- iterate_arguments.ita -> iterate_over_arguments

Unfortunately I forgot to push these changes to PyPI for a
month and a half!

PyPI v3.0.1 - 2025-09-09
~~~~~~~~~~~~~~~~~~~~~~~~

Corrected incorrect dependencies.

PyPI v3.0.0 - 2025-08-31
~~~~~~~~~~~~~~~~~~~~~~~~

Discovered I was not quite compliant with
Python typing 3.12+ conventions.

- No longer explicitly using TypeVar directly.

  - Removed Unions with Never from .py files

    - the "happy path" returns just types (pythonic convention)
    - stubgen actually puts them back in .pyi files

- renamed it.it -> iterate_arguments.ita
- renamed lca.latest_common_ancestor -> latest_common_ancestor.lca

PyPI v2.2.0 - 2025-08-30
~~~~~~~~~~~~~~~~~~~~~~~~

Moved for pythonic_fp.gadgets package to a new GitHub repo,
pythonic-fp-gadgets. Replaced it with the empty Python
module pythonic_fp.name_claim in pythonic-fp.

The gadgets package being different from the other namespace
packages was throwing off my workflow.

- added function it.it
- added function lca.latest_common_ancestor

Update - 2025-08-09
~~~~~~~~~~~~~~~~~~~

Preparing for upcoming PyPI release for gadgets.

- decided to make gadget's pyproject.toml the exemplar for rest of pythonic-fp namespace
- pythonic_fp.gadget works with previous and next release of singletons

PyPI v1.1.0 - 2025-08-02
~~~~~~~~~~~~~~~~~~~~~~~~

Released pythonic-fp v1.1.0 which contains pythonic_fp.gadgets package.

Update - 2025-08-01
~~~~~~~~~~~~~~~~~~~

Added package pythonic_fp.gadgets to the "name-claim" PyPI
project pythonic-fp. The gadgets library is for simple,
but useful, functions and data structures with minimal
dependencies.
