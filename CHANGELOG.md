# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.6] - 2025-08-04

### Added
- Functional badges in README.md for CI status, license, and versions
- Collections requirements with version constraints for `community.general` 10.x
- CHANGELOG documentation with complete release history

### Changed
- **BREAKING**: Requires `community.general` collection version 10.x (11+ removes Proxmox modules)
- Enhanced documentation with prerequisites section for collection installation
- Updated CI/CD workflows to use collections/requirements.yml

### Fixed
- All ansible-lint violations (production profile compliance)
- GitHub Actions CodeQL deprecation warnings (updated to v3)
- Trailing spaces and formatting issues throughout codebase
- Long line violations in Ansible tasks with YAML folded strings
- Ansible-lint configuration compatibility issues
- Yamllint configuration for ansible-lint requirements

## [1.0.5] - 2025-08-03

### Added
- MIT License for free usage
- Comprehensive GitHub infrastructure (issue templates, PR templates, CI/CD workflows)
- Multi-distribution dependency installation support (RHEL, Debian, macOS, SUSE, Arch)
- Hierarchical configuration system with intelligent merging
- English internationalization for global accessibility
- Complete documentation restructure and optimization (800+ → 442 lines)
- Security policies and best practices guide (SECURITY.md)
- Contributing guidelines (CONTRIBUTING.md)
- Automated testing with GitHub Actions (CI/CD)
- Security scanning with Trivy
- Ansible lint configuration and yamllint setup

### Changed
- Documentation language changed from German to English
- README completely restructured for better usability
- Improved error handling and debugging information
- Enhanced CI/CD workflows with multiple Ansible version testing (2.14, 2.15, 2.16)

### Fixed
- Template improvements for better repository handling
- Deployment methods for network interfaces, storage, and users

## [1.0.4] - Previous Release

### Fixed
- Template fixes for better repository handling
- Various bug fixes and improvements

## [1.0.3] - Previous Release

### Fixed
- Typography and minor text corrections

## [1.0.2] - Previous Release

### Changed
- Updates to main task file

## [1.0.1] - Previous Release

### Changed  
- Updates to main task file

## [1.0.0] - Initial Release

### Added
- Automated VM creation on Proxmox VE with Kickstart configurations
- Dynamic storage configuration with LVM support
- Multi-network interface support with VLAN
- Flexible user management with SSH keys
- Rocky Linux 9 optimization
- ISO management and upload functionality
- Hierarchical configuration through defaults, group_vars, and host_vars
