# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.13.1] - 2026-01-07]

### Added

- Netbox 4.5 Support

## [0.13.0] - 2025-11-04]

## Fixed 

- version parsing error: `Version` instead of `str`.

## [0.12.0] - 2025-11-04]

### Fixed

- Version parsing to be compatible with docker container

## [0.11.0] - 2025-11-04] 

- README.md fixes

## [0.0.10] - 2025-11-04] 

### Fixed

- Netbox 4.4 Compatibility "from netbox.views.generic import ObjectChildrenView"

## [0.0.9] - 2024-11-12

### Fixed

- pynetbox API usage bug `The requested url: .../nb-itsm/configuration-item/ could not be found`. Was caused by underscore instead of dash in `configuration_item`.

## [0.0.2] - 2024-11-06

### Added

- Added TenantGroup reference in Service

### Removed

- Removed backup_profile
- Removed Ports & Protocol for Application

### Changed

- Changed Plugin name & name
- Fixed typos and refactored various sections of the code
- Fixed empty mermaid diagrams

### Fixed

- broken API URL to work with pynetbox

## [0.0.1] - 2024-09-17

### Changed

- Forked from https://github.com/renatoalmeidaoliveira/nbservice/
  in version: [42aa8875c2289a797ec33f3045cb374d52a7efea](https://github.com/renatoalmeidaoliveira/nbservice/commit/42aa8875c2289a797ec33f3045cb374d52a7efea)

[unreleased]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/compare/v0.0.1...HEAD
[0.0.9]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/tags/v0.0.10
[0.0.9]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/tags/v0.0.9
[0.0.2]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/tags/v0.0.2
[0.0.1]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/tags/v0.0.1
[0.0.0]: https://projects.cispa.saarland/it/services/itsm/netbox-plugin-itsm/-/tags/v0.0.0
