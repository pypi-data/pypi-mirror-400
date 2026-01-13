# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-01-07

### Added

- Initial release with Django 5.0+ support
- Firebird 2.5, 3.0, 4.0, and 5.0+ compatibility
- Full Django ORM support (models, queries, aggregations)
- Database migrations support
- `inspectdb` command for introspecting existing databases
- `inspectdb_firebird` enhanced command with foreign key ordering
- Native BOOLEAN support for Firebird 3.0+
- Timezone support for Firebird 4.0+
- SKIP LOCKED support for Firebird 5.0+
- Window functions and FILTER clause for Firebird 3.0+
- Expression indexes with COMPUTED BY syntax
- Partial indexes with WHERE clause
- 279 unit tests

### Notes

- JSONField is not supported (Firebird lacks native JSON type)
- DISTINCT ON is not supported (Firebird limitation)
- DDL operations cannot be rolled back (Firebird auto-commits DDL)

[Unreleased]: https://github.com/joseanoxp/django-firebird-backend/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/joseanoxp/django-firebird-backend/releases/tag/v0.1.1
