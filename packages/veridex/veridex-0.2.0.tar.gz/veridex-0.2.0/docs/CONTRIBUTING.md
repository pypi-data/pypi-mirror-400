# Contributing to Veridex

Thank you for your interest in contributing to Veridex! This document provides guidelines for contributing to the project.

## Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/veridex.git
   cd veridex
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev,text,image,audio]"
   ```

## Code Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use Black for code formatting: `black veridex/ tests/`
- Use flake8 for linting: `flake8 veridex/`
- Add type hints where possible
- Write docstrings for all public APIs

## Testing

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=veridex --cov-report=term
```

## Adding a New Detector

1. Create a new file in the appropriate module (`text/`, `image/`, or `audio/`)
2. Inherit from `BaseSignal`
3. Implement required methods:
   - `name` property
   - `dtype` property
   - `run(input_data)` method
   - `check_dependencies()` method

Example:
```python
from veridex.core.signal import BaseSignal, DetectionResult

class MyDetector(BaseSignal):
    @property
    def name(self) -> str:
        return "my_detector"
    
    @property
    def dtype(self) -> str:
        return "text"  # or "image", "audio"
    
    def check_dependencies(self) -> None:
        # Check for required packages
        pass
    
    def run(self, input_data) -> DetectionResult:
        # Implementation
        return DetectionResult(
            score=0.5,
            confidence=0.8,
            metadata={}
        )
```

4. Add tests in `tests/`
5. Update module `__init__.py` to export the new detector
6. Add documentation

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add tests
4. Run the test suite
5. Format code: `black veridex/ tests/`
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted with Black
- [ ] No linting errors
- [ ] CHANGELOG.md updated
- [ ] All tests passing

## Bug Reports

When filing a bug report, include:
- Python version
- Veridex version
- Operating system
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages/stack traces

## Feature Requests

When requesting a feature:
- Check existing issues first
- Provide clear use case
- Consider implementation complexity
- Be open to discussion

## Code of Conduct

- Be respectful and professional
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

## Questions?

- Open a GitHub issue
- Check existing documentation
- Review examples in `examples/`

Thank you for contributing to Veridex! 🎉
