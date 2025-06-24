# Project Management Guidelines

This file defines project management standards and tooling requirements for maintaining code quality, dependency management, and development workflows. These guidelines ensure consistent project setup and maintenance practices.

## Python Environment Management

### 1. UV Tool Usage
Use the **uv** tool for all Python project management tasks:

#### Project Initialization
```bash
# Create new Python project
uv init project-name

# Initialize in existing directory
uv init
```

#### Dependency Management
```bash
# Add dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Install all dependencies
uv sync

# Update dependencies
uv lock --upgrade
```

#### Environment Management
```bash
# Create and activate virtual environment
uv venv

# Run commands in the environment
uv run python script.py
uv run pytest

# Install project in editable mode
uv pip install -e .
```

**CRITICAL**: Always use `uv` instead of `pip`, `pipenv`, `poetry`, or other Python package managers for consistency.

## Code Quality Standards

### 2. Ruff Linting
Use **ruff** for code linting and issue detection:

#### Linting Command
```bash
# Check for issues and auto-fix when possible
uvx ruff check --fix
```

#### Required Workflow
1. Run linting before any code commit
2. Address all linting issues before proceeding
3. Auto-fix issues when ruff provides fixes
4. Manually resolve issues that require code changes

**Configuration**: Place ruff configuration in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "W", "C90", "I", "N", "UP", "YTT", "S", "BLE", "FBT", "B", "A", "COM", "C4", "DTZ", "T10", "EM", "EXE", "FA", "ISC", "ICN", "G", "INP", "PIE", "T20", "PYI", "PT", "Q", "RSE", "RET", "SLF", "SLOT", "SIM", "TID", "TCH", "INT", "ARG", "PTH", "TD", "FIX", "ERA", "PD", "PGH", "PL", "TRY", "FLY", "NPY", "AIR", "PERF", "FURB", "LOG", "RUF"]
ignore = ["E501", "COM812", "ISC001"]
```

### 3. Ruff Formatting
Use **ruff** for code formatting:

#### Formatting Command
```bash
# Format all Python files
uvx ruff format
```

#### Required Workflow
1. Run formatting before any code commit
2. Format applies consistent style across all files
3. No manual formatting adjustments needed after ruff format
4. Formatting should be before after linting fixes

## Issue Resolution Protocol

### 4. Three-Try Rule for Linting Issues
When encountering linting issues, follow this strict protocol:

#### Attempt 1: Auto-Fix
```bash
uvx ruff check --fix
```
- Let ruff automatically fix issues where possible
- Review the changes to ensure they're appropriate
- Re-run to check if all issues are resolved

#### Attempt 2: Manual Code Changes
If issues remain after auto-fix:
- Read the specific linting error messages
- Make targeted code changes to address each issue
- Focus on the root cause, not just silencing warnings
- Re-run linting to verify fixes

#### Attempt 3: Configuration Adjustment
If issues persist after manual fixes:
- Consider if the linting rule is appropriate for the specific case
- Add specific `# noqa` comments for unavoidable violations
- Update `pyproject.toml` configuration if rule conflicts with project needs
- Document the reasoning for any configuration changes

#### Escalation After 3 Tries
If linting issues cannot be resolved after 3 attempts:
1. **STOP** further attempts to fix the issues
2. Document the specific errors encountered
3. Document all attempted solutions
4. **RAISE TO USER** with detailed information:
   - Exact linting error messages
   - Code sections causing issues
   - All attempted fixes and their results
   - Recommended next steps

**Example escalation message:**
```
Unable to resolve linting issues after 3 attempts:

Errors:
- src/module.py:45:12: E731 Do not assign a lambda expression, use a def
- src/module.py:67:8: F841 Local variable 'unused_var' is assigned to but never used

Attempts made:
1. Auto-fix: Resolved 8/10 issues, 2 remain
2. Manual fix: Removed unused_var, lambda issue persists due to API constraint
3. Configuration: Added noqa comment, but issue relates to security concern

Recommendation: Review lambda usage for security implications before suppressing rule.
```

## Development Workflow

### 5. Standard Development Process
Follow this process for all code changes:

1. **Setup**: Ensure `uv` environment is active
2. **Development**: Write/modify code
3. **Linting**: Run `uvx ruff check --fix`
4. **Formatting**: Run `uvx ruff format`
5. **Testing**: Run tests with `uv run pytest`
6. **Commit**: Only commit if all steps pass

### 6. CI/CD Integration
Include these checks in automated workflows:
```yaml
# Example GitHub Actions step
- name: Lint and Format
  run: |
    uvx ruff check --diff
    uvx ruff format --diff
```

## File Structure Requirements

### 7. Required Configuration Files
Every Python project MUST include:

- `pyproject.toml` - Project metadata and tool configuration
- `.python-version` - Python version specification for uv
- `uv.lock` - Locked dependency versions (commit to version control)

### 8. Environment Files
- `.env.example` - Template for environment variables
- `.gitignore` - Include standard Python ignores plus uv-specific patterns

## Enforcement Checklist

Before any code submission, verify:
- [ ] `uv sync` runs without errors
- [ ] `uvx ruff check --fix` passes with no remaining issues
- [ ] `uvx ruff format` has been applied
- [ ] All tests pass with `uv run pytest`
- [ ] No hardcoded secrets or credentials
- [ ] Documentation updated for any new dependencies

## Troubleshooting

### Common Issues
1. **uv not found**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. **Ruff conflicts**: Check `pyproject.toml` configuration
3. **Lock file conflicts**: Run `uv lock` to regenerate
4. **Environment issues**: Delete `.venv` and run `uv sync`

### Getting Help
If issues persist beyond the three-try rule or standard troubleshooting:
1. Document the exact error messages
2. Include relevant configuration files
3. Provide steps to reproduce the issue
4. Escalate to project maintainer or senior developer
