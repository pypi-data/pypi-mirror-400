=====================
TypeChecked Changelog
=====================

0.9.0-beta (2026-01-08)
=======================

- Updated details of ImmutableTypedDict to clarify usage of the `__immutable__`
  key for marking TypedDicts as immutable and to simplify the internal implementation
  to use NotRequired[Never] as the type of the `__immutable__` key to provide
  a clearer type hint for static type checkers.
- Centralized import of Never, NotRequired, Required, and ReadOnly types to
  typechecked._types to minimize repetitive versioned imports across modules.

0.8.1-beta.1 (2026-01-08)
=========================

- Documentation fix to README.rst for PyPI compatibility.

0.8.0-beta.1 (2026-01-08)
=========================

- Initial beta release of version 0.8.0.
