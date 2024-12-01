# Contributing to CloverAI

Thank you for your interest in contributing to CloverAI! We're excited to welcome you to our community. This guide will help you get started with contributing to our AI governance framework.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Issues](#reporting-issues)
- [Style Guide](#style-guide)
- [Community](#community)

## Code of Conduct

CloverAI follows an inclusive, respectful Code of Conduct. By participating, you are expected to:
- Be respectful and inclusive of differing viewpoints
- Use welcoming and inclusive language
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the Repository**
   ```bash
   git clone https://github.com/your-username/CloverAI.git
   cd CloverAI
   git remote add upstream https://github.com/shankypedia/CloverAI.git
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-fix-name
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Development Setup

1. **Environment Setup**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   # or
   .\venv\Scripts\activate  # Windows
   ```

2. **Install Development Tools**
   ```bash
   pip install black isort pytest pytest-cov flake8
   ```

3. **Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

## Contribution Guidelines

### Types of Contributions
- Bug fixes
- Feature implementations
- Documentation improvements
- Test coverage improvements
- Performance optimizations

### Best Practices
1. **Code Quality**
   - Write clean, readable code
   - Follow PEP 8 style guide
   - Add type hints to new functions
   - Include docstrings for all functions

2. **Testing**
   - Add unit tests for new features
   - Ensure all tests pass locally
   - Maintain or improve test coverage
   - Test edge cases

3. **Documentation**
   - Update relevant documentation
   - Add docstrings to new code
   - Include example usage where appropriate
   - Update README if needed

4. **Commit Messages**
   ```
   type(scope): brief description

   Detailed description of changes and their impact.
   
   Fixes #issue_number
   ```
   Types: feat, fix, docs, style, refactor, test, chore

## Pull Request Process

1. **Before Submitting**
   - Update your fork with upstream changes
   - Run all tests locally
   - Run code formatting tools
   - Update documentation

2. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Added new tests
   - [ ] All tests passing
   - [ ] No regression

   ## Documentation
   - [ ] Updated relevant docs
   - [ ] Added docstrings
   - [ ] Updated README
   ```

3. **Review Process**
   - A maintainer will review your PR
   - Address any requested changes
   - Once approved, a maintainer will merge

## Reporting Issues

1. **Bug Reports**
   ```markdown
   ## Bug Description
   Clear description of the bug

   ## Steps to Reproduce
   1. Step 1
   2. Step 2
   3. ...

   ## Expected Behavior
   What should happen

   ## Actual Behavior
   What actually happens

   ## Environment
   - OS: [e.g., Ubuntu 20.04]
   - Python version: [e.g., 3.8.5]
   - CloverAI version: [e.g., 1.0.0]
   ```

2. **Feature Requests**
   ```markdown
   ## Feature Description
   Clear description of the proposed feature

   ## Use Case
   Why this feature would be useful

   ## Proposed Implementation
   Optional: Your ideas on how to implement
   ```

## Style Guide

### Python Code Style
- Follow PEP 8
- Use type hints
- Maximum line length: 88 characters
- Use docstring format:
  ```python
  def function_name(param1: type, param2: type) -> return_type:
      """
      Brief description.

      Args:
          param1: Description
          param2: Description

      Returns:
          Description of return value

      Raises:
          ExceptionType: Description
      """
  ```

### Documentation Style
- Clear and concise
- Include code examples
- Use proper markdown formatting
- Keep tutorial sections beginner-friendly

## Community

- **Discussions**: Use GitHub Discussions for questions
- **Discord**: Join our community chat
- **Issues**: GitHub Issues for bugs and features
- **Email**: maintainers@cloverai.org

### Recognition
Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Community showcase

## License
By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

Thank you for contributing to CloverAI! Your help makes this project better for everyone. If you have any questions, feel free to reach out to the maintainers.
