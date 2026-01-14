# Contributing to URL Content Type Detector

Thank you for your interest in contributing! We welcome contributions from everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please [open an issue](https://github.com/krsahil/url-content-type-detector/issues/new) with:
- A clear title and description
- Steps to reproduce the issue
- Expected vs actual behavior
- Python version and OS

### Suggesting Features

Have an idea? [Open an issue](https://github.com/krsahil/url-content-type-detector/issues/new) and describe:
- The feature you'd like to see
- Why it would be useful
- Any implementation ideas (optional)

### Submitting Code

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone it
git clone https://github.com/YOUR-USERNAME/url-content-type-detector.git
cd url_content_type_detector
```

#### 2. Set Up Development Environment

```bash
# Install dependencies
uv pip install -e .
uv pip install pytest
```

#### 3. Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name
```

#### 4. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add tests for new features
- Update documentation if needed

#### 5. Test Your Changes

```bash
# Run tests
pytest tests/
```

#### 6. Commit Your Changes

```bash
git add .
git commit -m "Add: brief description of your changes"
```

Use clear commit messages:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for updates to existing features
- `Docs:` for documentation changes

#### 7. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a pull request on GitHub with:
- A clear title
- Description of what changed
- Any related issue numbers (e.g., "Fixes #123")

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and simple

## Testing

- Write tests for new features
- Ensure all tests pass before submitting
- Test with Python 3.8+ if possible

## Questions?

Feel free to [open an issue](https://github.com/krsahil/url-content-type-detector/issues) or email **krsahil8825@gmail.com**.

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

---

Thank you for contributing! 🎉
