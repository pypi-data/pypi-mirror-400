# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/compare/v0.2.1...v0.3.0) (2026-01-08)


### Features

* Implement precise UTM georeferencing and add validation tests ([953dca6](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/commit/953dca66209347cf8a26a2367b889389dbd4eb0e))

## [0.2.1](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/compare/v0.2.0...v0.2.1) (2026-01-08)


### Documentation

* fix links and improve readme ([dc24bc1](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/commit/dc24bc1d380fb39edbf650f2cc92f228546f81ef))

## [0.2.0](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/compare/v0.1.0...v0.2.0) (2026-01-08)


### Bug Fixes

* **deps:** add missing 'just' ([0b253d0](https://github.com/RISE-Dependable-Transport-Systems/osm-to-xodr/commit/0b253d05865a2c97144af5c850ac3123323685ce))

## [0.1.0] - Unreleased

### Added

- Initial release
- CLI tool for converting OSM files to OpenDRIVE format
- Two-pass conversion with plain roads and objects/signals
- Support for SUMO netconvert parameters via environment variables
- Post-processing to convert objects to signals for CARLA compatibility
