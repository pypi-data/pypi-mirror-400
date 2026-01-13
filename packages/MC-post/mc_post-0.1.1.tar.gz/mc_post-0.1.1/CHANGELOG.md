# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-01-05

### Added
- Professional GitHub Pages documentation site with Jekyll
- Comprehensive tutorials: Getting Started and Advanced GSA
- Financial risk analysis example
- Automated documentation deployment workflow
- Repository cleanup with proper .gitignore configuration

### Fixed
- GitHub Actions CI/CD pipeline (updated deprecated actions)
- Jekyll build errors in documentation deployment
- Jupyter notebook JSON parsing issues
- Broken documentation links and repository URLs
- Code complexity issues in CI pipeline

### Changed
- Streamlined CI workflow for faster builds
- Enhanced documentation structure and navigation
- Improved notebook-to-HTML conversion with better templates
- Repository organization (removed development clutter)

### Infrastructure
- Ultra-fast CI focusing on core functionality
- Robust error handling in documentation builds
- Professional documentation site deployment
- Clean repository structure for better user experience

## [0.1.0] - 2024-01-05

### Added
- Initial release of MCPost package
- Core GSA functionality with multiple sensitivity metrics
- Monte Carlo and Quasi-Monte Carlo integration methods
- Modern Python packaging with pyproject.toml
- Comprehensive test suite with property-based tests
- Documentation and examples
- CI/CD workflows for automated testing and release
- Distribution and release infrastructure

### Features
- **Global Sensitivity Analysis**:
  - Mutual Information and Distance Correlation metrics
  - Permutation Importance with Random Forest
  - Gaussian Process surrogates with ARD kernels
  - Sobol' indices for variance-based analysis
  - Partial Dependence Plots for interpretability
  - Chunked processing for large datasets
  
- **Monte Carlo Integration**:
  - Standard Monte Carlo with importance sampling
  - Quasi-Monte Carlo methods (Sobol, Halton)
  - Automatic integration with adaptive strategies
  - Flexible PDF specification
  - Chunked integration for memory efficiency
  
- **Package Infrastructure**:
  - Modern packaging with optional dependencies
  - Type hints and comprehensive documentation
  - Extensive testing with property-based tests
  - Performance optimizations for large datasets
  - Backward compatibility with existing code
  - Extension interfaces for custom methods
  - Automated CI/CD with GitHub Actions
  - PyPI distribution ready