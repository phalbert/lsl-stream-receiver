# Contributing Guidelines

Welcome to the LSL Stream Receiver project! We're excited to have you contribute to this open-source research tool. This document provides detailed guidelines for contributing to the project.

## 📋 Table of Contents

- [Getting Started](#-getting-started)
- [Development Workflow](#-development-workflow)
- [Code Standards](#-code-standards)
- [Testing Guidelines](#-testing-guidelines)
- [Documentation](#-documentation)
- [Pull Request Process](#-pull-request-process)
- [Issue Management](#-issue-management)
- [Community Guidelines](#-community-guidelines)
- [Recognition](#-recognition)

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- **Python 3.8+** installed
- **Git** for version control
- **GitHub account** for pull requests
- **Basic understanding** of LSL (Lab Streaming Layer)

### Development Environment Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/lsl-stream-receiver.git
   cd lsl-stream-receiver
   ```

3. **Set up the development environment**:
   ```bash
   make setup          # Install dependencies
   make dev           # Start development server
   ```

4. **Verify your setup**:
   ```bash
   make health        # Run health checks
   make test          # Run tests
   make lint          # Check code quality
   ```

### Project Structure Overview

```
lsl-stream-receiver/
├── lsl_receiver/           # Core Python library
│   ├── __init__.py
│   ├── core.py            # Main StreamManager class
│   ├── data_logger.py     # Data logging functionality
│   └── quality_assessor.py # Quality assessment
├── streamlit_app/         # Web interface
│   ├── app.py            # Main Streamlit application
│   └── config.py         # Configuration management
├── examples/             # Usage examples
│   ├── basic_receiver.py
│   ├── csv_logger.py
│   └── real_time_plotter.py
├── docs/                # Documentation
│   ├── README.md        # Technical documentation
│   ├── contributing.md  # This file
│   └── quick_start.md   # User guide
└── tests/              # Test suite
    ├── test_core.py
    └── test_integration.py
```

## 🔄 Development Workflow

### 1. Create Feature Branches

Always create feature branches for your work:

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description

# Or for documentation
git checkout -b docs/update-readme
```

### 2. Make Changes

- **Small, focused changes**: Each PR should address one specific issue
- **Follow coding standards**: Use the project's style and conventions
- **Add tests**: Include tests for new functionality
- **Update documentation**: Keep docs in sync with code changes

### 3. Test Your Changes

```bash
# Run all tests
make test

# Run specific test files
python -m pytest tests/test_core.py

# Run with coverage
python -m pytest --cov=lsl_receiver tests/

# Run linting
make lint
make format
```

### 4. Commit and Push

```bash
# Stage your changes
git add .

# Commit with clear message
git commit -m "Add: Feature description

- What was changed
- Why it was changed
- How it impacts users"

# Push to your fork
git push origin feature/your-feature-name
```

### 5. Create Pull Request

1. **Navigate to the original repository** on GitHub
2. **Click "Compare & pull request"**
3. **Fill out the PR template**:
   - Clear title and description
   - Link to related issues
   - Screenshots for UI changes
   - Testing instructions

## 📏 Code Standards

### Python Style Guidelines

- **PEP 8**: Follow Python Enhancement Proposal 8
- **Black formatting**: Use `black` for consistent code formatting
- **Type hints**: Include type annotations for all functions
- **Docstrings**: Use Google-style docstrings

**Example function with proper formatting:**

```python
from typing import Dict, List, Optional
import numpy as np

def process_stream_data(
    stream_data: Dict[str, np.ndarray],
    sampling_rate: float,
    remove_outliers: bool = True,
) -> Dict[str, np.ndarray]:
    """
    Process incoming stream data with optional outlier removal.

    Args:
        stream_data: Dictionary mapping stream names to data arrays
        sampling_rate: Expected sampling rate in Hz
        remove_outliers: Whether to apply outlier detection

    Returns:
        Dictionary with processed data arrays

    Raises:
        ValueError: If sampling rate is invalid
        KeyError: If required streams are missing
    """
    if sampling_rate <= 0:
        raise ValueError("Sampling rate must be positive")

    processed_data = {}

    for stream_name, data in stream_data.items():
        # Apply processing logic
        processed = _apply_filters(data, sampling_rate)

        if remove_outliers:
            processed = _remove_outliers(processed)

        processed_data[stream_name] = processed

    return processed_data
```

### Import Organization

Organize imports in this order:
1. Standard library imports
2. Third-party imports
3. Local imports

```python
# Standard library
import os
import sys
from typing import Dict, List

# Third-party imports
import numpy as np
import pandas as pd
from pylsl import StreamInlet

# Local imports
from lsl_receiver.core import StreamManager
from lsl_receiver.utils import validate_stream_info
```

### Naming Conventions

- **Variables**: `snake_case` (e.g., `stream_data`, `sampling_rate`)
- **Functions**: `snake_case` (e.g., `process_data()`, `validate_input()`)
- **Classes**: `PascalCase` (e.g., `StreamManager`, `DataLogger`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_BUFFER_SIZE`)
- **Private functions**: Start with underscore (e.g., `_internal_helper()`)

## 🧪 Testing Guidelines

### Test Structure

```python
import pytest
import numpy as np
from lsl_receiver.core import StreamManager

class TestStreamManager:
    """Test cases for StreamManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = StreamManager()
        self.test_data = np.random.randn(100, 8)

    def test_initialization(self):
        """Test StreamManager initialization."""
        assert self.manager.is_running is False
        assert self.manager.streams == {}

    def test_start_receiving(self):
        """Test starting data reception."""
        result = self.manager.start_receiving()
        assert result is True
        assert self.manager.is_running is True

    def test_invalid_sampling_rate(self):
        """Test error handling for invalid sampling rates."""
        with pytest.raises(ValueError, match="Sampling rate must be positive"):
            self.manager._validate_sampling_rate(-1.0)

    @pytest.mark.parametrize("n_samples", [1, 10, 100])
    def test_buffer_sizes(self, n_samples):
        """Test different buffer sizes."""
        # Test implementation
        pass
```

### Testing Best Practices

- **Test one thing per test**: Each test should verify one behavior
- **Use descriptive names**: Test names should explain what's being tested
- **Include edge cases**: Test boundary conditions and error cases
- **Mock external dependencies**: Use mocks for LSL streams and file I/O
- **Test error conditions**: Verify proper error handling

### Test Coverage

Aim for comprehensive test coverage:
- **Unit tests**: 90%+ coverage for individual functions
- **Integration tests**: Test component interactions
- **Regression tests**: Prevent reintroduction of old bugs
- **Performance tests**: Ensure changes don't degrade performance

## 📚 Documentation

### Docstring Standards

Use Google-style docstrings for all public functions and classes:

```python
class StreamManager:
    """Manages multiple LSL streams with synchronized data reception.

    This class provides the main interface for discovering, connecting to,
    and receiving data from multiple Lab Streaming Layer streams. It handles
    stream reconnection, data buffering, and quality monitoring.

    Attributes:
        streams (Dict[str, StreamInlet]): Connected stream inlets
        is_running (bool): Whether data reception is active
        buffer_size (int): Size of data buffer for each stream

    Example:
        >>> manager = StreamManager()
        >>> manager.connect_to_streams(discovered_streams)
        >>> manager.start_receiving()
        >>> data = manager.get_latest_data()
    """

    def start_receiving(self) -> bool:
        """Start receiving data from connected streams.

        Returns:
            bool: True if started successfully, False otherwise

        Raises:
            RuntimeError: If already running or no streams connected
        """
        # Implementation
        pass
```

### Documentation Updates

When adding or modifying features:
1. **Update docstrings** for affected functions
2. **Update README.md** with usage examples
3. **Add code examples** to appropriate sections
4. **Include screenshots** for UI changes
5. **Update API documentation** in docs/README.md

## 🔀 Pull Request Process

### PR Requirements

1. **Clear description**: Explain what was changed and why
2. **Related issues**: Link to any related GitHub issues
3. **Testing**: All tests pass and new tests are included
4. **Documentation**: Updated docstrings and user-facing docs
5. **Screenshots**: Include before/after images for UI changes

### PR Template

Use this template for your pull requests:

```markdown
## Description

[Brief description of changes]

## Related Issues

- Closes #123 (if applicable)
- Related to #456 (if applicable)

## Changes Made

- Added new feature X to class Y
- Fixed bug in function Z
- Updated documentation for method W

## Testing

- Added unit tests for new functionality
- Verified integration with existing components
- Tested edge cases and error conditions

## Screenshots

[Include screenshots for UI changes]

## Checklist

- [x] Tests pass
- [x] Code formatted with black
- [x] Linting passes
- [x] Documentation updated
- [x] No breaking changes
```

### Review Process

1. **Automated checks**: CI/CD runs tests and linting
2. **Maintainer review**: Code reviewed for style and functionality
3. **Feedback integration**: Address any requested changes
4. **Final approval**: Approved PRs are merged by maintainers

## 🎫 Issue Management

### Reporting Bugs

When reporting bugs, include:
- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, etc.)
- **Minimal example** that reproduces the issue

### Feature Requests

For new features:
- **Problem description**: What problem does this solve?
- **Proposed solution**: How would it work?
- **Alternatives considered**: Other approaches evaluated
- **Additional context**: Why this feature is important

### Issue Labels

We use these labels to categorize issues:
- `bug`: Confirmed bugs or issues
- `enhancement`: New features or improvements
- `documentation`: Documentation updates
- `question`: Questions from users
- `good first issue`: Suitable for new contributors
- `help wanted`: Needs community assistance

## 🤝 Community Guidelines

### Code of Conduct

We expect all contributors to:
- **Be respectful**: Treat others with kindness and consideration
- **Be collaborative**: Work together to achieve common goals
- **Be constructive**: Provide helpful feedback and suggestions
- **Be inclusive**: Welcome diverse perspectives and experiences
- **Be patient**: Understand that people work at different paces

### Communication

- **GitHub Issues**: Use for bug reports and feature requests
- **Pull Requests**: Use for code changes and discussions
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Email**: Contact maintainers for sensitive or private matters

### Getting Help

If you need help:
1. **Check existing issues** for similar problems
2. **Read the documentation** thoroughly
3. **Try the examples** in the examples/ directory
4. **Ask in GitHub Discussions** for usage questions
5. **Create an issue** for bugs or feature requests

## 🏆 Recognition

### Contributor Recognition

Contributors are recognized through:
- **GitHub contributor graphs** and statistics
- **Changelog entries** for significant contributions
- **README acknowledgments** for major contributors
- **Lab meeting shoutouts** for outstanding work
- **Co-authorship** on research papers using the tool

### Contribution Levels

- **Contributor**: Submitted code, documentation, or bug reports
- **Active Contributor**: Regular contributions over time
- **Core Contributor**: Significant impact on project development
- **Maintainer**: Project leadership and decision-making

### Hall of Fame

Major contributors are listed in the README and project documentation. We especially recognize:
- First-time contributors to open source
- Researchers contributing domain expertise
- Developers improving code quality and architecture
- Documentation writers making the project more accessible

## 📜 License and Copyright

By contributing to this project, you agree that:
- Your contributions will be licensed under the same MIT License
- You have the right to contribute the code you're submitting
- You understand that contributions become part of the project
- You may be credited for your work in the project documentation

---

Thank you for contributing to the LSL Stream Receiver project! Your work helps advance research and makes this tool better for the entire community.

*Last updated: $(date)*
