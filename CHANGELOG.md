# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2021-01-08

### Added

- Support for new Revolut CSV format.
- 2021 exchange rates cache

## [0.5.0] - 2020-03-21

### Added

- Support for SELL CANCEL and SC activities

## [0.4.0] - 2020-02-16

### Added

- Support for multiple parsers
- Display profit/loss in currency

### Fixed

- Fix missing requirement on Ubuntu Server 20.04

## [0.3.0] - 2020-02-08

### Added

- SSO activities support
- Improved SSP activities calculation

### Fixed

- Fix missing description on cash activities
- Fix parsing company where additional purchase info is missing from description

## [0.2.0] - 2020-02-08

### Added

- SSO activities added to unsupported list
- Improved error handling

## [0.1.0] - 2020-02-05

### Added

- Support for all DIV activities such as DIVCGL, DIVCGS, DIVFT, DIVROC.

## [0.0.1] - 2020-02-05

### Added

- GUI.
- Support for parser plug-ins.
- Trading 212 platform support.
- Support for SSP and MAS activities.
- Improved dividend listing.
- Support for cached exchange rates.

### Fixed

- KeyError: 'paid_tax_amount'
- Revolut DIV amount already includes paid tax.
- Many PDF parsing issues.
- Documentation errors.
