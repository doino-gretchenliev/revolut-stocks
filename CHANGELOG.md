# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
