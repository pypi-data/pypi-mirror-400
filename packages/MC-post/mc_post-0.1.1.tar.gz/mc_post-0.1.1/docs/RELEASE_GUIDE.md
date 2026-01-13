# MCPost Release Guide

This document outlines the process for releasing new versions of MCPost, including backward compatibility policies and migration guides.

## Release Process

### 1. Pre-Release Checklist

Before creating a new release, ensure the following:

- [ ] All tests pass on CI/CD
- [ ] Code coverage is above 80%
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with new version
- [ ] Version number follows semantic versioning
- [ ] Backward compatibility is maintained or breaking changes are documented
- [ ] Migration guide is created for breaking changes (if any)

### 2. Version Numbering

MCPost follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backward compatible manner
- **PATCH** version when you make backward compatible bug fixes

#### Version Examples

- `1.0.0` - Initial stable release
- `1.1.0` - New features, backward compatible
- `1.1.1` - Bug fixes, backward compatible
- `2.0.0` - Breaking changes, not backward compatible

### 3. Release Steps

#### Step 1: Update Version

1. Update version in `mcpost/_version.py`:
   ```python
   __version__ = "1.1.0"
   ```

2. Update `VERSION_INFO` tuple:
   ```python
   VERSION_INFO = (1, 1, 0)
   ```

#### Step 2: Update CHANGELOG.md

1. Move items from `[Unreleased]` to new version section
2. Add release date
3. Create new empty `[Unreleased]` section

Example:
```markdown
## [Unreleased]

## [1.1.0] - 2024-02-15

### Added
- New chunked processing for large datasets
- Performance improvements for GSA pipeline

### Fixed
- Memory leak in GP fitting
- Edge case in Sobol sampling
```

#### Step 3: Create Release

1. Commit changes:
   ```bash
   git add mcpost/_version.py CHANGELOG.md
   git commit -m "Release v1.1.0"
   ```

2. Create and push tag:
   ```bash
   git tag v1.1.0
   git push origin main
   git push origin v1.1.0
   ```

3. The GitHub Actions workflow will automatically:
   - Run tests
   - Build packages
   - Create GitHub release
   - Publish to PyPI

#### Step 4: Verify Release

1. Check GitHub release page
2. Verify PyPI upload
3. Test installation:
   ```bash
   pip install mcpost==1.1.0
   python -c "import mcpost; print(mcpost.__version__)"
   ```

## Backward Compatibility Policy

### Commitment

MCPost is committed to maintaining backward compatibility within major versions. This means:

- **Minor versions** (1.0.0 → 1.1.0): No breaking changes
- **Patch versions** (1.1.0 → 1.1.1): Only bug fixes, no API changes
- **Major versions** (1.x.x → 2.0.0): May include breaking changes

### What We Consider Breaking Changes

- Removing public functions or classes
- Changing function signatures (parameters, return types)
- Changing default behavior that affects results
- Removing or renaming modules
- Changing exception types for existing error conditions

### What We Don't Consider Breaking Changes

- Adding new optional parameters with sensible defaults
- Adding new functions or classes
- Improving error messages
- Performance improvements
- Bug fixes that correct incorrect behavior
- Changes to private APIs (functions/classes starting with `_`)

### Deprecation Process

When we need to make breaking changes:

1. **Deprecation Warning**: Mark old API as deprecated with warning
2. **Grace Period**: Maintain deprecated API for at least one minor version
3. **Removal**: Remove deprecated API in next major version

Example deprecation:
```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated and will be removed in v2.0.0. "
        "Use new_function instead.",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

## Migration Guides

### General Migration Strategy

When upgrading MCPost versions:

1. **Read the CHANGELOG**: Check for breaking changes
2. **Test thoroughly**: Run your existing code with new version
3. **Update gradually**: Fix deprecation warnings before they become errors
4. **Use version pinning**: Pin to specific versions in production

### Version-Specific Migration Guides

#### Migrating to v2.0.0 (Future)

*This section will be updated when v2.0.0 is released.*

**Breaking Changes:**
- TBD

**Migration Steps:**
- TBD

#### Migrating from Legacy Scripts

If you're migrating from the original `gsa_pipeline.py` and `mc_int.py` scripts (legacy compatibility mocks are available in `tests/legacy_mocks/` for reference):

**Before (Legacy):**
```python
# Old script usage
from gsa_pipeline import gsa_for_target
from mc_int import monte_carlo_integral

result = gsa_for_target(X, y, param_names)
integral = monte_carlo_integral(params, data, p_target)
```

**After (MCPost Package):**
```python
# New package usage
from mcpost import gsa_for_target, monte_carlo_integral

result = gsa_for_target(X, y, param_names)  # Same API
integral = monte_carlo_integral(params, data, p_target)  # Same API
```

**Benefits of Migration:**
- Better error handling and validation
- Improved performance and memory efficiency
- Type hints and better IDE support
- Comprehensive testing and reliability
- Regular updates and bug fixes

## Release Automation

### GitHub Actions Workflows

MCPost uses automated workflows for releases:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs on every push and PR
   - Tests across multiple Python versions and OS
   - Checks code quality and coverage

2. **Release Workflow** (`.github/workflows/release.yml`):
   - Triggers on version tags (`v*`)
   - Builds and tests packages
   - Creates GitHub release
   - Publishes to PyPI

### Required Secrets

Configure these secrets in GitHub repository settings:

- `PYPI_API_TOKEN`: PyPI API token for package publishing
- `CODECOV_TOKEN`: Codecov token for coverage reporting (optional)

### Manual Release (Emergency)

If automated release fails, you can release manually:

1. Build package:
   ```bash
   python -m build
   ```

2. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

3. Create GitHub release manually through web interface

## Post-Release Tasks

After each release:

1. **Announce**: Update documentation and announce on relevant channels
2. **Monitor**: Watch for issues and user feedback
3. **Plan**: Update roadmap and plan next release
4. **Archive**: Archive old documentation versions if needed

## Hotfix Process

For critical bugs requiring immediate release:

1. Create hotfix branch from release tag:
   ```bash
   git checkout -b hotfix/v1.1.1 v1.1.0
   ```

2. Fix the bug and test thoroughly

3. Update version to patch level (1.1.0 → 1.1.1)

4. Follow normal release process

5. Merge hotfix back to main:
   ```bash
   git checkout main
   git merge hotfix/v1.1.1
   ```

## Support Policy

- **Latest major version**: Full support with new features and bug fixes
- **Previous major version**: Security fixes and critical bug fixes for 1 year
- **Older versions**: No official support, but community contributions welcome

## Questions and Support

For questions about releases:

- Check existing [GitHub Issues](https://github.com/mcpost/mcpost/issues)
- Create new issue with `release` label
- Contact maintainers for urgent release issues