# Contributing to MuleSoft Developer Scripts

Thank you for your interest in contributing! This guide will help you get started.

## 🎯 How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/mulesoft-dev-scripts/issues)
2. If not, create a new issue using the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has already been requested
2. Create a new issue using the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)
3. Describe:
   - The problem it solves
   - Your proposed solution
   - Example use case

### Contributing Code

1. **Fork the repository**
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow the code style of existing scripts
   - Add comments for complex logic
   - Update documentation (README.md) if needed
4. **Test your changes**:
   ```bash
   # Test the script
   python script.py --help
   python script.py --project-path /test/path
   ```
5. **Commit your changes**:
   ```bash
   git commit -m "Add: description of your change"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

## 📝 Code Style Guidelines

### Python Scripts

- Use Python 3.7+ features
- Follow PEP 8 style guide
- Maximum line length: 120 characters
- Use descriptive variable names
- Add docstrings for functions and classes
- Include type hints where helpful

### Shell Scripts

- Use bash 4.0+ features
- Add comments explaining complex logic
- Use meaningful variable names
- Handle errors with `set -euo pipefail`
- Add help text with `--help` flag

### Documentation

- Update README.md for each project
- Include usage examples
- Document all command-line options
- Add example error scenarios

## 🧪 Testing

Before submitting a PR:

1. **Test locally** with a real MuleSoft project
2. **Test edge cases** (empty projects, missing files, etc.)
3. **Test help output**: `python script.py --help`
4. **Test error handling**: Invalid paths, malformed files, etc.
5. **Check output formats**: Both text and JSON (if supported)

## 📋 Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated (README.md)
- [ ] No new warnings generated
- [ ] Tested locally with real projects
- [ ] All existing tests pass (if applicable)

## 🏗️ Project Structure

Each project is independent:

```
project-name/
├── README.md          # Project documentation
├── script.py          # Main script
└── (optional files)   # Additional files if needed
```

## 🎨 Adding a New Project

1. Create a new folder in the root directory
2. Add your script(s) and README.md
3. Update main README.md with your project
4. Follow the existing project structure
5. Add to CI/CD workflows if needed

## ❓ Questions?

- Open an issue with the `question` label
- Check existing issues and discussions
- Review existing code for examples

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to MuleSoft Developer Scripts!** 🚀

