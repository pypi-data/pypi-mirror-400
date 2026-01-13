# 📦 Example Projects for Testing

This directory contains sample MuleSoft projects and test data to help you test all the scripts without needing real MuleSoft projects.

## 📁 Directory Structure

### `sample-mule-project/`
A **clean, well-structured** MuleSoft project that should pass most validations:
- ✅ Valid `mule-artifact.json`
- ✅ All properties defined
- ✅ Proper HTTP listeners
- ✅ RAML API specification
- ✅ MUnit tests included

**Use this to test:**
- Config validator (should pass)
- API validator (should pass)
- Security scanner (should pass)
- MUnit analyzer (should show coverage)

### `sample-mule-project-with-issues/`
A **problematic** MuleSoft project with intentional issues:
- ❌ Missing `minMuleVersion` in mule-artifact.json
- ❌ Missing properties referenced in XML
- ❌ Insecure HTTP listener
- ❌ Hardcoded secrets
- ❌ No MUnit tests

**Use this to test:**
- Config validator (should find missing properties)
- Security scanner (should find hardcoded secrets)
- API validator (should find insecure HTTP)
- MUnit analyzer (should show low coverage)

### `sample-logs/`
Sample log files for testing the log analyzer:
- `application.log` - Contains various log levels, correlation IDs, errors, and patterns

**Use this to test:**
- Log analyzer (should find correlation IDs, errors, flooding patterns)

## 🚀 Quick Test Guide

### Test Config Validator

```bash
# Test with good project (should pass)
cd config-validator
python validate-properties.py --project-path ../examples/sample-mule-project

# Test with problematic project (should find issues)
python validate-properties.py --project-path ../examples/sample-mule-project-with-issues
```

### Test Security Scanner

```bash
# Test with problematic project (should find secrets)
cd security-scanner
python secret-scan.py --path ../examples/sample-mule-project-with-issues --verbose
```

### Test API Validator

```bash
# Test with good project
cd api-validator
python raml-vs-flow-check.py --project-path ../examples/sample-mule-project --verbose
```

### Test MUnit Analyzer

```bash
# Test with good project
cd munit-analyzer
python munit-coverage.py --project-path ../examples/sample-mule-project --verbose
```

### Test Log Analyzer

```bash
# Test with sample logs
cd log-analyzer
python analyze-logs.py ../examples/sample-logs/application.log --verbose
```

### Test Runtime Diagnostics

```bash
# Test with good project
cd runtime-diagnostics
./mule-runtime-check.sh ../examples/sample-mule-project
```

## 🧪 Run All Tests

Use the test script to validate all tools:

```bash
cd examples
./test-all-scripts.sh
```

## 📝 Notes

- These are **simplified examples** for testing purposes
- Real MuleSoft projects will have more complex structures
- Some validations may behave differently with real projects
- Feel free to modify these examples to test specific scenarios

## 🔧 Customizing Examples

You can modify these examples to:
- Test specific error scenarios
- Add more complex configurations
- Test edge cases
- Demonstrate specific issues

---

**Happy Testing!** 🚀

